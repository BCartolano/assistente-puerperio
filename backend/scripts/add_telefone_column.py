#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para Adicionar Coluna Telefone ao Banco Existente
Purpose: Migração do schema para incluir telefone dos dados do CNES
"""

import os
import sys
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'cnes_cache.db')

def add_telefone_column():
    """Adiciona coluna telefone se não existir"""
    print("="*70)
    print("ADICIONANDO COLUNA TELEFONE AO BANCO")
    print("="*70)
    print()
    
    if not os.path.exists(DB_PATH):
        print(f"[ERRO] Banco de dados nao encontrado: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Verificar se coluna já existe
        cursor.execute("PRAGMA table_info(hospitals_cache)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'telefone' in columns:
            print("[INFO] Coluna 'telefone' ja existe no banco")
        else:
            print("[INFO] Adicionando coluna 'telefone'...")
            cursor.execute("ALTER TABLE hospitals_cache ADD COLUMN telefone TEXT")
            conn.commit()
            print("[OK] Coluna 'telefone' adicionada com sucesso")
        
        # Verificar estrutura final
        cursor.execute("PRAGMA table_info(hospitals_cache)")
        columns = cursor.fetchall()
        print("\n[INFO] Estrutura atual da tabela:")
        for col in columns:
            print(f"   - {col[1]}: {col[2]}")
        
    except Exception as e:
        print(f"[ERRO] Erro ao adicionar coluna: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_telefone_column()
