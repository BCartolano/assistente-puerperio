#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar e testar login de um usuário
"""

import sqlite3
import bcrypt
import base64
import sys
import os

# Configura encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Caminho do banco
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def check_user_password(email, password_to_test):
    """Verifica se a senha está correta para um usuário"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    email_lower = email.lower().strip()
    
    cursor.execute('''
        SELECT id, name, email, password_hash, email_verified 
        FROM users 
        WHERE email = ?
    ''', (email_lower,))
    
    user_data = cursor.fetchone()
    
    if not user_data:
        print(f"❌ Usuário com email '{email_lower}' não encontrado!")
        conn.close()
        return False
    
    user_id, user_name, user_email, stored_hash_str, email_verified = user_data
    
    print(f"\n{'='*60}")
    print(f"👤 Usuário encontrado:")
    print(f"   ID: {user_id}")
    print(f"   Nome: {user_name}")
    print(f"   Email: {user_email}")
    print(f"   Email verificado: {'Sim' if email_verified == 1 else 'Não'}")
    print(f"{'='*60}\n")
    
    # Tenta diferentes formatos de hash
    stored_hash = None
    hash_format = "desconhecido"
    
    try:
        # Formato novo: base64
        stored_hash = base64.b64decode(stored_hash_str.encode('utf-8'))
        hash_format = "base64"
        print(f"✅ Hash decodificado como base64")
    except Exception as e1:
        try:
            # Formato antigo: tentar como bytes diretos
            if isinstance(stored_hash_str, bytes):
                stored_hash = stored_hash_str
                hash_format = "bytes diretos"
                print(f"✅ Hash processado como bytes diretos")
            else:
                # Formato muito antigo: tentar como string UTF-8
                if stored_hash_str.startswith('$2'):
                    stored_hash = stored_hash_str.encode('utf-8')
                    hash_format = "string bcrypt"
                    print(f"✅ Hash processado como string bcrypt")
                else:
                    print(f"❌ Hash em formato desconhecido: {stored_hash_str[:50]}...")
                    conn.close()
                    return False
        except Exception as e2:
            print(f"❌ Erro ao processar hash: {e2}")
            conn.close()
            return False
    
    # Testa a senha
    try:
        if stored_hash:
            is_correct = bcrypt.checkpw(password_to_test.encode('utf-8'), stored_hash)
            
            if is_correct:
                print(f"✅ SENHA CORRETA! A senha fornecida está correta.")
                conn.close()
                return True
            else:
                print(f"❌ SENHA INCORRETA! A senha fornecida não corresponde ao hash armazenado.")
                print(f"\n💡 Possíveis soluções:")
                print(f"   1. Verifique se digitou a senha corretamente")
                print(f"   2. Use 'Esqueci minha senha' para redefinir")
                print(f"   3. Execute: python backend/reset_password.py {email}")
                conn.close()
                return False
        else:
            print(f"❌ Não foi possível processar o hash.")
            conn.close()
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar senha: {e}")
        conn.close()
        return False

def reset_user_password(email, new_password):
    """Redefine a senha de um usuário"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    email_lower = email.lower().strip()
    
    # Verifica se usuário existe
    cursor.execute('SELECT id FROM users WHERE email = ?', (email_lower,))
    user = cursor.fetchone()
    
    if not user:
        print(f"❌ Usuário não encontrado!")
        conn.close()
        return False
    
    # Gera novo hash
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(new_password.encode('utf-8'), salt)
    password_hash_b64 = base64.b64encode(password_hash).decode('utf-8')
    
    # Atualiza no banco
    cursor.execute('''
        UPDATE users 
        SET password_hash = ?, email_verified = 1
        WHERE email = ?
    ''', (password_hash_b64, email_lower))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Senha redefinida com sucesso!")
    print(f"   Email: {email_lower}")
    print(f"   Novo hash (primeiros 50 chars): {password_hash_b64[:50]}...")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python backend/check_login.py <email> [senha] [--reset]")
        print("\nExemplos:")
        print("  python backend/check_login.py bruno.santos.cartolano@gmail.com")
        print("  python backend/check_login.py bruno.santos.cartolano@gmail.com minha_senha")
        print("  python backend/check_login.py bruno.santos.cartolano@gmail.com nova_senha --reset")
        sys.exit(1)
    
    email = sys.argv[1]
    
    if '--reset' in sys.argv:
        if len(sys.argv) < 3:
            print("❌ Erro: Forneça a nova senha ao usar --reset")
            sys.exit(1)
        new_password = sys.argv[2]
        reset_user_password(email, new_password)
    else:
        if len(sys.argv) >= 3:
            password = sys.argv[2]
            check_user_password(email, password)
        else:
            print(f"🔍 Verificando usuário: {email}")
            print(f"   (Para testar senha, forneça como segundo argumento)")
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, email, email_verified FROM users WHERE email = ?', (email.lower().strip(),))
            user = cursor.fetchone()
            conn.close()
            if user:
                print(f"✅ Usuário encontrado: {user[1]} (ID: {user[0]})")
                print(f"   Email verificado: {'Sim' if user[3] == 1 else 'Não'}")
            else:
                print(f"❌ Usuário não encontrado")

