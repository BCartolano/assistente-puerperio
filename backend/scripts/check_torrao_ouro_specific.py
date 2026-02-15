#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar Hospital Torrão de Ouro específico (Estrada Dr Bezerra De Menezes)
Purpose: Identificar CNES e dados que indicam saúde mental
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

# Buscar Hospital Torrão de Ouro com endereço específico
cur.execute("""
    SELECT cnes_id, name, fantasy_name, address, city, state, has_maternity, tipo_unidade,
           natureza_juridica, management, cnpj, codigo_servicos
    FROM hospitals_cache
    WHERE (UPPER(COALESCE(name,'')) LIKE '%TORRAO%' OR UPPER(COALESCE(fantasy_name,'')) LIKE '%TORRAO%')
       AND (UPPER(COALESCE(address,'')) LIKE '%BEZERRA%' OR UPPER(COALESCE(address,'')) LIKE '%MENEZES%')
    ORDER BY cnes_id
""")

rows = cur.fetchall()
print(f"Encontrados {len(rows)} hospitais 'Torrão de Ouro' com endereço Bezerra de Menezes:\n")
for r in rows:
    print(f"CNES: {r['cnes_id']}")
    print(f"  Nome: {r['fantasy_name'] or r['name']}")
    print(f"  Endereço: {r['address']}")
    print(f"  Cidade: {r['city']}, Estado: {r['state']}")
    print(f"  has_maternity: {r['has_maternity']}")
    print(f"  tipo_unidade: {r['tipo_unidade']}")
    print(f"  natureza_juridica: {r['natureza_juridica']}")
    print(f"  management: {r['management']}")
    print(f"  codigo_servicos: {r['codigo_servicos']}")
    print()

# Buscar também por "ESTRADA DR BEZERRA" ou "ESTRADA BEZERRA"
cur.execute("""
    SELECT cnes_id, name, fantasy_name, address, city, state, has_maternity, tipo_unidade,
           natureza_juridica, management, cnpj, codigo_servicos
    FROM hospitals_cache
    WHERE UPPER(COALESCE(address,'')) LIKE '%ESTRADA%BEZERRA%'
       OR UPPER(COALESCE(address,'')) LIKE '%ESTRADA%MENEZES%'
    ORDER BY cnes_id
""")

rows2 = cur.fetchall()
if rows2:
    print(f"\nEncontrados {len(rows2)} hospitais com endereço 'Estrada Bezerra/Menezes':\n")
    for r in rows2:
        print(f"CNES: {r['cnes_id']}")
        print(f"  Nome: {r['fantasy_name'] or r['name']}")
        print(f"  Endereço: {r['address']}")
        print(f"  Cidade: {r['city']}, Estado: {r['state']}")
        print(f"  has_maternity: {r['has_maternity']}")
        print(f"  tipo_unidade: {r['tipo_unidade']}")
        print(f"  codigo_servicos: {r['codigo_servicos']}")
        print()

conn.close()
