#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de Cálculo Geoespacial
Purpose: Implementar Fórmula de Haversine para cálculo de distância
"""

import math
from typing import Tuple


def haversine_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    Calcula a distância entre dois pontos geográficos usando a fórmula de Haversine
    
    Args:
        lat1: Latitude do primeiro ponto
        lon1: Longitude do primeiro ponto
        lat2: Latitude do segundo ponto
        lon2: Longitude do segundo ponto
    
    Returns:
        Distância em quilômetros
    """
    # Raio da Terra em km
    R = 6371.0
    
    # Converter graus para radianos
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Diferença de coordenadas
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Fórmula de Haversine
    a = (
        math.sin(dlat / 2) ** 2 +
        math.cos(lat1_rad) *
        math.cos(lat2_rad) *
        math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Distância em km
    distance = R * c
    
    return distance


def calculate_distance_km(
    user_location: Tuple[float, float],
    facility_location: Tuple[float, float]
) -> float:
    """
    Calcula distância entre localização do usuário e facilidade
    
    Args:
        user_location: (latitude, longitude) do usuário
        facility_location: (latitude, longitude) da facilidade
    
    Returns:
        Distância em quilômetros
    """
    lat1, lon1 = user_location
    lat2, lon2 = facility_location
    
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return float('inf')  # Retorna infinito se coordenadas inválidas
    
    return haversine_distance(lat1, lon1, lat2, lon2)


def filter_by_radius(
    facilities: list,
    user_lat: float,
    user_lon: float,
    radius_km: float
) -> list:
    """
    Filtra facilidades dentro do raio especificado
    
    Args:
        facilities: Lista de dicionários com facilidades (devem ter 'lat' e 'long')
        user_lat: Latitude do usuário
        user_lon: Longitude do usuário
        radius_km: Raio em km
    
    Returns:
        Lista de facilidades dentro do raio, com 'distance_km' adicionado
    """
    filtered = []
    
    for facility in facilities:
        facility_lat = facility.get('lat')
        facility_lon = facility.get('long')
        
        if facility_lat is None or facility_lon is None:
            continue  # Pula facilidades sem coordenadas
        
        distance = haversine_distance(user_lat, user_lon, facility_lat, facility_lon)
        
        if distance <= radius_km:
            facility['distance_km'] = round(distance, 2)
            filtered.append(facility)
    
    # Ordena por distância (mais próximo primeiro)
    filtered.sort(key=lambda x: x.get('distance_km', float('inf')))
    
    return filtered
