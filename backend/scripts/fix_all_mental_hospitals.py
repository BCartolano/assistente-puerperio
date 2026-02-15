#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrigir todos os hospitais de saúde mental (remover has_maternity=1)
Purpose: Remover has_maternity=1 de hospitais especializados em saúde mental/dependência química
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

# Lista de CNES de hospitais de saúde mental
mental_hospitals_cnes = [
    '2085569',   # Hospital Francisca Júlia CVV
    '0014001',   # Associação de Pesquisa e Tratamento Alcoolismo
    '2078406',   # Hosp Independência
    '2270188',   # SEAP RJ Centro Trat Em Dependência Química Roberto Medeiros
    '7092571',   # Hospital Independência
    '7609566',   # Unidade de Dependência Química Vida
]

# Atualizar todos
placeholders = ','.join('?' * len(mental_hospitals_cnes))
cur.execute(f"""
    UPDATE hospitals_cache
    SET has_maternity = 0
    WHERE cnes_id IN ({placeholders})
    AND has_maternity = 1
""", mental_hospitals_cnes)
n = cur.rowcount

# Verificar quais foram atualizados
cur.execute(f"""
    SELECT cnes_id, name, fantasy_name, address, has_maternity
    FROM hospitals_cache
    WHERE cnes_id IN ({placeholders})
""", mental_hospitals_cnes)
updated = cur.fetchall()

conn.commit()
cur.close()
conn.close()

print(f"Corrigido: {n} hospital(is)")
print("\nHospitais atualizados:")
for h in updated:
    print(f"  CNES {h['cnes_id']}: {h['fantasy_name'] or h['name']} - has_maternity = {h['has_maternity']}")
