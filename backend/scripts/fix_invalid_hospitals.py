#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrigir Hospitais com Problemas
Purpose: Remover/corrigir hospitais com coordenadas inválidas ou suspeitas
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

def fix_invalid_hospitals():
    """Corrige hospitais com coordenadas inválidas ou suspeitas"""
    print("="*70)
    print("CORREÇÃO DE HOSPITAIS COM PROBLEMAS")
    print("="*70)
    print()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Coordenadas válidas para Brasil
    BRASIL_LAT_MIN = -35.0
    BRASIL_LAT_MAX = 5.0
    BRASIL_LON_MIN = -75.0
    BRASIL_LON_MAX = -30.0
    
    total_removidos = 0
    
    # 1. Remover hospitais com coordenadas fora do Brasil
    print("[1] Removendo hospitais com coordenadas fora do Brasil...")
    cursor.execute("""
        SELECT cnes_id, name, fantasy_name, lat, long
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
        print(f"   [CORRIGINDO] {len(fora_brasil)} hospitais com coordenadas fora do Brasil:")
        for hosp in fora_brasil:
            nome = hosp['fantasy_name'] or hosp['name'] or 'Sem nome'
            print(f"      - {nome} (CNES: {hosp['cnes_id']}, Lat: {hosp['lat']}, Long: {hosp['long']})")
        
        # Remover has_maternity=1 destes hospitais (não são válidos para busca)
        cursor.execute("""
            UPDATE hospitals_cache
            SET has_maternity = 0
            WHERE tipo_unidade IN ('05', '07', 'HOSPITAL')
            AND has_maternity = 1
            AND lat IS NOT NULL AND long IS NOT NULL
            AND lat != 0 AND long != 0
            AND (
                lat < ? OR lat > ? OR long < ? OR long > ?
            )
        """, (BRASIL_LAT_MIN, BRASIL_LAT_MAX, BRASIL_LON_MIN, BRASIL_LON_MAX))
        removidos = cursor.rowcount
        total_removidos += removidos
        print(f"   [OK] {removidos} hospitais removidos da busca de maternidades")
    else:
        print("   [OK] Nenhum hospital com coordenadas fora do Brasil")
    
    # 2. Identificar coordenadas duplicadas (mais de 5 hospitais no mesmo ponto)
    print("\n[2] Verificando coordenadas duplicadas (erro de geocodificação)...")
    cursor.execute("""
        SELECT lat, long, COUNT(*) as count, GROUP_CONCAT(cnes_id) as cnes_ids
        FROM hospitals_cache
        WHERE tipo_unidade IN ('05', '07', 'HOSPITAL')
        AND has_maternity = 1
        AND lat IS NOT NULL AND long IS NOT NULL
        AND lat != 0 AND long != 0
        AND lat BETWEEN ? AND ? AND long BETWEEN ? AND ?
        GROUP BY lat, long
        HAVING COUNT(*) > 5
    """, (BRASIL_LAT_MIN, BRASIL_LAT_MAX, BRASIL_LON_MIN, BRASIL_LON_MAX))
    duplicatas = cursor.fetchall()
    
    if duplicatas:
        print(f"   [AVISO] {len(duplicatas)} grupos de coordenadas duplicadas encontrados")
        print("   [INFO] Estes hospitais provavelmente têm coordenadas incorretas (geocodificação errada)")
        print("   [ACAO] Verificando se podem ser corrigidos ou devem ser removidos...")
        
        # Para cada grupo duplicado, verificar se há endereços válidos
        for dup in duplicatas:
            lat, lon = dup['lat'], dup['long']
            count = dup['count']
            cnes_ids = dup['cnes_ids'].split(',')
            
            print(f"\n      Grupo: {count} hospitais em Lat={lat}, Long={lon}")
            
            # Verificar endereços destes hospitais
            cursor.execute("""
                SELECT cnes_id, name, fantasy_name, address, city, state
                FROM hospitals_cache
                WHERE cnes_id IN ({})
                LIMIT 5
            """.format(','.join(['?' for _ in cnes_ids[:10]])), cnes_ids[:10])
            hospitais = cursor.fetchall()
            
            # Se todos têm endereços diferentes mas mesma coordenada, é erro de geocodificação
            enderecos_diferentes = len(set(h['address'] for h in hospitais if h['address']))
            if enderecos_diferentes > 1:
                print(f"         [ERRO] {enderecos_diferentes} endereços diferentes na mesma coordenada - erro de geocodificação")
                print(f"         [ACAO] Removendo has_maternity=1 para estes hospitais (coordenadas não confiáveis)")
                
                # Remover has_maternity=1 (coordenadas não confiáveis)
                cursor.execute("""
                    UPDATE hospitals_cache
                    SET has_maternity = 0
                    WHERE cnes_id IN ({})
                """.format(','.join(['?' for _ in cnes_ids])), cnes_ids)
                removidos = cursor.rowcount
                total_removidos += removidos
                print(f"         [OK] {removidos} hospitais removidos")
    else:
        print("   [OK] Nenhuma coordenada duplicada suspeita")
    
    # 3. Remover hospitais com nomes suspeitos (apenas se realmente suspeito)
    print("\n[3] Verificando hospitais com nomes suspeitos...")
    # "Rio Do Testo" pode ser legítimo (nome de lugar), vamos ser conservadores
    # Só remover se for claramente teste/exemplo
    cursor.execute("""
        SELECT cnes_id, name, fantasy_name
        FROM hospitals_cache
        WHERE tipo_unidade IN ('05', '07', 'HOSPITAL')
        AND has_maternity = 1
        AND (
            UPPER(COALESCE(name, '')) LIKE '%TESTE%' AND UPPER(COALESCE(name, '')) NOT LIKE '%TEST%'
            OR UPPER(COALESCE(fantasy_name, '')) LIKE '%TESTE%' AND UPPER(COALESCE(fantasy_name, '')) NOT LIKE '%TEST%'
        )
        AND (
            UPPER(COALESCE(name, '')) LIKE '%TESTE%EXEMPLO%'
            OR UPPER(COALESCE(fantasy_name, '')) LIKE '%TESTE%EXEMPLO%'
        )
    """)
    suspeitos = cursor.fetchall()
    if suspeitos:
        print(f"   [REMOVENDO] {len(suspeitos)} hospitais claramente suspeitos...")
        for hosp in suspeitos:
            nome = hosp['fantasy_name'] or hosp['name'] or 'Sem nome'
            print(f"      - {nome} (CNES: {hosp['cnes_id']})")
        cursor.execute("""
            UPDATE hospitals_cache
            SET has_maternity = 0
            WHERE cnes_id IN ({})
        """.format(','.join(['?' for _ in suspeitos])), [h['cnes_id'] for h in suspeitos])
        removidos = cursor.rowcount
        total_removidos += removidos
        print(f"   [OK] {removidos} hospitais removidos")
    else:
        print("   [OK] Nenhum hospital claramente suspeito encontrado")
    
    # 4. Adicionar validação de coordenadas no banco (atualizar has_maternity=0 para coordenadas inválidas)
    print("\n[4] Validando todas as coordenadas restantes...")
    cursor.execute("""
        UPDATE hospitals_cache
        SET has_maternity = 0
        WHERE tipo_unidade IN ('05', '07', 'HOSPITAL')
        AND has_maternity = 1
        AND (
            lat IS NULL OR long IS NULL
            OR lat = 0 OR long = 0
            OR lat < ? OR lat > ? OR long < ? OR long > ?
        )
    """, (BRASIL_LAT_MIN, BRASIL_LAT_MAX, BRASIL_LON_MIN, BRASIL_LON_MAX))
    validacao = cursor.rowcount
    if validacao > 0:
        print(f"   [OK] {validacao} hospitais adicionais com coordenadas inválidas removidos")
        total_removidos += validacao
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*70)
    print("CORREÇÃO CONCLUÍDA")
    print("="*70)
    print(f"[OK] Total de hospitais corrigidos: {total_removidos}")
    print(f"[INFO] Estes hospitais foram marcados com has_maternity=0 (não aparecerão na busca)")
    
    return True

if __name__ == "__main__":
    success = fix_invalid_hospitals()
    sys.exit(0 if success else 1)
