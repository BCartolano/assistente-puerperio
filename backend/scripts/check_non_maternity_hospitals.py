#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar Hospitais que NÃO são de Maternidade
Purpose: Identificar hospitais de Visão, Ortopedia, etc. que ainda aparecem
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

def check_non_maternity_hospitals():
    """Identifica hospitais não relacionados a maternidade"""
    print("="*70)
    print("VERIFICAÇÃO DE HOSPITAIS NÃO DE MATERNIDADE")
    print("="*70)
    print()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Termos a excluir (especialidades não relacionadas a maternidade)
    excluded_terms = [
        # Visão/Oftalmologia
        'VISÃO', 'VISAO', 'VISUAL', 'OFTA', 'OFTALMO', 'OLHO', 'OLHOS',
        'RETINA', 'CÓRNEA', 'CORNEA', 'CATARATA', 'GLAUCOMA',
        # Ortopedia
        'ORTO', 'ORTOD', 'ORTOPED', 'ORTOPÉD', 'TRAUMATO', 'FRATURA',
        'OSSO', 'OSSOS', 'COLUNA', 'JOELHO', 'QUADRIL', 'OMBRO',
        # Outras especialidades
        'CARDIOL', 'CARDIAC', 'CORAÇÃO', 'CORACAO',
        'ONCO', 'CANCER', 'CÂNCER',
        'PSIQUIATR', 'MENTAL', 'PSICOLÓGICO', 'PSICOLOGICO',
        'CIRURGIA PLÁSTICA', 'CIRURGIA PLASTICA', 'ESTÉTICA', 'ESTETICA',
        'REABILITAÇÃO', 'REABILITACAO', 'FISIOTERAPIA',
        'ORTHO', 'ORTHOPEDIC',
    ]
    
    problemas = []
    
    # Buscar hospitais com has_maternity=1 que contêm termos excluídos
    print("[1] Verificando hospitais com has_maternity=1 que contêm termos excluídos...")
    
    for term in excluded_terms:
        cursor.execute("""
            SELECT cnes_id, name, fantasy_name, address, city, state, tipo_unidade
            FROM hospitals_cache
            WHERE has_maternity = 1
            AND tipo_unidade IN ('05', '07', 'HOSPITAL')
            AND (
                UPPER(COALESCE(name, '')) LIKE ?
                OR UPPER(COALESCE(fantasy_name, '')) LIKE ?
            )
            LIMIT 50
        """, (f'%{term}%', f'%{term}%'))
        
        results = cursor.fetchall()
        if results:
            print(f"\n   [ERRO] Encontrados hospitais com '{term}':")
            for hosp in results:
                nome = hosp['fantasy_name'] or hosp['name'] or 'Sem nome'
                problemas.append({
                    'cnes_id': hosp['cnes_id'],
                    'nome': nome,
                    'termo': term,
                    'endereco': hosp['address']
                })
                print(f"      - {nome} (CNES: {hosp['cnes_id']})")
                print(f"        Endereço: {hosp['address']}")
    
    print("\n" + "="*70)
    print(f"RESUMO: {len(problemas)} hospitais não relacionados a maternidade encontrados")
    print("="*70)
    
    conn.close()
    return problemas

if __name__ == "__main__":
    problemas = check_non_maternity_hospitals()
    sys.exit(0 if len(problemas) == 0 else 1)
