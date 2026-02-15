#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Específico: Verificar que filtro MATERNITY exclui UPAs
Purpose: Validar que busca de maternidades NÃO retorna UPAs
"""

import os
import sys
import sqlite3

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

def test_maternity_excludes_upas():
    """Testa que busca MATERNITY não retorna UPAs"""
    print("="*70)
    print("TESTE CRÍTICO: Filtro MATERNITY deve EXCLUIR UPAs")
    print("="*70)
    print()
    
    service = FacilityService()
    
    # Coordenadas de São Paulo (exemplo)
    lat = -23.5505
    lon = -46.6333
    
    print(f"[TESTE] Buscando hospitais maternos próximos de SP...")
    print(f"   Coordenadas: lat={lat}, lon={lon}")
    print(f"   Filtro: MATERNITY")
    print()
    
    try:
        results, _, _ = service.search_facilities(
            latitude=lat,
            longitude=lon,
            radius_km=20,
            filter_type="MATERNITY",
            is_emergency=True,
            search_mode="all"
        )
        
        print(f"[RESULTADO] Encontrados {len(results)} estabelecimentos")
        print()
        
        # Verificar se há UPAs nos resultados
        upas_encontradas = []
        hospitais_encontrados = []
        
        for result in results:
            tipo = result.get('type', '')
            is_emergency_only = result.get('tags', {}).get('emergency_only', False)
            has_maternity = result.get('tags', {}).get('maternity', False)
            name = result.get('display_name') or result.get('name', 'Sem nome')
            
            # Verificar se é UPA
            if tipo == 'UPA' or tipo == '73' or is_emergency_only:
                upas_encontradas.append({
                    'name': name,
                    'type': tipo,
                    'is_emergency_only': is_emergency_only,
                    'has_maternity': has_maternity
                })
            else:
                hospitais_encontrados.append({
                    'name': name,
                    'type': tipo,
                    'has_maternity': has_maternity
                })
        
        # Resultado do teste
        print("="*70)
        print("RESULTADO DO TESTE")
        print("="*70)
        
        if upas_encontradas:
            print(f"[ERRO CRITICO] {len(upas_encontradas)} UPA(s) encontrada(s) na busca de maternidades!")
            print()
            print("UPAs encontradas (NAO DEVERIAM APARECER):")
            for upa in upas_encontradas:
                print(f"   - {upa['name']} (Tipo: {upa['type']}, Maternidade: {upa['has_maternity']})")
            print()
            print("[FALHA] Filtro MATERNITY esta retornando UPAs!")
            return False
        else:
            print(f"[SUCESSO] Nenhuma UPA encontrada na busca de maternidades")
            print()
            print(f"[OK] {len(hospitais_encontrados)} hospital(is) materno(s) encontrado(s):")
            for i, hosp in enumerate(hospitais_encontrados[:10], 1):  # Mostrar apenas 10 primeiros
                print(f"   {i}. {hosp['name']} (Tipo: {hosp['type']}, Maternidade: {hosp['has_maternity']})")
            if len(hospitais_encontrados) > 10:
                print(f"   ... e mais {len(hospitais_encontrados) - 10} hospitais")
            print()
            print("[OK] TESTE PASSOU: Filtro MATERNITY esta funcionando corretamente!")
            return True
            
    except Exception as e:
        print(f"[ERRO] Erro ao executar teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_maternity_excludes_upas()
    sys.exit(0 if success else 1)
