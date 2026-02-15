#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar Hospital Policlin duplicado
Purpose: Identificar qual Policlin tem maternidade e qual não tem
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

cur.execute("""
    SELECT cnes_id, name, fantasy_name, address, city, state, has_maternity, tipo_unidade
    FROM hospitals_cache
    WHERE (UPPER(COALESCE(name,'')) LIKE '%POLICLIN%' OR UPPER(COALESCE(fantasy_name,'')) LIKE '%POLICLIN%')
    AND tipo_unidade IN ('05', '07', 'HOSPITAL')
    ORDER BY has_maternity DESC, cnes_id
""")

rows = cur.fetchall()
print(f"Encontrados {len(rows)} hospitais 'Policlin':\n")
for r in rows:
    print(f"CNES: {r['cnes_id']}")
    print(f"  Nome: {r['fantasy_name'] or r['name']}")
    print(f"  Endereço: {r['address']}")
    print(f"  Cidade: {r['city']}, Estado: {r['state']}")
    print(f"  has_maternity: {r['has_maternity']}")
    print(f"  tipo_unidade: {r['tipo_unidade']}")
    print()

conn.close()
