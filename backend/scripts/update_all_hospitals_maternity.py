#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Atualizar TODOS os Hospitais para has_maternity=1
Purpose: Marcar todos os hospitais (05, 07) como tendo maternidade, exceto exceções claras
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

def update_all_hospitals_maternity():
    """Marca todos os hospitais (05, 07) como tendo maternidade, exceto exceções"""
    print("="*70)
    print("ATUALIZAÇÃO: Marcar TODOS os Hospitais como tendo Maternidade")
    print("="*70)
    print()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Termos que indicam que NÃO tem maternidade
    excluded_keywords = [
        'PSIQUIATRIA', 'PSIQUIATRICO', 'MENTAL',
        'ORTOPEDIA', 'ORTODOXIA', 'TRAUMATOLOGIA',
        'CARDIOLOGIA', 'CARDIACO', 'CARDIAC',
        'ONCOLOGIA', 'ONCOLOGICO', 'CANCER',
        'REABILITACAO', 'FISIOTERAPIA',
        'CIRURGIA PLASTICA', 'ESTETICA',
        'ORTOPEDICO', 'ORTOPEDISTA',
        'ORTHO',  # Excluir "Orthoservice" e similares
        'CIRURGIA CARDIACA', 'CIRURGIA CARDIACA',
        'TRATAMENTO CANCER', 'INSTITUTO DO CANCER'
    ]
    
    # 1. Primeiro, verificar quantos hospitais serão atualizados
    print("[1] Verificando hospitais que serão marcados com has_maternity=1...")
    
    # Query para contar hospitais que devem ter maternidade
    query_count = """
        SELECT COUNT(*) as count
        FROM hospitals_cache
        WHERE tipo_unidade IN ('05', '07', 'HOSPITAL')
          AND has_maternity = 0
          AND is_emergency_only = 0
          AND (tipo_unidade != '73' AND tipo_unidade != 'UPA')
    """
    
    # Adicionar exclusões por nome
    for keyword in excluded_keywords:
        query_count += f" AND UPPER(COALESCE(name, '')) NOT LIKE '%{keyword}%'"
        query_count += f" AND UPPER(COALESCE(fantasy_name, '')) NOT LIKE '%{keyword}%'"
    
    cursor.execute(query_count)
    count = cursor.fetchone()['count']
    print(f"   [OK] {count:,} hospitais serão marcados com has_maternity=1")
    
    # 2. Atualizar
    print("\n[2] Atualizando hospitais...")
    query_update = """
        UPDATE hospitals_cache
        SET has_maternity = 1
        WHERE tipo_unidade IN ('05', '07', 'HOSPITAL')
          AND has_maternity = 0
          AND is_emergency_only = 0
          AND (tipo_unidade != '73' AND tipo_unidade != 'UPA')
    """
    
    # Adicionar exclusões por nome
    for keyword in excluded_keywords:
        query_update += f" AND UPPER(COALESCE(name, '')) NOT LIKE '%{keyword}%'"
        query_update += f" AND UPPER(COALESCE(fantasy_name, '')) NOT LIKE '%{keyword}%'"
    
    cursor.execute(query_update)
    updated = cursor.rowcount
    conn.commit()
    
    print(f"   [OK] {updated:,} hospitais atualizados")
    
    # 3. Verificar resultado final
    print("\n[3] Verificando resultado final...")
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
    total_com_maternidade = cursor.fetchone()['count']
    print(f"   [OK] Total de hospitais com has_maternity=1: {total_com_maternidade:,}")
    
    # 4. Teste: Hospitais próximos de Taubaté
    print("\n[4] Teste: Hospitais próximos de Taubaté/SP (50km):")
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM hospitals_cache
        WHERE tipo_unidade IN ('05', '07', 'HOSPITAL')
          AND has_maternity = 1
          AND lat IS NOT NULL 
          AND long IS NOT NULL
          AND lat != 0 
          AND long != 0
          AND (6371 * acos(
                cos(radians(-23.1931904)) * 
                cos(radians(lat)) * 
                cos(radians(long) - radians(-45.7998336)) + 
                sin(radians(-23.1931904)) * 
                sin(radians(lat))
            )) <= 50
    """)
    dentro_50km = cursor.fetchone()['count']
    print(f"   [OK] Hospitais dentro de 50km: {dentro_50km}")
    
    conn.close()
    
    print("\n" + "="*70)
    print("ATUALIZAÇÃO CONCLUÍDA")
    print("="*70)
    print(f"[OK] {updated:,} hospitais atualizados com has_maternity=1")
    print(f"[OK] Total agora: {total_com_maternidade:,} hospitais com maternidade")
    
    return True

if __name__ == "__main__":
    success = update_all_hospitals_maternity()
    sys.exit(0 if success else 1)
