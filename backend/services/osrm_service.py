# -*- coding: utf-8 -*-
"""
Serviço de roteamento gratuito usando OSRM (Open Source Routing Machine)
100% gratuito, baseado em OpenStreetMap
Substitui Google Maps API para reduzir custos a zero
"""

import time
import logging
from typing import List, Dict, Optional
import requests

logger = logging.getLogger(__name__)

# Cache simples em memória (TTL de 5 minutos)
_cache = {}
_cache_ttl = 300  # 5 minutos em segundos

# URL do OSRM público (para testes)
# Para produção, recomenda-se instalar via Docker para melhor performance
OSRM_BASE_URL = "http://router.project-osrm.org"


def _get_cache_key(lat: float, lon: float, hospitais_ids: List[str]) -> str:
    """Gera chave de cache baseada em coordenadas e IDs dos hospitais"""
    ids_str = ','.join(sorted(hospitais_ids))
    return f"{lat:.4f},{lon:.4f}:{ids_str}"


def _is_cache_valid(cache_entry: Dict) -> bool:
    """Verifica se entrada de cache ainda é válida"""
    if not cache_entry:
        return False
    timestamp = cache_entry.get('timestamp', 0)
    return (time.time() - timestamp) < _cache_ttl


class OSRMService:
    """Serviço para cálculo de rotas usando OSRM (gratuito)"""
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Inicializa serviço OSRM
        
        Args:
            base_url: URL base do OSRM (padrão: servidor público)
        """
        self.base_url = base_url or OSRM_BASE_URL
        logger.info(f"✅ OSRM Service inicializado (URL: {self.base_url})")
    
    def esta_disponivel(self) -> bool:
        """Verifica se o serviço está disponível"""
        try:
            # Testa conectividade com uma rota simples
            test_url = f"{self.base_url}/route/v1/driving/-46.6333,-23.5505;-46.6333,-23.5505?overview=false"
            response = requests.get(test_url, timeout=2)
            return response.status_code == 200
        except Exception:
            return False
    
    def obter_rota(
        self,
        lat_origem: float,
        lon_origem: float,
        lat_dest: float,
        lon_dest: float
    ) -> Optional[Dict]:
        """
        Obtém rota entre dois pontos usando OSRM
        
        Args:
            lat_origem: Latitude de origem
            lon_origem: Longitude de origem
            lat_dest: Latitude de destino
            lon_dest: Longitude de destino
        
        Returns:
            Dicionário com distância, duração e tempo em segundos, ou None se erro
        """
        try:
            # Formato OSRM: /route/v1/{profile}/{coordinates}?overview=false
            # coordinates: lon1,lat1;lon2,lat2
            url = (
                f"{self.base_url}/route/v1/driving/"
                f"{lon_origem},{lat_origem};{lon_dest},{lat_dest}"
                f"?overview=false&alternatives=false"
            )
            
            response = requests.get(url, timeout=5)
            
            if response.status_code != 200:
                logger.warning(f"⚠️ OSRM retornou status {response.status_code}")
                return None
            
            data = response.json()
            
            if data.get('code') != 'Ok' or not data.get('routes'):
                logger.warning(f"⚠️ OSRM retornou código: {data.get('code')}")
                return None
            
            route = data['routes'][0]
            
            # OSRM retorna distância em metros e tempo em segundos
            distancia_metros = route.get('distance', 0)
            tempo_segundos = route.get('duration', 0)
            
            distancia_km = distancia_metros / 1000.0
            tempo_minutos = tempo_segundos / 60.0
            
            return {
                "distancia_km": round(distancia_km, 1),
                "distancia_texto": f"{distancia_km:.1f} km",
                "tempo_minutos": int(tempo_minutos),
                "tempo_texto": f"{int(tempo_minutos)} min",
                "segundos_total": int(tempo_segundos)
            }
            
        except requests.exceptions.Timeout:
            logger.warning("⚠️ Timeout ao consultar OSRM")
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao consultar OSRM: {e}", exc_info=True)
            return None
    
    def ordenar_por_tempo_real(
        self,
        lat_user: float,
        lon_user: float,
        lista_hospitais: List[Dict],
        usar_cache: bool = True
    ) -> List[Dict]:
        """
        Ordena hospitais por tempo de viagem real usando OSRM (gratuito)
        
        Args:
            lat_user: Latitude do usuário
            lon_user: Longitude do usuário
            lista_hospitais: Lista de hospitais (já filtrados por proximidade)
            usar_cache: Se deve usar cache de 5 minutos
        
        Returns:
            Lista de hospitais ordenada por tempo de viagem (mais rápido primeiro)
        """
        if not lista_hospitais:
            return []
        
        # Verifica cache
        if usar_cache:
            hospitais_ids = [str(h.get('cnes', '')) for h in lista_hospitais]
            cache_key = _get_cache_key(lat_user, lon_user, hospitais_ids)
            
            if cache_key in _cache and _is_cache_valid(_cache[cache_key]):
                logger.info("✅ Usando dados do cache OSRM (5 minutos)")
                return _cache[cache_key]['resultados']
        
        hospitais_com_coords = []
        
        # Calcula tempo de viagem para cada hospital
        for hospital in lista_hospitais:
            lat_hosp = hospital.get('latitude')
            lon_hosp = hospital.get('longitude')
            
            if not lat_hosp or not lon_hosp:
                # Hospital sem coordenadas vai para o final
                hospital['segundos_total'] = float('inf')
                hospitais_com_coords.append(hospital)
                continue
            
            # Consulta OSRM para obter tempo real
            rota = self.obter_rota(
                lat_origem=lat_user,
                lon_origem=lon_user,
                lat_dest=lat_hosp,
                lon_dest=lon_hosp
            )
            
            if rota:
                hospital['distancia_rua'] = rota['distancia_texto']
                hospital['tempo_estimado'] = rota['tempo_texto']
                hospital['segundos_total'] = rota['segundos_total']
                hospital['estimativa'] = f"{rota['tempo_minutos']} min"
            else:
                # Se OSRM falhar, usa distância linear como fallback
                distancia_km = hospital.get('distancia_km', 0)
                # Estimativa aproximada: 1km = 2 minutos em média
                tempo_estimado = int(distancia_km * 2)
                hospital['tempo_estimado'] = f"~{tempo_estimado} min"
                hospital['segundos_total'] = tempo_estimado * 60
                hospital['distancia_rua'] = f"{distancia_km:.1f} km"
            
            hospitais_com_coords.append(hospital)
        
        # Ordena pelo hospital que chega mais rápido (não pelo mais perto)
        hospitais_ordenados = sorted(
            hospitais_com_coords,
            key=lambda x: x.get('segundos_total', float('inf'))
        )
        
        # Salva no cache
        if usar_cache:
            _cache[cache_key] = {
                'resultados': hospitais_ordenados,
                'timestamp': time.time()
            }
        
        logger.info(f"✅ Hospitais ordenados por tempo de viagem (OSRM)")
        return hospitais_ordenados


# Instância global (singleton)
_osrm_service = None


def get_osrm_service() -> OSRMService:
    """Retorna instância global do serviço OSRM"""
    global _osrm_service
    if _osrm_service is None:
        _osrm_service = OSRMService()
    return _osrm_service


def gerar_link_google_maps(lat: float, lon: float) -> str:
    """
    Gera link gratuito para Google Maps Web/App
    
    Args:
        lat: Latitude do destino
        lon: Longitude do destino
    
    Returns:
        URL do Google Maps
    """
    return f"https://www.google.com/maps/dir/?api=1&destination={lat},{lon}&travelmode=driving"


def gerar_link_waze(lat: float, lon: float) -> str:
    """
    Gera link gratuito para Waze App
    
    Args:
        lat: Latitude do destino
        lon: Longitude do destino
    
    Returns:
        URL do Waze
    """
    return f"https://waze.com/ul?ll={lat},{lon}&navigate=yes"
