#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validação Web de Hospitais - Processamento em Lotes
Purpose: Validar via web se hospitais têm Ala da Maternidade (processamento em lotes)
"""

import os
import sys
import sqlite3
import json
from typing import Dict, List, Optional

# Configuração de encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'cnes_cache.db')
RESULTS_FILE = os.path.join(BASE_DIR, 'backend', 'scripts', 'maternity_validation_results.json')

def get_hospitals_batch(batch_num: int, batch_size: int = 10) -> List[Dict]:
    """Obtém um lote específico de hospitais"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    offset = (batch_num - 1) * batch_size
    
    cursor.execute("""
        SELECT cnes_id, name, fantasy_name, address, city, state, telefone
        FROM hospitals_cache
        WHERE has_maternity = 1
        AND tipo_unidade IN ('05', '07', 'HOSPITAL')
        ORDER BY cnes_id
        LIMIT ? OFFSET ?
    """, (batch_size, offset))
    
    hospitals = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return hospitals


def build_search_queries(hospital: Dict) -> Dict[str, str]:
    """Constrói queries de busca para o hospital"""
    name = hospital.get('fantasy_name') or hospital.get('name') or ''
    city = hospital.get('city') or ''
    state = hospital.get('state') or ''
    
    queries = {}
    
    # Query 1: Nome + Maternidade
    query1_parts = [name, 'maternidade']
    if city:
        query1_parts.insert(1, city)
    queries['maternidade'] = ' '.join(filter(None, query1_parts))
    
    # Query 2: Nome + Obstetrícia
    query2_parts = [name, 'obstetrícia']
    if city:
        query2_parts.insert(1, city)
    queries['obstetricia'] = ' '.join(filter(None, query2_parts))
    
    # Query 3: Nome + Parto
    query3_parts = [name, 'parto']
    if city:
        query3_parts.insert(1, city)
    queries['parto'] = ' '.join(filter(None, query3_parts))
    
    return queries


def save_batch_for_validation(batch_num: int, hospitals: List[Dict]) -> str:
    """Salva lote de hospitais para validação web"""
    batch_data = {
        'batch_num': batch_num,
        'total_hospitals': len(hospitals),
        'hospitals': []
    }
    
    for hospital in hospitals:
        hospital_data = {
            'cnes_id': hospital.get('cnes_id'),
            'name': hospital.get('fantasy_name') or hospital.get('name'),
            'address': hospital.get('address'),
            'city': hospital.get('city'),
            'state': hospital.get('state'),
            'telefone': hospital.get('telefone'),
            'search_queries': build_search_queries(hospital),
            'validation_status': 'pending'
        }
        batch_data['hospitals'].append(hospital_data)
    
    # Salvar em arquivo JSON
    output_file = os.path.join(BASE_DIR, 'backend', 'scripts', f'batch_{batch_num}_validation.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(batch_data, f, ensure_ascii=False, indent=2)
    
    return output_file


def main():
    """Gera lotes de hospitais para validação web"""
    print("="*70)
    print("GERAÇÃO DE LOTES PARA VALIDAÇÃO WEB")
    print("="*70)
    print()
    
    # Obter total
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM hospitals_cache
        WHERE has_maternity = 1
        AND tipo_unidade IN ('05', '07', 'HOSPITAL')
    """)
    total = cursor.fetchone()[0]
    conn.close()
    
    print(f"[INFO] Total de hospitais: {total}")
    print(f"[INFO] Processando em lotes de 10 hospitais")
    print()
    
    # Gerar primeiro lote
    batch_num = 1
    batch_size = 10
    hospitals = get_hospitals_batch(batch_num, batch_size)
    
    if not hospitals:
        print("[AVISO] Nenhum hospital encontrado")
        return
    
    output_file = save_batch_for_validation(batch_num, hospitals)
    print(f"[OK] Lote {batch_num} salvo em: {output_file}")
    print(f"[INFO] {len(hospitals)} hospitais preparados para validação web")
    print()
    print("HOSPITAIS DO LOTE 1:")
    for i, hospital in enumerate(hospitals, 1):
        name = hospital.get('fantasy_name') or hospital.get('name') or 'Sem nome'
        queries = build_search_queries(hospital)
        print(f"\n{i}. {name} (CNES: {hospital.get('cnes_id')})")
        print(f"   Queries de busca:")
        for query_type, query in queries.items():
            print(f"      - {query_type}: '{query}'")


if __name__ == "__main__":
    main()
