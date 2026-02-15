# -*- coding: utf-8 -*-
"""
Serviço de busca espacial otimizada usando BallTree
Encontra maternidades próximas em milissegundos mesmo com 600k+ registros
"""

import os
import pickle
import numpy as np
import pandas as pd
from sklearn.neighbors import BallTree
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Caminhos padrão
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
INDEX_PATH = os.path.join(DATA_DIR, 'maternidades_index.pkl')
CSV_PATH = os.path.join(DATA_DIR, 'maternidades_processadas.csv')


class SpatialSearchService:
    """Serviço para busca espacial rápida de maternidades"""
    
    def __init__(self, csv_path: Optional[str] = None, index_path: Optional[str] = None):
        """
        Inicializa o serviço de busca espacial
        
        Args:
            csv_path: Caminho para CSV com dados processados
            index_path: Caminho para arquivo pickle com índice BallTree
        """
        self.csv_path = csv_path or CSV_PATH
        self.index_path = index_path or INDEX_PATH
        self.df = None
        self.tree = None
        self.indices_map = None
        self._load_data()
    
    def _load_data(self):
        """Carrega dados e índice espacial"""
        try:
            # Carrega CSV
            if os.path.exists(self.csv_path):
                self.df = pd.read_csv(self.csv_path, encoding='utf-8')
                logger.info(f"✅ Dados carregados: {len(self.df)} maternidades")
            else:
                logger.warning(f"⚠️ Arquivo CSV não encontrado: {self.csv_path}")
                return
            
            # Carrega índice BallTree
            if os.path.exists(self.index_path):
                with open(self.index_path, 'rb') as f:
                    index_data = pickle.load(f)
                    self.tree = index_data['tree']
                    self.indices_map = index_data['indices']
                logger.info("✅ Índice BallTree carregado")
            else:
                logger.warning(f"⚠️ Índice não encontrado, criando novo...")
                self._build_index()
                
        except Exception as e:
            logger.error(f"❌ Erro ao carregar dados: {e}", exc_info=True)
    
    def _build_index(self):
        """Constrói índice BallTree a partir dos dados"""
        if self.df is None or len(self.df) == 0:
            return
        
        coords_validas = self.df[['latitude', 'longitude']].dropna()
        if len(coords_validas) == 0:
            logger.warning("⚠️ Nenhuma coordenada válida encontrada")
            return
        
        # Converte para radianos
        coords_rad = np.deg2rad(coords_validas.values)
        self.tree = BallTree(coords_rad, metric='haversine')
        self.indices_map = coords_validas.index.tolist()
        
        # Salva índice
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        with open(self.index_path, 'wb') as f:
            pickle.dump({
                'tree': self.tree,
                'indices': self.indices_map
            }, f)
        logger.info("✅ Índice BallTree criado e salvo")
    
    def buscar_proximas(
        self,
        lat: float,
        lon: float,
        raio_km: float = 50,
        limite: int = 10,
        categoria: Optional[str] = None,
        apenas_com_telefone: bool = False
    ) -> List[Dict]:
        """
        Busca maternidades próximas usando BallTree
        
        Args:
            lat: Latitude do ponto de busca
            lon: Longitude do ponto de busca
            raio_km: Raio de busca em quilômetros
            limite: Número máximo de resultados
            categoria: Filtrar por 'Público' ou 'Privado' (opcional)
            apenas_com_telefone: Filtrar apenas estabelecimentos com telefone
        
        Returns:
            Lista de dicionários com informações das maternidades ordenadas por distância
        """
        if self.tree is None or self.df is None:
            logger.warning("⚠️ Dados não carregados, retornando lista vazia")
            return []
        
        try:
            # Converte coordenadas do usuário para radianos
            usuario_rad = np.deg2rad([[lat, lon]])
            
            # Raio da Terra em km é aproximadamente 6371
            raio_calculo = raio_km / 6371.0
            
            # Busca índices dos hospitais dentro do raio
            indices_encontrados = self.tree.query_radius(usuario_rad, r=raio_calculo)[0]
            
            if len(indices_encontrados) == 0:
                return []
            
            # Mapeia índices do BallTree para índices do DataFrame
            df_indices = [self.indices_map[i] for i in indices_encontrados]
            resultados = self.df.loc[df_indices].copy()
            
            # Calcula distâncias
            resultados['distancia_km'] = resultados.apply(
                lambda row: self._calcular_distancia_haversine(
                    lat, lon, row['latitude'], row['longitude']
                ),
                axis=1
            )
            
            # Filtros adicionais
            if categoria:
                resultados = resultados[resultados['categoria'] == categoria]
            
            if apenas_com_telefone:
                resultados = resultados[resultados['telefone'] != '']
            
            # Ordena por distância e limita resultados
            resultados = resultados.sort_values('distancia_km').head(limite)
            
            # Converte para lista de dicionários
            return resultados.to_dict('records')
            
        except Exception as e:
            logger.error(f"❌ Erro na busca espacial: {e}", exc_info=True)
            return []
    
    @staticmethod
    def _calcular_distancia_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calcula distância entre dois pontos usando fórmula de Haversine
        Considera a curvatura da Terra
        """
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371.0  # Raio da Terra em km
        
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        return round(R * c, 2)
    
    def esta_disponivel(self) -> bool:
        """Verifica se o serviço está disponível"""
        return self.tree is not None and self.df is not None and len(self.df) > 0


# Instância global (singleton)
_spatial_service = None


def get_spatial_service() -> SpatialSearchService:
    """Retorna instância global do serviço de busca espacial"""
    global _spatial_service
    if _spatial_service is None:
        _spatial_service = SpatialSearchService()
    return _spatial_service
