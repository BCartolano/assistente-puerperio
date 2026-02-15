#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrigir Santos Dumont e Prontil
Purpose: Remover has_maternity=1 de hospitais que não têm maternidade
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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'cnes_cache.db')

def fix_specific_hospitals():
    """Remove has_maternity=1 de hospitais específicos sem maternidade"""
    print("="*70)
    print("CORREÇÃO: SANTOS DUMONT E PRONTIL")
    print("="*70)
    print()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Santos Dumont (especializado em cirurgias, não tem maternidade)
    print("[1] Removendo has_maternity=1 de 'Santos Dumont'...")
    cursor.execute("""
        UPDATE hospitals_cache
        SET has_maternity = 0
        WHERE (UPPER(name) LIKE '%SANTOS DUMONT%' OR UPPER(fantasy_name) LIKE '%SANTOS DUMONT%')
        AND has_maternity = 1
    """)
    santos_removidos = cursor.rowcount
    print(f"   [OK] {santos_removidos} hospitais 'Santos Dumont' corrigidos")
    
    # 2. Prontil (infantil, não tem maternidade)
    print("\n[2] Removendo has_maternity=1 de 'Prontil'...")
    cursor.execute("""
        UPDATE hospitals_cache
        SET has_maternity = 0
        WHERE (UPPER(name) LIKE '%PRONTIL%' OR UPPER(fantasy_name) LIKE '%PRONTIL%')
        AND has_maternity = 1
    """)
    prontil_removidos = cursor.rowcount
    print(f"   [OK] {prontil_removidos} hospitais 'Prontil' corrigidos")
    
    # 3. Adicionar filtros para hospitais especializados em cirurgias
    print("\n[3] Removendo has_maternity=1 de hospitais especializados em cirurgias...")
    cirurgia_keywords = [
        'CIRURGIA', 'CIRURGICO', 'CIRÚRGICO',
        'ESPECIALIZADO EM CIRURGIA', 'ESPECIALIZADO EM CIRURGIAS',
        'MEDIA E ALTA COMPLEXIDADE', 'MÉDIA E ALTA COMPLEXIDADE',
        'CIRURGIA GERAL', 'CIRURGIA ESPECIALIZADA',
        'BUCO MAXILO', 'CABEÇA E PESCOÇO', 'CABECA E PESCOCO',
        'CARDIOVASCULAR', 'TORACICA', 'TORÁCICA', 'VASCULAR',
        'UROLOGIA', 'ONCOLOGIA'
    ]
    
    conditions = []
    params = []
    for keyword in cirurgia_keywords:
        conditions.append("(UPPER(COALESCE(name, '')) LIKE ? OR UPPER(COALESCE(fantasy_name, '')) LIKE ?)")
        params.extend([f'%{keyword}%', f'%{keyword}%'])
    
    if conditions:
        cursor.execute(f"""
            UPDATE hospitals_cache
            SET has_maternity = 0
            WHERE has_maternity = 1
            AND tipo_unidade IN ('05', '07', 'HOSPITAL')
            AND ({' OR '.join(conditions)})
            AND (
                UPPER(COALESCE(name, '')) NOT LIKE '%MATERNIDADE%'
                AND UPPER(COALESCE(fantasy_name, '')) NOT LIKE '%MATERNIDADE%'
                AND UPPER(COALESCE(name, '')) NOT LIKE '%OBSTETRICIA%'
                AND UPPER(COALESCE(fantasy_name, '')) NOT LIKE '%OBSTETRICIA%'
            )
        """, params)
        cirurgia_removidos = cursor.rowcount
        print(f"   [OK] {cirurgia_removidos} hospitais especializados em cirurgias corrigidos")
    
    conn.commit()
    conn.close()
    
    total = santos_removidos + prontil_removidos + cirurgia_removidos
    
    print("\n" + "="*70)
    print("CORREÇÃO CONCLUÍDA")
    print("="*70)
    print(f"[OK] Total de hospitais corrigidos: {total}")
    
    return True

if __name__ == "__main__":
    success = fix_specific_hospitals()
    sys.exit(0 if success else 1)
