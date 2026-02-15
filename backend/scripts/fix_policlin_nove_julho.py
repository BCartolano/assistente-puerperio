#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrigir Hospital Policlin Nove de Julho (não tem maternidade)
Purpose: Remover has_maternity=1 do Policlin Nove de Julho (Av. Nove de Julho, 430)
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

# CNES 3042529 - Hospital Policlin Nove de Julho (não tem maternidade)
cur.execute("""
    UPDATE hospitals_cache
    SET has_maternity = 0
    WHERE cnes_id = '3042529'
    AND has_maternity = 1
""")
n = cur.rowcount

conn.commit()
cur.close()
conn.close()

print(f"Corrigido: {n} hospital(s)")
print("Hospital Policlin Nove de Julho (CNES 3042529) - has_maternity = 0")
print("Hospital e Maternidade Policlin Adhemar (CNES 5259789) - mantém has_maternity = 1")
