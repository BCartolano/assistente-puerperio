# -*- coding: utf-8 -*-
"""
Serviço de conexão com PostgreSQL para estabelecimentos de saúde
Usa PostGIS para consultas espaciais de proximidade
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool
from flask import current_app
import logging

logger = logging.getLogger(__name__)

# Variáveis de ambiente para conexão PostgreSQL
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'sophia')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

# String de conexão
DATABASE_URL = None
if all([POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD]):
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}?sslmode=require"

# Engine global (criado sob demanda)
_postgres_engine = None


def get_postgres_engine():
    """
    Retorna engine SQLAlchemy para PostgreSQL
    Cria se não existir
    """
    global _postgres_engine
    
    if _postgres_engine is None:
        if not DATABASE_URL:
            logger.warning("⚠️ PostgreSQL não configurado. Variáveis POSTGRES_* não encontradas.")
            return None
        
        try:
            _postgres_engine = create_engine(
                DATABASE_URL,
                pool_pre_ping=True,
                poolclass=NullPool,  # Não mantém pool para evitar conexões órfãs
                connect_args={
                    "connect_timeout": 10,
                    "application_name": "sophia-backend"
                }
            )
            logger.info("✅ Engine PostgreSQL criado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao criar engine PostgreSQL: {e}")
            return None
    
    return _postgres_engine


def is_postgres_available():
    """Verifica se PostgreSQL está configurado e disponível"""
    engine = get_postgres_engine()
    if not engine:
        return False
    
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
