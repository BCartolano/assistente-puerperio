#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Teste rápido da API com dados reais"""

import sys
import os

# Configuração de encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

import requests
import json

# Teste 1: Centro de SP
print("=" * 80)
print("🧪 TESTE DE API - Dados Reais do CNES")
print("=" * 80)

payload = {
    "latitude": -23.5505,
    "longitude": -46.6333,
    "radius_km": 5,  # Raio menor para teste mais rápido
    "filter_type": "ALL",
    "is_emergency": False
}

try:
    r = requests.post('http://localhost:5000/api/v1/facilities/search', json=payload, timeout=30)
    r.raise_for_status()
    data = r.json()
    
    print(f"\n📍 Busca: Centro de São Paulo (raio 10km)")
    print(f"✅ Total encontrado: {data['meta']['total_results']} estabelecimentos")
    print(f"\n📋 Primeiros 5 resultados:")
    
    for i, result in enumerate(data['results'][:5], 1):
        tags = result.get('tags', {})
        print(f"\n{i}. {result['name']}")
        print(f"   Tipo: {result.get('type', 'N/A')}")
        print(f"   SUS: {'✅' if tags.get('sus') else '❌'}")
        print(f"   Maternidade: {'✅' if tags.get('maternity') else '❌'}")
        print(f"   UPA: {'✅' if tags.get('emergency_only') else '❌'}")
        print(f"   Distância: {result.get('distance_km', 0):.2f} km")
        if result.get('warning_message'):
            print(f"   ⚠️  Aviso: {result['warning_message']}")
    
    # Estatísticas dos resultados
    sus_count = sum(1 for r in data['results'] if r.get('tags', {}).get('sus'))
    privado_count = len(data['results']) - sus_count
    maternidade_count = sum(1 for r in data['results'] if r.get('tags', {}).get('maternity'))
    upa_count = sum(1 for r in data['results'] if r.get('tags', {}).get('emergency_only'))
    
    print(f"\n📊 Estatísticas dos resultados:")
    print(f"   🔵 SUS: {sus_count} ({sus_count/len(data['results'])*100:.1f}%)")
    print(f"   🟢 Privado: {privado_count} ({privado_count/len(data['results'])*100:.1f}%)")
    print(f"   👶 Maternidade: {maternidade_count}")
    print(f"   🟡 UPA: {upa_count}")
    
    print("\n" + "=" * 80)
    print("✅ API funcionando corretamente com dados reais!")
    print("=" * 80)
    
except requests.exceptions.RequestException as e:
    print(f"\n❌ Erro ao chamar API: {e}")
except Exception as e:
    print(f"\n❌ Erro: {e}")
    import traceback
    traceback.print_exc()
