#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste da Query de Maternidade
Purpose: Testar a query exata que é usada no filtro MATERNITY
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

# Caminho do banco
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'cnes_cache.db')

def test_maternity_query():
    """Testa a query exata do filtro MATERNITY"""
    print("="*70)
    print("TESTE DA QUERY DE MATERNIDADE")
    print("="*70)
    print()
    
    if not os.path.exists(DB_PATH):
        print(f"[ERRO] Banco de dados não encontrado: {DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Query exata do filtro MATERNITY
    query = """
        SELECT 
            cnes_id,
            name,
            fantasy_name,
            tipo_unidade,
            has_maternity,
            is_emergency_only,
            state
        FROM hospitals_cache
        WHERE lat IS NOT NULL 
          AND long IS NOT NULL
          AND tipo_unidade IN ('05', '07', 'HOSPITAL')
          AND tipo_unidade NOT IN ('73', 'UPA', '01', '02', '15', '40', 'UBS', '32', '71', '72')
          AND is_emergency_only = 0
          AND has_maternity = 1
        LIMIT 20
    """
    
    print("[QUERY] Executando query do filtro MATERNITY...")
    cursor.execute(query)
    resultados = cursor.fetchall()
    
    print(f"\n[RESULTADO] {len(resultados)} registros encontrados\n")
    
    # Verificar cada resultado
    problemas = []
    for i, row in enumerate(resultados, 1):
        tipo = row['tipo_unidade']
        is_emergency = row['is_emergency_only']
        has_maternity = row['has_maternity']
        name = row['name'] or row['fantasy_name'] or 'Sem nome'
        
        # Verificar se é UPA
        if tipo in ('73', 'UPA') or is_emergency == 1:
            problemas.append(f"UPA encontrada: {name} (Tipo: {tipo}, is_emergency_only: {is_emergency})")
        
        # Verificar se é UBS
        if tipo in ('01', '02', '15', '40', 'UBS', '32', '71', '72'):
            problemas.append(f"UBS encontrada: {name} (Tipo: {tipo})")
        
        # Verificar se não é hospital
        if tipo not in ('05', '07', 'HOSPITAL'):
            problemas.append(f"Tipo não hospitalar: {name} (Tipo: {tipo})")
        
        print(f"{i}. {name}")
        print(f"   Tipo: {tipo}, Maternidade: {has_maternity}, Emergency Only: {is_emergency}")
    
    if problemas:
        print("\n[ERRO] Problemas encontrados:")
        for problema in problemas:
            print(f"   - {problema}")
        return False
    else:
        print("\n[OK] Todos os resultados são hospitais com maternidade válidos!")
    
    # Verificar se há registros com tipo_unidade NULL que podem estar passando
    print("\n[VERIFICAÇÃO] Verificando registros com tipo_unidade NULL...")
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM hospitals_cache
        WHERE lat IS NOT NULL 
          AND long IS NOT NULL
          AND has_maternity = 1
          AND (tipo_unidade IS NULL OR tipo_unidade = '')
    """)
    null_types = cursor.fetchone()['count']
    if null_types > 0:
        print(f"   [AVISO] {null_types} registros com tipo_unidade NULL e has_maternity=1")
        print("   [INFO] Estes registros NÃO passam pelo filtro MATERNITY (tipo_unidade IN ('05', '07', 'HOSPITAL'))")
    else:
        print("   [OK] Nenhum registro com tipo_unidade NULL e has_maternity=1")
    
    conn.close()
    
    print("\n" + "="*70)
    print("TESTE CONCLUÍDO")
    print("="*70)
    
    return len(problemas) == 0

if __name__ == "__main__":
    success = test_maternity_query()
    sys.exit(0 if success else 1)
