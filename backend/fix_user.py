#!/usr/bin/env python3
"""
Script para corrigir problemas de autenticação de usuários
Permite deletar ou resetar a senha de um usuário específico
"""

import sqlite3
import sys
import os

# Caminho do banco de dados
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def list_users():
    """Lista todos os usuários do banco"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, created_at FROM users')
    users = cursor.fetchall()
    conn.close()
    
    if not users:
        print("Nenhum usuário encontrado no banco de dados.")
        return []
    
    print("\n=== USUÁRIOS CADASTRADOS ===")
    for user in users:
        print(f"ID: {user[0]} | Nome: {user[1]} | Email: {user[2]} | Criado em: {user[3]}")
    print()
    
    return users

def delete_user(email):
    """Deleta um usuário pelo email"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Busca o usuário
    cursor.execute('SELECT id FROM users WHERE email = ?', (email.lower(),))
    user = cursor.fetchone()
    
    if not user:
        print(f"Usuário com email '{email}' não encontrado.")
        conn.close()
        return False
    
    user_id = user[0]
    
    # Deleta vacinas associadas
    cursor.execute('DELETE FROM vacinas_tomadas WHERE user_id = ?', (user_id,))
    
    # Deleta usuário
    cursor.execute('DELETE FROM users WHERE email = ?', (email.lower(),))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Usuário '{email}' deletado com sucesso!")
    return True

def main():
    print("=" * 50)
    print("🔧 FERRAMENTA DE CORREÇÃO DE USUÁRIOS")
    print("=" * 50)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Banco de dados não encontrado em: {DB_PATH}")
        sys.exit(1)
    
    # Lista usuários
    users = list_users()
    
    if not users:
        print("Banco de dados vazio. Você pode fazer um novo cadastro.")
        sys.exit(0)
    
    print("\nO que você deseja fazer?")
    print("1. Deletar um usuário (permitirá novo cadastro com o mesmo email)")
    print("2. Sair")
    
    choice = input("\nEscolha uma opção (1 ou 2): ").strip()
    
    if choice == '1':
        email = input("\nDigite o email do usuário que deseja deletar: ").strip().lower()
        if email:
            confirm = input(f"Tem certeza que deseja deletar o usuário '{email}'? (s/n): ").strip().lower()
            if confirm in ['s', 'sim', 'y', 'yes']:
                if delete_user(email):
                    print("\n✅ Pronto! Agora você pode fazer um novo cadastro com este email.")
                else:
                    print("\n❌ Não foi possível deletar o usuário.")
            else:
                print("Operação cancelada.")
        else:
            print("Email não fornecido.")
    else:
        print("Saindo...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)

