#!/usr/bin/env python3
"""
Script para verificar status de um usuário no banco
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def check_user(email):
    """Verifica o status de um usuário"""
    if not os.path.exists(DB_PATH):
        print("Banco de dados não encontrado!")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, name, email, email_verified, email_verification_token 
        FROM users 
        WHERE email = ?
    ''', (email.lower(),))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        print(f"❌ Usuário com email '{email}' não encontrado.")
        return
    
    user_id, name, email_db, email_verified, token = user
    
    print("=" * 50)
    print(f"👤 USUÁRIO: {name}")
    print(f"📧 Email: {email_db}")
    print(f"🆔 ID: {user_id}")
    print(f"✅ Email verificado: {'SIM' if email_verified == 1 else 'NÃO'}")
    print(f"🔑 Token de verificação: {'Existe' if token else 'Não existe'}")
    print("=" * 50)
    
    if email_verified == 0:
        print("\n⚠️ ATENÇÃO: Email NÃO está verificado!")
        print("Ação: Verifique seu email ou use o script para marcar como verificado.")
    else:
        print("\n✅ Email está verificado! Login deve funcionar.")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        email = sys.argv[1]
    else:
        email = input("Digite o email para verificar: ").strip().lower()
    
    check_user(email)

