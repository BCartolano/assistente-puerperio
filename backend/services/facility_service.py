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
import unicodedata
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

# UF -> código IBGE 2 dígitos (CNES/state no DB). Brasil todo: 27 estados + DF.
UF_TO_CODE = {
    'AC': '12', 'AL': '27', 'AM': '13', 'AP': '16', 'BA': '29', 'CE': '23',
    'DF': '53', 'ES': '32', 'GO': '52', 'MA': '21', 'MG': '31', 'MS': '50',
    'MT': '51', 'PA': '15', 'PB': '25', 'PE': '26', 'PI': '22', 'PR': '41',
    'RJ': '33', 'RN': '24', 'RO': '11', 'RR': '14', 'RS': '43', 'SC': '42',
    'SE': '28', 'SP': '35', 'TO': '17',
}


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
        is_emergency: bool,
        search_mode: str = "all",
        state: Optional[str] = None,
        city: Optional[str] = None
    ) -> Tuple[str, list]:
        """
        Constrói query SQL com filtros apropriados
        
        ESTRATÉGIA ARQUITETURAL: Queries segregadas por modo de busca
        - Modo EMERGENCY: APENAS Hospitais (05, 07) e UPAs (73) - CRÍTICO PARA SEGURANÇA
        - Modo BASIC: APENAS UBS/Postos (01, 02, 15, 40) - Para vacinação e atenção básica
        - Modo ALL: Todos os tipos permitidos (compatibilidade)
        
        REGRA CRÍTICA DE SEGURANÇA (PO):
        - search_mode="emergency": FILTRO RÍGIDO - apenas 05, 07, 73
        - search_mode="basic": FILTRO RÍGIDO - apenas 01, 02, 15, 40
        - Não misturar emergência com atenção básica na mesma lista
        
        REGRA DE NEGÓCIO (PM):
        - Se is_emergency=True: Ignora filtros de convênio
        - Se filter_type=MATERNITY: Apenas has_maternity=1
        - Se filter_type=SUS: Apenas is_sus=1
        - Se filter_type=PRIVATE: Apenas is_sus=0
        - state/city: Filtro Brasil todo (5570 municípios, 27 estados + DF). Ignora raio quando informado.
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
                telefone,
                data_source_date
            FROM hospitals_cache
            WHERE lat IS NOT NULL 
              AND long IS NOT NULL
              AND lat != 0 
              AND long != 0
              AND lat BETWEEN -35.0 AND 5.0
              AND long BETWEEN -75.0 AND -30.0
        """
        
        params = []
        
        # REGRA CRÍTICA: Se buscar MATERNIDADE, APENAS hospitais com maternidade (EXCLUIR UPAs, UBS, USF)
        if filter_type == "MATERNITY":
            # MATERNIDADE: APENAS Hospitais (05, 07) COM maternidade
            # CRÍTICO: EXCLUIR UPAs, UBS, USF, Ambulatórios - APENAS HOSPITAIS
            # FILTRO ULTRA-RIGOROSO: Garantir que apenas hospitais apareçam, mesmo com dados inconsistentes
            
            # 1. APENAS tipos de hospital permitidos (não aceitar NULL)
            maternity_types = ['05', '07', 'HOSPITAL']
            maternity_placeholders = ','.join(['?' for _ in maternity_types])
            base_query += f" AND tipo_unidade IN ({maternity_placeholders})"
            params.extend(maternity_types)
            base_query += " AND tipo_unidade IS NOT NULL"  # CRÍTICO: Não aceitar NULL
            
            # 2. EXCLUIR explicitamente: UPAs, UBS, USF, Ambulatórios (segurança extra)
            excluded_maternity = ['73', 'UPA', '01', '02', '15', '40', 'UBS', '32', '71', '72', 'OUTROS']
            excluded_placeholders = ','.join(['?' for _ in excluded_maternity])
            base_query += f" AND tipo_unidade NOT IN ({excluded_placeholders})"
            params.extend(excluded_maternity)
            
            # 3. Garantir que não é UPA (tripla verificação) - CORRIGIDO: Remover OR IS NULL
            base_query += " AND is_emergency_only = 0"  # UPAs têm is_emergency_only=1
            base_query += " AND tipo_unidade != '73'"  # Verificação extra (sem OR NULL)
            base_query += " AND tipo_unidade != 'UPA'"  # Verificação extra (sem OR NULL)
            
            # 4. Garantir que tem maternidade
            base_query += " AND has_maternity = 1"  # CRÍTICO: Apenas com maternidade
            
            # 5. CRÍTICO: Excluir nomes que contenham especialidades não relacionadas a maternidade
            excluded_name_terms = [
                'OTORRINOLARINGOLOG', 'OTORRINO',
                'TERAPIA OCUPACIONAL',
                'PSICOLOGIA', 'PSICÓLOGO', 'PSICÓLOGA', 'PSIQUIATRIA',
                'GRUPAMENTO DE APOIO', 'GRUPAMENTO APOIO',
                'CENTRO OCUPACIONAL', 'CENTRO DE TREINAMENTO', 'CENTRO OCUPACIONAL E DE TREINAMENTO',
                'CENTRO DE APOIO', 'CENTRO APOIO',
                'ORTHO',  # Excluir "Orthoservice" e similares
                'ORTOPEDIA', 'ORTOPEDICO', 'ORTOPEDISTA',
                'CARDIOLOGIA', 'CARDIACO', 'CARDIAC',
                'ONCOLOGIA', 'ONCOLOGICO', 'CANCER',
                'REABILITACAO', 'FISIOTERAPIA',
                # Cirurgia plástica / estética (não maternidade)
                'CIRURGIA PLASTICA', 'CIRURGIA PLÁSTICA', 'PLASTICA', 'PLÁSTICA',
                'ESTETICA', 'ESTÉTICA', 'HOSPITAL DE CIRURGIA', 'CIRURGIA ESTETICA',
                'PSIQUIATRICO', 'MENTAL'
            ]
            for term in excluded_name_terms:
                base_query += f" AND UPPER(COALESCE(name, '')) NOT LIKE '%{term}%'"
                base_query += f" AND UPPER(COALESCE(fantasy_name, '')) NOT LIKE '%{term}%'"
            
            # 5b. Blacklist CNES: hospitais sem maternidade (cirurgia plástica, oncologia/cardiologia)
            base_query += " AND cnes_id NOT IN ('3105571', '0009601', '2085569', '0014001', '2078406', '2270188', '7092571', '7609566', '0002593', '0003085', '0007714', '0014125', '0016292', '0027707', '0106518', '0219622', '0228494', '0235385', '0262862')"  # Blacklist completa: saúde mental, clínicas específicas, COVID temporário
            
            # 6. Excluir nomes que contenham "UPA", "DIVISÃO", "GRUPAMENTO", "CLÍNICA DE TERAPIA" explicitamente
            base_query += " AND UPPER(COALESCE(name, '')) NOT LIKE '%UPA%'"
            base_query += " AND UPPER(COALESCE(fantasy_name, '')) NOT LIKE '%UPA%'"
            base_query += " AND UPPER(COALESCE(name, '')) NOT LIKE '%DIVISÃO%'"
            base_query += " AND UPPER(COALESCE(fantasy_name, '')) NOT LIKE '%DIVISÃO%'"
            base_query += " AND UPPER(COALESCE(name, '')) NOT LIKE '%DIVISAO%'"
            base_query += " AND UPPER(COALESCE(fantasy_name, '')) NOT LIKE '%DIVISAO%'"
            base_query += " AND UPPER(COALESCE(name, '')) NOT LIKE '%GRUPAMENTO%'"
            base_query += " AND UPPER(COALESCE(fantasy_name, '')) NOT LIKE '%GRUPAMENTO%'"
            base_query += " AND UPPER(COALESCE(name, '')) NOT LIKE '%CLINICA DE TERAPIA%'"
            base_query += " AND UPPER(COALESCE(fantasy_name, '')) NOT LIKE '%CLINICA DE TERAPIA%'"
            base_query += " AND UPPER(COALESCE(name, '')) NOT LIKE '%CLÍNICA DE TERAPIA%'"
            base_query += " AND UPPER(COALESCE(fantasy_name, '')) NOT LIKE '%CLÍNICA DE TERAPIA%'"
            
            logger.info("👶 FILTRO MATERNIDADE ULTRA-RIGOROSO: Buscando APENAS hospitais (05, 07) COM maternidade - UPAs/UBS/USF/Ambulatórios/Especialidades EXCLUÍDAS")
        
        # REGRA CRÍTICA DE SEGURANÇA: Filtro rígido baseado em search_mode (apenas se não for MATERNITY)
        elif search_mode == "emergency":
            # MODO EMERGÊNCIA: APENAS Hospitais e UPAs
            # CRÍTICO: Não incluir UBS/Postos aqui
            emergency_types = ['05', '07', '73', 'HOSPITAL', 'UPA']
            emergency_placeholders = ','.join(['?' for _ in emergency_types])
            base_query += f" AND tipo_unidade IN ({emergency_placeholders})"
            params.extend(emergency_types)
            logger.info("🔴 MODO EMERGÊNCIA: Buscando apenas Hospitais (05, 07) e UPAs (73)")
            
        elif search_mode == "basic":
            # MODO ATENÇÃO BÁSICA: APENAS UBS/Postos
            # CRÍTICO: Não incluir Hospitais aqui
            basic_types = ['01', '02', '15', '40', 'UBS']
            basic_placeholders = ','.join(['?' for _ in basic_types])
            base_query += f" AND tipo_unidade IN ({basic_placeholders})"
            params.extend(basic_types)
            logger.info("💉 MODO ATENÇÃO BÁSICA: Buscando apenas UBS/Postos (01, 02, 15, 40)")
            
        else:
            # MODO ALL: Todos os tipos permitidos (compatibilidade)
            allowed_types = ['05', '07', '73', '01', '02', '15', '40', 'HOSPITAL', 'UPA', 'UBS']
            allowed_placeholders = ','.join(['?' for _ in allowed_types])
            base_query += f" AND (tipo_unidade IN ({allowed_placeholders}) OR tipo_unidade IS NULL)"
            params.extend(allowed_types)
        
        # EXCLUSÃO EXPLÍCITA: Consultórios (22) e Farmácias (43) - sempre aplicado
        # CRÍTICO: Se for MATERNITY, não aplicar esta exclusão (já está filtrado acima)
        if filter_type != "MATERNITY":
            excluded_types = ['22', '43']
            excluded_placeholders = ','.join(['?' for _ in excluded_types])
            base_query += f" AND (tipo_unidade NOT IN ({excluded_placeholders}) OR tipo_unidade IS NULL)"
            params.extend(excluded_types)
        
        # Filtros adicionais baseados em filter_type (apenas se não for MATERNITY, que já foi tratado acima)
        if filter_type != "MATERNITY":
            if filter_type == "SUS":
                base_query += " AND is_sus = 1"
            elif filter_type == "PRIVATE":
                base_query += " AND is_sus = 0"
            elif filter_type == "EMERGENCY_ONLY":
                base_query += " AND is_emergency_only = 1"
        
        # Filtro Brasil todo: estado (UF) e/ou município (5570 municípios, 27 estados + DF)
        if state and state.strip():
            state_val = state.strip().upper()
            # DB usa código IBGE (35, 33...). Aceitar UF (SP, RJ) ou código.
            state_code = UF_TO_CODE.get(state_val) if len(state_val) == 2 else None
            state_code = state_code or (state_val if state_val.isdigit() and len(state_val) <= 2 else None)
            if state_code:
                base_query += " AND TRIM(COALESCE(state,'')) = ?"
                params.append(state_code)
        if city and city.strip():
            base_query += " AND (TRIM(COALESCE(city,'')) LIKE ? OR TRIM(COALESCE(city,'')) = ?)"
            c = city.strip()
            params.extend([f"%{c}%", c])
        
        # Não ordenar aqui - vamos ordenar por distância e categoria após filtrar por raio
        # base_query += " ORDER BY name"
        
        return base_query, params
    
    def _validate_data_completeness(self, row: sqlite3.Row) -> Dict:
        """
        FASE 3: Valida completude dos dados críticos
        
        Retorna flags indicando quais campos estão faltando para exibir avisos no frontend.
        CRÍTICO para responsabilidade jurídica: avisar quando dados estão incompletos.
        """
        missing_fields = []
        warnings = []
        
        # Campos críticos para exibição
        if not row.get('name') and not row.get('fantasy_name'):
            missing_fields.append('nome')
            warnings.append('Nome não disponível')
        
        if not row.get('address'):
            missing_fields.append('endereco')
            warnings.append('Endereço incompleto')
        
        # Telefone: Não adicionar warning (Google Maps mostra quando disponível)
        # if not row.get('telefone'):
        #     missing_fields.append('telefone')
        #     warnings.append('Telefone não disponível - Confirme diretamente com a unidade')
        
        if not row.get('lat') or not row.get('long') or row.get('lat') == 0 or row.get('long') == 0:
            missing_fields.append('coordenadas')
            warnings.append('Localização aproximada - Confirme endereço antes de se deslocar')
        
        # Determinar nível de completude
        # Nota: Telefone não é mais considerado crítico (Google Maps mostra quando disponível)
        total_critical = 3  # nome, endereco, coordenadas (telefone removido)
        missing_count = len(missing_fields)
        completeness_pct = ((total_critical - missing_count) / total_critical) * 100
        
        # Nível de completude
        if completeness_pct >= 100:
            completeness_level = 'complete'
        elif completeness_pct >= 75:
            completeness_level = 'mostly_complete'
        elif completeness_pct >= 50:
            completeness_level = 'partial'
        else:
            completeness_level = 'incomplete'
        
        return {
            'is_complete': missing_count == 0,
            'completeness_level': completeness_level,
            'completeness_pct': completeness_pct,
            'missing_fields': missing_fields,
            'warnings': warnings,
            'has_phone': bool(row.get('telefone')),
            'has_address': bool(row.get('address')),
            'has_coordinates': bool(row.get('lat') and row.get('long') and row.get('lat') != 0 and row.get('long') != 0)
        }
    
    def _format_facility_tags(self, row: sqlite3.Row) -> Dict:
        """
        Formata tags da facilidade usando DADOS EXATOS do CSV
        
        CRÍTICO PARA RESPONSABILIDADE JURÍDICA:
        - Usa APENAS dados do CSV (CO_NATUREZA_JUR, TP_GESTAO)
        - NÃO infere ou assume informações não explícitas
        
        REGRAS BASEADAS NO CSV:
        - Natureza jurídica 1xxx -> PÚBLICO/SUS (dados exatos)
        - Natureza jurídica 3999 -> FILANTRÓPICO/ACEITA SUS (dados exatos)
        - Natureza jurídica 2xxx -> PRIVADO (dados exatos)
        - Se natureza_juridica for NULL -> Não inferir, manter is_sus como está (vem do CSV)
        """
        # Usar dados EXATOS salvos no banco (já processados do CSV)
        is_sus = bool(row['is_sus'])  # Já determinado pelo determine_is_sus() baseado em CO_NATUREZA_JUR
        has_maternity = bool(row['has_maternity'])
        is_emergency_only = bool(row['is_emergency_only'])
        
        # Determina se é privado baseado em natureza jurídica (dados exatos do CSV)
        natureza_jur = str(row.get('natureza_juridica') or '').upper()
        # Se não aceita SUS OU natureza jurídica indica privado
        is_private = not is_sus or ('EMPRESARIAL' in natureza_jur or 'PRIV' in natureza_jur)
        
        return {
            'sus': is_sus,
            'private': is_private,
            'maternity': has_maternity,
            'emergency_only': is_emergency_only
        }
    
    def _generate_badges(self, tags: Dict, row: sqlite3.Row, filter_type: str = "ALL") -> List[str]:
        """
        Gera badges visuais simplificados (sem duplicatas)
        
        REGRA: Um badge de emergência, um badge de SUS/Público quando aplicável
        
        REGRA UX EXPERT:
        - Verde Escuro: Hospital com Maternidade (Privado)
        - Azul SUS: Hospital/Maternidade Pública
        - Amarelo: UPA/Pronto Atendimento
        - Cinza: UBS (Apenas rotina)
        
        CRÍTICO: Se filter_type == "MATERNITY", não adicionar "NÃO REALIZA PARTO"
        (apenas hospitais aparecem, então não precisa do aviso)
        """
        badges = []
        
        # Badge de Emergência (apenas um)
        if tags['emergency_only']:
            badges.append("EMERGÊNCIA")  # Simplificado: apenas "EMERGÊNCIA"
            # CRÍTICO: Não mostrar "NÃO REALIZA PARTO" em busca de maternidades (só hospitais aparecem)
            if filter_type != "MATERNITY":
                badges.append("NÃO REALIZA PARTO")  # Aviso importante apenas fora de busca de maternidades
        elif tags['maternity']:
            # Badge de Maternidade
            badges.append("MATERNIDADE")
            
            # Badge SUS/Público (apenas um, quando aplicável)
            if tags['sus']:
                badges.append("ACEITA SUS/PÚBLICO")  # Unificado: "ACEITA SUS/PÚBLICO"
            else:
                badges.append("PRIVADO")
        else:
            # Para outros casos (não emergência, não maternidade)
            if tags['sus']:
                badges.append("ACEITA SUS/PÚBLICO")  # Unificado
            else:
                badges.append("PRIVADO")
        
        return badges
    
    def _generate_warning_message(
        self,
        tags: Dict,
        row: sqlite3.Row,
        filter_type: str = "ALL"
    ) -> Optional[str]:
        """
        Gera mensagem de aviso conforme regras do PM e Analyst
        
        REGRA CRÍTICA (PM + Analyst):
        - UPA: "Esta unidade não realiza partos, apenas estabilização"
        - Hospital sem maternidade para busca de parto: Não deve aparecer (filtrado antes)
        - Bases SAMU: "Apenas Base Administrativa/Saída - Não é hospital"
        
        CRÍTICO: Se filter_type == "MATERNITY", NÃO retornar warning
        (apenas hospitais aparecem, então não precisa do aviso "não faz parto")
        """
        # CRÍTICO: Em busca de maternidades, não mostrar warnings (só hospitais aparecem)
        if filter_type == "MATERNITY":
            return None
        
        # Verificar se é base do SAMU
        if self._is_samu_base(row):
            return "⚠️ Apenas Base Administrativa/Saída - Não é hospital. Não atende pacientes diretamente."
        
        if tags['emergency_only']:
            return "⚠️ Esta unidade não realiza partos, apenas estabilização. Em caso de emergência obstétrica, estabilização e transferência para hospital com maternidade."
        
        return None
    
    def _determine_facility_type(self, row: sqlite3.Row) -> str:
        """Determina tipo de facilidade baseado em tipo_unidade"""
        tipo_unidade = str(row['tipo_unidade'] or '').strip()
        
        # Se já for tipo mapeado, retornar diretamente
        if tipo_unidade in ('HOSPITAL', 'UPA', 'UBS', 'OUTROS'):
            return tipo_unidade
        
        # UPA (Unidade de Pronto Atendimento)
        if tipo_unidade == '73':
            return "UPA"
        # UBS/Postos de Saúde (Pontos de Vacinação)
        elif tipo_unidade in ('01', '02', '15', '32', '40', '71', '72'):
            return "UBS"
        # Hospitais (Geral e Especializado)
        elif tipo_unidade in ('05', '07'):
            return "HOSPITAL"
        # Consultórios Isolados
        elif tipo_unidade == '22':
            return "CONSULTÓRIO"
        # Bases do SAMU
        elif tipo_unidade in ('80', '81', '82'):
            return "SAMU"
        else:
            return "OUTROS"
    
    def _is_vaccination_point(self, row: sqlite3.Row) -> bool:
        """
        Identifica se é ponto de vacinação baseado em CO_TIPO_UNIDADE
        
        Tipos de vacinação:
        - 01: Posto de Saúde
        - 02: Centro de Saúde / Unidade Básica
        - 15: Unidade Mista
        - 32: Centro de Atenção Psicossocial
        - 40: Unidade de Apoio Diagnóstico e Terapia
        - 71: Centro de Atenção Integral à Saúde Mental
        - 72: Centro de Atenção Integral à Saúde da Mulher
        """
        tipo_unidade = str(row['tipo_unidade'] or '').strip()
        # Pode ser código ('01', '02') ou tipo mapeado ('UBS')
        vaccination_codes = ['01', '02', '15', '32', '40', '71', '72']
        vaccination_types = ['UBS']
        return tipo_unidade in vaccination_codes or tipo_unidade in vaccination_types
    
    def _is_samu_base(self, row: sqlite3.Row) -> bool:
        """Identifica se é base do SAMU"""
        tipo_unidade = str(row['tipo_unidade'] or '').strip()
        # Verificar também no nome
        name = str(row.get('name', '') or '').upper()
        fantasy_name = str(row.get('fantasy_name', '') or '').upper()
        # Pode ser código ('80', '81', '82') ou tipo mapeado
        return tipo_unidade in ('80', '81', '82') or 'SAMU' in tipo_unidade.upper() or 'SAMU' in name or 'SAMU' in fantasy_name
    
    def _is_hospital(self, row: sqlite3.Row) -> bool:
        """Identifica se é hospital (Geral ou Especializado)"""
        tipo_unidade = str(row['tipo_unidade'] or '').strip()
        # Pode ser código ('05', '07') ou tipo mapeado ('HOSPITAL')
        return tipo_unidade in ('05', '07') or tipo_unidade == 'HOSPITAL'
    
    def _get_priority_score(self, facility: Dict, is_emergency: bool) -> int:
        """
        Calcula score de prioridade para ordenação
        
        Prioridade:
        1. Hospitais (emergência/internação) - score 100
        2. UPAs (emergência) - score 90
        3. Pontos de vacinação - score 80
        4. Outros - score 50
        5. Consultórios isolados - score 10 (despriorizados)
        6. Bases SAMU - score 5 (apenas administrativo)
        """
        tipo_unidade = str(facility.get('tipo_unidade', '') or '').strip()
        
        # Hospitais têm máxima prioridade em emergência (código ou tipo mapeado)
        if is_emergency and (tipo_unidade in ('05', '07') or tipo_unidade == 'HOSPITAL'):
            return 100
        
        # UPAs em emergência
        if is_emergency and (tipo_unidade == '73' or tipo_unidade == 'UPA'):
            return 90
        
        # Pontos de vacinação
        if self._is_vaccination_point_from_dict(facility):
            return 80
        
        # Consultórios isolados - despriorizados
        if tipo_unidade == '22':
            return 10
        
        # Bases SAMU - muito baixa prioridade (apenas administrativo)
        if self._is_samu_base_from_dict(facility):
            return 5
        
        # Outros
        return 50
    
    def _is_vaccination_point_from_dict(self, facility: Dict) -> bool:
        """Helper para verificar vacinação a partir de dict"""
        tipo_unidade = str(facility.get('tipo_unidade', '') or '').strip()
        vaccination_codes = ['01', '02', '15', '32', '40', '71', '72']
        vaccination_types = ['UBS']
        return tipo_unidade in vaccination_codes or tipo_unidade in vaccination_types
    
    def _is_samu_base_from_dict(self, facility: Dict) -> bool:
        """Helper para verificar SAMU a partir de dict"""
        tipo_unidade = str(facility.get('tipo_unidade', '') or '').strip()
        name = str(facility.get('name', '') or '').upper()
        fantasy_name = str(facility.get('fantasy_name', '') or '').upper()
        return tipo_unidade in ('80', '81', '82') or 'SAMU' in tipo_unidade.upper() or 'SAMU' in name or 'SAMU' in fantasy_name
    
    def _format_address(self, row: sqlite3.Row) -> Optional[str]:
        """
        Formata endereço completo para exibição e Google Maps
        
        CRÍTICO: Retorna endereço completo (rua, número, bairro, cidade, estado)
        para garantir localização exata no Google Maps.
        """
        parts = []
        
        # Endereço base (rua, número)
        if row.get('address'):
            parts.append(row['address'])
        
        # Bairro
        if row.get('neighborhood'):
            parts.append(row['neighborhood'])
        
        # Cidade
        if row.get('city'):
            parts.append(row['city'])
        
        # Estado (UF)
        if row.get('state'):
            # Se state é código (35, 33), tentar converter para UF
            state_val = str(row['state']).strip()
            if state_val.isdigit() and len(state_val) <= 2:
                # Mapear código para UF (se disponível)
                code_to_uf = {v: k for k, v in UF_TO_CODE.items()}
                state_val = code_to_uf.get(state_val, state_val)
            parts.append(state_val)
        
        return ', '.join(parts) if parts else None
    
    def _sanitize_name(self, name: str) -> Optional[str]:
        """
        Sanitiza nome removendo termos comerciais problemáticos
        
        Filtra: drogaria, farma, farmácia, removale, ambulância privada, etc.
        """
        if not name:
            return None
        
        name_lower = name.lower().strip()
        
        # Termos comerciais que indicam que não é unidade de saúde pública
        # CRÍTICO: Adicionar termos que NÃO são hospitais com maternidade
        blacklist_terms = [
            'drogaria', 'farma', 'farmácia', 'farmácias',
            'removale', 'removale', 'ambulância', 'ambulancia',
            'transporte', 'transporte médico', 'clínica estética',
            'estética', 'beleza', 'cosmético'
        ]
        
        # Se contém qualquer termo da blacklist, retornar None (será filtrado)
        for term in blacklist_terms:
            if term in name_lower:
                logger.warning(f"🚫 Nome filtrado por blacklist: {name} (contém '{term}')")
                return None
        
        # Especialidades que NÃO são maternidade (verificar como palavras completas)
        # CRÍTICO: Verificar palavras completas para evitar falsos positivos (ex: "Christovao" não deve ser filtrado por "to")
        excluded_specialties = [
            'otorrinolaringologista', 'otorrinolaringologia', 'otorrino',
            'terapia ocupacional',  # Verificar frase completa
            'psicologia', 'psicólogo', 'psicóloga', 'psiquiatria',
            'grupamento de apoio', 'grupamento apoio',
            'centro ocupacional', 'centro de treinamento', 'centro ocupacional e de treinamento',
            'centro de apoio', 'centro apoio'
        ]
        
        # Verificar palavras completas (não substrings)
        import re
        words_in_name = set(re.findall(r'\b\w+\b', name_lower))
        for specialty in excluded_specialties:
            specialty_words = set(re.findall(r'\b\w+\b', specialty.lower()))
            # Se todas as palavras da especialidade estão no nome (como palavras completas), filtrar
            if specialty_words.issubset(words_in_name) or specialty.lower() in name_lower:
                logger.warning(f"🚫 Nome filtrado por especialidade não relacionada: {name} (contém '{specialty}')")
                return None
        
        return name.strip()
    
    def _clean_name_from_location(self, name: str) -> Optional[str]:
        """
        Remove Estado/Município do nome do hospital
        
        Args:
            name: Nome do hospital que pode conter Estado/Município
        
        Returns:
            Nome limpo sem Estado/Município
        """
        if not name:
            return None
        
        name_clean = name.strip()
        
        # Lista de estados (siglas)
        estados = ['SP', 'RJ', 'MG', 'RS', 'PR', 'SC', 'BA', 'GO', 'PE', 'CE', 'PA', 'MA', 
                   'MS', 'ES', 'PB', 'AL', 'RN', 'PI', 'TO', 'MT', 'DF', 'AC', 'AP', 'RO', 
                   'RR', 'SE', 'AM']
        
        # Lista de municípios comuns
        municipios = [
            'SAO PAULO', 'RIO DE JANEIRO', 'BELO HORIZONTE', 'BRASILIA', 'SALVADOR', 
            'FORTALEZA', 'CURITIBA', 'RECIFE', 'PORTO ALEGRE', 'BELEM', 'MANAUS',
            'SAO JOSE DOS CAMPOS', 'CAMPINAS', 'GUARULHOS', 'SAO BERNARDO DO CAMPO',
            'SAO CAETANO DO SUL', 'SANTO ANDRE', 'OSASCO', 'RIBEIRAO PRETO', 'SOROCABA'
        ]
        
        # Remover estados do final do nome
        for estado in estados:
            # Padrões: " - SP", " -SP", " SP", " (SP)", " [SP]"
            patterns = [
                f' - {estado}',
                f'-{estado}',
                f' {estado}',
                f'({estado})',
                f'[{estado}]',
                f', {estado}',
                f',{estado}'
            ]
            for pattern in patterns:
                if name_clean.upper().endswith(pattern.upper()):
                    name_clean = name_clean[:-len(pattern)].strip()
        
        # Remover municípios do final do nome
        for municipio in municipios:
            # Padrões similares
            patterns = [
                f' - {municipio}',
                f'-{municipio}',
                f' {municipio}',
                f'({municipio})',
                f'[{municipio}]',
                f', {municipio}',
                f',{municipio}'
            ]
            for pattern in patterns:
                if name_clean.upper().endswith(pattern.upper()):
                    name_clean = name_clean[:-len(pattern)].strip()
        
        return name_clean if name_clean else None
    
    def _is_person_name(self, name: str) -> bool:
        """
        Detecta se o nome parece ser de uma pessoa física (ex: "Monica Araujo")
        
        Heurística: Nomes próprios geralmente têm 2-3 palavras e não contêm
        termos institucionais.
        """
        if not name:
            return False
        
        name_clean = name.strip()
        words = name_clean.split()
        
        # Se tiver mais de 4 palavras, provavelmente não é nome de pessoa
        if len(words) > 4:
            return False
        
        # Se tiver menos de 2 palavras, pode ser nome de pessoa ou instituição
        if len(words) < 2:
            return False
        
        # Termos institucionais que indicam que não é nome de pessoa
        institutional_terms = [
            'hospital', 'hosp', 'maternidade', 'unidade', 'ubs', 'upa',
            'centro', 'posto', 'clínica', 'clinica', 'saúde', 'saude',
            'municipal', 'estadual', 'federal', 'público', 'publico'
        ]
        
        name_lower = name_clean.lower()
        for term in institutional_terms:
            if term in name_lower:
                return False
        
        # Se passou pelos filtros e tem 2-3 palavras, provavelmente é nome de pessoa
        if 2 <= len(words) <= 3:
            return True
        
        return False
    
    def _improve_display_name(
        self,
        name: str,
        fantasy_name: str,
        facility_type: str,
        city: Optional[str],
        neighborhood: Optional[str]
    ) -> tuple:
        """
        Melhora o nome de exibição seguindo regra UX: Tipo + Bairro como título principal
        
        REGRA UX (Arquiteto):
        - Título principal: Tipo + Bairro (ex: "UBS Jardim Santa Inês II")
        - Subtítulo: Nome da pessoa/homenagem (ex: "Dr. José da Cruz Passos Junior")
        - Para Hospitais: Nome deve ser limpo (sem nomes de pessoas)
        - Para UBS: Aceitar nomes de pessoas mas prefixar com "UBS - [Nome]"
        
        Returns:
            Tuple de (título_principal, subtítulo)
        """
        type_display = {
            'HOSPITAL': 'Hospital',
            'UPA': 'UPA',
            'UBS': 'UBS',
            'CONSULTÓRIO': 'Unidade de Saúde',
            'SAMU': 'Base SAMU',
            'OUTROS': 'Unidade de Saúde'
        }
        
        type_label = type_display.get(facility_type, 'Unidade de Saúde')
        
        # Para Hospitais: Nome deve ser limpo (sem nomes de pessoas, sem Estado/Município)
        if facility_type == 'HOSPITAL':
            # Limpar nome fantasia (remover Estado/Município se presente)
            clean_fantasy = self._clean_name_from_location(fantasy_name) if fantasy_name else None
            clean_name = self._clean_name_from_location(name) if name else None
            
            # Se nome fantasia limpo não é nome de pessoa, usar
            if clean_fantasy and not self._is_person_name(clean_fantasy):
                main_title = clean_fantasy
                subtitle = None
            # Se razão social limpa não é nome de pessoa, usar
            elif clean_name and not self._is_person_name(clean_name):
                main_title = clean_name
                subtitle = None
            # Se ambos são nomes de pessoas, usar tipo + bairro (NÃO cidade/estado)
            else:
                if neighborhood:
                    main_title = f"{type_label} - {neighborhood}"
                else:
                    main_title = type_label
                subtitle = None
        
        # Para UBS: Aceitar nomes de pessoas mas prefixar com "UBS - [Nome]"
        elif facility_type in ('UBS', 'OUTROS'):
            # Limpar nomes (remover Estado/Município)
            clean_fantasy = self._clean_name_from_location(fantasy_name) if fantasy_name else None
            clean_name = self._clean_name_from_location(name) if name else None
            
            # Se nome fantasia limpo não é nome de pessoa, usar diretamente
            if clean_fantasy and not self._is_person_name(clean_fantasy):
                main_title = clean_fantasy
                subtitle = None
            # Se nome fantasia é nome de pessoa, prefixar com tipo
            elif fantasy_name and self._is_person_name(fantasy_name):
                if neighborhood:
                    main_title = f"{type_label} - {neighborhood}"
                else:
                    main_title = type_label
                subtitle = fantasy_name  # Nome da pessoa como subtítulo
            # Se razão social limpa não é nome de pessoa, usar
            elif clean_name and not self._is_person_name(clean_name):
                main_title = clean_name
                subtitle = None
            # Se ambos são nomes de pessoas, usar tipo + bairro (NÃO cidade/estado)
            else:
                if neighborhood:
                    main_title = f"{type_label} - {neighborhood}"
                else:
                    main_title = type_label
                subtitle = fantasy_name or name  # Nome da pessoa como subtítulo
        
        # Para outros tipos (UPA, etc)
        else:
            # Limpar nomes (remover Estado/Município)
            clean_fantasy = self._clean_name_from_location(fantasy_name) if fantasy_name else None
            clean_name = self._clean_name_from_location(name) if name else None
            
            if clean_fantasy and not self._is_person_name(clean_fantasy):
                main_title = clean_fantasy
                subtitle = None
            elif clean_name and not self._is_person_name(clean_name):
                main_title = clean_name
                subtitle = None
            else:
                if neighborhood:
                    main_title = f"{type_label} - {neighborhood}"
                else:
                    main_title = type_label
                subtitle = None
        
        return (main_title, subtitle)
    
    def search_facilities(
        self,
        latitude: Optional[float],
        longitude: Optional[float],
        radius_km: float = 10.0,
        filter_type: str = "ALL",
        is_emergency: bool = False,
        search_mode: str = "all",
        state: Optional[str] = None,
        city: Optional[str] = None
    ) -> Tuple[List[Dict], Optional[str], bool]:
        """
        Busca facilidades dentro do raio especificado ou por estado/município (Brasil todo).
        
        Args:
            latitude: Latitude do usuário (opcional se state/city informados)
            longitude: Longitude do usuário (opcional se state/city informados)
            radius_km: Raio de busca em km
            filter_type: Tipo de filtro (ALL, SUS, PRIVATE, EMERGENCY_ONLY, MATERNITY)
            is_emergency: Se True, ignora filtros de convênio
            search_mode: Modo de busca
            state: Filtro por UF (ex: SP, RJ). 27 estados + DF.
            city: Filtro por município. 5570 municípios.
        
        Returns:
            Tuple de (resultados, data_source_date, is_cache_fallback)
        """
        try:
            filter_by_region = bool((state or "").strip() or (city or "").strip())
            use_coords = latitude is not None and longitude is not None
            
            if filter_by_region:
                radius_km = 5000.0
                logger.info(f"🇧🇷 Filtro Brasil todo: state={state!r}, city={city!r} (raio ignorado)")
            elif search_mode == "emergency" and radius_km < 20.0:
                radius_km = 20.0
                logger.info(f"🔴 Raio aumentado para {radius_km}km em modo emergência")
            
            if filter_by_region and not use_coords:
                logger.info("🇧🇷 Busca por estado/município sem geolocalização: ordenação por cidade/nome")
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query, params = self._build_filter_query(
                filter_type, is_emergency, search_mode,
                state=state or None,
                city=city or None
            )
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            data_source_date = None
            if rows:
                cursor.execute("SELECT MAX(data_source_date) as max_date FROM hospitals_cache")
                result = cursor.fetchone()
                if result and result['max_date']:
                    data_source_date = result['max_date']
            
            conn.close()
            
            facilities = [dict(row) for row in rows]
            
            facilities_validas = []
            for facility in facilities:
                lat = facility.get('lat')
                lon = facility.get('long')
                if (lat is None or lon is None or lat == 0 or lon == 0 or
                    not (-35.0 <= lat <= 5.0) or not (-75.0 <= lon <= -30.0)):
                    logger.warning(f"🚫 Hospital {facility.get('cnes_id')} ({facility.get('name')}) com coordenadas inválidas")
                    continue
                facilities_validas.append(facility)
            
            if filter_by_region and not use_coords:
                # Sem geolocalização: não filtrar por raio, distance_km=0, ordenar por cidade/nome
                for f in facilities_validas:
                    f['distance_km'] = 0.0
                filtered_facilities = facilities_validas
                filtered_facilities.sort(key=lambda x: (
                    (x.get('city') or '').upper(),
                    (x.get('name') or x.get('fantasy_name') or '').upper()
                ))
            else:
                filtered_facilities = filter_by_radius(
                    facilities_validas,
                    latitude,
                    longitude,
                    radius_km
                )
            
            # Desduplicar: mesmo lugar (mesma lat/long) = manter apenas o mais próximo
            seen_coords = {}
            deduped = []
            for f in filtered_facilities:
                key = (round(float(f.get('lat') or 0), 5), round(float(f.get('long') or 0), 5))
                if key not in seen_coords:
                    seen_coords[key] = f
                    deduped.append(f)
            n_before_dedup = len(filtered_facilities)
            filtered_facilities = deduped
            if n_before_dedup != len(deduped):
                logger.info(f"🔄 Desduplicação: {n_before_dedup} → {len(deduped)} (mesmo lugar removido)")
            
            for facility in filtered_facilities:
                facility['priority_score'] = self._get_priority_score(facility, is_emergency)
            
            if use_coords:
                filtered_facilities.sort(key=lambda x: (-x.get('priority_score', 0), x.get('distance_km', float('inf'))))
            
            MAX_RESULTS = 500 if filter_by_region else 100
            filtered_facilities = filtered_facilities[:MAX_RESULTS]
            
            logger.info(f"📊 Resultados filtrados: {len(filtered_facilities)} estabelecimentos")
            
            # Formatar resultados
            formatted_results = []
            for facility in filtered_facilities:
                # Converter para Row-like object para métodos que esperam sqlite3.Row
                class RowLike:
                    def __init__(self, d):
                        self._dict = d
                    def __getitem__(self, key):
                        return self._dict.get(key)
                    def get(self, key, default=None):
                        return self._dict.get(key, default)
                
                row_like = RowLike(facility)
                
                tags = self._format_facility_tags(row_like)
                # FASE 3: Validar completude dos dados
                data_validation = self._validate_data_completeness(row_like)
                # CRÍTICO: Se for busca MATERNITY, não mostrar "NÃO REALIZA PARTO" (só hospitais aparecem)
                badges = self._generate_badges(tags, row_like, filter_type)
                warning = self._generate_warning_message(tags, row_like, filter_type)
                facility_type = self._determine_facility_type(row_like)
                is_vaccination = self._is_vaccination_point(row_like)
                is_hospital = self._is_hospital(row_like)
                is_samu = self._is_samu_base(row_like)
                
                # Sanitizar nomes (filtrar farmácias, drogarias, especialidades não relacionadas, etc.)
                name_raw = facility.get('name', '')
                fantasy_name_raw = facility.get('fantasy_name', '')
                
                # CRÍTICO: Validação de coordenadas (ANTES de qualquer outro filtro)
                lat = facility.get('lat')
                lon = facility.get('long')
                if (lat is None or lon is None or 
                    lat == 0 or lon == 0 or
                    not (-35.0 <= lat <= 5.0) or 
                    not (-75.0 <= lon <= -30.0)):
                    logger.warning(f"🚫 Hospital {facility.get('cnes_id')} ({name_raw}) filtrado: coordenadas inválidas (lat={lat}, lon={lon})")
                    continue
                
                # CRÍTICO: Em busca MATERNITY, filtrar termos não relacionados e garantir que é hospital
                if filter_type == "MATERNITY":
                    # Verificação 1: Tipo de unidade DEVE ser hospital (OBRIGATÓRIO)
                    tipo_unidade = facility.get('tipo_unidade', '').strip()
                    if not tipo_unidade or tipo_unidade not in ('05', '07', 'HOSPITAL'):
                        logger.warning(f"🚫 Estabelecimento {facility.get('cnes_id')} ({name_raw}) filtrado: tipo_unidade={tipo_unidade} não é hospital")
                        continue
                    
                    # Verificação 2: NÃO pode ser UPA (tripla verificação)
                    if tipo_unidade in ('73', 'UPA') or facility.get('is_emergency_only', 0) == 1:
                        logger.warning(f"🚫 Estabelecimento {facility.get('cnes_id')} ({name_raw}) filtrado: é UPA")
                        continue
                    
                    # Verificação 3: NÃO pode ser UBS/USF
                    if tipo_unidade in ('01', '02', '15', '40', 'UBS', '32', '71', '72', 'OUTROS'):
                        logger.warning(f"🚫 Estabelecimento {facility.get('cnes_id')} ({name_raw}) filtrado: é UBS/USF/OUTROS")
                        continue
                    
                    # Verificação 4: Nome não pode conter termos não relacionados
                    name_upper = (name_raw or '').upper()
                    fantasy_upper = (fantasy_name_raw or '').upper()
                    
                    excluded_maternity_terms = [
                        'OTORRINOLARINGOLOG', 'OTORRINO',
                        'TERAPIA OCUPACIONAL',
                        'PSICOLOGIA', 'PSICÓLOGO', 'PSICÓLOGA', 'PSIQUIATRIA',
                        'PSIQUIATRICO', 'MENTAL', 'SAUDE MENTAL', 'SAÚDE MENTAL',
                        'CVV', 'CENTRO DE VALORIZACAO', 'CENTRO DE VALORIZAÇÃO', 'VALORIZACAO DA VIDA',
                        'DEPENDENCIA QUIMICA', 'DEPENDÊNCIA QUÍMICA', 'DEPENDENCIA', 'DEPENDÊNCIA',
                        'QUIMICA', 'QUÍMICA', 'ADICCAO', 'ADICÇÃO', 'ALCOOLISMO', 'ALCOOLISMO',
                        'DROGADICCAO', 'DROGADIÇÃO', 'TRATAMENTO DROGAS', 'TRATAMENTO DROGA',
                        'FRANCISCA JULIA', 'FRANCISCA JÚLIA', 'FRANCISCAJULIA',
                        'GRUPAMENTO DE APOIO', 'GRUPAMENTO APOIO',
                        'CENTRO OCUPACIONAL', 'CENTRO DE TREINAMENTO',
                        'CENTRO OCUPACIONAL E DE TREINAMENTO',
                        'CENTRO DE APOIO', 'CENTRO APOIO',
                        'UPA',  # Excluir explicitamente nomes com "UPA"
                        'DIVISÃO', 'DIVISAO',  # Excluir "Divisão de Saúde"
                        'GRUPAMENTO',  # Excluir "Grupamento de Apoio"
                        'CLINICA DE TERAPIA', 'CLÍNICA DE TERAPIA',  # Excluir clínicas de terapia
                        # Ortopedia
                        'ORTHO', 'ORTOPEDIA', 'ORTOPEDICO', 'ORTOPEDISTA',
                        'ORTO', 'TRAUMATO', 'FRATURA', 'OSSO', 'OSSOS', 'COLUNA', 'JOELHO', 'QUADRIL', 'OMBRO',
                        # Visão/Oftalmologia
                        'VISÃO', 'VISAO', 'VISUAL', 'OFTA', 'OFTALMO', 'OLHO', 'OLHOS',
                        'RETINA', 'CÓRNEA', 'CORNEA', 'CATARATA', 'GLAUCOMA',
                        # Pediatria/Hospitais Infantis
                        'INFANTIL', 'PEDIATRIA', 'PEDIATRICO', 'PEDIATRICA', 'PEDIATRIC',
                        'CRIANCA', 'CRIANÇA', 'BABY', 'BEBE', 'BEBÊ',
                        # Cirurgia plástica / estética (não maternidade)
                        'CIRURGIA PLASTICA', 'CIRURGIA PLÁSTICA', 'PLASTICA', 'PLÁSTICA',
                        'ESTETICA', 'ESTÉTICA', 'HOSPITAL DE CIRURGIA', 'CIRURGIA ESTETICA',
                        # Outras especialidades
                        'CARDIOLOGIA', 'CARDIACO', 'CARDIAC', 'CORAÇÃO', 'CORACAO',
                        'ONCOLOGIA', 'ONCOLOGICO', 'CANCER', 'CÂNCER',
                        'REABILITACAO', 'FISIOTERAPIA',
                        'PSIQUIATRICO', 'MENTAL'
                    ]
                    
                    # Se contém qualquer termo excluído, pular
                    if any(term in name_upper or term in fantasy_upper for term in excluded_maternity_terms):
                        logger.warning(f"🚫 Estabelecimento {facility.get('cnes_id')} ({name_raw}) filtrado: contém termo não relacionado a maternidade")
                        continue
                    
                    # Blacklist curada: hospitais sem maternidade (ex.: cirurgia plástica, oncologia)
                    cnes_id = str(facility.get('cnes_id') or '').strip()
                    blacklist_cnes = [
                        # Cirurgia plástica / outras especialidades
                        '3105571',   # Hospital Esplanada - cirurgia plástica (Av São João, SJ Campos)
                        '0009601',   # Hospital Pio XII - oncologia/cardiologia (R Paraguassu, SJ Campos)
                        # Saúde mental / dependência química
                        '2085569',   # Hospital Francisca Júlia CVV - saúde mental/dependência química (Estrada Dr Bezerra de Menezes, Torrão de Ouro, SJ Campos)
                        '0014001',   # Associação de Pesquisa e Tratamento Alcoolismo (Vila de Lourdes, PR)
                        '2078406',   # Hosp Independência - possível saúde mental (Jardim Pedro José Nu, SP)
                        '2270188',   # SEAP RJ Centro Trat Em Dependência Química Roberto Medeiros (Bangu, RJ)
                        '7092571',   # Hospital Independência - possível saúde mental (Jardim Carvalho, RS)
                        '7609566',   # Unidade de Dependência Química Vida (Santo Antônio do Descoberto, GO)
                        '0027707',   # Clínica Pinel - saúde mental/psiquiatria (Belo Horizonte, MG)
                        '0003085',   # Clínica de Repouso São Marcello - saúde mental (Aracaju, SE)
                        '0106518',   # Clínica Terapêutica Virtude - saúde mental
                        '0228494',   # Serenity Clínica de Desospitalização - saúde mental
                        '0235385',   # Clínica Terapêutica Sonho de Vida - saúde mental
                        # Clínicas específicas (não hospitais de maternidade)
                        '0002593',   # Clínica Santa Helena Suissa - clínica específica
                        '0016292',   # Clínica Dr Helio Rotenberg - clínica específica
                        '0007714',   # Clínica de Acident São Francisco - clínica de acidentes
                        '0014125',   # Center Clínicas - centro de clínicas
                        '0219622',   # Policlínica Municipal Geomarco Coelho - sem maternidade confirmada
                        # Hospitais temporários / específicos
                        '0262862',   # Hospital das Clínicas Covid 19 - hospital temporário COVID
                    ]
                    if cnes_id in blacklist_cnes:
                        logger.warning(f"🚫 Estabelecimento {cnes_id} ({name_raw}) filtrado: blacklist maternidade")
                        continue
                    _raw = (facility.get('city') or '') + ' ' + (facility.get('address') or '')
                    city_norm = ''.join(c for c in unicodedata.normalize('NFD', _raw.upper()) if unicodedata.category(c) != 'Mn')
                    blacklist_maternity = [
                        ('ESPLANADA', 'JOSE DOS CAMPOS'),
                        ('PIO XII', 'JOSE DOS CAMPOS'),
                        ('PIO 12', 'JOSE DOS CAMPOS'),
                    ]
                    if any(nb in (name_upper + ' ' + fantasy_upper) and cb in city_norm for nb, cb in blacklist_maternity):
                        logger.warning(f"🚫 Estabelecimento {facility.get('cnes_id')} ({name_raw}) filtrado: blacklist maternidade")
                        continue
                
                name = self._sanitize_name(name_raw)
                fantasy_name = self._sanitize_name(fantasy_name_raw)
                
                # Se ambos os nomes foram filtrados, pular este estabelecimento
                if not name and not fantasy_name:
                    logger.warning(f"🚫 Estabelecimento {facility.get('cnes_id')} filtrado por sanitização de nome")
                    continue
                
                # Melhorar nome de exibição (tratar nomes de profissionais)
                # Retorna tuple (título_principal, subtítulo)
                main_title, subtitle = self._improve_display_name(
                    name or '',
                    fantasy_name or '',
                    facility_type,
                    facility.get('city'),
                    facility.get('neighborhood')
                )
                display_name = main_title  # Para compatibilidade
                
                # Gerar google_search_term para frontend
                google_search_term = f"{display_name} Emergency" if is_emergency else f"{display_name}"
                
                formatted_result = {
                    'id': f"cnes_{facility['cnes_id']}",
                    'name': name or '',
                    'fantasy_name': fantasy_name or '',
                    'display_name': display_name,  # Nome formatado para exibição (título principal)
                    'display_subtitle': subtitle,  # Subtítulo (nome de pessoa/homenagem)
                    'type': facility_type,
                    'tags': tags,
                    'badges': badges,
                    'isVaccinationPoint': is_vaccination,  # Flag para pontos de vacinação
                    'isHospital': is_hospital,  # Flag para hospitais
                    'isSamuBase': is_samu,  # Flag para bases SAMU
                    'address': self._format_address(row_like),
                    'city': facility.get('city'),
                    'state': facility.get('state'),
                    'distance_km': facility.get('distance_km', 0),
                    'distance_type': 'linear',  # Indica que é distância em linha reta (Haversine)
                    'lat': facility.get('lat'),
                    'long': facility.get('long'),
                    'google_search_term': google_search_term,
                    'warning_message': warning,
                    'phone': facility.get('telefone'),  # Dados exatos do CSV (NU_TELEFONE)
                    'cnpj': facility.get('cnpj'),
                    'management': facility.get('management'),  # Gestão (Municipal/Estadual/Federal)
                    'natureza_juridica': facility.get('natureza_juridica'),  # Para validação
                    'priority_score': facility.get('priority_score', 0),  # Para debug
                    # FASE 3: Validação de dados
                    'data_validation': data_validation
                }
                
                formatted_results.append(formatted_result)
            
            return formatted_results, data_source_date, False
            
        except FileNotFoundError as e:
            logger.error(f"❌ Erro: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Erro ao buscar facilidades: {e}")
            raise
