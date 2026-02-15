#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrigir Empresas Fantasmas e Coordenadas Duplicadas
Purpose: Remover empresas fantasmas e corrigir coordenadas duplicadas
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

def fix_duplicate_coordinates():
    """Remove hospitais com coordenadas duplicadas (erro de geocodificação)"""
    print("="*70)
    print("CORREÇÃO DE COORDENADAS DUPLICADAS")
    print("="*70)
    print()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Encontrar grupos de coordenadas duplicadas (mais de 3 hospitais no mesmo ponto)
    print("[1] Identificando coordenadas duplicadas...")
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
    """)
    
    duplicates = cursor.fetchall()
    
    if not duplicates:
        print("   [OK] Nenhuma coordenada duplicada encontrada")
        conn.close()
        return 0
    
    print(f"   [ENCONTRADOS] {len(duplicates)} grupos de coordenadas duplicadas")
    
    total_removidos = 0
    
    for dup in duplicates:
        lat, lon = dup['lat'], dup['long']
        count = dup['count']
        cnes_ids = dup['cnes_ids'].split(',')
        
        print(f"\n   Grupo: {count} hospitais em Lat={lat}, Long={lon}")
        
        # Verificar endereços destes hospitais
        cursor.execute("""
            SELECT cnes_id, name, fantasy_name, address
            FROM hospitals_cache
            WHERE cnes_id IN ({})
        """.format(','.join(['?' for _ in cnes_ids])), cnes_ids)
        
        hospitais = cursor.fetchall()
        
        # Se todos têm endereços diferentes mas mesma coordenada, é erro de geocodificação
        enderecos = [h['address'] for h in hospitais if h['address']]
        enderecos_unicos = len(set(enderecos))
        
        if enderecos_unicos > 1:
            print(f"      [ERRO] {enderecos_unicos} endereços diferentes na mesma coordenada")
            print(f"      [ACAO] Removendo has_maternity=1 (coordenadas não confiáveis)")
            
            # Remover has_maternity=1 (coordenadas não confiáveis)
            cursor.execute("""
                UPDATE hospitals_cache
                SET has_maternity = 0
                WHERE cnes_id IN ({})
            """.format(','.join(['?' for _ in cnes_ids])), cnes_ids)
            
            removidos = cursor.rowcount
            total_removidos += removidos
            print(f"      [OK] {removidos} hospitais removidos")
            
            # Mostrar exemplos
            for hosp in hospitais[:3]:
                nome = hosp['fantasy_name'] or hosp['name'] or 'Sem nome'
                print(f"         - {nome} (CNES: {hosp['cnes_id']})")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*70)
    print("CORREÇÃO CONCLUÍDA")
    print("="*70)
    print(f"[OK] Total de hospitais removidos: {total_removidos}")
    
    return total_removidos


def fix_generic_names():
    """Remove hospitais com nomes muito genéricos sem informações adicionais"""
    print("\n" + "="*70)
    print("CORREÇÃO DE NOMES GENÉRICOS")
    print("="*70)
    print()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Nomes muito genéricos que podem ser empresas fantasmas
    generic_patterns = [
        ('HOSPITAL', "name = 'HOSPITAL' OR name LIKE 'HOSPITAL %' OR fantasy_name = 'HOSPITAL' OR fantasy_name LIKE 'HOSPITAL %'"),
        ('UNIDADE', "name = 'UNIDADE' OR name LIKE 'UNIDADE %' OR fantasy_name = 'UNIDADE' OR fantasy_name LIKE 'UNIDADE %'"),
    ]
    
    total_removidos = 0
    
    for pattern_name, condition in generic_patterns:
        # Buscar hospitais com nome genérico E sem telefone E sem endereço completo
        cursor.execute(f"""
            SELECT COUNT(*) as count
            FROM hospitals_cache
            WHERE has_maternity = 1
            AND tipo_unidade IN ('05', '07', 'HOSPITAL')
            AND ({condition})
            AND (telefone IS NULL OR telefone = '')
            AND (address IS NULL OR address = '' OR address LIKE '%NULL%')
        """)
        
        count = cursor.fetchone()['count']
        
        if count > 0:
            print(f"[{pattern_name}] {count} hospitais com nome genérico e sem contato")
            
            cursor.execute(f"""
                UPDATE hospitals_cache
                SET has_maternity = 0
                WHERE has_maternity = 1
                AND tipo_unidade IN ('05', '07', 'HOSPITAL')
                AND ({condition})
                AND (telefone IS NULL OR telefone = '')
                AND (address IS NULL OR address = '' OR address LIKE '%NULL%')
            """)
            
            removidos = cursor.rowcount
            total_removidos += removidos
            print(f"   [OK] {removidos} hospitais removidos")
    
    conn.commit()
    conn.close()
    
    return total_removidos


def main():
    """Corrige empresas fantasmas e coordenadas duplicadas"""
    print("="*70)
    print("CORREÇÃO: EMPRESAS FANTASMAS E COORDENADAS DUPLICADAS")
    print("="*70)
    print()
    
    # 1. Corrigir coordenadas duplicadas
    removed_duplicates = fix_duplicate_coordinates()
    
    # 2. Corrigir nomes genéricos sem informações
    removed_generic = fix_generic_names()
    
    total = removed_duplicates + removed_generic
    
    print("\n" + "="*70)
    print("RESUMO FINAL")
    print("="*70)
    print(f"[OK] Total de hospitais corrigidos: {total}")
    print(f"   - Coordenadas duplicadas: {removed_duplicates}")
    print(f"   - Nomes genéricos: {removed_generic}")
    
    if total > 0:
        print(f"\n[SUCESSO] {total} hospitais suspeitos removidos da busca de maternidades!")
    else:
        print("\n[INFO] Nenhum hospital adicional precisou ser removido")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
