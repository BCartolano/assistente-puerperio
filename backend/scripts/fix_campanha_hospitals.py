#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remover Hospitais de Campanha da busca de maternidade
Purpose: Hospitais de campanha são temporários e não têm maternidade
"""

import os
import sys
import sqlite3

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'cnes_cache.db')

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Remover has_maternity=1 de hospitais de campanha/retaguarda
cur.execute("""
    UPDATE hospitals_cache
    SET has_maternity = 0
    WHERE has_maternity = 1
    AND (
        UPPER(COALESCE(name,'')) LIKE '%CAMPANHA%'
        OR UPPER(COALESCE(fantasy_name,'')) LIKE '%CAMPANHA%'
        OR UPPER(COALESCE(name,'')) LIKE '%RETAGUARDA%'
        OR UPPER(COALESCE(fantasy_name,'')) LIKE '%RETAGUARDA%'
        OR (UPPER(COALESCE(name,'')) LIKE '%UNIDADE DE INTERNACAO%' AND UPPER(COALESCE(name,'')) NOT LIKE '%MATERNIDADE%')
        OR (UPPER(COALESCE(fantasy_name,'')) LIKE '%UNIDADE DE INTERNACAO%' AND UPPER(COALESCE(fantasy_name,'')) NOT LIKE '%MATERNIDADE%')
        OR (UPPER(COALESCE(name,'')) LIKE '%CENTRO DE INTERNACAO%' AND UPPER(COALESCE(name,'')) NOT LIKE '%MATERNIDADE%')
        OR (UPPER(COALESCE(fantasy_name,'')) LIKE '%CENTRO DE INTERNACAO%' AND UPPER(COALESCE(fantasy_name,'')) NOT LIKE '%MATERNIDADE%')
    )
""")
n_fixed = cur.rowcount

# Listar alguns exemplos
cur.execute("""
    SELECT cnes_id, name, fantasy_name
    FROM hospitals_cache
    WHERE has_maternity = 0
    AND (
        UPPER(COALESCE(name,'')) LIKE '%CAMPANHA%'
        OR UPPER(COALESCE(fantasy_name,'')) LIKE '%CAMPANHA%'
        OR UPPER(COALESCE(name,'')) LIKE '%RETAGUARDA%'
        OR UPPER(COALESCE(fantasy_name,'')) LIKE '%RETAGUARDA%'
    )
    LIMIT 10
""")
examples = cur.fetchall()

conn.commit()
cur.close()
conn.close()

print(f"✅ {n_fixed} hospitais de campanha/retaguarda removidos da busca de maternidade")
print()
print("Exemplos de hospitais corrigidos:")
for ex in examples:
    print(f"  - {ex['fantasy_name'] or ex['name']} (CNES: {ex['cnes_id']})")
