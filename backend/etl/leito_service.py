#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de Validação de Leitos
Purpose: Validar se hospital tem leitos de obstetrícia usando tbLeito
"""

import os
import csv
from typing import Dict, Set, Optional

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Caminhos possíveis para tbLeito
LEITO_PATHS = [
    os.path.join(BASE_DIR, 'data', 'tbLeito202512'),
    os.path.join(BASE_DIR, 'data', 'tbLeito202512.csv'),
]

# Cache de tipos de leitos de obstetrícia
_OBSTETR_LEITO_CODES: Optional[Set[str]] = None
_OBSTETR_LEITO_DESCRIPTIONS: Optional[Set[str]] = None


def load_leito_reference() -> tuple[Set[str], Set[str]]:
    """
    Carrega tabela de referência tbLeito e identifica códigos de leitos de obstetrícia
    
    Returns:
        Tuple de (códigos de leitos de obstetrícia, descrições de leitos de obstetrícia)
    """
    global _OBSTETR_LEITO_CODES, _OBSTETR_LEITO_DESCRIPTIONS
    
    if _OBSTETR_LEITO_CODES is not None:
        return _OBSTETR_LEITO_CODES, _OBSTETR_LEITO_DESCRIPTIONS
    
    obstetr_codes = set()
    obstetr_descriptions = set()
    
    # Encontrar arquivo
    leito_path = None
    for path in LEITO_PATHS:
        if os.path.exists(path):
            leito_path = path
            break
    
    if not leito_path:
        # Se arquivo não encontrado, usar valores padrão conhecidos
        obstetr_codes.add('02')  # TP_LEITO=02 conforme especificação do usuário
        obstetr_descriptions.add('OBSTETRICIA')
        obstetr_descriptions.add('OBSTETRÍCIA')
        obstetr_descriptions.add('OBSTETRICIA CIRURGICA')
        return obstetr_codes, obstetr_descriptions
    
    try:
        with open(leito_path, 'r', encoding='ISO-8859-1', errors='replace') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            for row in reader:
                tp_leito = row.get('TP_LEITO', '').strip()
                ds_leito = row.get('DS_LEITO', '').strip().upper()
                co_leito = row.get('CO_LEITO', '').strip()
                
                # Verificar se é leito de obstetrícia
                # TP_LEITO=02 conforme especificação do usuário
                if tp_leito == '02':
                    obstetr_codes.add(co_leito)
                    obstetr_codes.add(tp_leito)
                    if ds_leito:
                        obstetr_descriptions.add(ds_leito)
                
                # Verificar descrição contém "OBSTETR"
                if 'OBSTETR' in ds_leito:
                    obstetr_codes.add(co_leito)
                    if tp_leito:
                        obstetr_codes.add(tp_leito)
                    obstetr_descriptions.add(ds_leito)
    
    except Exception as e:
        # Em caso de erro, usar valores padrão
        print(f"⚠️  Erro ao carregar tbLeito: {e}")
        obstetr_codes.add('02')
        obstetr_descriptions.add('OBSTETRICIA')
        obstetr_descriptions.add('OBSTETRÍCIA')
    
    _OBSTETR_LEITO_CODES = obstetr_codes
    _OBSTETR_LEITO_DESCRIPTIONS = obstetr_descriptions
    
    return obstetr_codes, obstetr_descriptions


def has_obstetr_leito(tp_leito: Optional[str] = None, 
                      ds_leito: Optional[str] = None,
                      co_leito: Optional[str] = None) -> bool:
    """
    Verifica se o tipo/descrição de leito indica obstetrícia
    
    Args:
        tp_leito: Tipo de leito (TP_LEITO)
        ds_leito: Descrição do leito (DS_LEITO)
        co_leito: Código do leito (CO_LEITO)
    
    Returns:
        True se for leito de obstetrícia
    """
    obstetr_codes, obstetr_descriptions = load_leito_reference()
    
    # Verificar código
    if co_leito and co_leito.strip() in obstetr_codes:
        return True
    
    if tp_leito and tp_leito.strip() in obstetr_codes:
        return True
    
    # Verificar descrição
    if ds_leito:
        ds_upper = ds_leito.strip().upper()
        if any(desc in ds_upper for desc in obstetr_descriptions):
            return True
        if 'OBSTETR' in ds_upper:
            return True
    
    return False


def has_obstetr_service(co_servico: Optional[str] = None) -> bool:
    """
    Verifica se o código de serviço indica obstetrícia
    
    Args:
        co_servico: Código de serviço (CO_SERVICO)
        Valor esperado: "141" = Atenção à Saúde Reprodutiva/Obstetrícia
    
    Returns:
        True se for serviço de obstetrícia
    """
    if not co_servico:
        return False
    
    # CO_SERVICO=141 conforme especificação do usuário
    servicos = [s.strip() for s in str(co_servico).split(',')]
    return '141' in servicos


def validate_maternity_with_leitos(row: Dict[str, str]) -> Optional[bool]:
    """
    Valida se hospital tem maternidade usando dados de leitos (quando disponíveis)
    
    Args:
        row: Linha do CSV com dados do estabelecimento
    
    Returns:
        True se confirmado que tem maternidade
        False se confirmado que NÃO tem maternidade
        None se não há dados suficientes para validar
    """
    # Por enquanto, retorna None pois não temos dados de leitos no tbEstabelecimento
    # Esta função pode ser usada quando integrarmos dados de leitos de outro arquivo
    return None
