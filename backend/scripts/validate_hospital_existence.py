#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validação de Existência de Hospitais
Purpose: Detectar empresas fantasmas e hospitais que não existem
"""

import os
import sys
import sqlite3
import json

# Configuração de encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'cnes_cache.db')

def get_hospitals_batch(batch_num: int, batch_size: int = 10) -> list:
    """Obtém um lote de hospitais para validação"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    offset = (batch_num - 1) * batch_size
    
    cursor.execute("""
        SELECT cnes_id, name, fantasy_name, address, city, state, lat, long, telefone
        FROM hospitals_cache
        WHERE has_maternity = 1
        AND tipo_unidade IN ('05', '07', 'HOSPITAL')
        ORDER BY cnes_id
        LIMIT ? OFFSET ?
    """, (batch_size, offset))
    
    hospitals = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return hospitals


def build_existence_query(hospital: dict) -> str:
    """Constrói query para verificar existência do hospital"""
    name = hospital.get('fantasy_name') or hospital.get('name') or ''
    city = hospital.get('city') or ''
    state = hospital.get('state') or ''
    
    # Query: nome + cidade + estado
    query_parts = [name]
    if city:
        query_parts.append(city)
    if state:
        query_parts.append(state)
    
    return ' '.join(filter(None, query_parts))


def build_location_query(hospital: dict) -> str:
    """Constrói query para verificar localização no Google Maps"""
    name = hospital.get('fantasy_name') or hospital.get('name') or ''
    address = hospital.get('address') or ''
    city = hospital.get('city') or ''
    state = hospital.get('state') or ''
    
    # Query: nome + endereço completo
    query_parts = [name]
    if address:
        query_parts.append(address)
    if city:
        query_parts.append(city)
    if state:
        query_parts.append(state)
    
    return ' '.join(filter(None, query_parts))


def save_batch_for_validation(batch_num: int, hospitals: list) -> str:
    """Salva lote para validação"""
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
            'lat': hospital.get('lat'),
            'long': hospital.get('long'),
            'telefone': hospital.get('telefone'),
            'existence_query': build_existence_query(hospital),
            'location_query': build_location_query(hospital),
            'validation_status': 'pending'
        }
        batch_data['hospitals'].append(hospital_data)
    
    output_file = os.path.join(BASE_DIR, 'backend', 'scripts', f'validation_batch_{batch_num}.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(batch_data, f, ensure_ascii=False, indent=2)
    
    return output_file


def main():
    """Gera primeiro lote para validação"""
    print("="*70)
    print("VALIDAÇÃO DE EXISTÊNCIA E LOCALIZAÇÃO DE HOSPITAIS")
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
    hospitals = get_hospitals_batch(batch_num, 10)
    
    if not hospitals:
        print("[AVISO] Nenhum hospital encontrado")
        return
    
    output_file = save_batch_for_validation(batch_num, hospitals)
    print(f"[OK] Lote {batch_num} salvo em: {output_file}")
    print()
    
    print("HOSPITAIS DO LOTE 1 PARA VALIDAÇÃO:")
    for i, hospital in enumerate(hospitals, 1):
        name = hospital.get('fantasy_name') or hospital.get('name') or 'Sem nome'
        address = hospital.get('address') or 'Sem endereço'
        lat = hospital.get('lat')
        lon = hospital.get('long')
        
        print(f"\n{i}. {name} (CNES: {hospital.get('cnes_id')})")
        print(f"   Endereço: {address}")
        print(f"   Coordenadas: Lat={lat}, Long={lon}")
        print(f"   Query existência: '{build_existence_query(hospital)}'")
        print(f"   Query localização: '{build_location_query(hospital)}'")


if __name__ == "__main__":
    main()
