#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir dados de maternidade no banco
Purpose: Garantir que apenas hospitais (05, 07) tenham has_maternity=1
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

def fix_maternity_data():
    """Corrige dados de maternidade - apenas hospitais (05, 07) devem ter has_maternity=1"""
    print("="*70)
    print("CORREÇÃO DE DADOS DE MATERNIDADE")
    print("="*70)
    print()
    
    if not os.path.exists(DB_PATH):
        print(f"[ERRO] Banco de dados não encontrado: {DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Encontrar UPAs com has_maternity=1
    print("[1] Verificando UPAs com has_maternity=1...")
    cursor.execute("""
        SELECT cnes_id, name, tipo_unidade, has_maternity, is_emergency_only
        FROM hospitals_cache
        WHERE (tipo_unidade = '73' OR tipo_unidade = 'UPA' OR is_emergency_only = 1)
        AND has_maternity = 1
    """)
    upas = cursor.fetchall()
    
    if upas:
        print(f"   [AVISO] Encontradas {len(upas)} UPAs com has_maternity=1 (CORRIGINDO)...")
        for upa in upas:
            print(f"      - {upa['name']} (CNES: {upa['cnes_id']}, Tipo: {upa['tipo_unidade']})")
        # Corrigir
        cursor.execute("""
            UPDATE hospitals_cache
            SET has_maternity = 0
            WHERE (tipo_unidade = '73' OR tipo_unidade = 'UPA' OR is_emergency_only = 1)
            AND has_maternity = 1
        """)
        print(f"   [OK] {cursor.rowcount} UPAs corrigidas")
    else:
        print("   [OK] Nenhuma UPA com has_maternity=1 encontrada")
    
    # 2. Encontrar UBS/USF/Ambulatórios com has_maternity=1
    print()
    print("[2] Verificando UBS/USF/Ambulatórios com has_maternity=1...")
    cursor.execute("""
        SELECT cnes_id, name, tipo_unidade, has_maternity
        FROM hospitals_cache
        WHERE tipo_unidade IN ('01', '02', '15', '40', 'UBS', '32', '71', '72')
        AND has_maternity = 1
    """)
    ubs_usf = cursor.fetchall()
    
    if ubs_usf:
        print(f"   [AVISO] Encontradas {len(ubs_usf)} UBS/USF/Ambulatórios com has_maternity=1 (CORRIGINDO)...")
        for unit in ubs_usf:
            print(f"      - {unit['name']} (CNES: {unit['cnes_id']}, Tipo: {unit['tipo_unidade']})")
        # Corrigir
        cursor.execute("""
            UPDATE hospitals_cache
            SET has_maternity = 0
            WHERE tipo_unidade IN ('01', '02', '15', '40', 'UBS', '32', '71', '72')
            AND has_maternity = 1
        """)
        print(f"   [OK] {cursor.rowcount} UBS/USF/Ambulatórios corrigidos")
    else:
        print("   [OK] Nenhuma UBS/USF/Ambulatório com has_maternity=1 encontrada")
    
    # 3. Encontrar unidades não-hospitalares (que não são 05, 07, HOSPITAL) com has_maternity=1
    print()
    print("[3] Verificando unidades não-hospitalares com has_maternity=1...")
    cursor.execute("""
        SELECT cnes_id, name, tipo_unidade, has_maternity
        FROM hospitals_cache
        WHERE has_maternity = 1
        AND tipo_unidade NOT IN ('05', '07', 'HOSPITAL')
        AND tipo_unidade NOT IN ('73', 'UPA', '01', '02', '15', '40', 'UBS', '32', '71', '72')
    """)
    others = cursor.fetchall()
    
    if others:
        print(f"   [AVISO] Encontradas {len(others)} unidades não-hospitalares com has_maternity=1 (CORRIGINDO)...")
        for unit in others:
            print(f"      - {unit['name']} (CNES: {unit['cnes_id']}, Tipo: {unit['tipo_unidade']})")
        # Corrigir
        cursor.execute("""
            UPDATE hospitals_cache
            SET has_maternity = 0
            WHERE has_maternity = 1
            AND tipo_unidade NOT IN ('05', '07', 'HOSPITAL')
            AND tipo_unidade NOT IN ('73', 'UPA', '01', '02', '15', '40', 'UBS', '32', '71', '72')
        """)
        print(f"   [OK] {cursor.rowcount} unidades não-hospitalares corrigidas")
    else:
        print("   [OK] Nenhuma unidade não-hospitalar com has_maternity=1 encontrada")
    
    # 4. Verificar hospitais (05, 07) com has_maternity=0 mas que têm nome sugerindo maternidade
    print()
    print("[4] Verificando hospitais (05, 07) sem has_maternity=1 mas com nome sugerindo maternidade...")
    cursor.execute("""
        SELECT cnes_id, name, fantasy_name, tipo_unidade, has_maternity
        FROM hospitals_cache
        WHERE tipo_unidade IN ('05', '07', 'HOSPITAL')
        AND has_maternity = 0
        AND (UPPER(name) LIKE '%MATERNIDADE%' OR UPPER(name) LIKE '%MATERNO%'
             OR UPPER(fantasy_name) LIKE '%MATERNIDADE%' OR UPPER(fantasy_name) LIKE '%MATERNO%'
             OR UPPER(name) LIKE '%OBSTETRICIA%' OR UPPER(name) LIKE '%OBSTETRICO%'
             OR UPPER(fantasy_name) LIKE '%OBSTETRICIA%' OR UPPER(fantasy_name) LIKE '%OBSTETRICO%')
    """)
    hospitals_without_flag = cursor.fetchall()
    
    if hospitals_without_flag:
        print(f"   [AVISO] Encontrados {len(hospitals_without_flag)} hospitais com nome sugerindo maternidade mas has_maternity=0:")
        for hosp in hospitals_without_flag:
            print(f"      - {hosp['name']} (CNES: {hosp['cnes_id']}, Tipo: {hosp['tipo_unidade']})")
        print("   [INFO] Estes hospitais podem precisar de revisão manual")
    else:
        print("   [OK] Nenhum hospital encontrado nesta situação")
    
    # Commit mudanças
    conn.commit()
    conn.close()
    
    print()
    print("="*70)
    print("CORREÇÃO CONCLUÍDA")
    print("="*70)
    
    return True

if __name__ == "__main__":
    success = fix_maternity_data()
    sys.exit(0 if success else 1)
