#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Busca de Maternidades
Purpose: Validar que a busca de hospitais maternos está funcionando corretamente
"""

import os
import sys
import sqlite3

# Adicionar path do backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'cnes_cache.db')

def test_maternity_search():
    """Testa busca de hospitais com maternidade"""
    print("="*70)
    print("TESTE DE BUSCA DE MATERNIDADES")
    print("="*70)
    print()
    
    if not os.path.exists(DB_PATH):
        print(f"[ERRO] Banco de dados nao encontrado: {DB_PATH}")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Teste 1: Verificar se há hospitais com maternidade
    print("[TESTE 1] Verificando hospitais com maternidade...")
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM hospitals_cache 
        WHERE has_maternity = 1
    """)
    total_maternity = cursor.fetchone()['count']
    print(f"   [OK] Total de hospitais com maternidade: {total_maternity}")
    
    if total_maternity == 0:
        print("   [AVISO] Nenhum hospital com maternidade encontrado!")
        print("   [DICA] Execute o script de ingestao: python backend/etl/data_ingest.py")
        conn.close()
        return False
    
    # Teste 2: Verificar se há hospitais (tipo 05, 07) com maternidade
    print("\n[TESTE 2] Verificando hospitais (tipo 05, 07) com maternidade...")
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM hospitals_cache 
        WHERE has_maternity = 1
          AND tipo_unidade IN ('05', '07', 'HOSPITAL')
    """)
    hospitais_maternidade = cursor.fetchone()['count']
    print(f"   [OK] Hospitais (tipo 05/07/HOSPITAL) com maternidade: {hospitais_maternidade}")
    
    if hospitais_maternidade == 0:
        print("   [AVISO] Nenhum hospital do tipo correto com maternidade!")
        conn.close()
        return False
    
    # Teste 3: Verificar se UPAs não têm maternidade
    print("\n[TESTE 3] Verificando que UPAs nao tem maternidade...")
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM hospitals_cache 
        WHERE tipo_unidade IN ('73', 'UPA')
          AND has_maternity = 1
    """)
    upas_com_maternidade = cursor.fetchone()['count']
    
    if upas_com_maternidade > 0:
        print(f"   [ERRO] {upas_com_maternidade} UPAs marcadas com maternidade (ERRO CRITICO!)")
        conn.close()
        return False
    else:
        print("   [OK] Nenhuma UPA marcada com maternidade (correto)")
    
    # Teste 4: Verificar se há telefones salvos
    print("\n[TESTE 4] Verificando campo telefone...")
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM hospitals_cache 
        WHERE telefone IS NOT NULL AND telefone != ''
    """)
    com_telefone = cursor.fetchone()['count']
    
    # Verificar se coluna existe
    cursor.execute("PRAGMA table_info(hospitals_cache)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'telefone' not in columns:
        print("   [AVISO] Coluna 'telefone' nao existe no banco!")
        print("   [DICA] Execute: python backend/scripts/add_telefone_column.py")
    else:
        print(f"   [OK] Hospitais com telefone: {com_telefone}")
        if com_telefone == 0:
            print("   [AVISO] Nenhum telefone salvo. Re-execute a ingestao do CSV.")
    
    # Teste 5: Verificar dados críticos
    print("\n[TESTE 5] Verificando dados criticos...")
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN address IS NOT NULL AND address != '' THEN 1 ELSE 0 END) as com_endereco,
            SUM(CASE WHEN lat IS NOT NULL AND long IS NOT NULL AND lat != 0 AND long != 0 THEN 1 ELSE 0 END) as com_coords,
            SUM(CASE WHEN is_sus IS NOT NULL THEN 1 ELSE 0 END) as com_sus_flag,
            SUM(CASE WHEN management IS NOT NULL THEN 1 ELSE 0 END) as com_gestao
        FROM hospitals_cache
        WHERE has_maternity = 1
          AND tipo_unidade IN ('05', '07', 'HOSPITAL')
    """)
    stats = cursor.fetchone()
    
    print(f"   Total de hospitais maternos: {stats['total']}")
    print(f"   Com endereco: {stats['com_endereco']} ({stats['com_endereco']/stats['total']*100:.1f}%)")
    print(f"   Com coordenadas: {stats['com_coords']} ({stats['com_coords']/stats['total']*100:.1f}%)")
    print(f"   Com flag SUS: {stats['com_sus_flag']} ({stats['com_sus_flag']/stats['total']*100:.1f}%)")
    print(f"   Com gestao: {stats['com_gestao']} ({stats['com_gestao']/stats['total']*100:.1f}%)")
    
    # Teste 6: Exemplo de busca (simulação)
    print("\n[TESTE 6] Exemplo de busca (coordenadas de Sao Paulo)...")
    cursor.execute("""
        SELECT 
            name,
            fantasy_name,
            address,
            telefone,
            tipo_unidade,
            has_maternity,
            is_sus,
            management,
            lat,
            long,
            (6371 * acos(
                cos(radians(-23.5505)) * 
                cos(radians(lat)) * 
                cos(radians(long) - radians(-46.6333)) + 
                sin(radians(-23.5505)) * 
                sin(radians(lat))
            )) AS distance_km
        FROM hospitals_cache
        WHERE has_maternity = 1
          AND tipo_unidade IN ('05', '07', 'HOSPITAL')
          AND lat IS NOT NULL 
          AND long IS NOT NULL
          AND lat != 0 
          AND long != 0
        ORDER BY distance_km
        LIMIT 5
    """)
    
    exemplos = cursor.fetchall()
    if exemplos:
        print(f"   [OK] Encontrados {len(exemplos)} hospitais maternos proximos de SP:")
        for i, row in enumerate(exemplos, 1):
            nome = row['fantasy_name'] or row['name'] or 'Sem nome'
            distancia = row['distance_km']
            sus = "SUS" if row['is_sus'] else "Privado"
            telefone = row['telefone'] or "Nao disponivel"
            print(f"   {i}. {nome} ({sus}) - {distancia:.1f} km - Tel: {telefone}")
    else:
        print("   [AVISO] Nenhum hospital materno encontrado proximo de SP")
    
    conn.close()
    
    print("\n" + "="*70)
    print("RESUMO DOS TESTES")
    print("="*70)
    print("[OK] Testes de validacao concluidos!")
    print("[INFO] Se todos os testes passaram, a busca de maternidades esta funcionando.")
    print()
    
    return True

if __name__ == "__main__":
    test_maternity_search()
