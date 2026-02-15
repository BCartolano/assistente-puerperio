#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Verificação de Coordenadas de Hospitais
Purpose: Identificar hospitais sem coordenadas válidas no banco de dados
"""

import os
import sys
import sqlite3

# Adicionar path do backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'cnes_cache.db')

def check_hospital_coordinates():
    """Verifica coordenadas de hospitais no banco de dados"""
    print("="*70)
    print("VERIFICAÇÃO DE COORDENADAS DE HOSPITAIS")
    print("="*70)
    print()
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Banco de dados não encontrado: {DB_PATH}")
        print("💡 Execute o script de ingestão primeiro: python backend/etl/data_ingest.py")
        return
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Primeiro, verificar o que existe no banco
    print("DIAGNOSTICO DO BANCO DE DADOS")
    print("="*70)
    
    # Contar total de registros
    cursor.execute("SELECT COUNT(*) as total FROM hospitals_cache")
    total_registros = cursor.fetchone()['total']
    print(f"[INFO] Total de registros no banco: {total_registros}")
    
    if total_registros == 0:
        print("\n[AVISO] BANCO DE DADOS VAZIO!")
        print("[DICA] Execute o script de ingestao primeiro:")
        print("   python backend/etl/data_ingest.py")
        conn.close()
        return
    
    # Ver quais tipos de unidade existem
    cursor.execute("""
        SELECT tipo_unidade, COUNT(*) as count 
        FROM hospitals_cache 
        WHERE tipo_unidade IS NOT NULL
        GROUP BY tipo_unidade 
        ORDER BY count DESC
        LIMIT 20
    """)
    tipos_existentes = cursor.fetchall()
    
    print(f"\n[INFO] Tipos de unidade encontrados no banco:")
    if tipos_existentes:
        for row in tipos_existentes:
            print(f"   - '{row['tipo_unidade']}': {row['count']} registros")
    else:
        print("   [AVISO] Nenhum tipo encontrado (todos NULL?)")
    
    # Verificar se há registros NULL
    cursor.execute("SELECT COUNT(*) as count FROM hospitals_cache WHERE tipo_unidade IS NULL")
    null_count = cursor.fetchone()['count']
    if null_count > 0:
        print(f"   - NULL: {null_count} registros")
    print()
    
    # Verificar especificamente por códigos de hospital
    print("[INFO] Buscando hospitais por codigos numericos...")
    cursor.execute("""
        SELECT tipo_unidade, COUNT(*) as count 
        FROM hospitals_cache 
        WHERE tipo_unidade IN ('05', '07', '73')
        GROUP BY tipo_unidade
    """)
    hospitais_por_codigo = cursor.fetchall()
    if hospitais_por_codigo:
        for row in hospitais_por_codigo:
            print(f"   - Codigo '{row['tipo_unidade']}': {row['count']} registros")
    else:
        print("   [AVISO] Nenhum hospital encontrado pelos codigos 05, 07, 73")
    
    # Verificar por tipos mapeados
    print("\n[INFO] Buscando hospitais por tipos mapeados...")
    cursor.execute("""
        SELECT tipo_unidade, COUNT(*) as count 
        FROM hospitals_cache 
        WHERE tipo_unidade IN ('HOSPITAL', 'UPA')
        GROUP BY tipo_unidade
    """)
    hospitais_mapeados = cursor.fetchall()
    if hospitais_mapeados:
        for row in hospitais_mapeados:
            print(f"   - Tipo '{row['tipo_unidade']}': {row['count']} registros")
    else:
        print("   [AVISO] Nenhum hospital encontrado pelos tipos HOSPITAL, UPA")
    print()
    
    # Buscar todos os hospitais (códigos originais E tipos mapeados)
    # O banco pode ter: '05', '07', '73' (códigos) OU 'HOSPITAL', 'UPA' (mapeados)
    query = """
        SELECT 
            cnes_id,
            name,
            fantasy_name,
            tipo_unidade,
            lat,
            long,
            address,
            city,
            neighborhood
        FROM hospitals_cache
        WHERE tipo_unidade IN ('05', '07', '73', 'HOSPITAL', 'UPA')
           OR tipo_unidade LIKE '%HOSPITAL%'
           OR tipo_unidade LIKE '%UPA%'
        ORDER BY tipo_unidade, name
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    print("="*70)
    print(f"[INFO] Total de Hospitais/UPAs encontrados: {len(rows)}\n")
    
    if len(rows) == 0:
        print("[AVISO] NENHUM HOSPITAL/UPA ENCONTRADO!")
        print("\n[DICA] Possiveis causas:")
        print("   1. O banco nao foi populado com dados de hospitais")
        print("   2. Os tipos estao armazenados de forma diferente")
        print("   3. Os hospitais foram filtrados durante a ingestao")
        print("\n[INFO] Verificando registros com coordenadas validas...")
        
        # Verificar se há registros com coordenadas (qualquer tipo)
        cursor.execute("""
            SELECT COUNT(*) as count 
            FROM hospitals_cache 
            WHERE lat IS NOT NULL AND long IS NOT NULL 
              AND lat != 0 AND long != 0
        """)
        com_coords = cursor.fetchone()['count']
        print(f"   Registros com coordenadas validas: {com_coords}")
        
        if com_coords > 0:
            print("\n[DICA] Sugestao: Verifique como os tipos estao armazenados:")
            print("   SELECT DISTINCT tipo_unidade FROM hospitals_cache LIMIT 10;")
        
        conn.close()
        return
    
    # Categorizar por status de coordenadas
    with_coords = []
    without_coords = []
    invalid_coords = []
    
    for row in rows:
        lat = row['lat']
        long = row['long']
        
        # Verificar se coordenadas são válidas
        if lat is None or long is None:
            without_coords.append(row)
        elif lat == 0.0 or long == 0.0:
            invalid_coords.append(row)
        elif abs(lat) > 90 or abs(long) > 180:
            invalid_coords.append(row)
        else:
            with_coords.append(row)
    
    # Relatório
    print("="*70)
    print("RESUMO")
    print("="*70)
    print(f"[OK] Com coordenadas validas: {len(with_coords)}")
    print(f"[ERRO] Sem coordenadas (NULL): {len(without_coords)}")
    print(f"[AVISO] Coordenadas invalidas (0 ou fora do range): {len(invalid_coords)}")
    print()
    
    # Listar hospitais sem coordenadas
    if without_coords:
        print("="*70)
        print(f"HOSPITAIS SEM COORDENADAS ({len(without_coords)})")
        print("="*70)
        for row in without_coords[:20]:  # Limitar a 20 para não poluir
            tipo = row['tipo_unidade']
            nome = row['fantasy_name'] or row['name'] or 'Sem nome'
            endereco = row['address'] or 'Sem endereço'
            print(f"\n[ERRO] {tipo} - {nome}")
            print(f"   Endereço: {endereco}")
            print(f"   CNES: {row['cnes_id']}")
        if len(without_coords) > 20:
            print(f"\n... e mais {len(without_coords) - 20} hospitais sem coordenadas")
        print()
    
    # Listar hospitais com coordenadas inválidas
    if invalid_coords:
        print("="*70)
        print(f"HOSPITAIS COM COORDENADAS INVÁLIDAS ({len(invalid_coords)})")
        print("="*70)
        for row in invalid_coords[:20]:  # Limitar a 20
            tipo = row['tipo_unidade']
            nome = row['fantasy_name'] or row['name'] or 'Sem nome'
            lat = row['lat']
            long = row['long']
            print(f"\n[AVISO] {tipo} - {nome}")
            print(f"   Coordenadas: ({lat}, {long})")
            print(f"   CNES: {row['cnes_id']}")
        if len(invalid_coords) > 20:
            print(f"\n... e mais {len(invalid_coords) - 20} hospitais com coordenadas inválidas")
        print()
    
    # Estatísticas por tipo
    print("="*70)
    print("ESTATÍSTICAS POR TIPO")
    print("="*70)
    
    tipos = {}
    for row in rows:
        tipo = row['tipo_unidade']
        if tipo not in tipos:
            tipos[tipo] = {'total': 0, 'com_coords': 0, 'sem_coords': 0}
        tipos[tipo]['total'] += 1
        
        lat = row['lat']
        long = row['long']
        if lat and long and lat != 0 and long != 0 and abs(lat) <= 90 and abs(long) <= 180:
            tipos[tipo]['com_coords'] += 1
        else:
            tipos[tipo]['sem_coords'] += 1
    
    for tipo, stats in sorted(tipos.items()):
        pct = (stats['com_coords'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"{tipo:15} | Total: {stats['total']:3} | Com coords: {stats['com_coords']:3} ({pct:5.1f}%) | Sem coords: {stats['sem_coords']:3}")
    
    print()
    
    # Recomendações
    if without_coords or invalid_coords:
        print("="*70)
        print("RECOMENDAÇÕES")
        print("="*70)
        print("1. Hospitais sem coordenadas não aparecerão na busca geográfica")
        print("2. Considere usar geocoding (Google Maps API, OpenStreetMap) para")
        print("   popular coordenadas baseadas no endereço (CEP + Número)")
        print("3. Script de geocoding pode ser criado em: backend/scripts/geocode_hospitals.py")
        print()
    
    conn.close()

if __name__ == "__main__":
    check_hospital_coordinates()
