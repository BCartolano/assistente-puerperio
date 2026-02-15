#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar outros hospitais de saúde mental no banco
Purpose: Identificar hospitais que podem estar marcados incorretamente como tendo maternidade
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

# Termos relacionados a saúde mental
mental_terms = [
    'PSIQUIATRIA', 'PSIQUIATRICO', 'MENTAL', 'CVV', 'VALORIZACAO', 'VALORIZAÇÃO',
    'DEPENDENCIA', 'DEPENDÊNCIA', 'QUIMICA', 'QUÍMICA', 'ADICCAO', 'ADICÇÃO',
    'ALCOOLISMO', 'DROGADICCAO', 'DROGADIÇÃO'
]

# Buscar hospitais que podem ser de saúde mental
cur.execute("""
    SELECT cnes_id, name, fantasy_name, address, city, state, has_maternity, tipo_unidade
    FROM hospitals_cache
    WHERE tipo_unidade IN ('05', '07', 'HOSPITAL')
    AND has_maternity = 1
    AND (
        UPPER(COALESCE(name,'')) LIKE '%PSIQUIATR%'
        OR UPPER(COALESCE(fantasy_name,'')) LIKE '%PSIQUIATR%'
        OR UPPER(COALESCE(name,'')) LIKE '%MENTAL%'
        OR UPPER(COALESCE(fantasy_name,'')) LIKE '%MENTAL%'
        OR UPPER(COALESCE(name,'')) LIKE '%CVV%'
        OR UPPER(COALESCE(fantasy_name,'')) LIKE '%CVV%'
        OR UPPER(COALESCE(name,'')) LIKE '%VALORIZACAO%'
        OR UPPER(COALESCE(fantasy_name,'')) LIKE '%VALORIZACAO%'
        OR UPPER(COALESCE(name,'')) LIKE '%DEPENDENCIA%'
        OR UPPER(COALESCE(fantasy_name,'')) LIKE '%DEPENDENCIA%'
        OR UPPER(COALESCE(name,'')) LIKE '%QUIMICA%'
        OR UPPER(COALESCE(fantasy_name,'')) LIKE '%QUIMICA%'
        OR UPPER(COALESCE(name,'')) LIKE '%ADICCAO%'
        OR UPPER(COALESCE(fantasy_name,'')) LIKE '%ADICCAO%'
        OR UPPER(COALESCE(name,'')) LIKE '%ALCOOLISMO%'
        OR UPPER(COALESCE(fantasy_name,'')) LIKE '%ALCOOLISMO%'
    )
    ORDER BY cnes_id
    LIMIT 50
""")

rows = cur.fetchall()
print(f"Encontrados {len(rows)} hospitais que podem ser de saúde mental (com has_maternity=1):\n")
for r in rows:
    print(f"CNES: {r['cnes_id']}")
    print(f"  Nome: {r['fantasy_name'] or r['name']}")
    print(f"  Endereço: {r['address']}")
    print(f"  Cidade: {r['city']}, Estado: {r['state']}")
    print(f"  has_maternity: {r['has_maternity']}")
    print()

conn.close()
