#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Encontrar TODAS as Duplicatas
Purpose: Identificar e remover duplicatas por nome e localização
"""

import os
import sys
import sqlite3
import json
from datetime import datetime
from collections import defaultdict

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'cnes_cache.db')
REPORT_FILE = os.path.join(BASE_DIR, 'backend', 'scripts', 'duplicates_report.json')

def normalize_name(name: str) -> str:
    """Normaliza nome para comparação"""
    if not name:
        return ''
    # Remover acentos, espaços extras, converter para maiúscula
    import unicodedata
    normalized = unicodedata.normalize('NFD', name.upper())
    normalized = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    # Remover caracteres especiais
    normalized = ''.join(c for c in normalized if c.isalnum() or c.isspace())
    # Remover espaços extras
    normalized = ' '.join(normalized.split())
    return normalized

def find_duplicates():
    """Encontra todas as duplicatas"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Buscar todos os hospitais com maternidade
    cur.execute("""
        SELECT cnes_id, name, fantasy_name, address, city, state, lat, long
        FROM hospitals_cache
        WHERE has_maternity = 1
        AND tipo_unidade IN ('05', '07', 'HOSPITAL')
    """)
    
    hospitals = [dict(row) for row in cur.fetchall()]
    
    # Duplicatas por nome normalizado
    by_name = defaultdict(list)
    for h in hospitals:
        name = normalize_name(h.get('fantasy_name') or h.get('name', ''))
        if name and len(name) > 5:  # Ignorar nomes muito curtos
            by_name[name].append(h)
    
    # Duplicatas por localização (mesma lat/long)
    by_location = defaultdict(list)
    for h in hospitals:
        lat = h.get('lat')
        lon = h.get('long')
        if lat and lon and lat != 0 and lon != 0:
            key = (round(float(lat), 4), round(float(lon), 4))
            by_location[key].append(h)
    
    # Identificar duplicatas
    duplicates_to_remove = set()
    duplicates_report = []
    
    # Duplicatas por nome
    for name, hospitals_list in by_name.items():
        if len(hospitals_list) > 1:
            # Manter o primeiro, remover os outros
            for h in hospitals_list[1:]:
                duplicates_to_remove.add(h['cnes_id'])
                duplicates_report.append({
                    'cnes_id': h['cnes_id'],
                    'name': h.get('fantasy_name') or h.get('name', ''),
                    'type': 'duplicate_name',
                    'normalized_name': name,
                    'count': len(hospitals_list)
                })
    
    # Duplicatas por localização
    for loc, hospitals_list in by_location.items():
        if len(hospitals_list) > 1:
            # Manter o primeiro, remover os outros
            for h in hospitals_list[1:]:
                if h['cnes_id'] not in duplicates_to_remove:  # Não duplicar remoção
                    duplicates_to_remove.add(h['cnes_id'])
                    duplicates_report.append({
                        'cnes_id': h['cnes_id'],
                        'name': h.get('fantasy_name') or h.get('name', ''),
                        'type': 'duplicate_location',
                        'lat': loc[0],
                        'long': loc[1],
                        'count': len(hospitals_list)
                    })
    
    # Remover duplicatas do banco
    if duplicates_to_remove:
        placeholders = ','.join('?' * len(duplicates_to_remove))
        cur.execute(f"""
            UPDATE hospitals_cache
            SET has_maternity = 0
            WHERE cnes_id IN ({placeholders})
        """, list(duplicates_to_remove))
        n_removed = cur.rowcount
    else:
        n_removed = 0
    
    conn.commit()
    cur.close()
    conn.close()
    
    return duplicates_report, n_removed

def main():
    print("=" * 80)
    print("IDENTIFICAÇÃO DE DUPLICATAS")
    print("=" * 80)
    print()
    
    print("🔍 Procurando duplicatas por nome e localização...")
    duplicates, n_removed = find_duplicates()
    
    print()
    print("=" * 80)
    print("RESULTADO")
    print("=" * 80)
    print(f"🔄 Duplicatas encontradas: {len(duplicates)}")
    print(f"🚫 Duplicatas removidas: {n_removed}")
    print()
    
    # Salvar relatório
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_duplicates': len(duplicates),
        'removed': n_removed,
        'duplicates': duplicates[:200]  # Primeiros 200
    }
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Relatório salvo em: {REPORT_FILE}")
    print()
    print("✅ Análise de duplicatas concluída!")

if __name__ == '__main__':
    main()
