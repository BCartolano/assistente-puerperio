#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de Busca de Facilidades
Purpose: Buscar e filtrar hospitais/UPAs/UBS do banco CNES
Author: Dev Agent (baseado em health_data_audit rules)
"""

import os
import sqlite3
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime

try:
    from .geo_service import filter_by_radius
except ImportError:
    # Fallback para importação absoluta
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from services.geo_service import filter_by_radius

logger = logging.getLogger(__name__)

# Caminho do banco de dados
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'cnes_cache.db')


class FacilityService:
    """Serviço para busca de facilidades de saúde"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Inicializa o serviço
        
        Args:
            db_path: Caminho do banco de dados (default: cnes_cache.db)
        """
        self.db_path = db_path or DB_PATH
        self._check_database()
    
    def _check_database(self):
        """Verifica se o banco de dados existe"""
        if not os.path.exists(self.db_path):
            logger.warning(f"⚠️ Banco de dados não encontrado: {self.db_path}")
            logger.warning("💡 Execute o script de ingestão: python backend/etl/data_ingest.py")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Obtém conexão com o banco de dados"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(
                f"Banco de dados não encontrado: {self.db_path}. "
                "Execute o script de ingestão primeiro."
            )
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Retorna dict-like rows
        return conn
    
    def _build_filter_query(
        self,
        filter_type: str,
        is_emergency: bool
    ) -> Tuple[str, list]:
        """
        Constrói query SQL com filtros apropriados
        
        REGRA DE NEGÓCIO (PM):
        - Se is_emergency=True: Ignora filtros de convênio, retorna UPAs e Hospitais
        - Se filter_type=MATERNITY: Apenas has_maternity=1
        - Se filter_type=SUS: Apenas is_sus=1
        - Se filter_type=PRIVATE: Apenas is_sus=0
        """
        base_query = """
            SELECT 
                cnes_id,
                name,
                fantasy_name,
                address,
                city,
                state,
                neighborhood,
                lat,
                long,
                has_maternity,
                is_emergency_only,
                is_sus,
                management,
                tipo_unidade,
                natureza_juridica,
                cnpj,
                data_source_date
            FROM hospitals_cache
            WHERE lat IS NOT NULL 
              AND long IS NOT NULL
              AND (
                  tipo_unidade IN ('HOSPITAL', 'UPA', 'UBS', 'OUTROS')
                  OR tipo_unidade IS NULL
              )
        """
        
        params = []
        
        # REGRA CRÍTICA (PM): Emergência ignora filtros de convênio
        if is_emergency:
            # Em emergência, retorna UPAs e Hospitais (não UBS para consulta de rotina)
            base_query += " AND (is_emergency_only = 1 OR has_maternity = 1 OR tipo_unidade IN ('05', '07'))"
        else:
            # Filtros normais baseados em filter_type
            if filter_type == "MATERNITY":
                base_query += " AND has_maternity = 1"
            elif filter_type == "SUS":
                base_query += " AND is_sus = 1"
            elif filter_type == "PRIVATE":
                base_query += " AND is_sus = 0"
            elif filter_type == "EMERGENCY_ONLY":
                base_query += " AND is_emergency_only = 1"
            # filter_type == "ALL" não adiciona filtro adicional
        
        # Não ordenar aqui - vamos ordenar por distância após filtrar por raio
        # base_query += " ORDER BY name"
        
        return base_query, params
    
    def _format_facility_tags(self, row: sqlite3.Row) -> Dict:
        """
        Formata tags da facilidade conforme regras do Analyst
        
        REGRAS DO ANALYST:
        - Natureza jurídica 1xxx -> PÚBLICO/SUS
        - Natureza jurídica 3999 -> FILANTRÓPICO/ACEITA SUS
        - Natureza jurídica 2xxx -> PRIVADO
        """
        is_sus = bool(row['is_sus'])
        has_maternity = bool(row['has_maternity'])
        is_emergency_only = bool(row['is_emergency_only'])
        
        # Determina se é privado
        is_private = not is_sus or (
            row['natureza_juridica'] and 
            'PRIV' in str(row['natureza_juridica']).upper()
        )
        
        return {
            'sus': is_sus,
            'private': is_private,
            'maternity': has_maternity,
            'emergency_only': is_emergency_only
        }
    
    def _generate_badges(self, tags: Dict, row: sqlite3.Row) -> List[str]:
        """
        Gera badges visuais conforme UX Expert
        
        REGRA UX EXPERT:
        - Verde Escuro: Hospital com Maternidade (Privado)
        - Azul SUS: Hospital/Maternidade Pública
        - Amarelo: UPA/Pronto Atendimento
        - Cinza: UBS (Apenas rotina)
        """
        badges = []
        
        if tags['emergency_only']:
            badges.append("EMERGÊNCIA APENAS")
            badges.append("NÃO REALIZA PARTO")
        elif tags['maternity']:
            if tags['sus']:
                badges.append("ACEITA SUS")
                badges.append("MATERNIDADE")
            else:
                badges.append("MATERNIDADE")
                badges.append("PRIVADO")
        elif tags['sus']:
            badges.append("ACEITA SUS")
        else:
            badges.append("PRIVADO")
        
        return badges
    
    def _generate_warning_message(
        self,
        tags: Dict,
        row: sqlite3.Row
    ) -> Optional[str]:
        """
        Gera mensagem de aviso conforme regras do PM e Analyst
        
        REGRA CRÍTICA (PM + Analyst):
        - UPA: "Esta unidade não realiza partos, apenas estabilização"
        - Hospital sem maternidade para busca de parto: Não deve aparecer (filtrado antes)
        """
        if tags['emergency_only']:
            return "⚠️ Esta unidade não realiza partos, apenas estabilização. Em caso de emergência obstétrica, estabilização e transferência para hospital com maternidade."
        
        return None
    
    def _determine_facility_type(self, row: sqlite3.Row) -> str:
        """Determina tipo de facilidade baseado em tipo_unidade"""
        tipo_unidade = str(row['tipo_unidade'] or '')[:2]
        
        if tipo_unidade == '73':
            return "UPA"
        elif tipo_unidade in ('01', '02'):
            return "UBS"
        else:
            return "HOSPITAL"
    
    def _format_address(self, row: sqlite3.Row) -> Optional[str]:
        """Formata endereço completo"""
        parts = []
        
        if row['address']:
            parts.append(row['address'])
        if row['neighborhood']:
            parts.append(row['neighborhood'])
        if row['city']:
            parts.append(row['city'])
        if row['state']:
            parts.append(row['state'])
        
        return ', '.join(parts) if parts else None
    
    def search_facilities(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 10.0,
        filter_type: str = "ALL",
        is_emergency: bool = False
    ) -> Tuple[List[Dict], Optional[str], bool]:
        """
        Busca facilidades dentro do raio especificado
        
        Args:
            latitude: Latitude do usuário
            longitude: Longitude do usuário
            radius_km: Raio de busca em km
            filter_type: Tipo de filtro (ALL, SUS, PRIVATE, EMERGENCY_ONLY, MATERNITY)
            is_emergency: Se True, ignora filtros de convênio (regra de emergência)
        
        Returns:
            Tuple de (resultados, data_source_date, is_cache_fallback)
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Construir query com filtros
            query, params = self._build_filter_query(filter_type, is_emergency)
            
            # Executar query
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Obter data_source_date (do primeiro registro, se existir)
            data_source_date = None
            if rows:
                # Buscar data_source_date mais recente
                cursor.execute("SELECT MAX(data_source_date) as max_date FROM hospitals_cache")
                result = cursor.fetchone()
                if result and result['max_date']:
                    data_source_date = result['max_date']
            
            conn.close()
            
            # Converter rows para dicts
            facilities = []
            for row in rows:
                facility = dict(row)
                facilities.append(facility)
            
            # Filtrar por raio usando cálculo Haversine
            filtered_facilities = filter_by_radius(
                facilities,
                latitude,
                longitude,
                radius_km
            )
            
            # OTIMIZAÇÃO: Limitar a 100 resultados mais próximos (performance mobile)
            MAX_RESULTS = 100
            filtered_facilities = filtered_facilities[:MAX_RESULTS]
            
            logger.info(f"📊 Resultados filtrados: {len(filtered_facilities)} estabelecimentos dentro do raio")
            
            # Formatar resultados
            formatted_results = []
            for facility in filtered_facilities:
                tags = self._format_facility_tags(facility)
                badges = self._generate_badges(tags, facility)
                warning = self._generate_warning_message(tags, facility)
                facility_type = self._determine_facility_type(facility)
                
                # Gerar google_search_term para frontend
                name = facility.get('fantasy_name') or facility.get('name', '')
                google_search_term = f"{name} Emergency"
                
                formatted_result = {
                    'id': f"cnes_{facility['cnes_id']}",
                    'name': facility.get('name', ''),
                    'fantasy_name': facility.get('fantasy_name'),
                    'type': facility_type,
                    'tags': tags,
                    'badges': badges,
                    'address': self._format_address(facility),
                    'city': facility.get('city'),
                    'state': facility.get('state'),
                    'distance_km': facility.get('distance_km', 0),
                    'lat': facility.get('lat'),
                    'long': facility.get('long'),
                    'google_search_term': google_search_term,
                    'warning_message': warning,
                    'phone': None,  # Não está no CNES, será preenchido via Google Maps
                    'cnpj': facility.get('cnpj')
                }
                
                formatted_results.append(formatted_result)
            
            return formatted_results, data_source_date, False
            
        except FileNotFoundError as e:
            logger.error(f"❌ Erro: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Erro ao buscar facilidades: {e}")
            raise
