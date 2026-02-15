#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar Hospital Torrão de Ouro (saúde mental)
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

# Buscar Hospital Torrão de Ouro
cur.execute("""
    SELECT cnes_id, name, fantasy_name, address, city, state, has_maternity, tipo_unidade,
           natureza_juridica, management, cnpj
    FROM hospitals_cache
    WHERE (UPPER(COALESCE(name,'')) LIKE '%TORRAO%' OR UPPER(COALESCE(fantasy_name,'')) LIKE '%TORRAO%')
       OR (UPPER(COALESCE(name,'')) LIKE '%OURO%' AND UPPER(COALESCE(name,'')) LIKE '%HOSPITAL%')
    ORDER BY cnes_id
""")

rows = cur.fetchall()
print(f"Encontrados {len(rows)} hospitais 'Torrão de Ouro':\n")
for r in rows:
    print(f"CNES: {r['cnes_id']}")
    print(f"  Nome: {r['fantasy_name'] or r['name']}")
    print(f"  Endereço: {r['address']}")
    print(f"  Cidade: {r['city']}, Estado: {r['state']}")
    print(f"  has_maternity: {r['has_maternity']}")
    print(f"  tipo_unidade: {r['tipo_unidade']}")
    print(f"  natureza_juridica: {r['natureza_juridica']}")
    print(f"  management: {r['management']}")
    print()

# Verificar tbLeito se disponível (pode não estar no schema atual)
try:
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tbLeito'")
    if cur.fetchone():
        print("\n=== Verificando tbLeito ===")
        for r in rows:
            cnes_id = r['cnes_id']
            cur.execute("""
                SELECT CO_SERVICO, TP_LEITO, DS_LEITO, COUNT(*) as total
                FROM tbLeito
                WHERE CO_UNIDADE = ?
                GROUP BY CO_SERVICO, TP_LEITO, DS_LEITO
            """, (cnes_id,))
            leitos = cur.fetchall()
            if leitos:
                print(f"\nCNES {cnes_id} - Leitos:")
                for l in leitos:
                    print(f"  Serviço: {l['CO_SERVICO']}, Tipo: {l['TP_LEITO']}, Descrição: {l['DS_LEITO']}, Total: {l['total']}")
            else:
                print(f"\nCNES {cnes_id} - Nenhum leito encontrado em tbLeito")
    else:
        print("\n⚠️ Tabela tbLeito não encontrada no banco")
except Exception as e:
    print(f"\n⚠️ Erro ao verificar tbLeito: {e}")

conn.close()
