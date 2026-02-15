#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificação do Filtro de Maternidade
Purpose: Verificar se o filtro está funcionando corretamente em todo o Brasil
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

def verify_maternity_filter():
    """Verifica se o filtro de maternidade está funcionando corretamente"""
    print("="*70)
    print("VERIFICAÇÃO DO FILTRO DE MATERNIDADE")
    print("="*70)
    print()
    
    if not os.path.exists(DB_PATH):
        print(f"[ERRO] Banco de dados não encontrado: {DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Verificar UPAs com has_maternity=1
    print("[1] Verificando UPAs com has_maternity=1...")
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM hospitals_cache 
        WHERE (tipo_unidade = '73' OR tipo_unidade = 'UPA' OR is_emergency_only = 1)
        AND has_maternity = 1
    """)
    upas = cursor.fetchone()['count']
    if upas > 0:
        print(f"   [ERRO CRÍTICO] {upas} UPAs com has_maternity=1 encontradas!")
        cursor.execute("""
            SELECT cnes_id, name, tipo_unidade 
            FROM hospitals_cache 
            WHERE (tipo_unidade = '73' OR tipo_unidade = 'UPA' OR is_emergency_only = 1)
            AND has_maternity = 1
            LIMIT 5
        """)
        for row in cursor.fetchall():
            print(f"      - {row['name']} (CNES: {row['cnes_id']}, Tipo: {row['tipo_unidade']})")
        return False
    else:
        print("   [OK] Nenhuma UPA com has_maternity=1")
    
    # 2. Verificar UBS/USF com has_maternity=1
    print("\n[2] Verificando UBS/USF com has_maternity=1...")
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM hospitals_cache 
        WHERE tipo_unidade IN ('01', '02', '15', '40', 'UBS', '32', '71', '72')
        AND has_maternity = 1
    """)
    ubs_usf = cursor.fetchone()['count']
    if ubs_usf > 0:
        print(f"   [ERRO CRÍTICO] {ubs_usf} UBS/USF com has_maternity=1 encontradas!")
        cursor.execute("""
            SELECT cnes_id, name, tipo_unidade 
            FROM hospitals_cache 
            WHERE tipo_unidade IN ('01', '02', '15', '40', 'UBS', '32', '71', '72')
            AND has_maternity = 1
            LIMIT 5
        """)
        for row in cursor.fetchall():
            print(f"      - {row['name']} (CNES: {row['cnes_id']}, Tipo: {row['tipo_unidade']})")
        return False
    else:
        print("   [OK] Nenhuma UBS/USF com has_maternity=1")
    
    # 3. Verificar hospitais (05, 07) com has_maternity=1
    print("\n[3] Verificando hospitais (05, 07) com has_maternity=1...")
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM hospitals_cache 
        WHERE tipo_unidade IN ('05', '07', 'HOSPITAL')
        AND has_maternity = 1
        AND is_emergency_only = 0
    """)
    hospitais = cursor.fetchone()['count']
    print(f"   [OK] {hospitais} hospitais (05, 07) com has_maternity=1 encontrados")
    
    # 4. Testar query do filtro MATERNITY
    print("\n[4] Testando query do filtro MATERNITY...")
    query = """
        SELECT 
            cnes_id,
            name,
            tipo_unidade,
            has_maternity,
            is_emergency_only
        FROM hospitals_cache
        WHERE lat IS NOT NULL 
          AND long IS NOT NULL
          AND tipo_unidade IN ('05', '07', 'HOSPITAL')
          AND tipo_unidade NOT IN ('73', 'UPA', '01', '02', '15', '40', 'UBS', '32', '71', '72')
          AND is_emergency_only = 0
          AND has_maternity = 1
        LIMIT 10
    """
    cursor.execute(query)
    resultados = cursor.fetchall()
    
    print(f"   [OK] Query retornou {len(resultados)} resultados")
    
    # Verificar se há UPAs/UBS nos resultados
    upas_encontradas = [r for r in resultados if r['tipo_unidade'] in ('73', 'UPA') or r['is_emergency_only'] == 1]
    ubs_encontradas = [r for r in resultados if r['tipo_unidade'] in ('01', '02', '15', '40', 'UBS', '32', '71', '72')]
    
    if upas_encontradas:
        print(f"   [ERRO CRÍTICO] {len(upas_encontradas)} UPAs encontradas nos resultados!")
        for upa in upas_encontradas:
            print(f"      - {upa['name']} (Tipo: {upa['tipo_unidade']})")
        return False
    
    if ubs_encontradas:
        print(f"   [ERRO CRÍTICO] {len(ubs_encontradas)} UBS encontradas nos resultados!")
        for ubs in ubs_encontradas:
            print(f"      - {ubs['name']} (Tipo: {ubs['tipo_unidade']})")
        return False
    
    print("   [OK] Nenhuma UPA ou UBS encontrada nos resultados")
    
    # 5. Verificar distribuição por estado
    print("\n[5] Verificando distribuição por estado...")
    cursor.execute("""
        SELECT 
            state,
            COUNT(*) as count
        FROM hospitals_cache
        WHERE tipo_unidade IN ('05', '07', 'HOSPITAL')
          AND has_maternity = 1
          AND is_emergency_only = 0
          AND state IS NOT NULL
        GROUP BY state
        ORDER BY count DESC
        LIMIT 10
    """)
    estados = cursor.fetchall()
    print("   [OK] Top 10 estados com hospitais maternos:")
    for estado in estados:
        print(f"      - {estado['state']}: {estado['count']} hospitais")
    
    conn.close()
    
    print("\n" + "="*70)
    print("VERIFICAÇÃO CONCLUÍDA")
    print("="*70)
    print("[OK] Filtro de maternidade está funcionando corretamente!")
    print()
    
    return True

if __name__ == "__main__":
    success = verify_maternity_filter()
    sys.exit(0 if success else 1)
