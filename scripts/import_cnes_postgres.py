#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para importar dados do CNES para PostgreSQL com PostGIS
Rode isso uma vez só após criar a tabela no Azure Database for PostgreSQL

Uso:
    python scripts/import_cnes_postgres.py

Variáveis de ambiente necessárias:
    POSTGRES_HOST - Host do servidor PostgreSQL (ex: seu-server.postgres.database.azure.com)
    POSTGRES_DB - Nome do banco de dados (ex: sophia)
    POSTGRES_USER - Usuário do banco
    POSTGRES_PASSWORD - Senha do banco
    CNES_CSV_PATH - Caminho para o arquivo CSV do CNES (ex: BASE_DE_DADOS_CNES_202512/tbEstabelecimento202410.csv)
"""

import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging

# Configura logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()

# Configuração do banco de dados
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'sophia')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
CNES_CSV_PATH = os.getenv('CNES_CSV_PATH', 'BASE_DE_DADOS_CNES_202512/tbEstabelecimento202410.csv')

# Validação de variáveis obrigatórias
if not all([POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD]):
    logger.error("❌ Variáveis de ambiente obrigatórias não configuradas:")
    logger.error("   POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD")
    sys.exit(1)

if not os.path.exists(CNES_CSV_PATH):
    logger.error(f"❌ Arquivo CSV não encontrado: {CNES_CSV_PATH}")
    sys.exit(1)

# String de conexão PostgreSQL
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}?sslmode=require"

logger.info("🔌 Conectando ao PostgreSQL...")
try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    # Testa conexão
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        logger.info(f"✅ Conectado ao PostgreSQL: {result.fetchone()[0][:50]}...")
except Exception as e:
    logger.error(f"❌ Erro ao conectar ao PostgreSQL: {e}")
    sys.exit(1)

logger.info(f"📂 Lendo arquivo CSV: {CNES_CSV_PATH}")
try:
    # Lê CSV com encoding latin1 e separador ;
    df = pd.read_csv(
        CNES_CSV_PATH,
        encoding='latin1',
        sep=';',
        low_memory=False,
        dtype=str  # Lê tudo como string primeiro para evitar problemas de tipo
    )
    logger.info(f"✅ CSV lido: {len(df)} linhas encontradas")
except Exception as e:
    logger.error(f"❌ Erro ao ler CSV: {e}")
    sys.exit(1)

# Códigos de unidades que têm maternidade (ajuste conforme necessário)
# Baseado nos códigos TP_UNIDADE do CNES
codigos_maternidade = ['05', '07', '36', '39', '68', '73', '74', '75', '76']

logger.info(f"🔍 Filtrando estabelecimentos com maternidade (códigos: {codigos_maternidade})...")
if 'TP_UNIDADE' in df.columns:
    df_filtered = df[df['TP_UNIDADE'].isin(codigos_maternidade)].copy()
    logger.info(f"✅ {len(df_filtered)} estabelecimentos com maternidade encontrados")
else:
    logger.warning("⚠️ Coluna TP_UNIDADE não encontrada, importando todos os estabelecimentos")
    df_filtered = df.copy()

# Converte coordenadas (CNES usa formato: graus * 1000000)
logger.info("📍 Convertendo coordenadas...")
try:
    # Remove linhas sem coordenadas válidas
    df_filtered = df_filtered[
        df_filtered['NU_LATITUDE'].notna() & 
        df_filtered['NU_LONGITUDE'].notna()
    ].copy()
    
    # Converte para float e divide por 1000000
    df_filtered['latitude'] = pd.to_numeric(df_filtered['NU_LATITUDE'], errors='coerce') / 1000000
    df_filtered['longitude'] = pd.to_numeric(df_filtered['NU_LONGITUDE'], errors='coerce') / 1000000
    
    # Remove linhas com coordenadas inválidas
    df_filtered = df_filtered[
        df_filtered['latitude'].notna() & 
        df_filtered['longitude'].notna() &
        (df_filtered['latitude'] >= -90) & (df_filtered['latitude'] <= 90) &
        (df_filtered['longitude'] >= -180) & (df_filtered['longitude'] <= 180)
    ].copy()
    
    logger.info(f"✅ {len(df_filtered)} estabelecimentos com coordenadas válidas")
except Exception as e:
    logger.error(f"❌ Erro ao converter coordenadas: {e}")
    sys.exit(1)

# Seleciona e renomeia colunas
logger.info("📋 Preparando dados para inserção...")
colunas_mapeamento = {
    'CO_CNES': 'cnes',
    'NO_FANTASIA': 'nome_fantasia',
    'latitude': 'latitude',
    'longitude': 'longitude',
    'NO_LOGRADOURO': 'logradouro',
    'NO_BAIRRO': 'bairro',
    'CO_MUNICIPIO_GESTOR': 'municipio',
    'SG_UF': 'uf',
    'NU_TELEFONE': 'telefone'
}

# Cria DataFrame final apenas com colunas necessárias
df_final = pd.DataFrame()
for col_origem, col_destino in colunas_mapeamento.items():
    if col_origem in df_filtered.columns:
        df_final[col_destino] = df_filtered[col_origem]
    else:
        logger.warning(f"⚠️ Coluna {col_origem} não encontrada no CSV")

# Adiciona colunas booleanas
df_final['tem_maternidade'] = True
df_final['aceita_sus'] = True  # Ajuste conforme necessário baseado nos dados
df_final['convenio'] = False
df_final['particular'] = False

# Limita tamanho dos campos de texto
df_final['nome_fantasia'] = df_final['nome_fantasia'].astype(str).str[:255]
df_final['logradouro'] = df_final['logradouro'].astype(str).str[:255]
df_final['bairro'] = df_final['bairro'].astype(str).str[:100]
df_final['municipio'] = df_final['municipio'].astype(str).str[:100]
df_final['telefone'] = df_final['telefone'].astype(str).str[:20]
df_final['cnes'] = df_final['cnes'].astype(str).str[:20]

# Remove duplicatas por CNES
df_final = df_final.drop_duplicates(subset=['cnes'], keep='first')
logger.info(f"✅ {len(df_final)} estabelecimentos únicos preparados para inserção")

# Insere no banco usando método eficiente
logger.info("💾 Inserindo dados no PostgreSQL...")
try:
    # Usa método 'multi' para inserção em lote eficiente
    df_final.to_sql(
        'estabelecimentos_saude',
        engine,
        if_exists='append',  # Adiciona aos dados existentes
        index=False,
        method='multi',
        chunksize=1000  # Insere em lotes de 1000
    )
    logger.info("✅ Dados inseridos com sucesso!")
except Exception as e:
    logger.error(f"❌ Erro ao inserir dados: {e}")
    sys.exit(1)

# Cria geometria PostGIS para todos os registros
logger.info("🗺️ Criando geometrias PostGIS...")
try:
    with engine.connect() as conn:
        # Atualiza geometria para todos os registros que não têm
        conn.execute(text("""
            UPDATE estabelecimentos_saude
            SET geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)
            WHERE geom IS NULL AND latitude IS NOT NULL AND longitude IS NOT NULL
        """))
        conn.commit()
        logger.info("✅ Geometrias PostGIS criadas!")
except Exception as e:
    logger.error(f"❌ Erro ao criar geometrias: {e}")
    sys.exit(1)

# Verifica resultado final
logger.info("🔍 Verificando resultado final...")
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM estabelecimentos_saude"))
        total = result.fetchone()[0]
        result = conn.execute(text("SELECT COUNT(*) FROM estabelecimentos_saude WHERE geom IS NOT NULL"))
        com_geom = result.fetchone()[0]
        logger.info(f"✅ Importação concluída!")
        logger.info(f"   Total de estabelecimentos: {total}")
        logger.info(f"   Com geometria PostGIS: {com_geom}")
except Exception as e:
    logger.error(f"❌ Erro ao verificar resultado: {e}")

logger.info("🎉 Processo de importação finalizado com sucesso!")
