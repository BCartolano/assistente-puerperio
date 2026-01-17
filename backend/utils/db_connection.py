# -*- coding: utf-8 -*-
"""
Helper para conexões SQLite otimizadas
Aplica WAL mode e configurações de performance automaticamente
"""
import sqlite3
import os

def get_db_connection(db_path, timeout=20.0):
    """
    Cria conexão SQLite otimizada para múltiplas conexões simultâneas
    
    Args:
        db_path: str - Caminho do banco de dados
        timeout: float - Timeout de conexão (default: 20.0 segundos)
    
    Returns:
        sqlite3.Connection - Conexão configurada com WAL mode
    """
    conn = sqlite3.connect(db_path, timeout=timeout)
    
    # Ativa WAL mode para melhor performance com múltiplas conexões simultâneas
    # Importante para Beta Fechado (10-20 usuárias simultâneas)
    conn.execute('PRAGMA journal_mode=WAL;')
    conn.execute('PRAGMA synchronous=NORMAL;')  # Balance entre segurança e performance
    conn.execute('PRAGMA cache_size=-64000;')  # 64MB cache (melhora performance)
    
    return conn
