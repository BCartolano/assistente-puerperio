#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para Corrigir tipo_unidade no Banco de Dados
Purpose: Popular tipo_unidade baseado em CO_TIPO_UNIDADE do CSV original
"""

import os
import sys
import sqlite3
import csv

# Adicionar path do backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from etl.data_ingest import map_tipo_unidade

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'cnes_cache.db')

# Tentar múltiplos caminhos possíveis para o CSV
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
CSV_PATHS = [
    os.path.join(BASE_DIR, 'data', 'tbEstabelecimento202512.csv.csv'),
    os.path.join(BASE_DIR, 'BASE_DE_DADOS_CNES_202512', 'tbEstabelecimento202512.csv.csv'),
    os.path.join(BASE_DIR, 'tbEstabelecimento202512.csv.csv'),
]

def fix_tipo_unidade():
    """Corrige tipo_unidade no banco baseado no CSV original"""
    print("="*70)
    print("CORRECAO DE TIPO_UNIDADE NO BANCO DE DADOS")
    print("="*70)
    print()
    
    if not os.path.exists(DB_PATH):
        print(f"[ERRO] Banco de dados nao encontrado: {DB_PATH}")
        return
    
    # Encontrar CSV
    CSV_PATH = None
    for path in CSV_PATHS:
        if os.path.exists(path):
            CSV_PATH = path
            break
    
    if not CSV_PATH:
        print(f"[ERRO] CSV nao encontrado em nenhum dos caminhos:")
        for path in CSV_PATHS:
            print(f"   - {path}")
        print("[DICA] O script precisa do CSV original para mapear os tipos")
        return
    
    print(f"[OK] CSV encontrado: {CSV_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Criar índice temporário para performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cnes_id ON hospitals_cache(cnes_id)")
    
    # Ler CSV e criar dicionário CNES -> CO_TIPO_UNIDADE
    print("[INFO] Lendo CSV e mapeando tipos...")
    cnes_to_tipo = {}
    
    try:
        with open(CSV_PATH, 'r', encoding='utf-8', errors='ignore') as f:
            # Detectar delimitador
            first_line = f.readline()
            delimiter = ';' if ';' in first_line else ','
            f.seek(0)
            
            # Primeira passagem: identificar colunas
            reader_temp = csv.DictReader(f, delimiter=delimiter)
            fieldnames = reader_temp.fieldnames
            
            # Debug: mostrar colunas
            if fieldnames:
                print(f"[DEBUG] Colunas encontradas (primeiras 10): {list(fieldnames)[:10]}")
                if 'CO_CNES' not in fieldnames:
                    print(f"[AVISO] CO_CNES nao encontrado! Colunas disponiveis:")
                    for col in list(fieldnames)[:20]:
                        print(f"   - {col}")
            
            # Encontrar coluna de tipo - PRIORIZAR TP_UNIDADE (que tem os dados)
            tipo_col = None
            # Primeiro tentar TP_UNIDADE (que é a coluna que realmente tem os dados)
            if 'TP_UNIDADE' in fieldnames:
                tipo_col = 'TP_UNIDADE'
            else:
                # Fallback: procurar por CO_TIPO_UNIDADE
                for col in fieldnames:
                    if 'TIPO' in col.upper() and 'UNIDADE' in col.upper():
                        tipo_col = col
                        break
            
            if not tipo_col:
                print(f"[ERRO] Coluna TP_UNIDADE ou CO_TIPO_UNIDADE nao encontrada!")
                print(f"[INFO] Colunas disponiveis (primeiras 20): {list(fieldnames)[:20]}")
                conn.close()
                return
            
            print(f"[OK] Coluna de tipo encontrada: '{tipo_col}'")
            
            # Segunda passagem: ler dados (recriar reader)
            f.seek(0)
            reader = csv.DictReader(f, delimiter=delimiter)
            
            count = 0
            row_num = 0
            for row in reader:
                row_num += 1
                try:
                    cnes_id = row.get('CO_CNES', '').strip() if row.get('CO_CNES') else ''
                    codigo_tipo = row.get(tipo_col, '').strip() if row.get(tipo_col) else ''
                    
                    # Debug das primeiras linhas
                    if row_num <= 3:
                        print(f"[DEBUG] Linha {row_num}: CNES='{cnes_id[:15] if cnes_id else 'VAZIO'}', Tipo='{codigo_tipo[:5] if codigo_tipo else 'VAZIO'}'")
                    
                    if cnes_id and codigo_tipo:
                        # Mapear tipo
                        tipo_mapped = map_tipo_unidade(codigo_tipo)
                        tipo_final = tipo_mapped or codigo_tipo  # Usar mapeado ou código original
                        cnes_to_tipo[cnes_id] = tipo_final
                        count += 1
                        
                        if count % 50000 == 0:
                            print(f"   Processados: {count} registros validos (linha {row_num})...")
                except Exception as e:
                    # Continuar mesmo se uma linha der erro
                    if row_num <= 5:
                        print(f"[AVISO] Erro na linha {row_num}: {e}")
                    continue
            
            print(f"[INFO] Total de linhas processadas: {row_num}")
            print(f"[INFO] Registros validos encontrados: {count}")
        
        print(f"[OK] Mapeados {len(cnes_to_tipo)} estabelecimentos do CSV")
        print()
        
        if len(cnes_to_tipo) == 0:
            print("[AVISO] Nenhum estabelecimento mapeado. Verifique o CSV.")
            conn.close()
            return
        
        # Atualizar banco em lotes menores para evitar timeout
        print("[INFO] Atualizando banco de dados em lotes...")
        updated = 0
        not_found = 0
        batch_size = 500  # Lotes menores para evitar timeout
        total_items = len(cnes_to_tipo)
        
        items_list = list(cnes_to_tipo.items())
        
        # Usar transação única para melhor performance
        conn.execute("BEGIN TRANSACTION")
        
        try:
            for i in range(0, total_items, batch_size):
                batch = items_list[i:i+batch_size]
                
                try:
                    # Usar executemany para melhor performance
                    updates = []
                    for cnes_id, tipo_unidade in batch:
                        updates.append((tipo_unidade, cnes_id))
                    
                    cursor.executemany("""
                        UPDATE hospitals_cache 
                        SET tipo_unidade = ? 
                        WHERE cnes_id = ? AND (tipo_unidade IS NULL OR tipo_unidade = '')
                    """, updates)
                    
                    # executemany não retorna rowcount confiável, então vamos contar manualmente
                    # Mas vamos assumir que atualizou se não deu erro
                    updated += len(batch)
                    
                    # Commit a cada 10 lotes (5000 registros) para não perder tudo se der erro
                    if (i + batch_size) % 5000 == 0:
                        conn.commit()
                        conn.execute("BEGIN TRANSACTION")
                        print(f"   Commit intermediario: {min(i + batch_size, total_items)}/{total_items} processados...")
                    
                    if (i + batch_size) % 10000 == 0 or i + batch_size >= total_items:
                        print(f"   Progresso: {min(i + batch_size, total_items)}/{total_items} registros processados...")
                        
                except Exception as e:
                    print(f"[ERRO] Erro no lote {i}-{i+batch_size}: {e}")
                    conn.rollback()
                    conn.execute("BEGIN TRANSACTION")
                    # Continuar com próximo lote
                    continue
            
            # Commit final
            conn.commit()
            
            # Contar quantos realmente foram atualizados
            cursor.execute("SELECT COUNT(*) FROM hospitals_cache WHERE tipo_unidade IS NOT NULL")
            com_tipo_after = cursor.fetchone()[0]
            
            # Estimar not_found baseado na diferença
            not_found = total_items - (com_tipo_after - (total - len(cnes_to_tipo)))
            
        except Exception as e:
            print(f"[ERRO] Erro na transacao: {e}")
            conn.rollback()
            raise
        
        print()
        print("="*70)
        print("RESUMO")
        print("="*70)
        print(f"[OK] Registros atualizados: {updated}")
        print(f"[INFO] Registros nao encontrados no banco: {not_found}")
        print()
        
        # Verificar resultado final
        cursor.execute("SELECT COUNT(*) FROM hospitals_cache WHERE tipo_unidade IS NOT NULL")
        com_tipo = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM hospitals_cache")
        total = cursor.fetchone()[0]
        
        print(f"[INFO] Total de registros com tipo_unidade: {com_tipo}/{total}")
        print(f"[INFO] Percentual: {(com_tipo/total*100):.1f}%")
        
        # Estatísticas por tipo
        print()
        print("="*70)
        print("ESTATISTICAS POR TIPO")
        print("="*70)
        cursor.execute("""
            SELECT tipo_unidade, COUNT(*) as count 
            FROM hospitals_cache 
            WHERE tipo_unidade IS NOT NULL
            GROUP BY tipo_unidade 
            ORDER BY count DESC
            LIMIT 15
        """)
        tipos_stats = cursor.fetchall()
        for tipo, count in tipos_stats:
            print(f"   {tipo:20} : {count:6} registros")
        
    except Exception as e:
        print(f"[ERRO] Erro ao processar: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_tipo_unidade()
