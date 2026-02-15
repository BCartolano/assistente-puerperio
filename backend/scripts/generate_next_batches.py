#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerar Próximos Lotes para Validação Web
Purpose: Gerar lotes 2-10 para validação web
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

def generate_batch(batch_num: int, batch_size: int = 10):
    """Gera um lote específico de hospitais"""
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
    
    if not hospitals:
        return None
    
    # Preparar dados do lote
    batch_data = {
        'batch_num': batch_num,
        'total_hospitals': len(hospitals),
        'hospitals': []
    }
    
    for hospital in hospitals:
        name = hospital.get('fantasy_name') or hospital.get('name') or 'Sem nome'
        city = hospital.get('city') or ''
        state = hospital.get('state') or ''
        
        # Gerar queries de busca
        queries = {
            'maternidade': f"{name} {city} {state} maternidade".strip(),
            'obstetricia': f"{name} {city} {state} obstetrícia".strip(),
            'parto': f"{name} {city} {state} parto".strip()
        }
        
        hospital_data = {
            'cnes_id': hospital.get('cnes_id'),
            'name': name,
            'address': hospital.get('address'),
            'city': city,
            'state': state,
            'telefone': hospital.get('telefone'),
            'search_queries': queries,
            'validation_status': 'pending'
        }
        batch_data['hospitals'].append(hospital_data)
    
    # Salvar arquivo JSON
    output_file = os.path.join(BASE_DIR, 'backend', 'scripts', f'batch_{batch_num}_validation.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(batch_data, f, ensure_ascii=False, indent=2)
    
    return output_file


def main():
    """Gera próximos lotes (2-10)"""
    print("="*70)
    print("GERAÇÃO DE LOTES 2-10 PARA VALIDAÇÃO WEB")
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
    print(f"[INFO] Gerando lotes 2-10 (10 hospitais por lote)")
    print()
    
    generated = []
    for batch_num in range(2, 11):
        output_file = generate_batch(batch_num)
        if output_file:
            generated.append(batch_num)
            print(f"[OK] Lote {batch_num} gerado: {output_file}")
        else:
            print(f"[AVISO] Lote {batch_num} não gerado (sem mais hospitais)")
            break
    
    print()
    print("="*70)
    print("RESUMO")
    print("="*70)
    print(f"[OK] {len(generated)} lotes gerados: {generated}")
    print()
    print("[PRÓXIMOS PASSOS]")
    print("1. Para cada lote, usar web_search para buscar informações")
    print("2. Analisar resultados usando process_web_validation.py")
    print("3. Atualizar banco de dados com resultados")


if __name__ == "__main__":
    main()
