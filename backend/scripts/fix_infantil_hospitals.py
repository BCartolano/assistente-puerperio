#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remover Hospitais Infantis/Pediátricos
Purpose: Remover has_maternity=1 de hospitais infantis/pediátricos
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

def fix_infantil_hospitals():
    """Remove has_maternity=1 de hospitais infantis/pediátricos"""
    print("="*70)
    print("CORREÇÃO: REMOVENDO HOSPITAIS INFANTIS/PEDIÁTRICOS")
    print("="*70)
    print()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Termos relacionados a hospitais infantis/pediátricos
    infantil_terms = [
        'INFANTIL',
        'PEDIATRIA', 'PEDIATRICO', 'PEDIATRICA', 'PEDIATRIC',
        'CRIANCA', 'CRIANÇA',
        'BABY', 'BEBE', 'BEBÊ'
    ]
    
    # Verificar quantos existem antes
    print("[1] Verificando hospitais infantis/pediátricos...")
    conditions = []
    params = []
    
    for term in infantil_terms:
        conditions.append("(UPPER(COALESCE(name, '')) LIKE ? OR UPPER(COALESCE(fantasy_name, '')) LIKE ?)")
        params.extend([f'%{term}%', f'%{term}%'])
    
    if conditions:
        # Contar antes
        cursor.execute(f"""
            SELECT COUNT(*) as count, 
                   GROUP_CONCAT(cnes_id || ':' || COALESCE(fantasy_name, name, 'Sem nome')) as examples
            FROM hospitals_cache
            WHERE has_maternity = 1
            AND tipo_unidade IN ('05', '07', 'HOSPITAL')
            AND ({' OR '.join(conditions)})
        """, params)
        
        result = cursor.fetchone()
        count = result['count']
        
        if count > 0:
            print(f"   [ENCONTRADOS] {count} hospitais infantis/pediátricos marcados com maternidade")
            
            # Mostrar alguns exemplos
            cursor.execute(f"""
                SELECT cnes_id, name, fantasy_name
                FROM hospitals_cache
                WHERE has_maternity = 1
                AND tipo_unidade IN ('05', '07', 'HOSPITAL')
                AND ({' OR '.join(conditions)})
                LIMIT 10
            """, params)
            
            exemplos = cursor.fetchall()
            print("\n   [EXEMPLOS]:")
            for hosp in exemplos:
                nome = hosp['fantasy_name'] or hosp['name'] or 'Sem nome'
                print(f"      - {nome} (CNES: {hosp['cnes_id']})")
            
            # Remover has_maternity=1
            print(f"\n[2] Removendo has_maternity=1 destes hospitais...")
            cursor.execute(f"""
                UPDATE hospitals_cache
                SET has_maternity = 0
                WHERE has_maternity = 1
                AND tipo_unidade IN ('05', '07', 'HOSPITAL')
                AND ({' OR '.join(conditions)})
            """, params)
            
            removidos = cursor.rowcount
            print(f"   [OK] {removidos} hospitais infantis/pediátricos removidos da busca de maternidades")
            
            conn.commit()
            
            # Verificar se ainda há problemas
            print("\n[3] Verificando se ainda há hospitais infantis...")
            cursor.execute(f"""
                SELECT COUNT(*) as count
                FROM hospitals_cache
                WHERE has_maternity = 1
                AND tipo_unidade IN ('05', '07', 'HOSPITAL')
                AND ({' OR '.join(conditions)})
            """, params)
            restantes = cursor.fetchone()['count']
            
            if restantes == 0:
                print("   [OK] Nenhum hospital infantil restante!")
            else:
                print(f"   [AVISO] Ainda há {restantes} hospitais infantis marcados como maternidade")
        else:
            print("   [OK] Nenhum hospital infantil encontrado com has_maternity=1")
    else:
        print("[AVISO] Nenhum termo de exclusão definido")
    
    conn.close()
    
    print("\n" + "="*70)
    print("CORREÇÃO CONCLUÍDA")
    print("="*70)
    
    return True

if __name__ == "__main__":
    success = fix_infantil_hospitals()
    sys.exit(0 if success else 1)
