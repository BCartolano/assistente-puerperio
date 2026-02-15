# -*- coding: utf-8 -*-
"""
Rota Flask para buscar hospitais próximos usando PostGIS ou BallTree
Endpoint: /api/hospitais-proximos

Prioridade:
1. PostgreSQL + PostGIS (se disponível) - mais rápido e escalável
2. BallTree (fallback) - funciona com CSV processado

Regras: raio máximo 50 km; endereço exibido via reverse geocoding (Nominatim) quando faltar; não exibir lat/lon para a mãe.
"""

from flask import Blueprint, request, jsonify
from sqlalchemy import text
import logging
import time

try:
    from flask_login import current_user
except ImportError:
    current_user = None

from backend.services.postgres_service import get_postgres_engine, is_postgres_available
from backend.services.spatial_search_service import get_spatial_service
from backend.services.osrm_service import get_osrm_service, gerar_link_google_maps, gerar_link_waze

logger = logging.getLogger(__name__)

# Cache simples para evitar repetir reverse geocode na mesma requisição
_nominatim_cache = {}
_NOMINATIM_LAST_CALL = 0.0
_NOMINATIM_MIN_INTERVAL = 1.0  # 1 req/seg (política Nominatim)


def _reverse_geocode_nominatim(lat, lon):
    """Converte coordenadas em endereço legível (Rua, Bairro, Cidade) via OpenStreetMap Nominatim (gratuito)."""
    if lat is None or lon is None:
        return None
    key = (round(float(lat), 5), round(float(lon), 5))
    if key in _nominatim_cache:
        return _nominatim_cache[key]
    global _NOMINATIM_LAST_CALL
    now = time.time()
    if now - _NOMINATIM_LAST_CALL < _NOMINATIM_MIN_INTERVAL:
        time.sleep(_NOMINATIM_MIN_INTERVAL - (now - _NOMINATIM_LAST_CALL))
    try:
        import requests
        r = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json"},
            headers={"User-Agent": "Sophia-Puerperio/1.0"},
            timeout=5,
        )
        _NOMINATIM_LAST_CALL = time.time()
        if r.status_code != 200:
            return None
        data = r.json()
        addr = data.get("address") or {}
        parts = [
            addr.get("road") or addr.get("street"),
            addr.get("house_number"),
            addr.get("suburb") or addr.get("neighbourhood") or addr.get("quarter"),
            addr.get("city") or addr.get("town") or addr.get("municipality") or addr.get("county"),
            addr.get("state"),
        ]
        parts = [str(p).strip() for p in parts if p]
        display = data.get("display_name") or ", ".join(parts) if parts else None
        if display:
            _nominatim_cache[key] = display
        return display
    except Exception as e:
        logger.debug("Nominatim reverse geocode falhou: %s", e)
        return None

hospitais_bp = Blueprint('hospitais', __name__)


