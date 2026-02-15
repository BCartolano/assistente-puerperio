#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrigir Hospital Francisca Júlia CVV (saúde mental, não tem maternidade)
Purpose: Remover has_maternity=1 do Hospital Francisca Júlia CVV (CNES 2085569)
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

# CNES 2085569 - Hospital Francisca Júlia CVV (saúde mental/dependência química, não tem maternidade)
cur.execute("""
    UPDATE hospitals_cache
    SET has_maternity = 0
    WHERE cnes_id = '2085569'
    AND has_maternity = 1
""")
n = cur.rowcount

conn.commit()
cur.close()
conn.close()

print(f"Corrigido: {n} hospital(s)")
print("Hospital Francisca Júlia CVV (CNES 2085569) - has_maternity = 0")
print("Motivo: Hospital especializado em saúde mental e dependência química, não oferece serviços de maternidade")
