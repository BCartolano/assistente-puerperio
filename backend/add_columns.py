#!/usr/bin/env python3
"""
Script para adicionar colunas que faltam no banco de dados
"""

import sqlite3
import os

# Caminho do banco de dados
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def add_missing_columns():
    """Adiciona colunas que faltam na tabela users"""
    if not os.path.exists(DB_PATH):
        print("Banco de dados não encontrado!")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verifica quais colunas existem
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = [column[1] for column in cursor.fetchall()]
    
    print("Colunas existentes:", existing_columns)
    
    # Colunas que devem existir
    required_columns = {
        'email_verified': 'INTEGER DEFAULT 0',
        'email_verification_token': 'TEXT',
        'reset_password_token': 'TEXT',
        'reset_password_expires': 'TIMESTAMP'
    }
    
    # Adiciona colunas que faltam
    added = []
    for column_name, column_type in required_columns.items():
        if column_name not in existing_columns:
            try:
                cursor.execute(f'ALTER TABLE users ADD COLUMN {column_name} {column_type}')
                added.append(column_name)
                print(f"✅ Coluna '{column_name}' adicionada com sucesso!")
            except Exception as e:
                print(f"❌ Erro ao adicionar coluna '{column_name}': {e}")
        else:
            print(f"✓ Coluna '{column_name}' já existe")
    
    conn.commit()
    conn.close()
    
    if added:
        print(f"\n🎉 Colunas adicionadas: {', '.join(added)}")
    else:
        print("\n✅ Todas as colunas já existem!")
    
    return len(added)

if __name__ == "__main__":
    print("=" * 50)
    print("🔧 ADICIONANDO COLUNAS FALTANTES")
    print("=" * 50)
    
    try:
        count = add_missing_columns()
        print(f"\n✅ Processo concluído! {count} coluna(s) adicionada(s).")
    except Exception as e:
        print(f"\n❌ Erro: {e}")

