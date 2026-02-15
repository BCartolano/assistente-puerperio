#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar Hospitais Específicos
Purpose: Verificar Santos Dumont e Prontil
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

def check_specific_hospitals():
    """Verifica hospitais específicos mencionados pelo usuário"""
    print("="*70)
    print("VERIFICAÇÃO DE HOSPITAIS ESPECÍFICOS")
    print("="*70)
    print()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Verificar Santos Dumont
    print("[1] Verificando 'Santos Dumont'...")
    cursor.execute("""
        SELECT cnes_id, name, fantasy_name, tipo_unidade, has_maternity, city, state
        FROM hospitals_cache
        WHERE (UPPER(name) LIKE '%SANTOS DUMONT%' OR UPPER(fantasy_name) LIKE '%SANTOS DUMONT%')
        AND has_maternity = 1
        LIMIT 10
    """)
    santos_dumont = cursor.fetchall()
    
    if santos_dumont:
        print(f"   [ENCONTRADOS] {len(santos_dumont)} hospitais 'Santos Dumont' com has_maternity=1:")
        for hosp in santos_dumont:
            nome = hosp['fantasy_name'] or hosp['name'] or 'Sem nome'
            print(f"      - {nome} (CNES: {hosp['cnes_id']}, Tipo: {hosp['tipo_unidade']}, Cidade: {hosp['city']}, Estado: {hosp['state']})")
    else:
        print("   [OK] Nenhum hospital 'Santos Dumont' com has_maternity=1 encontrado")
    
    # Verificar Prontil
    print("\n[2] Verificando 'Prontil'...")
    cursor.execute("""
        SELECT cnes_id, name, fantasy_name, tipo_unidade, has_maternity, city, state
        FROM hospitals_cache
        WHERE (UPPER(name) LIKE '%PRONTIL%' OR UPPER(fantasy_name) LIKE '%PRONTIL%')
        AND has_maternity = 1
        LIMIT 10
    """)
    prontil = cursor.fetchall()
    
    if prontil:
        print(f"   [ENCONTRADOS] {len(prontil)} hospitais 'Prontil' com has_maternity=1:")
        for hosp in prontil:
            nome = hosp['fantasy_name'] or hosp['name'] or 'Sem nome'
            print(f"      - {nome} (CNES: {hosp['cnes_id']}, Tipo: {hosp['tipo_unidade']}, Cidade: {hosp['city']}, Estado: {hosp['state']})")
    else:
        print("   [OK] Nenhum hospital 'Prontil' com has_maternity=1 encontrado")
    
    # Verificar hospitais com Estado/Município no nome
    print("\n[3] Verificando hospitais com Estado/Município no nome...")
    estados = ['SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'GO', 'PE', 'CE', 'PA', 'MA', 'MS', 'ES', 'PB', 'AL', 'RN', 'PI', 'TO', 'MT', 'DF', 'AC', 'AP', 'RO', 'RR', 'SE', 'AM']
    municipios_comuns = ['SAO PAULO', 'RIO DE JANEIRO', 'BELO HORIZONTE', 'BRASILIA', 'SALVADOR', 'FORTALEZA', 'CURITIBA', 'RECIFE', 'PORTO ALEGRE', 'BELEM', 'MANAUS', 'SAO JOSE DOS CAMPOS']
    
    conditions = []
    params = []
    
    for estado in estados:
        conditions.append("(UPPER(name) LIKE ? OR UPPER(fantasy_name) LIKE ?)")
        params.extend([f'%{estado}%', f'%{estado}%'])
    
    for municipio in municipios_comuns:
        conditions.append("(UPPER(name) LIKE ? OR UPPER(fantasy_name) LIKE ?)")
        params.extend([f'%{municipio}%', f'%{municipio}%'])
    
    if conditions:
        cursor.execute(f"""
            SELECT cnes_id, name, fantasy_name, city, state
            FROM hospitals_cache
            WHERE has_maternity = 1
            AND tipo_unidade IN ('05', '07', 'HOSPITAL')
            AND ({' OR '.join(conditions)})
            LIMIT 10
        """, params)
        
        com_estado_municipio = cursor.fetchall()
        if com_estado_municipio:
            print(f"   [ENCONTRADOS] {len(com_estado_municipio)} hospitais com Estado/Município no nome:")
            for hosp in com_estado_municipio:
                nome = hosp['fantasy_name'] or hosp['name'] or 'Sem nome'
                print(f"      - {nome} (CNES: {hosp['cnes_id']}, Cidade: {hosp['city']}, Estado: {hosp['state']})")
        else:
            print("   [OK] Nenhum hospital com Estado/Município no nome encontrado")
    
    conn.close()
    
    print("\n" + "="*70)
    print("VERIFICAÇÃO CONCLUÍDA")
    print("="*70)

if __name__ == "__main__":
    check_specific_hospitals()
