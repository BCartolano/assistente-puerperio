#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para o sistema de busca espacial
Testa busca de maternidades próximas usando BallTree

Uso:
    python scripts/test_spatial_search.py
"""

import sys
import os

# Adiciona backend ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.services.spatial_search_service import get_spatial_service
import time

def testar_busca():
    """Testa busca de maternidades próximas"""
    print("🔍 Testando sistema de busca espacial...")
    
    service = get_spatial_service()
    
    if not service.esta_disponivel():
        print("❌ Serviço não disponível. Execute process_cnes_optimized.py primeiro!")
        return
    
    # Coordenadas de teste (São Paulo - Avenida Paulista)
    lat = -23.5505
    lon = -46.6333
    raio_km = 20
    
    print(f"\n📍 Buscando maternidades próximas de:")
    print(f"   Latitude: {lat}")
    print(f"   Longitude: {lon}")
    print(f"   Raio: {raio_km} km")
    
    # Teste de performance
    inicio = time.time()
    resultados = service.buscar_proximas(
        lat=lat,
        lon=lon,
        raio_km=raio_km,
        limite=10
    )
    tempo_ms = (time.time() - inicio) * 1000
    
    print(f"\n⏱️ Tempo de busca: {tempo_ms:.2f} ms")
    print(f"✅ Encontrados {len(resultados)} hospitais\n")
    
    # Mostra resultados
    for i, hospital in enumerate(resultados[:5], 1):
        print(f"{i}. {hospital.get('nome_fantasia', 'N/A')}")
        print(f"   📍 {hospital.get('endereco_completo', 'N/A')}")
        print(f"   📞 {hospital.get('telefone', 'N/A')}")
        print(f"   🏥 {hospital.get('categoria', 'N/A')}")
        print(f"   📏 {hospital.get('distancia_km', 0):.2f} km")
        print()
    
    if len(resultados) > 5:
        print(f"... e mais {len(resultados) - 5} hospitais\n")
    
    print("✅ Teste concluído com sucesso!")

if __name__ == '__main__':
    testar_busca()
