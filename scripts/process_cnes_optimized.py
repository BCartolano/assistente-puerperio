#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script otimizado para processar dados do CNES e filtrar maternidades
Usa técnicas de Big Data para lidar com 600k+ registros eficientemente

Uso:
    python scripts/process_cnes_optimized.py caminho/para/tbEstabelecimento.csv

Saída:
    - maternidades_processadas.csv (dados limpos e filtrados)
    - maternidades_index.pkl (índice BallTree para buscas rápidas)
"""

import pandas as pd
import numpy as np
import re
import sys
import os
import pickle
from pathlib import Path
from sklearn.neighbors import BallTree
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def limpar_telefone(tel):
    """Limpa e padroniza número de telefone"""
    if pd.isna(tel):
        return ""
    # Remove tudo que não é dígito
    limpo = re.sub(r'\D', '', str(tel))
    # Padroniza para formato brasileiro
    if len(limpo) == 10:
        return f"({limpo[:2]}) {limpo[2:6]}-{limpo[6:]}"
    elif len(limpo) == 11:
        return f"({limpo[:2]}) {limpo[2:7]}-{limpo[7:]}"
    return limpo


def classificar_natureza(cod):
    """Classifica natureza jurídica baseada em códigos CONCLA/IBGE"""
    if pd.isna(cod):
        return 'Outros'
    cod_str = str(cod).strip()
    if cod_str.startswith('1'):  # Administração Pública
        return 'Público'
    elif cod_str.startswith(('2', '3')):  # Empresas e Entidades sem fins lucrativos
        return 'Privado'
    return 'Outros'


def filtrar_maternidades(df):
    """Filtra apenas estabelecimentos com maternidade"""
    logger.info(f"📊 Total de registros no CSV: {len(df)}")
    
    # Códigos de unidades que têm maternidade (TP_UNIDADE do CNES)
    codigos_maternidade = ['05', '07', '36', '39', '68', '73', '74', '75', '76']
    
    # Filtra por código de unidade
    if 'TP_UNIDADE' in df.columns:
        df_filtrado = df[df['TP_UNIDADE'].isin(codigos_maternidade)].copy()
        logger.info(f"✅ {len(df_filtrado)} estabelecimentos com código de maternidade")
    else:
        # Fallback: busca por descrição de leito ou nome
        colunas_busca = ['DESC_LEITO', 'NO_FANTASIA', 'NO_RAZAO_SOCIAL']
        mask = pd.Series([False] * len(df))
        for col in colunas_busca:
            if col in df.columns:
                mask |= df[col].str.contains('MATERNIDADE|OBSTETRICO|OBSTETRICA', case=False, na=False)
        df_filtrado = df[mask].copy()
        logger.info(f"✅ {len(df_filtrado)} estabelecimentos com maternidade (busca por texto)")
    
    return df_filtrado


def processar_dados(caminho_csv, output_dir='data'):
    """Processa arquivo CSV do CNES e gera dados otimizados"""
    
    logger.info(f"📂 Lendo arquivo: {caminho_csv}")
    
    # Colunas essenciais para o sistema de emergência
    colunas_interesse = [
        'CO_CNES', 'NO_FANTASIA', 'NO_LOGRADOURO', 'NU_ENDERECO', 
        'NO_BAIRRO', 'CO_MUNICIPIO_GESTOR', 'SG_UF', 
        'NU_TELEFONE', 'CO_NATUREZA_JUR', 'TP_UNIDADE',
        'NU_LATITUDE', 'NU_LONGITUDE'
    ]
    
    try:
        # Lê apenas colunas necessárias para economizar memória
        df = pd.read_csv(
            caminho_csv,
            encoding='latin1',
            sep=';',
            usecols=colunas_interesse,
            low_memory=False,
            dtype=str  # Lê tudo como string primeiro
        )
        logger.info(f"✅ CSV carregado: {len(df)} linhas")
    except Exception as e:
        logger.error(f"❌ Erro ao ler CSV: {e}")
        # Tenta ler todas as colunas se algumas não existirem
        df = pd.read_csv(caminho_csv, encoding='latin1', sep=';', low_memory=False)
        logger.info(f"⚠️ Carregado com todas as colunas: {len(df)} linhas")
    
    # 1. Filtrar apenas maternidades
    df_maternidade = filtrar_maternidades(df)
    
    if len(df_maternidade) == 0:
        logger.error("❌ Nenhuma maternidade encontrada!")
        return None
    
    # 2. Converter coordenadas (CNES usa formato: graus * 1000000)
    logger.info("📍 Convertendo coordenadas...")
    df_maternidade['latitude'] = pd.to_numeric(
        df_maternidade.get('NU_LATITUDE', 0), errors='coerce'
    ) / 1000000
    df_maternidade['longitude'] = pd.to_numeric(
        df_maternidade.get('NU_LONGITUDE', 0), errors='coerce'
    ) / 1000000
    
    # Remove linhas sem coordenadas válidas
    df_maternidade = df_maternidade[
        df_maternidade['latitude'].notna() & 
        df_maternidade['longitude'].notna() &
        (df_maternidade['latitude'] >= -90) & (df_maternidade['latitude'] <= 90) &
        (df_maternidade['longitude'] >= -180) & (df_maternidade['longitude'] <= 180)
    ].copy()
    
    logger.info(f"✅ {len(df_maternidade)} estabelecimentos com coordenadas válidas")
    
    # 3. Limpeza e padronização
    logger.info("🧹 Limpando e padronizando dados...")
    
    # Limpar telefones
    df_maternidade['telefone_limpo'] = df_maternidade.get('NU_TELEFONE', '').apply(limpar_telefone)
    
    # Classificar natureza jurídica
    df_maternidade['categoria'] = df_maternidade.get('CO_NATUREZA_JUR', '').apply(classificar_natureza)
    
    # Criar endereço completo
    df_maternidade['endereco_completo'] = (
        df_maternidade.get('NO_LOGRADOURO', '').astype(str) + ', ' +
        df_maternidade.get('NU_ENDERECO', '').astype(str) + ' - ' +
        df_maternidade.get('NO_BAIRRO', '').astype(str) + ', ' +
        df_maternidade.get('SG_UF', '').astype(str)
    )
    
    # 4. Selecionar e renomear colunas finais
    df_final = pd.DataFrame({
        'cnes': df_maternidade.get('CO_CNES', ''),
        'nome_fantasia': df_maternidade.get('NO_FANTASIA', ''),
        'logradouro': df_maternidade.get('NO_LOGRADOURO', ''),
        'numero': df_maternidade.get('NU_ENDERECO', ''),
        'bairro': df_maternidade.get('NO_BAIRRO', ''),
        'municipio': df_maternidade.get('CO_MUNICIPIO_GESTOR', ''),
        'uf': df_maternidade.get('SG_UF', ''),
        'telefone': df_maternidade['telefone_limpo'],
        'categoria': df_maternidade['categoria'],
        'endereco_completo': df_maternidade['endereco_completo'],
        'latitude': df_maternidade['latitude'],
        'longitude': df_maternidade['longitude']
    })
    
    # Remove duplicatas por CNES
    df_final = df_final.drop_duplicates(subset=['cnes'], keep='first')
    logger.info(f"✅ {len(df_final)} estabelecimentos únicos processados")
    
    # FILTRO CRÍTICO PARA EMERGÊNCIA: Remove hospitais sem telefone
    # Em emergências de maternidade, linha morta é risco crítico
    antes_filtro = len(df_final)
    df_final = df_final[df_final['telefone_limpo'] != ''].copy()
    depois_filtro = len(df_final)
    removidos = antes_filtro - depois_filtro
    if removidos > 0:
        logger.warning(f"⚠️ {removidos} estabelecimentos removidos por não terem telefone (risco crítico em emergências)")
    logger.info(f"✅ {len(df_final)} estabelecimentos com telefone válido (essencial para emergências)")
    
    # 5. Criar índice BallTree para buscas rápidas
    logger.info("🌳 Criando índice espacial BallTree...")
    coords_validas = df_final[['latitude', 'longitude']].dropna()
    if len(coords_validas) > 0:
        # Converte para radianos (exigência da BallTree para Haversine)
        coords_rad = np.deg2rad(coords_validas.values)
        tree = BallTree(coords_rad, metric='haversine')
        
        # Salva o índice
        os.makedirs(output_dir, exist_ok=True)
        tree_path = os.path.join(output_dir, 'maternidades_index.pkl')
        with open(tree_path, 'wb') as f:
            pickle.dump({
                'tree': tree,
                'indices': coords_validas.index.tolist()
            }, f)
        logger.info(f"✅ Índice BallTree salvo em: {tree_path}")
    
    # 6. Salvar CSV processado
    csv_path = os.path.join(output_dir, 'maternidades_processadas.csv')
    df_final.to_csv(csv_path, index=False, encoding='utf-8')
    logger.info(f"✅ Dados processados salvos em: {csv_path}")
    
    # Estatísticas finais
    logger.info("\n📊 Estatísticas finais:")
    logger.info(f"   Total de maternidades: {len(df_final)}")
    logger.info(f"   Públicas: {len(df_final[df_final['categoria'] == 'Público'])}")
    logger.info(f"   Privadas: {len(df_final[df_final['categoria'] == 'Privado'])}")
    logger.info(f"   Com telefone: {len(df_final[df_final['telefone'] != ''])}")
    
    return df_final


if __name__ == '__main__':
    if len(sys.argv) < 2:
        logger.error("❌ Uso: python process_cnes_optimized.py <caminho_para_csv>")
        sys.exit(1)
    
    caminho_csv = sys.argv[1]
    if not os.path.exists(caminho_csv):
        logger.error(f"❌ Arquivo não encontrado: {caminho_csv}")
        sys.exit(1)
    
    processar_dados(caminho_csv)
