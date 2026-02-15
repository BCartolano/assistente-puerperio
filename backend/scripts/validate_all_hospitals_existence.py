#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validação Completa de Existência e Localização
Purpose: Sistema completo para validar todos os hospitais
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

def identify_suspicious_hospitals():
    """Identifica hospitais suspeitos (possíveis empresas fantasmas)"""
    print("="*70)
    print("IDENTIFICAÇÃO DE HOSPITAIS SUSPEITOS")
    print("="*70)
    print()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    suspicious = []
    
    # 1. Hospitais sem telefone e sem endereço completo
    print("[1] Hospitais sem telefone E sem endereço completo...")
    cursor.execute("""
        SELECT cnes_id, name, fantasy_name, address, telefone
        FROM hospitals_cache
        WHERE has_maternity = 1
        AND tipo_unidade IN ('05', '07', 'HOSPITAL')
        AND (telefone IS NULL OR telefone = '')
        AND (address IS NULL OR address = '' OR address LIKE '%NULL%')
        LIMIT 20
    """)
    sem_contato = cursor.fetchall()
    if sem_contato:
        print(f"   [SUSPEITOS] {len(sem_contato)} hospitais sem telefone e endereço")
        for hosp in sem_contato[:5]:
            nome = hosp['fantasy_name'] or hosp['name'] or 'Sem nome'
            suspicious.append({
                'cnes_id': hosp['cnes_id'],
                'name': nome,
                'reason': 'Sem telefone e endereço completo'
            })
            print(f"      - {nome} (CNES: {hosp['cnes_id']})")
    else:
        print("   [OK] Nenhum hospital sem telefone e endereço")
    
    # 2. Hospitais com nomes genéricos demais
    print("\n[2] Hospitais com nomes muito genéricos...")
    generic_names = ['HOSPITAL', 'UNIDADE', 'CENTRO', 'POSTO', 'CLINICA', 'CLÍNICA']
    for generic in generic_names:
        cursor.execute("""
            SELECT cnes_id, name, fantasy_name
            FROM hospitals_cache
            WHERE has_maternity = 1
            AND tipo_unidade IN ('05', '07', 'HOSPITAL')
            AND (
                (UPPER(name) = ? OR UPPER(name) LIKE ?)
                OR (UPPER(fantasy_name) = ? OR UPPER(fantasy_name) LIKE ?)
            )
            LIMIT 10
        """, (generic, f'{generic}%', generic, f'{generic}%'))
        genericos = cursor.fetchall()
        if genericos:
            print(f"   [SUSPEITOS] {len(genericos)} hospitais com nome genérico '{generic}'")
            for hosp in genericos[:3]:
                nome = hosp['fantasy_name'] or hosp['name'] or 'Sem nome'
                if not any(s['cnes_id'] == hosp['cnes_id'] for s in suspicious):
                    suspicious.append({
                        'cnes_id': hosp['cnes_id'],
                        'name': nome,
                        'reason': f'Nome muito genérico: {generic}'
                    })
    
    # 3. Hospitais com coordenadas duplicadas (mesma localização)
    print("\n[3] Hospitais com coordenadas duplicadas (possível erro)...")
    cursor.execute("""
        SELECT lat, long, COUNT(*) as count, GROUP_CONCAT(cnes_id) as cnes_ids
        FROM hospitals_cache
        WHERE has_maternity = 1
        AND tipo_unidade IN ('05', '07', 'HOSPITAL')
        AND lat IS NOT NULL AND long IS NOT NULL
        AND lat != 0 AND long != 0
        AND lat BETWEEN -35.0 AND 5.0 AND long BETWEEN -75.0 AND -30.0
        GROUP BY lat, long
        HAVING COUNT(*) > 3
        ORDER BY count DESC
        LIMIT 10
    """)
    duplicatas = cursor.fetchall()
    if duplicatas:
        print(f"   [SUSPEITOS] {len(duplicatas)} grupos de coordenadas duplicadas")
        for dup in duplicatas[:3]:
            cnes_ids = dup['cnes_ids'].split(',')
            print(f"      - {dup['count']} hospitais na mesma localização (Lat={dup['lat']}, Long={dup['long']})")
            # Adicionar apenas alguns para não sobrecarregar
            for cnes_id in cnes_ids[:2]:
                if not any(s['cnes_id'] == cnes_id for s in suspicious):
                    cursor.execute("SELECT fantasy_name, name FROM hospitals_cache WHERE cnes_id = ?", (cnes_id,))
                    hosp = cursor.fetchone()
                    if hosp:
                        nome = hosp['fantasy_name'] or hosp['name'] or 'Sem nome'
                        suspicious.append({
                            'cnes_id': cnes_id,
                            'name': nome,
                            'reason': f'Coordenadas duplicadas ({dup["count"]} hospitais no mesmo ponto)'
                        })
    
    conn.close()
    
    print("\n" + "="*70)
    print("RESUMO DE HOSPITAIS SUSPEITOS")
    print("="*70)
    print(f"Total de hospitais suspeitos encontrados: {len(suspicious)}")
    print("\n[RECOMENDAÇÃO] Validar estes hospitais via busca web para confirmar existência")
    
    return suspicious


def main():
    """Identifica hospitais suspeitos"""
    suspicious = identify_suspicious_hospitals()
    
    if suspicious:
        print("\n[PRÓXIMOS PASSOS]")
        print("1. Validar cada hospital suspeito via busca web")
        print("2. Verificar existência e localização")
        print("3. Remover empresas fantasmas do banco")


if __name__ == "__main__":
    main()
