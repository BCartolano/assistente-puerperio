#!/usr/bin/env python3
"""
Script para verificar manualmente o email de um usuário
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def verify_user_email(email):
    """Marca o email de um usuário como verificado"""
    if not os.path.exists(DB_PATH):
        print("❌ Banco de dados não encontrado!")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verifica se usuário existe
    cursor.execute('SELECT id, name, email_verified FROM users WHERE email = ?', (email.lower(),))
    user = cursor.fetchone()
    
    if not user:
        print(f"❌ Usuário com email '{email}' não encontrado.")
        conn.close()
        return False
    
    user_id, name, email_verified = user
    
    if email_verified == 1:
        print(f"✅ Email de '{name}' já está verificado!")
        conn.close()
        return True
    
    # Marca como verificado
    cursor.execute('''
        UPDATE users 
        SET email_verified = 1, email_verification_token = NULL
        WHERE email = ?
    ''', (email.lower(),))
    
    conn.commit()
    conn.close()
    
    print("=" * 50)
    print(f"✅ Email de '{name}' ({email}) foi marcado como VERIFICADO!")
    print("Agora você pode fazer login normalmente.")
    print("=" * 50)
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        email = input("Digite o email para verificar: ").strip().lower()
    
    verify_user_email(email)

