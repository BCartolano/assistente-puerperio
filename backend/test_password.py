#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar se uma senha corresponde ao hash no banco
Útil para debug de problemas de login
"""

import sqlite3
import bcrypt
import base64
import sys
import os

# Caminho do banco
DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")

def test_password(email, password_to_test):
    """Testa se a senha está correta"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    email_lower = email.lower().strip()
    
    cursor.execute('''
        SELECT id, name, email, password_hash, email_verified 
        FROM users 
        WHERE email = ?
    ''', (email_lower,))
    
    user_data = cursor.fetchone()
    conn.close()
    
    if not user_data:
        print(f"❌ Usuário não encontrado: {email_lower}")
        return False
    
    user_id, user_name, user_email, stored_hash_str, email_verified = user_data
    
    print(f"\n{'='*70}")
    print(f"🔍 TESTE DE SENHA")
    print(f"{'='*70}")
    print(f"Email: {email_lower}")
    print(f"ID: {user_id}")
    print(f"Nome: {user_name}")
    print(f"Email verificado: {'Sim ✅' if email_verified == 1 else 'Não ❌'}")
    print(f"{'='*70}\n")
    
    # Tenta diferentes formatos
    stored_hash = None
    hash_format = "desconhecido"
    success = False
    
    # 1. Tentar base64 (formato novo)
    try:
        stored_hash = base64.b64decode(stored_hash_str.encode('utf-8'))
        hash_format = "base64"
        print(f"✅ Hash decodificado como BASE64")
        success = True
    except Exception as e:
        print(f"❌ Erro ao decodificar base64: {e}")
    
    # 2. Se base64 falhou, tentar outros formatos
    if not success:
        try:
            if isinstance(stored_hash_str, bytes):
                stored_hash = stored_hash_str
                hash_format = "bytes diretos"
                print(f"✅ Hash processado como BYTES DIRETOS")
                success = True
            elif stored_hash_str.startswith('$2'):
                stored_hash = stored_hash_str.encode('utf-8')
                hash_format = "string bcrypt"
                print(f"✅ Hash processado como STRING BCRYPT")
                success = True
            else:
                print(f"❌ Formato de hash desconhecido!")
                print(f"   Primeiros 100 chars: {stored_hash_str[:100]}...")
                return False
        except Exception as e:
            print(f"❌ Erro ao processar hash alternativo: {e}")
            return False
    
    if not stored_hash:
        print(f"❌ Não foi possível processar o hash!")
        return False
    
    # Testa a senha
    print(f"\n{'='*70}")
    print(f"🔐 TESTANDO SENHA...")
    print(f"{'='*70}")
    print(f"Hash length: {len(stored_hash)} bytes")
    print(f"Formato: {hash_format}")
    print(f"Senha fornecida: {'*' * len(password_to_test)}")
    
    try:
        is_correct = bcrypt.checkpw(password_to_test.encode('utf-8'), stored_hash)
        
        print(f"\n{'='*70}")
        if is_correct:
            print(f"✅✅✅ SENHA CORRETA! ✅✅✅")
            print(f"{'='*70}")
            return True
        else:
            print(f"❌❌❌ SENHA INCORRETA! ❌❌❌")
            print(f"{'='*70}")
            print(f"\n💡 SOLUÇÕES POSSÍVEIS:")
            print(f"   1. Verifique se digitou a senha corretamente")
            print(f"   2. A senha pode ter sido alterada ou corrompida")
            print(f"   3. Use 'Esqueci minha senha' para redefinir")
            print(f"   4. Execute: python backend/reset_user_password.py {email}")
            return False
    except Exception as e:
        print(f"❌ ERRO ao verificar senha: {e}")
        print(f"{'='*70}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python backend/test_password.py <email> <senha>")
        print("\nExemplo:")
        print("  python backend/test_password.py bruno.santos.cartolano@gmail.com minha_senha")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    test_password(email, password)

