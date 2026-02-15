#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrigir cirurgia plástica/estética e blacklist maternidade
Purpose: Marcar has_maternity=0 para hospitais de cirurgia plástica, estética e blacklist curada
"""

import os
import sys
import sqlite3
import unicodedata

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'cnes_cache.db')

EXCLUDED_TERMS = [
    'CIRURGIA PLASTICA', 'CIRURGIA PLÁSTICA', 'PLASTICA', 'PLÁSTICA',
    'ESTETICA', 'ESTÉTICA', 'HOSPITAL DE CIRURGIA', 'CIRURGIA ESTETICA',
]

BLACKLIST_CNES = [
    '3105571',   # Hospital Esplanada - cirurgia plástica (Av São João, SJ Campos)
    '0009601',   # Hospital Pio XII - oncologia/cardiologia (R Paraguassu, SJ Campos)
]


def run():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    n1 = 0
    for term in EXCLUDED_TERMS:
        cur.execute("""
            UPDATE hospitals_cache
            SET has_maternity = 0
            WHERE has_maternity = 1
            AND (UPPER(COALESCE(name,'')) LIKE ? OR UPPER(COALESCE(fantasy_name,'')) LIKE ?)
        """, (f'%{term}%', f'%{term}%'))
        n1 += cur.rowcount

    n2 = 0
    for cid in BLACKLIST_CNES:
        cur.execute("UPDATE hospitals_cache SET has_maternity = 0 WHERE cnes_id = ? AND has_maternity = 1", (cid,))
        n2 += cur.rowcount

    conn.commit()
    cur.close()
    conn.close()

    print('Cirurgia plástica/estética e blacklist:')
    print(f'  Atualizados por termos (cirurgia plástica, estética): {n1}')
    print(f'  Atualizados por blacklist CNES (Esplanada, Pio XII SJ Campos): {n2}')
    print(f'  Total: {n1 + n2}')
    return 0


if __name__ == '__main__':
    sys.exit(run())
