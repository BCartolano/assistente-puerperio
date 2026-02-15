#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script one-off: remove todos os usuários do banco exceto o criador (bruno.santos.cartolano@gmail.com).
Execute uma vez a partir da raiz do projeto: python backend/scripts/delete_users_keep_creator.py
"""
import os
import sqlite3

# Mesmo DB que o app usa (backend/users.db)
_script_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.dirname(_script_dir)
DB_PATH = os.path.join(_backend_dir, "users.db")

CREATOR_EMAIL = "bruno.santos.cartolano@gmail.com"

def _normalize_email(s):
    if s is None:
        return ""
    return str(s).strip().lower()

def main():
    email_keep = _normalize_email(CREATOR_EMAIL)
    if not email_keep:
        print("Erro: email do criador inválido.")
        return 1

    if not os.path.exists(DB_PATH):
        print(f"Banco não encontrado: {DB_PATH}")
        return 1

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, email FROM users")
    all_users = cursor.fetchall()
    to_delete = [(row[0], row[1]) for row in all_users if _normalize_email(row[1]) != email_keep]
    to_keep = [(row[0], row[1]) for row in all_users if _normalize_email(row[1]) == email_keep]

    if not to_keep:
        print(f"Nenhum usuário com email '{CREATOR_EMAIL}' encontrado. Nenhuma exclusão feita para não remover todos.")
        conn.close()
        return 0

    if not to_delete:
        print("Nenhum outro usuário além do criador. Nada a excluir.")
        conn.close()
        return 0

    print(f"Mantendo: {to_keep[0][1]} (id={to_keep[0][0]})")
    print(f"Excluindo {len(to_delete)} usuário(s):")
    for uid, em in to_delete:
        print(f"  - id={uid}, email={em}")

    cursor.execute("DELETE FROM users WHERE email != ?", (email_keep,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()

    print(f"Concluído: {deleted} cadastro(s) excluído(s). Restou apenas {CREATOR_EMAIL}.")
    return 0

if __name__ == "__main__":
    exit(main())
