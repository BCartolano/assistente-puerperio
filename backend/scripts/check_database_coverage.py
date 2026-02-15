#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificação da Cobertura do Banco de Dados
Purpose: Verificar quantos hospitais com maternidade existem no banco e quantos têm coordenadas
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

# Caminho do banco
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'cnes_cache.db')

def check_database_coverage():
    """Verifica cobertura do banco de dados"""
    print("="*70)
    print("VERIFICAÇÃO DA COBERTURA DO BANCO DE DADOS")
    print("="*70)
    print()
    
    if not os.path.exists(DB_PATH):
        print(f"[ERRO] Banco de dados não encontrado: {DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Total de registros no banco
    cursor.execute("SELECT COUNT(*) as count FROM hospitals_cache")
    total = cursor.fetchone()['count']
    print(f"[1] Total de registros no banco: {total:,}")
    
    # 2. Hospitais (05, 07) com maternidade
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM hospitals_cache 
        WHERE tipo_unidade IN ('05', '07', 'HOSPITAL')
        AND has_maternity = 1
    """)
    hospitais_maternidade = cursor.fetchone()['count']
    print(f"[2] Hospitais (05, 07) com has_maternity=1: {hospitais_maternidade:,}")
    
    # 3. Hospitais com maternidade E coordenadas válidas
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
    com_coords = cursor.fetchone()['count']
    print(f"[3] Hospitais com maternidade E coordenadas válidas: {com_coords:,}")
    
    # 4. Hospitais por estado
    print("\n[4] Distribuição de hospitais maternos por estado:")
    cursor.execute("""
        SELECT 
            state,
            COUNT(*) as count
        FROM hospitals_cache
        WHERE tipo_unidade IN ('05', '07', 'HOSPITAL')
          AND has_maternity = 1
          AND lat IS NOT NULL 
          AND long IS NOT NULL
          AND lat != 0 
          AND long != 0
          AND state IS NOT NULL
        GROUP BY state
        ORDER BY count DESC
    """)
    estados = cursor.fetchall()
    for estado in estados[:10]:
        print(f"   - Estado {estado['state']}: {estado['count']} hospitais")
    if len(estados) > 10:
        print(f"   ... e mais {len(estados) - 10} estados")
    
    # 5. Teste com coordenadas do usuário (Taubaté/SP)
    print("\n[5] Teste: Hospitais próximos de Taubaté/SP (lat=-23.1931904, lon=-45.7998336):")
    cursor.execute("""
        SELECT 
            name,
            fantasy_name,
            state,
            city,
            tipo_unidade,
            lat,
            long,
            (6371 * acos(
                cos(radians(-23.1931904)) * 
                cos(radians(lat)) * 
                cos(radians(long) - radians(-45.7998336)) + 
                sin(radians(-23.1931904)) * 
                sin(radians(lat))
            )) AS distance_km
        FROM hospitals_cache
        WHERE tipo_unidade IN ('05', '07', 'HOSPITAL')
          AND has_maternity = 1
          AND lat IS NOT NULL 
          AND long IS NOT NULL
          AND lat != 0 
          AND long != 0
        ORDER BY distance_km
        LIMIT 10
    """)
    hospitais_proximos = cursor.fetchall()
    print(f"   Encontrados {len(hospitais_proximos)} hospitais próximos:")
    for i, hosp in enumerate(hospitais_proximos, 1):
        nome = hosp['fantasy_name'] or hosp['name'] or 'Sem nome'
        distancia = hosp['distance_km']
        cidade = hosp['city'] or 'Sem cidade'
        estado = hosp['state'] or 'Sem estado'
        print(f"   {i}. {nome}")
        print(f"      Cidade: {cidade}, Estado: {estado}, Distância: {distancia:.1f} km")
    
    # 6. Verificar se há hospitais sem coordenadas
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM hospitals_cache 
        WHERE tipo_unidade IN ('05', '07', 'HOSPITAL')
        AND has_maternity = 1
        AND (lat IS NULL OR long IS NULL OR lat = 0 OR long = 0)
    """)
    sem_coords = cursor.fetchone()['count']
    print(f"\n[6] Hospitais com maternidade MAS SEM coordenadas válidas: {sem_coords:,}")
    if sem_coords > 0:
        print("   [AVISO] Estes hospitais não aparecem na busca por localização!")
        print("   [DICA] Verificar se o CSV tem coordenadas para estes registros")
    
    # 7. Verificar raio de busca (50km)
    print("\n[7] Hospitais dentro de 50km de Taubaté/SP:")
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
    print(f"   Encontrados: {dentro_50km} hospitais dentro de 50km")
    
    # 8. Verificar raio maior (100km)
    print("\n[8] Hospitais dentro de 100km de Taubaté/SP:")
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
            )) <= 100
    """)
    dentro_100km = cursor.fetchone()['count']
    print(f"   Encontrados: {dentro_100km} hospitais dentro de 100km")
    
    conn.close()
    
    print("\n" + "="*70)
    print("VERIFICAÇÃO CONCLUÍDA")
    print("="*70)
    
    return True

if __name__ == "__main__":
    check_database_coverage()
