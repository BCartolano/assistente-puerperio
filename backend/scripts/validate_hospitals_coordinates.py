#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validação de Coordenadas e Hospitais
Purpose: Verificar hospitais com coordenadas inválidas ou suspeitas
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

def validate_hospitals():
    """Valida hospitais com coordenadas inválidas ou suspeitas"""
    print("="*70)
    print("VALIDAÇÃO DE COORDENADAS E HOSPITAIS")
    print("="*70)
    print()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Coordenadas válidas para Brasil (aproximadamente)
    BRASIL_LAT_MIN = -35.0  # Sul
    BRASIL_LAT_MAX = 5.0    # Norte
    BRASIL_LON_MIN = -75.0  # Oeste
    BRASIL_LON_MAX = -30.0  # Leste
    
    problemas = []
    
    # 1. Hospitais com coordenadas (0, 0) ou NULL
    print("[1] Verificando hospitais com coordenadas (0, 0) ou NULL...")
    cursor.execute("""
        SELECT cnes_id, name, fantasy_name, lat, long, address, city, state
        FROM hospitals_cache
        WHERE tipo_unidade IN ('05', '07', 'HOSPITAL')
        AND has_maternity = 1
        AND (
            lat IS NULL OR long IS NULL 
            OR lat = 0 OR long = 0
            OR (lat = 0 AND long = 0)
        )
        LIMIT 20
    """)
    coord_invalidas = cursor.fetchall()
    if coord_invalidas:
        print(f"   [ERRO] {len(coord_invalidas)} hospitais com coordenadas inválidas encontrados:")
        for hosp in coord_invalidas[:10]:
            nome = hosp['fantasy_name'] or hosp['name'] or 'Sem nome'
            problemas.append({
                'cnes_id': hosp['cnes_id'],
                'nome': nome,
                'problema': 'Coordenadas inválidas (0, 0 ou NULL)',
                'lat': hosp['lat'],
                'long': hosp['long']
            })
            print(f"      - {nome} (CNES: {hosp['cnes_id']}, Lat: {hosp['lat']}, Long: {hosp['long']})")
    else:
        print("   [OK] Nenhum hospital com coordenadas inválidas")
    
    # 2. Hospitais com coordenadas fora do Brasil
    print("\n[2] Verificando hospitais com coordenadas fora do Brasil...")
    cursor.execute("""
        SELECT cnes_id, name, fantasy_name, lat, long, address, city, state
        FROM hospitals_cache
        WHERE tipo_unidade IN ('05', '07', 'HOSPITAL')
        AND has_maternity = 1
        AND lat IS NOT NULL AND long IS NOT NULL
        AND lat != 0 AND long != 0
        AND (
            lat < ? OR lat > ? OR long < ? OR long > ?
        )
    """, (BRASIL_LAT_MIN, BRASIL_LAT_MAX, BRASIL_LON_MIN, BRASIL_LON_MAX))
    fora_brasil = cursor.fetchall()
    if fora_brasil:
        print(f"   [ERRO] {len(fora_brasil)} hospitais com coordenadas fora do Brasil:")
        for hosp in fora_brasil[:10]:
            nome = hosp['fantasy_name'] or hosp['name'] or 'Sem nome'
            problemas.append({
                'cnes_id': hosp['cnes_id'],
                'nome': nome,
                'problema': f'Coordenadas fora do Brasil (Lat: {hosp["lat"]}, Long: {hosp["long"]})',
                'lat': hosp['lat'],
                'long': hosp['long']
            })
            print(f"      - {nome} (CNES: {hosp['cnes_id']})")
            print(f"        Coordenadas: Lat={hosp['lat']}, Long={hosp['long']}")
    else:
        print("   [OK] Nenhum hospital com coordenadas fora do Brasil")
    
    # 3. Hospitais com coordenadas duplicadas (mesma lat/long)
    print("\n[3] Verificando hospitais com coordenadas duplicadas (possível erro)...")
    cursor.execute("""
        SELECT lat, long, COUNT(*) as count, GROUP_CONCAT(cnes_id) as cnes_ids, GROUP_CONCAT(name) as names
        FROM hospitals_cache
        WHERE tipo_unidade IN ('05', '07', 'HOSPITAL')
        AND has_maternity = 1
        AND lat IS NOT NULL AND long IS NOT NULL
        AND lat != 0 AND long != 0
        AND lat BETWEEN ? AND ? AND long BETWEEN ? AND ?
        GROUP BY lat, long
        HAVING COUNT(*) > 5
        ORDER BY count DESC
        LIMIT 10
    """, (BRASIL_LAT_MIN, BRASIL_LAT_MAX, BRASIL_LON_MIN, BRASIL_LON_MAX))
    duplicatas = cursor.fetchall()
    if duplicatas:
        print(f"   [AVISO] {len(duplicatas)} grupos de coordenadas duplicadas (mais de 5 hospitais no mesmo ponto):")
        for dup in duplicatas:
            print(f"      - Coordenadas: Lat={dup['lat']}, Long={dup['long']}")
            print(f"        {dup['count']} hospitais no mesmo local (possível erro de geocodificação)")
            print(f"        CNES IDs: {dup['cnes_ids'][:100]}...")
    else:
        print("   [OK] Nenhuma coordenada duplicada suspeita")
    
    # 4. Hospitais sem endereço completo
    print("\n[4] Verificando hospitais sem endereço completo...")
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM hospitals_cache
        WHERE tipo_unidade IN ('05', '07', 'HOSPITAL')
        AND has_maternity = 1
        AND (address IS NULL OR address = '' OR address LIKE '%NULL%')
    """)
    sem_endereco = cursor.fetchone()['count']
    if sem_endereco > 0:
        print(f"   [AVISO] {sem_endereco} hospitais sem endereço completo")
        cursor.execute("""
            SELECT cnes_id, name, fantasy_name
            FROM hospitals_cache
            WHERE tipo_unidade IN ('05', '07', 'HOSPITAL')
            AND has_maternity = 1
            AND (address IS NULL OR address = '' OR address LIKE '%NULL%')
            LIMIT 10
        """)
        exemplos = cursor.fetchall()
        for hosp in exemplos:
            nome = hosp['fantasy_name'] or hosp['name'] or 'Sem nome'
            problemas.append({
                'cnes_id': hosp['cnes_id'],
                'nome': nome,
                'problema': 'Endereço ausente ou inválido'
            })
            print(f"      - {nome} (CNES: {hosp['cnes_id']})")
    else:
        print("   [OK] Todos os hospitais têm endereço")
    
    # 5. Hospitais com nomes suspeitos (possíveis empresas fantasmas)
    print("\n[5] Verificando hospitais com nomes suspeitos...")
    suspeitos_keywords = [
        'TESTE', 'TEST', 'EXEMPLO', 'EXAMPLE',
        'XXXX', 'YYYY', 'ZZZZ', 'AAAA',
        'NOME FANTASIA', 'RAZAO SOCIAL',
        'TEMPORARIO', 'TEMPORÁRIO'
    ]
    
    cursor.execute("""
        SELECT cnes_id, name, fantasy_name, address, city, state
        FROM hospitals_cache
        WHERE tipo_unidade IN ('05', '07', 'HOSPITAL')
        AND has_maternity = 1
        AND (
            UPPER(COALESCE(name, '')) LIKE '%TESTE%'
            OR UPPER(COALESCE(name, '')) LIKE '%TEST%'
            OR UPPER(COALESCE(fantasy_name, '')) LIKE '%TESTE%'
            OR UPPER(COALESCE(fantasy_name, '')) LIKE '%TEST%'
        )
        LIMIT 20
    """)
    suspeitos = cursor.fetchall()
    if suspeitos:
        print(f"   [AVISO] {len(suspeitos)} hospitais com nomes suspeitos (possíveis empresas fantasmas):")
        for hosp in suspeitos:
            nome = hosp['fantasy_name'] or hosp['name'] or 'Sem nome'
            problemas.append({
                'cnes_id': hosp['cnes_id'],
                'nome': nome,
                'problema': 'Nome suspeito (possível empresa fantasma)'
            })
            print(f"      - {nome} (CNES: {hosp['cnes_id']})")
    else:
        print("   [OK] Nenhum hospital com nome suspeito")
    
    # 6. Total de problemas encontrados
    print("\n" + "="*70)
    print("RESUMO DE PROBLEMAS ENCONTRADOS")
    print("="*70)
    print(f"Total de problemas: {len(problemas)}")
    
    if problemas:
        print("\n[RECOMENDAÇÃO] Criar script para corrigir/remover estes registros")
    else:
        print("\n[OK] Nenhum problema encontrado!")
    
    conn.close()
    
    return problemas

if __name__ == "__main__":
    problemas = validate_hospitals()
    sys.exit(0 if len(problemas) == 0 else 1)