@hospitais_bp.route('/api/hospitais-proximos', methods=['GET'])
def hospitais_proximos():
    """
    Busca hospitais com maternidade próximos usando PostGIS ou BallTree
    
    Query params:
        lat (float): Latitude do ponto de busca
        lon (float): Longitude do ponto de busca
        radius_km (float, opcional): Raio de busca em km (padrão: 50km)
        limit (int, opcional): Limite de resultados (padrão: 10)
        categoria (str, opcional): Filtrar por 'Público' ou 'Privado'
        apenas_com_telefone (bool, opcional): Filtrar apenas com telefone (padrão: False)
    
    Returns:
        JSON com lista de hospitais ordenados por distância
    """
    # Tenta usar PostgreSQL primeiro, depois BallTree como fallback
    use_postgres = is_postgres_available()
    use_balltree = False
    
    if not use_postgres:
        spatial_service = get_spatial_service()
        use_balltree = spatial_service.esta_disponivel()
        
        if not use_balltree:
            logger.warning("⚠️ Nenhum sistema de busca disponível")
            return jsonify({
                "erro": "Serviço temporariamente indisponível",
                "mensagem": "Banco de dados não está configurado. Execute o script de processamento primeiro."
            }), 503
    
    try:
        # Obtém parâmetros da query string
        lat = float(request.args.get('lat', 0))
        lon = float(request.args.get('lon', 0))
        radius_km = float(request.args.get('radius_km', 50))
        radius_km = min(50.0, max(0.1, radius_km))  # Limite máximo 50 km no backend
        limit = int(request.args.get('limit', 10))
        categoria = request.args.get('categoria')  # 'Público' ou 'Privado'
        apenas_com_telefone = request.args.get('apenas_com_telefone', 'false').lower() in ('true', '1', 'sim', 's')
        
        # Validação básica
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return jsonify({
                "erro": "Coordenadas inválidas",
                "mensagem": "Latitude deve estar entre -90 e 90, longitude entre -180 e 180"
            }), 400
        
        try:
            uid = str(current_user.id) if current_user and getattr(current_user, 'is_authenticated', False) else 'anon'
        except Exception:
            uid = 'anon'
        logger.info("[LOGIN] Usuário %s acessando de: %s, %s", uid, lat, lon)
        print("[LOGIN] Usuário {} acessando de: {}, {}".format(uid, lat, lon))
        
        if radius_km <= 0 or radius_km > 50:
            return jsonify({
                "erro": "Raio inválido",
                "mensagem": "Raio deve estar entre 0 e 50 km"
            }), 400
        
        if limit <= 0 or limit > 100:
            return jsonify({
                "erro": "Limite inválido",
                "mensagem": "Limite deve estar entre 1 e 100"
            }), 400
        
        hospitais = []
        
        # Usa PostgreSQL + PostGIS se disponível
        if use_postgres:
            sql_query = text("""
                SELECT 
                    cnes,
                    nome_fantasia,
                    logradouro,
                    bairro,
                    municipio,
                    uf,
                    telefone,
                    tem_maternidade,
                    tem_uti_neonatal,
                    aceita_sus,
                    convenio,
                    particular,
                    latitude,
                    longitude,
                    ROUND(
                        ST_Distance(
                            geom::geography, 
                            ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography
                        ) / 1000.0, 
                        1
                    ) AS distancia_km
                FROM estabelecimentos_saude 
                WHERE 
                    geom IS NOT NULL
                    AND ST_DWithin(
                        geom::geography, 
                        ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography, 
                        :radius_meters
                    )
                    AND tem_maternidade = TRUE
                ORDER BY distancia_km ASC
                LIMIT :limit_result;
            """)
            
            engine = get_postgres_engine()
            with engine.connect() as conn:
                result = conn.execute(
                    sql_query,
                    {
                        "lat": lat,
                        "lon": lon,
                        "radius_meters": radius_km * 1000,
                        "limit_result": limit
                    }
                )
                
                for row in result:
                    hospitais.append({
                        "cnes": row.cnes,
                        "nome_fantasia": row.nome_fantasia,
                        "logradouro": row.logradouro,
                        "bairro": row.bairro,
                        "municipio": row.municipio,
                        "uf": row.uf,
                        "telefone": row.telefone,
                        "tem_maternidade": row.tem_maternidade,
                        "tem_uti_neonatal": row.tem_uti_neonatal,
                        "aceita_sus": row.aceita_sus,
                        "convenio": row.convenio,
                        "particular": row.particular,
                        "distancia_km": float(row.distancia_km) if row.distancia_km else None,
                        "latitude": float(row.latitude) if row.latitude else None,
                        "longitude": float(row.longitude) if row.longitude else None
                    })
        
        # Fallback: usa BallTree se PostgreSQL não estiver disponível
        elif use_balltree:
            resultados = spatial_service.buscar_proximas(
                lat=lat,
                lon=lon,
                raio_km=radius_km,
                limite=limit,
                categoria=categoria,
                apenas_com_telefone=apenas_com_telefone
            )
            
            for row in resultados:
                hospitais.append({
                    "cnes": row.get('cnes', ''),
                    "nome_fantasia": row.get('nome_fantasia', ''),
                    "logradouro": row.get('logradouro', ''),
                    "bairro": row.get('bairro', ''),
                    "municipio": row.get('municipio', ''),
                    "uf": row.get('uf', ''),
                    "telefone": row.get('telefone', ''),
                    "categoria": row.get('categoria', ''),
                    "endereco_completo": row.get('endereco_completo', ''),
                    "distancia_km": row.get('distancia_km', 0),
                    "latitude": float(row.get('latitude', 0)) if row.get('latitude') else None,
                    "longitude": float(row.get('longitude', 0)) if row.get('longitude') else None,
                    # Campos adicionais para compatibilidade com formatação de card
                    "tem_maternidade": row.get('tem_maternidade', True),
                    "tem_uti_neonatal": row.get('tem_uti_neonatal', False),
                    "aceita_sus": row.get('aceita_sus', False),
                    "convenio": row.get('convenio', False),
                    "particular": row.get('particular', False)
                })
        
        # Ordena por tempo de viagem real usando OSRM (100% gratuito)
        ordenar_por_tempo = request.args.get('ordenar_por_tempo', 'true').lower() in ('true', '1', 'sim', 's')
        
        if ordenar_por_tempo and len(hospitais) > 0:
            osrm = get_osrm_service()
            if osrm.esta_disponivel():
                logger.info("🚗 Ordenando por tempo de viagem real (OSRM - gratuito)...")
                # Limita a 10 para otimizar chamadas (OSRM público tem rate limit)
                top_hospitais = hospitais[:min(10, len(hospitais))]
                hospitais_ordenados = osrm.ordenar_por_tempo_real(
                    lat_user=lat,
                    lon_user=lon,
                    lista_hospitais=top_hospitais,
                    usar_cache=True  # Cache de 5 minutos
                )
                # Mantém apenas o limite solicitado
                hospitais = hospitais_ordenados[:limit]
                logger.info(f"✅ Ordenação por tempo real concluída (OSRM)")
            else:
                logger.warning("⚠️ OSRM não disponível, ordenando por distância linear")
        
        # Formata dados para cards de emergência
        hospitais_formatados = []
        for h in hospitais:
            telefone = h.get('telefone', '')
            telefone_limpo = telefone.replace('(', '').replace(')', '').replace('-', '').replace(' ', '')
            
            # Monta endereço completo
            endereco_parts = []
            if h.get('logradouro'):
                endereco_parts.append(h.get('logradouro'))
            if h.get('bairro'):
                endereco_parts.append(h.get('bairro'))
            if h.get('municipio'):
                endereco_parts.append(h.get('municipio'))
            if h.get('uf'):
                endereco_parts.append(h.get('uf'))
            endereco_completo = ' - '.join(endereco_parts) if endereco_parts else (h.get('endereco_completo', '') or '')
            if not endereco_completo:
                # Reverse geocoding (Nominatim) para exibir endereço em vez de lat/lon para a mãe
                addr = _reverse_geocode_nominatim(lat_hosp, lon_hosp)
                endereco_completo = addr or 'Endereço não disponível'
            
            # Formata informações de pagamento
            natureza = h.get('categoria', '') or h.get('tipo', '')
            sus = "Aceita Cartão SUS" if h.get('aceita_sus', False) else ""
            convenio = h.get('convenio', False)
            particular = h.get('particular', False)
            
            metodos_pagamento = []
            if sus:
                metodos_pagamento.append(sus)
            if convenio:
                metodos_pagamento.append("Aceita Convênios")
            if particular:
                metodos_pagamento.append("Aceita Particular")
            
            pagamento_texto = " / ".join(metodos_pagamento) if metodos_pagamento else "Informação não disponível"
            
            # Se não tem métodos de pagamento mas tem tipo, usa o tipo
            if not metodos_pagamento and natureza:
                pagamento_texto = natureza
            
            # Links gratuitos para GPS (Google Maps Web e Waze)
            lat_hosp = h.get('latitude')
            lon_hosp = h.get('longitude')
            link_gps = ""
            link_waze = ""
            if lat_hosp and lon_hosp:
                link_gps = gerar_link_google_maps(lat_hosp, lon_hosp)
                link_waze = gerar_link_waze(lat_hosp, lon_hosp)
            
            link_ligar = f"tel:{telefone_limpo}" if telefone_limpo else ""
            
            # Não expor lat/lon no resultado (exibir apenas endereço para a mãe)
            card = {
                "cnes": h.get('cnes', ''),
                "nome": h.get('nome_fantasia', ''),
                "endereco_exato": endereco_completo,
                "telefone": telefone,
                "telefone_limpo": telefone_limpo,
                "natureza": natureza,
                "sus": sus,
                "metodos_pagamento": pagamento_texto,
                "tem_maternidade": h.get('tem_maternidade', True),
                "tem_uti_neonatal": h.get('tem_uti_neonatal', False),
                "estimativa": h.get('estimativa', f"{h.get('distancia_km', 0):.1f} km"),
                "distancia": f"{h.get('distancia_km', 0):.1f} km",
                "distancia_rua": h.get('distancia_rua', ''),
                "tempo_estimado": h.get('tempo_estimado', ''),
                "segundos_total": h.get('segundos_total', 0),
                "link_gps": link_gps,
                "link_waze": link_waze,
                "link_ligar": link_ligar,
                "tipo": natureza
            }
            hospitais_formatados.append(card)
        
        logger.info(f"✅ Encontrados {len(hospitais_formatados)} hospitais próximos (lat={lat}, lon={lon}, raio={radius_km}km, método={'PostGIS' if use_postgres else 'BallTree'})")
        
        return jsonify({
            "items": hospitais_formatados,
            "count": len(hospitais_formatados),
            "meta": {
                "lat": lat,
                "lon": lon,
                "radius_km": radius_km,
                "limit": limit,
                "categoria": categoria,
                "metodo": "PostGIS" if use_postgres else "BallTree",
                "ordenado_por_tempo": ordenar_por_tempo and get_osrm_service().esta_disponivel(),
                "roteamento": "OSRM (gratuito)" if ordenar_por_tempo else "distância linear"
            }
        }), 200
        
    except ValueError as e:
        logger.warning(f"⚠️ Erro de validação: {e}")
        return jsonify({
            "erro": "Parâmetros inválidos",
            "mensagem": str(e)
        }), 400
    except Exception as e:
        logger.error(f"❌ Erro ao buscar hospitais: {e}", exc_info=True)
        return jsonify({
            "erro": "Erro interno do servidor",
            "mensagem": "Ocorreu um erro ao processar a busca. Tente novamente."
        }), 500
