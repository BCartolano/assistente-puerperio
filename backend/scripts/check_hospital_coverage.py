#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar Cobertura de Hospitais no Banco
Purpose: Ver quantos hospitais existem vs quantos têm has_maternity=1
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

def check_coverage():
    """Verifica cobertura de hospitais"""
    print("="*70)
    print("ANÁLISE DE COBERTURA DE HOSPITAIS")
    print("="*70)
    print()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Total de hospitais (05, 07)
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM hospitals_cache 
        WHERE tipo_unidade IN ('05', '07', 'HOSPITAL')
        AND lat IS NOT NULL 
        AND long IS NOT NULL
        AND lat != 0 
        AND long != 0
    """)
    total_hospitais = cursor.fetchone()['count']
    print(f"[1] Total de hospitais (05, 07) com coordenadas: {total_hospitais:,}")
    
    # Hospitais COM has_maternity=1
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM hospitals_cache 
        WHERE tipo_unidade IN ('05', '07', 'HOSPITAL')
        AND has_maternity = 1
        AND lat IS NOT NULL 
        AND long IS NOT NULL
        AND lat != 0 
        AND long != 0
    """)
    com_maternidade = cursor.fetchone()['count']
    print(f"[2] Hospitais COM has_maternity=1: {com_maternidade:,}")
    
    # Hospitais SEM has_maternity=1
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM hospitals_cache 
        WHERE tipo_unidade IN ('05', '07', 'HOSPITAL')
        AND has_maternity = 0
        AND lat IS NOT NULL 
        AND long IS NOT NULL
        AND lat != 0 
        AND long != 0
    """)
    sem_maternidade = cursor.fetchone()['count']
    print(f"[3] Hospitais SEM has_maternity=1: {sem_maternidade:,}")
    
    # Percentual
    if total_hospitais > 0:
        pct = (com_maternidade / total_hospitais) * 100
        print(f"[4] Percentual marcado com maternidade: {pct:.1f}%")
    
    # Exemplos de hospitais sem has_maternity=1
    print("\n[5] Exemplos de hospitais SEM has_maternity=1 (primeiros 10):")
    cursor.execute("""
        SELECT name, fantasy_name, tipo_unidade, state, city
        FROM hospitals_cache 
        WHERE tipo_unidade IN ('05', '07', 'HOSPITAL')
        AND has_maternity = 0
        AND lat IS NOT NULL 
        AND long IS NOT NULL
        AND lat != 0 
        AND long != 0
        LIMIT 10
    """)
    exemplos = cursor.fetchall()
    for i, hosp in enumerate(exemplos, 1):
        nome = hosp['fantasy_name'] or hosp['name'] or 'Sem nome'
        print(f"   {i}. {nome} (Tipo: {hosp['tipo_unidade']}, Estado: {hosp['state']})")
    
    conn.close()
    
    print("\n" + "="*70)
    print("CONCLUSÃO")
    print("="*70)
    if sem_maternidade > com_maternidade:
        print(f"[AVISO] Há {sem_maternidade:,} hospitais sem has_maternity=1!")
        print("[DICA] A heurística pode estar muito conservadora.")
        print("[DICA] Considerar marcar TODOS os hospitais (05, 07) como tendo maternidade.")
    else:
        print("[OK] Cobertura parece adequada.")
    
    return True

if __name__ == "__main__":
    check_coverage()
