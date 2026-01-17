#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar se WAL mode está ativo no banco de dados
"""
import sqlite3
import os
import sys

# Adiciona caminho do backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'backend', 'users.db')

def check_wal_mode():
    """Verifica se WAL mode está ativo"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verifica journal mode
        cursor.execute('PRAGMA journal_mode;')
        journal_mode = cursor.fetchone()[0]
        
        # Verifica outras configurações
        cursor.execute('PRAGMA synchronous;')
        synchronous = cursor.fetchone()[0]
        
        cursor.execute('PRAGMA cache_size;')
        cache_size = cursor.fetchone()[0]
        
        print("=" * 60)
        print("VERIFICAÇÃO DE CONFIGURAÇÃO DO BANCO DE DADOS")
        print("=" * 60)
        print(f"📁 Banco: {DB_PATH}")
        print(f"📊 Journal Mode: {journal_mode}")
        print(f"⚡ Synchronous: {synchronous}")
        print(f"💾 Cache Size: {cache_size} (páginas)")
        print("=" * 60)
        
        if journal_mode.upper() == 'WAL':
            print("✅ WAL mode está ATIVO - Pronto para múltiplas conexões simultâneas")
        else:
            print(f"⚠️ WAL mode NÃO está ativo (atual: {journal_mode})")
            print("   Recomendação: Ativar WAL mode para melhor performance")
        
        if synchronous == 1:  # NORMAL
            print("✅ Synchronous NORMAL - Balance entre segurança e performance")
        elif synchronous == 2:  # FULL
            print("⚠️ Synchronous FULL - Mais seguro, mas pode ser mais lento")
        else:
            print(f"ℹ️ Synchronous: {synchronous}")
        
        conn.close()
        return journal_mode.upper() == 'WAL'
        
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
        return False

if __name__ == '__main__':
    check_wal_mode()
