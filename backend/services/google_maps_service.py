# -*- coding: utf-8 -*-
"""
Serviço de integração com Google Maps API
Ordena hospitais por tempo de trânsito real (crucial para emergências)
"""

import os
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from functools import lru_cache

logger = logging.getLogger(__name__)

# Cache simples em memória (TTL de 5 minutos)
_cache = {}
_cache_ttl = 300  # 5 minutos em segundos


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


class GoogleMapsService:
    """Serviço para ordenação por tempo de trânsito real"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa serviço Google Maps
        
        Args:
            api_key: Chave da API do Google Maps (opcional, busca em env)
        """
        self.api_key = api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        self.client = None
        
        if self.api_key:
            try:
                import googlemaps
                self.client = googlemaps.Client(key=self.api_key)
                logger.info("✅ Google Maps API inicializada")
            except ImportError:
                logger.warning("⚠️ googlemaps não instalado. Execute: pip install googlemaps")
            except Exception as e:
                logger.error(f"❌ Erro ao inicializar Google Maps: {e}")
        else:
            logger.warning("⚠️ GOOGLE_MAPS_API_KEY não configurada. Ordenação por distância linear será usada.")
    
    def esta_disponivel(self) -> bool:
        """Verifica se o serviço está disponível"""
        return self.client is not None
    
    def ordenar_por_tempo_real(
        self,
        lat_user: float,
        lon_user: float,
        lista_hospitais: List[Dict],
        usar_cache: bool = True
    ) -> List[Dict]:
        """
        Ordena hospitais por tempo de trânsito real usando Google Maps API
        
        Args:
            lat_user: Latitude do usuário
            lon_user: Longitude do usuário
            lista_hospitais: Lista de hospitais (já filtrados por proximidade)
            usar_cache: Se deve usar cache de 5 minutos
        
        Returns:
            Lista de hospitais ordenada por tempo de trânsito (mais rápido primeiro)
        """
        if not self.esta_disponivel():
            logger.warning("⚠️ Google Maps não disponível, ordenando por distância linear")
            return sorted(lista_hospitais, key=lambda x: x.get('distancia_km', float('inf')))
        
        if not lista_hospitais:
            return []
        
        # Verifica cache
        if usar_cache:
            hospitais_ids = [str(h.get('cnes', '')) for h in lista_hospitais]
            cache_key = _get_cache_key(lat_user, lon_user, hospitais_ids)
            
            if cache_key in _cache and _is_cache_valid(_cache[cache_key]):
                logger.info("✅ Usando dados do cache (5 minutos)")
                return _cache[cache_key]['resultados']
        
        try:
            # Prepara destinos
            destinos = []
            hospitais_com_coords = []
            
            for h in lista_hospitais:
                lat = h.get('latitude')
                lon = h.get('longitude')
                if lat and lon:
                    destinos.append(f"{lat},{lon}")
                    hospitais_com_coords.append(h)
            
            if not destinos:
                logger.warning("⚠️ Nenhum hospital com coordenadas válidas")
                return lista_hospitais
            
            # Chama API de Distance Matrix
            logger.info(f"🌐 Consultando Google Maps API para {len(destinos)} hospitais...")
            matrix = self.client.distance_matrix(
                origins=[f"{lat_user},{lon_user}"],
                destinations=destinos,
                mode="driving",
                departure_time="now",  # Crucial para emergências - usa trânsito atual
                language="pt-BR",
                units="metric"
            )
            
            # Processa resultados
            if 'rows' not in matrix or not matrix['rows']:
                logger.warning("⚠️ Resposta inválida da API do Google Maps")
                return lista_hospitais
            
            elementos = matrix['rows'][0].get('elements', [])
            
            for i, hospital in enumerate(hospitais_com_coords):
                if i < len(elementos):
                    elemento = elementos[i]
                    status = elemento.get('status', '')
                    
                    if status == 'OK':
                        # Distância
                        distancia_info = elemento.get('distance', {})
                        hospital['distancia_rua'] = distancia_info.get('text', '')
                        hospital['distancia_metros'] = distancia_info.get('value', 0)
                        
                        # Tempo (com trânsito)
                        duracao_info = elemento.get('duration_in_traffic', elemento.get('duration', {}))
                        hospital['tempo_estimado'] = duracao_info.get('text', '')
                        hospital['segundos_total'] = duracao_info.get('value', 0)
                        
                        # Formata estimativa para card
                        tempo_min = hospital['segundos_total'] // 60
                        hospital['estimativa'] = f"{tempo_min} min (com trânsito)"
                    else:
                        logger.warning(f"⚠️ Status inválido para hospital {hospital.get('nome_fantasia')}: {status}")
                        # Valores padrão se API falhar
                        hospital['tempo_estimado'] = 'Indisponível'
                        hospital['segundos_total'] = float('inf')
            
            # Ordena pelo hospital que chega mais rápido (não pelo mais perto)
            hospitais_ordenados = sorted(
                hospitais_com_coords,
                key=lambda x: x.get('segundos_total', float('inf'))
            )
            
            # Adiciona hospitais sem coordenadas no final
            hospitais_sem_coords = [h for h in lista_hospitais if not (h.get('latitude') and h.get('longitude'))]
            hospitais_ordenados.extend(hospitais_sem_coords)
            
            # Salva no cache
            if usar_cache:
                _cache[cache_key] = {
                    'resultados': hospitais_ordenados,
                    'timestamp': time.time()
                }
            
            logger.info(f"✅ Hospitais ordenados por tempo de trânsito real")
            return hospitais_ordenados
            
        except Exception as e:
            logger.error(f"❌ Erro ao consultar Google Maps API: {e}", exc_info=True)
            # Fallback: ordena por distância linear
            return sorted(lista_hospitais, key=lambda x: x.get('distancia_km', float('inf')))


# Instância global (singleton)
_google_maps_service = None


def get_google_maps_service() -> GoogleMapsService:
    """Retorna instância global do serviço Google Maps"""
    global _google_maps_service
    if _google_maps_service is None:
        _google_maps_service = GoogleMapsService()
    return _google_maps_service
