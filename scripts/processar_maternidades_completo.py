#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Completo de Processamento de Maternidades
Integra: Filtro CNES + Busca Espacial (BallTree) + Roteamento (OSRM)
100% Gratuito - Sistema de Emergência Obstétrica

Uso:
    python scripts/processar_maternidades_completo.py caminho/para/tbEstabelecimento.csv

Saída:
    - maternidades_processadas.csv (dados limpos e filtrados)
    - maternidades_index.pkl (índice BallTree para buscas rápidas)
"""

import pandas as pd
import numpy as np
import pickle
import os
import sys
import logging
from pathlib import Path
from sklearn.neighbors import BallTree

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Diretórios
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'backend', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

CSV_OUTPUT = os.path.join(DATA_DIR, 'maternidades_processadas.csv')
INDEX_OUTPUT = os.path.join(DATA_DIR, 'maternidades_index.pkl')


def limpar_telefone(tel):
    """Limpa e padroniza número de telefone"""
    if pd.isna(tel) or tel == '':
        return ''
    tel_str = str(tel).strip()
    # Remove caracteres não numéricos
    tel_limpo = ''.join(filter(str.isdigit, tel_str))
    # Validação básica (deve ter pelo menos 10 dígitos)
    if len(tel_limpo) >= 10:
        return tel_limpo
    return ''


def classificar_natureza_juridica(natureza):
    """Classifica natureza jurídica em Público ou Privado"""
    if pd.isna(natureza):
        return 'Indefinido'
    natureza_str = str(natureza).strip()
    # Códigos que começam com 1 são públicos
    if natureza_str.startswith('1'):
        return 'Público (SUS)'
    # Códigos 2 e 3 são privados/convênio
    elif natureza_str.startswith(('2', '3')):
        return 'Privado/Convênio'
    return 'Indefinido'


def preparar_base_dados(caminho_csv):
    """
    Carrega e filtra dados do CNES para maternidades
    
    Filtros aplicados:
    - Possui leitos de maternidade/obstétrico
    - Tem telefone válido
    - Tem coordenadas válidas
    """
    logger.info(f"📂 Carregando CSV: {caminho_csv}")
    
    try:
        # Lê CSV com encoding apropriado
        df = pd.read_csv(caminho_csv, encoding='latin1', sep=';', low_memory=False)
        logger.info(f"✅ Carregados {len(df)} registros do CNES")
    except Exception as e:
        logger.error(f"❌ Erro ao carregar CSV: {e}")
        sys.exit(1)
    
    # 1. Filtro: Maternidade/Obstétrico
    # Verifica colunas relacionadas a leitos de maternidade
    colunas_leito = ['DESC_LEITO', 'DS_LEITO', 'NO_LEITO']
    coluna_leito = None
    
    for col in colunas_leito:
        if col in df.columns:
            coluna_leito = col
            break
    
    if coluna_leito:
        mask_maternidade = df[coluna_leito].str.contains(
            'MATERNIDADE|OBSTETRICO|OBSTÉTRICO', 
            case=False, 
            na=False
        )
        df_maternidade = df[mask_maternidade].copy()
        logger.info(f"✅ {len(df_maternidade)} estabelecimentos com leitos de maternidade")
    else:
        # Fallback: usa código de tipo de unidade
        codigos_maternidade = ['05', '07', '36', '39', '68', '73', '74', '75', '76']
        if 'TP_UNIDADE' in df.columns:
            df_maternidade = df[df['TP_UNIDADE'].isin(codigos_maternidade)].copy()
            logger.info(f"✅ {len(df_maternidade)} estabelecimentos por código de tipo")
        else:
            logger.warning("⚠️ Não encontrou coluna de leitos, usando todos os registros")
            df_maternidade = df.copy()
    
    # 2. Limpa telefones
    colunas_telefone = ['NU_TELEFONE', 'TELEFONE', 'NO_TELEFONE']
    coluna_telefone = None
    
    for col in colunas_telefone:
        if col in df_maternidade.columns:
            coluna_telefone = col
            break
    
    if coluna_telefone:
        df_maternidade['telefone_limpo'] = df_maternidade[coluna_telefone].apply(limpar_telefone)
    else:
        df_maternidade['telefone_limpo'] = ''
    
    # 3. Filtro CRÍTICO: Remove hospitais sem telefone (risco crítico em emergências)
    antes_filtro = len(df_maternidade)
    df_maternidade = df_maternidade[df_maternidade['telefone_limpo'] != ''].copy()
    removidos = antes_filtro - len(df_maternidade)
    if removidos > 0:
        logger.warning(f"⚠️ {removidos} estabelecimentos removidos por não terem telefone")
    logger.info(f"✅ {len(df_maternidade)} estabelecimentos com telefone válido")
    
    # 4. Processa coordenadas
    colunas_lat = ['NU_LATITUDE', 'LATITUDE', 'CO_LATITUDE']
    colunas_lon = ['NU_LONGITUDE', 'LONGITUDE', 'CO_LONGITUDE']
    
    coluna_lat = None
    coluna_lon = None
    
    for col in colunas_lat:
        if col in df_maternidade.columns:
            coluna_lat = col
            break
    
    for col in colunas_lon:
        if col in df_maternidade.columns:
            coluna_lon = col
            break
    
    if coluna_lat and coluna_lon:
        # Converte coordenadas (CNES usa formato: graus * 1000000)
        df_maternidade['latitude'] = pd.to_numeric(df_maternidade[coluna_lat], errors='coerce') / 1000000.0
        df_maternidade['longitude'] = pd.to_numeric(df_maternidade[coluna_lon], errors='coerce') / 1000000.0
        
        # Remove coordenadas inválidas
        df_maternidade = df_maternidade.dropna(subset=['latitude', 'longitude'])
        logger.info(f"✅ {len(df_maternidade)} estabelecimentos com coordenadas válidas")
    else:
        logger.error("❌ Não encontrou colunas de coordenadas")
        sys.exit(1)
    
    # 5. Classifica natureza jurídica
    colunas_natureza = ['NATUREZA_JURIDICA', 'CO_NATUREZA_JUR', 'NO_NATUREZA_JUR']
    coluna_natureza = None
    
    for col in colunas_natureza:
        if col in df_maternidade.columns:
            coluna_natureza = col
            break
    
    if coluna_natureza:
        df_maternidade['tipo'] = df_maternidade[coluna_natureza].apply(classificar_natureza_juridica)
    else:
        df_maternidade['tipo'] = 'Indefinido'
    
    # 6. Seleciona e renomeia colunas finais
    colunas_finais = {
        'CO_CNES': 'cnes',
        'NO_FANTASIA': 'nome_fantasia',
        'NO_LOGRADOURO': 'logradouro',
        'NO_BAIRRO': 'bairro',
        'NO_MUNICIPIO': 'municipio',
        'SG_UF': 'uf'
    }
    
    df_final = pd.DataFrame()
    for col_original, col_novo in colunas_finais.items():
        if col_original in df_maternidade.columns:
            df_final[col_novo] = df_maternidade[col_original]
        else:
            df_final[col_novo] = ''
    
    # Adiciona colunas processadas
    df_final['telefone'] = df_maternidade.get(coluna_telefone, '')
    df_final['telefone_limpo'] = df_maternidade['telefone_limpo']
    df_final['latitude'] = df_maternidade['latitude']
    df_final['longitude'] = df_maternidade['longitude']
    df_final['tipo'] = df_maternidade['tipo']
    
    # Remove duplicatas por CNES
    df_final = df_final.drop_duplicates(subset=['cnes'], keep='first')
    logger.info(f"✅ {len(df_final)} estabelecimentos únicos processados")
    
    # 7. Cria índice BallTree para buscas rápidas
    logger.info("🌳 Criando índice espacial BallTree...")
    coords_validas = df_final[['latitude', 'longitude']].dropna()
    
    if len(coords_validas) > 0:
        # Converte para radianos (exigência da BallTree para Haversine)
        coords_rad = np.deg2rad(coords_validas.values)
        tree = BallTree(coords_rad, metric='haversine')
        
        # Mapeia índices do BallTree para índices do DataFrame
        indices_map = coords_validas.index.tolist()
        
        # Salva dados e índice
        df_final.to_csv(CSV_OUTPUT, index=False, encoding='utf-8')
        logger.info(f"✅ Dados salvos em: {CSV_OUTPUT}")
        
        with open(INDEX_OUTPUT, 'wb') as f:
            pickle.dump({
                'tree': tree,
                'indices_map': indices_map
            }, f)
        logger.info(f"✅ Índice BallTree salvo em: {INDEX_OUTPUT}")
        
        logger.info("🎉 Processamento concluído com sucesso!")
        return df_final
    else:
        logger.error("❌ Nenhuma coordenada válida encontrada")
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python processar_maternidades_completo.py <caminho_para_csv>")
        sys.exit(1)
    
    caminho_csv = sys.argv[1]
    
    if not os.path.exists(caminho_csv):
        logger.error(f"❌ Arquivo não encontrado: {caminho_csv}")
        sys.exit(1)
    
    preparar_base_dados(caminho_csv)
