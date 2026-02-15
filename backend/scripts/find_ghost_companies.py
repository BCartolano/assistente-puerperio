#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Identificar Empresas Fantasmas
Purpose: Encontrar hospitais que não existem ou têm dados inválidos
"""

import os
import sys
import sqlite3
import json
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'cnes_cache.db')
REPORT_FILE = os.path.join(BASE_DIR, 'backend', 'scripts', 'ghost_companies_report.json')

def is_ghost_company(hospital: dict) -> tuple:
    """
    Verifica se é empresa fantasma
    Returns: (is_ghost, reason)
    """
    cnes_id = hospital.get('cnes_id', '')
    name = hospital.get('fantasy_name') or hospital.get('name', '')
    
    reasons = []
    
    # 1. Coordenadas inválidas ou ausentes
    lat = hospital.get('lat')
    lon = hospital.get('long')
    if not lat or not lon or lat == 0 or lon == 0:
        reasons.append('Coordenadas inválidas ou ausentes')
    
    # 2. Fora do Brasil
    if lat and lon:
        if not (-35.0 <= lat <= 5.0) or not (-75.0 <= lon <= -30.0):
            reasons.append('Coordenadas fora do Brasil')
    
    # 3. Sem endereço
    if not hospital.get('address'):
        reasons.append('Sem endereço')
    
    # 4. Nome muito genérico ou suspeito
    name_upper = name.upper()
    if name_upper in ['HOSPITAL', 'CLINICA', 'UNIDADE', 'CENTRO', 'ESTABELECIMENTO']:
        reasons.append('Nome muito genérico')
    elif len(name.strip()) < 5:
        reasons.append('Nome muito curto')
    
    # 5. Coordenadas duplicadas (mesma lat/long para muitos hospitais diferentes)
    # Isso será verificado separadamente
    
    # 6. Sem telefone E sem endereço completo
    if not hospital.get('telefone') and not hospital.get('address'):
        reasons.append('Sem telefone e sem endereço')
    
    if reasons:
        return (True, '; '.join(reasons))
    return (False, None)

def find_duplicate_coordinates(conn):
    """Encontra coordenadas duplicadas (possível empresa fantasma)"""
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            ROUND(lat, 4) as lat_rounded,
            ROUND(long, 4) as long_rounded,
            COUNT(*) as count,
            GROUP_CONCAT(cnes_id) as cnes_ids,
            GROUP_CONCAT(fantasy_name || '|' || name) as names
        FROM hospitals_cache
        WHERE has_maternity = 1
        AND lat IS NOT NULL AND long IS NOT NULL
        AND lat != 0 AND long != 0
        GROUP BY lat_rounded, long_rounded
        HAVING count > 3
        ORDER BY count DESC
    """)
    return cur.fetchall()

def main():
    print("=" * 80)
    print("IDENTIFICAÇÃO DE EMPRESAS FANTASMAS")
    print("=" * 80)
    print()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Buscar todos os hospitais com maternidade
    cur.execute("""
        SELECT cnes_id, name, fantasy_name, address, city, state, has_maternity, 
               tipo_unidade, lat, long, telefone
        FROM hospitals_cache
        WHERE has_maternity = 1
        AND tipo_unidade IN ('05', '07', 'HOSPITAL')
        ORDER BY cnes_id
    """)
    
    hospitals = [dict(row) for row in cur.fetchall()]
    print(f"📊 Analisando {len(hospitals)} hospitais...")
    print()
    
    print("🔍 Verificando empresas fantasmas...")
    ghost_companies = []
    
    for i, hospital in enumerate(hospitals, 1):
        is_ghost, reason = is_ghost_company(hospital)
        if is_ghost:
            ghost_companies.append({
                'cnes_id': hospital['cnes_id'],
                'name': hospital.get('fantasy_name') or hospital.get('name', ''),
                'address': hospital.get('address', ''),
                'lat': hospital.get('lat'),
                'long': hospital.get('long'),
                'reason': reason
            })
            
            # Remover do banco
            cur.execute("""
                UPDATE hospitals_cache
                SET has_maternity = 0
                WHERE cnes_id = ?
            """, (hospital['cnes_id'],))
        
        if i % 100 == 0:
            print(f"   Progresso: {i}/{len(hospitals)} analisados...")
    
    print()
    print("🔍 Verificando coordenadas duplicadas...")
    duplicate_coords = find_duplicate_coordinates(conn)
    
    duplicate_ghosts = []
    for dup in duplicate_coords:
        if dup['count'] > 5:  # Mais de 5 hospitais no mesmo lugar = suspeito
            cnes_ids = dup['cnes_ids'].split(',')
            names = dup['names'].split(',')
            # Manter apenas o primeiro, remover os outros
            for idx, cnes_id in enumerate(cnes_ids[1:], 1):
                duplicate_ghosts.append({
                    'cnes_id': cnes_id.strip(),
                    'name': names[idx].split('|')[0] if idx < len(names) else 'N/A',
                    'reason': f'Coordenadas duplicadas ({dup["count"]} hospitais no mesmo lugar)',
                    'lat': dup['lat_rounded'],
                    'long': dup['long_rounded']
                })
                cur.execute("""
                    UPDATE hospitals_cache
                    SET has_maternity = 0
                    WHERE cnes_id = ?
                """, (cnes_id.strip(),))
    
    conn.commit()
    cur.close()
    conn.close()
    
    total_removed = len(ghost_companies) + len(duplicate_ghosts)
    
    print()
    print("=" * 80)
    print("RESULTADO")
    print("=" * 80)
    print(f"👻 Empresas fantasmas encontradas: {len(ghost_companies)}")
    print(f"🔄 Duplicatas por coordenadas: {len(duplicate_ghosts)}")
    print(f"🚫 Total removido: {total_removed}")
    print()
    
    # Salvar relatório
    report = {
        'timestamp': datetime.now().isoformat(),
        'ghost_companies': ghost_companies[:100],  # Primeiros 100
        'duplicate_ghosts': duplicate_ghosts[:100],
        'total_ghost': len(ghost_companies),
        'total_duplicates': len(duplicate_ghosts),
        'total_removed': total_removed
    }
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Relatório salvo em: {REPORT_FILE}")
    print()
    print("✅ Análise de empresas fantasmas concluída!")

if __name__ == '__main__':
    main()
