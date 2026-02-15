#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para geocodificar endereços que não têm coordenadas
Usa GeoPy com Nominatim (OpenStreetMap) - GRATUITO mas com rate limit

Uso:
    python scripts/geocodificar_enderecos.py data/maternidades_processadas.csv

IMPORTANTE: 
- Use RateLimiter para respeitar limites do Nominatim (1 req/segundo)
- Para grandes volumes, considere usar API paga (Google Maps, Mapbox)
"""

import pandas as pd
import sys
import os
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def geocodificar_endereco(geocode_func, endereco, max_tentativas=3):
    """
    Tenta geocodificar um endereço com retry automático
    
    Args:
        geocode_func: Função de geocodificação (com rate limiter)
        endereco: String com endereço completo
        max_tentativas: Número máximo de tentativas
    
    Returns:
        Tupla (latitude, longitude) ou (None, None) se falhar
    """
    for tentativa in range(max_tentativas):
        try:
            location = geocode_func(endereco, timeout=10)
            if location:
                return location.latitude, location.longitude
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logger.warning(f"⚠️ Tentativa {tentativa + 1} falhou para '{endereco}': {e}")
            if tentativa < max_tentativas - 1:
                time.sleep(2)  # Aguarda antes de tentar novamente
        except Exception as e:
            logger.error(f"❌ Erro inesperado ao geocodificar '{endereco}': {e}")
            break
    
    return None, None


def geocodificar_csv(caminho_csv, output_csv=None):
    """
    Geocodifica endereços que não têm coordenadas no CSV
    
    Args:
        caminho_csv: Caminho para CSV com dados
        output_csv: Caminho para salvar CSV atualizado (opcional)
    """
    logger.info(f"📂 Lendo arquivo: {caminho_csv}")
    df = pd.read_csv(caminho_csv, encoding='utf-8')
    
    # Identifica linhas sem coordenadas
    sem_coords = df[
        (df['latitude'].isna()) | (df['longitude'].isna()) |
        (df['latitude'] == 0) | (df['longitude'] == 0)
    ].copy()
    
    logger.info(f"📍 {len(sem_coords)} estabelecimentos sem coordenadas encontrados")
    
    if len(sem_coords) == 0:
        logger.info("✅ Todos os estabelecimentos já têm coordenadas!")
        return df
    
    # Configura geocodificador
    geolocator = Nominatim(user_agent="sophia_geocoder")
    # RateLimiter: 1 requisição por segundo (respeita limites do Nominatim)
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    
    # Geocodifica endereços faltantes
    logger.info("🌍 Iniciando geocodificação (isso pode levar algum tempo)...")
    coordenadas_encontradas = 0
    
    for idx, row in sem_coords.iterrows():
        # Monta endereço completo
        endereco = f"{row.get('logradouro', '')}, {row.get('numero', '')}, {row.get('bairro', '')}, {row.get('municipio', '')}, {row.get('uf', '')}, Brasil"
        endereco = endereco.replace(' ,', ',').replace(', ,', ',').strip(', ')
        
        if not endereco or endereco == ', , , , Brasil':
            logger.warning(f"⚠️ Endereço inválido na linha {idx}, pulando...")
            continue
        
        lat, lon = geocodificar_endereco(geocode, endereco)
        
        if lat and lon:
            df.at[idx, 'latitude'] = lat
            df.at[idx, 'longitude'] = lon
            coordenadas_encontradas += 1
            logger.info(f"✅ [{coordenadas_encontradas}/{len(sem_coords)}] {row.get('nome_fantasia', 'N/A')}: {lat}, {lon}")
        else:
            logger.warning(f"❌ Não foi possível geocodificar: {endereco}")
        
        # Salva progresso a cada 10 registros
        if coordenadas_encontradas % 10 == 0:
            if output_csv:
                df.to_csv(output_csv, index=False, encoding='utf-8')
                logger.info(f"💾 Progresso salvo: {coordenadas_encontradas} coordenadas encontradas")
    
    logger.info(f"\n✅ Geocodificação concluída!")
    logger.info(f"   Total processado: {len(sem_coords)}")
    logger.info(f"   Coordenadas encontradas: {coordenadas_encontradas}")
    logger.info(f"   Taxa de sucesso: {coordenadas_encontradas/len(sem_coords)*100:.1f}%")
    
    # Salva arquivo final
    if output_csv:
        df.to_csv(output_csv, index=False, encoding='utf-8')
        logger.info(f"💾 Arquivo atualizado salvo em: {output_csv}")
    else:
        # Sobrescreve arquivo original
        df.to_csv(caminho_csv, index=False, encoding='utf-8')
        logger.info(f"💾 Arquivo original atualizado: {caminho_csv}")
    
    return df


if __name__ == '__main__':
    if len(sys.argv) < 2:
        logger.error("❌ Uso: python geocodificar_enderecos.py <caminho_para_csv> [output_csv]")
        sys.exit(1)
    
    caminho_csv = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(caminho_csv):
        logger.error(f"❌ Arquivo não encontrado: {caminho_csv}")
        sys.exit(1)
    
    geocodificar_csv(caminho_csv, output_csv)
