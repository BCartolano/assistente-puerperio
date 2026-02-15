#!/usr/bin/env python3
"""
Script para criar ou listar usuários no banco de dados.
Uso:
  python backend/criar_usuario.py                    # Lista todos os usuários
  python backend/criar_usuario.py email@exemplo.com  # Cria usuário (senha pedida no terminal)
  python backend/criar_usuario.py email@exemplo.com NomeDoUsuario  # Cria com nome
"""
import base64
import getpass
import os
import sqlite3
import sys

try:
    import bcrypt
except ImportError:
    print("[ERRO] Modulo bcrypt nao instalado. Execute: pip install bcrypt")
    sys.exit(1)

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")


def init_db_if_needed():
    """Garante que a tabela users existe."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            baby_name TEXT,
            email_verified INTEGER DEFAULT 1,
            email_verification_token TEXT,
            reset_password_token TEXT,
            reset_password_expires TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def list_users():
    """Lista todos os usuários cadastrados."""
    if not os.path.exists(DB_PATH):
        print("[ERRO] Banco de dados nao encontrado em:", os.path.abspath(DB_PATH))
        print("   Inicie o servidor uma vez para criar o banco.")
        return
    init_db_if_needed()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, email_verified FROM users ORDER BY id')
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        print("[!] Nenhum usuario cadastrado.")
        print("    Use: python backend/criar_usuario.py seu@email.com")
        return
    print("=" * 60)
    print("USUARIOS CADASTRADOS")
    print("=" * 60)
    for row in rows:
        uid, name, email, verified = row
        status = "[OK] verificado" if verified else "[ ] nao verificado"
        print(f"  ID {uid}: {name} <{email}> {status}")
    print("=" * 60)


def create_user(email: str, name: str = None, password: str = None):
    """Cria um usuário no banco."""
    init_db_if_needed()
    email = email.strip().lower()
    if not name:
        name = email.split("@")[0].replace(".", " ").title()
    if not password:
        password = getpass.getpass("Digite a senha (mín. 6 caracteres): ")
    if len(password) < 6:
        print("[ERRO] Senha deve ter no minimo 6 caracteres.")
        return False
    password_hash_bytes = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    password_hash = base64.b64encode(password_hash_bytes).decode("utf-8")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO users (name, email, password_hash, baby_name, email_verified)
            VALUES (?, ?, ?, ?, 1)
            """,
            (name, email, password_hash, None),
        )
        conn.commit()
        uid = cursor.lastrowid
        conn.close()
        print("=" * 60)
        print(f"✅ Usuário criado com sucesso!")
        print(f"   Nome:  {name}")
        print(f"   Email: {email}")
        print(f"   ID:    {uid}")
        print("   (Conta já verificada - pode fazer login imediatamente)")
        print("=" * 60)
        return True
    except sqlite3.IntegrityError as e:
        conn.close()
        if "UNIQUE constraint failed" in str(e):
            print("[ERRO] Este email ja esta cadastrado.")
            print("   Use 'Esqueci minha senha' no site ou verifique com: python backend/check_user.py", email)
        else:
            print("[ERRO] Erro ao criar usuario:", e)
        return False


def reset_password(email: str):
    """Reseta a senha de um usuario existente."""
    init_db_if_needed()
    email = email.strip().lower()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        print("[ERRO] Usuario nao encontrado:", email)
        return False
    uid, name = row
    conn.close()
    password = getpass.getpass("Nova senha (min. 6 caracteres): ")
    if len(password) < 6:
        print("[ERRO] Senha deve ter no minimo 6 caracteres.")
        return False
    password_hash_bytes = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    password_hash = base64.b64encode(password_hash_bytes).decode("utf-8")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password_hash = ? WHERE email = ?", (password_hash, email))
    conn.commit()
    conn.close()
    print("=" * 60)
    print("OK - Senha alterada com sucesso!")
    print("    Usuario:", name, "<" + email + ">")
    print("    Faça login com a nova senha.")
    print("=" * 60)
    return True


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        list_users()
    elif args[0] in ("--reset", "-r") and len(args) >= 2:
        reset_password(args[1])
    elif args[0] in ("--reset", "-r") and len(args) == 1:
        print("Uso: python backend/criar_usuario.py --reset seu@email.com")
    else:
        email = args[0]
        name = args[1] if len(args) > 1 else None
        init_db_if_needed()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE email = ?", (email.lower(),))
        exists = cursor.fetchone()
        conn.close()
        if exists:
            print("[!] Este email ja esta cadastrado.")
            print("    Para resetar a senha: python backend/criar_usuario.py --reset", email)
            sys.exit(1)
        create_user(email, name)
