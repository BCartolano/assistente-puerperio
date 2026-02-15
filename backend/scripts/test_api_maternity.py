#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Direto da API de Maternidade
Purpose: Testar a API diretamente para ver o que está sendo retornado
"""

import os
import sys
import json

# Configuração de encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Adicionar path do backend
backend_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, backend_path)
sys.path.insert(0, os.path.dirname(backend_path))

try:
    from services.facility_service import FacilityService
except ImportError:
    from backend.services.facility_service import FacilityService

def test_api_maternity():
    """Testa a API diretamente com filter_type=MATERNITY"""
    print("="*70)
    print("TESTE DIRETO DA API DE MATERNIDADE")
    print("="*70)
    print()
    
    service = FacilityService()
    
    # Coordenadas do usuário (do log: lat=-23.1931904, lon=-45.7998336)
    lat = -23.1931904
    lon = -45.7998336
    
    print(f"[TESTE] Buscando hospitais maternos próximos...")
    print(f"   Coordenadas: lat={lat}, lon={lon}")
    print(f"   Filtro: MATERNITY")
    print(f"   Raio: 50km")
    print()
    
    try:
        results, _, _ = service.search_facilities(
            latitude=lat,
            longitude=lon,
            radius_km=50,
            filter_type="MATERNITY",
            is_emergency=True,
            search_mode="all"
        )
        
        print(f"[RESULTADO] API retornou {len(results)} estabelecimentos")
        print()
        
        # Analisar resultados
        upas = []
        ubs = []
        outros = []
        hospitais = []
        
        for result in results:
            tipo = result.get('type', '')
            name = result.get('display_name') or result.get('name', 'Sem nome')
            is_emergency_only = result.get('tags', {}).get('emergency_only', False)
            has_maternity = result.get('tags', {}).get('maternity', False)
            
            # Verificar se é UPA
            if tipo == 'UPA' or tipo == '73' or is_emergency_only or 'UPA' in name.upper():
                upas.append({
                    'name': name,
                    'type': tipo,
                    'is_emergency_only': is_emergency_only,
                    'has_maternity': has_maternity
                })
            # Verificar se é UBS
            elif tipo == 'UBS' or tipo in ('01', '02', '15', '40'):
                ubs.append({
                    'name': name,
                    'type': tipo
                })
            # Verificar se é hospital
            elif tipo == 'HOSPITAL' or tipo in ('05', '07'):
                hospitais.append({
                    'name': name,
                    'type': tipo,
                    'has_maternity': has_maternity
                })
            else:
                outros.append({
                    'name': name,
                    'type': tipo
                })
        
        # Resultado
        print("="*70)
        print("ANÁLISE DOS RESULTADOS")
        print("="*70)
        
        if upas:
            print(f"\n[ERRO CRÍTICO] {len(upas)} UPA(s) encontrada(s):")
            for upa in upas[:10]:
                print(f"   - {upa['name']} (Tipo: {upa['type']}, Emergency Only: {upa['is_emergency_only']})")
            if len(upas) > 10:
                print(f"   ... e mais {len(upas) - 10} UPAs")
        
        if ubs:
            print(f"\n[ERRO CRÍTICO] {len(ubs)} UBS encontrada(s):")
            for ubs_item in ubs[:10]:
                print(f"   - {ubs_item['name']} (Tipo: {ubs_item['type']})")
            if len(ubs) > 10:
                print(f"   ... e mais {len(ubs) - 10} UBS")
        
        if outros:
            print(f"\n[ERRO CRÍTICO] {len(outros)} outros tipos encontrados:")
            for outro in outros[:10]:
                print(f"   - {outro['name']} (Tipo: {outro['type']})")
            if len(outros) > 10:
                print(f"   ... e mais {len(outros) - 10} outros")
        
        print(f"\n[OK] {len(hospitais)} hospital(is) encontrado(s):")
        for i, hosp in enumerate(hospitais[:10], 1):
            print(f"   {i}. {hosp['name']} (Tipo: {hosp['type']}, Maternidade: {hosp['has_maternity']})")
        if len(hospitais) > 10:
            print(f"   ... e mais {len(hospitais) - 10} hospitais")
        
        print()
        print("="*70)
        print("RESULTADO FINAL")
        print("="*70)
        
        if upas or ubs or outros:
            print("[FALHA] API está retornando UPAs/UBS/Outros quando deveria retornar APENAS hospitais!")
            return False
        else:
            print("[SUCESSO] API retornou APENAS hospitais com maternidade!")
            return True
            
    except Exception as e:
        print(f"[ERRO] Erro ao executar teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_api_maternity()
    sys.exit(0 if success else 1)
