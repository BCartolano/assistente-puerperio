#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Processar Validação de Existência e Localização
Purpose: Analisar resultados de busca web e identificar empresas fantasmas/localizações incorretas
"""

import os
import sys
import sqlite3
import re

# Configuração de encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'cnes_cache.db')

# Termos que indicam que hospital NÃO existe (empresa fantasma)
GHOST_COMPANY_INDICATORS = [
    'não encontrado', 'nao encontrado', 'não existe', 'nao existe',
    'encerrou atividades', 'fechou', 'desativado', 'extinto',
    'sem informações', 'sem site', 'não localizado', 'nao localizado'
]

# Termos que indicam que hospital EXISTE
EXISTENCE_CONFIRMATION = [
    'hospital', 'maternidade', 'unidade de saúde', 'clínica',
    'endereço', 'telefone', 'contato', 'atendimento',
    'especialidades', 'serviços', 'médicos'
]


def analyze_existence_result(search_result: str, hospital_name: str, hospital_address: str) -> dict:
    """
    Analisa resultado de busca para verificar existência do hospital
    
    Returns:
        {'exists': bool, 'confidence': float, 'is_ghost': bool, 'reason': str}
    """
    if not search_result:
        return {
            'exists': False,
            'confidence': 0.0,
            'is_ghost': True,
            'reason': 'Sem resultados de busca'
        }
    
    search_lower = search_result.lower()
    name_lower = hospital_name.lower()
    address_lower = (hospital_address or '').lower()
    
    # Verificar se resultado é sobre o hospital correto
    name_words = set(name_lower.split())
    result_words = set(search_lower.split())
    common_words = name_words.intersection(result_words)
    
    if len(name_words) > 0:
        match_ratio = len(common_words) / len(name_words)
        if match_ratio < 0.3:
            return {
                'exists': False,
                'confidence': 0.0,
                'is_ghost': True,
                'reason': f'Resultado não corresponde ao hospital (match: {match_ratio:.0%})'
            }
    
    # Verificar indicadores de empresa fantasma
    ghost_indicators = [ind for ind in GHOST_COMPANY_INDICATORS if ind in search_lower]
    if ghost_indicators:
        return {
            'exists': False,
            'confidence': 0.0,
            'is_ghost': True,
            'reason': f'Indicadores de empresa fantasma: {", ".join(ghost_indicators)}'
        }
    
    # Verificar confirmação de existência
    confirmation_indicators = [ind for ind in EXISTENCE_CONFIRMATION if ind in search_lower]
    
    # Verificar se endereço corresponde
    address_match = False
    if address_lower:
        # Extrair partes do endereço (rua, número)
        address_parts = [p.strip() for p in re.split(r'[,\s]+', address_lower) if p.strip() and len(p.strip()) > 2]
        if address_parts:
            # Verificar se pelo menos uma parte do endereço está no resultado
            address_match = any(part in search_lower for part in address_parts[:3])  # Primeiras 3 partes
    
    if confirmation_indicators:
        confidence = min(1.0, len(confirmation_indicators) / 3.0)
        if address_match:
            confidence = min(1.0, confidence + 0.3)
        
        return {
            'exists': True,
            'confidence': confidence,
            'is_ghost': False,
            'reason': f'Confirmado: {len(confirmation_indicators)} indicadores, endereço: {"corresponde" if address_match else "não verificado"}'
        }
    
    # Se não há indicadores claros, considerar incerto
    return {
        'exists': False,
        'confidence': 0.3,
        'is_ghost': True,
        'reason': 'Sem indicadores claros de existência'
    }


def analyze_location_result(search_result: str, hospital_name: str, expected_address: str, db_lat: float, db_long: float) -> dict:
    """
    Analisa resultado para verificar se localização está correta
    
    Returns:
        {'location_correct': bool, 'confidence': float, 'address_match': bool}
    """
    if not search_result:
        return {
            'location_correct': False,
            'confidence': 0.0,
            'address_match': False,
            'reason': 'Sem resultados de busca'
        }
    
    search_lower = search_result.lower()
    expected_lower = (expected_address or '').lower()
    
    # Extrair partes do endereço esperado
    if expected_lower:
        address_parts = [p.strip() for p in re.split(r'[,\s-]+', expected_lower) if p.strip() and len(p.strip()) > 2]
    else:
        address_parts = []
    
    # Verificar correspondência de endereço
    address_match = False
    matched_parts = []
    
    if address_parts:
        for part in address_parts[:5]:  # Primeiras 5 partes
            if part in search_lower:
                matched_parts.append(part)
                address_match = True
    
    # Calcular confiança baseada em correspondência
    if address_match:
        match_ratio = len(matched_parts) / min(len(address_parts), 5)
        confidence = min(1.0, match_ratio)
        
        return {
            'location_correct': True,
            'confidence': confidence,
            'address_match': True,
            'matched_parts': matched_parts,
            'reason': f'Endereço corresponde: {len(matched_parts)}/{min(len(address_parts), 5)} partes'
        }
    
    return {
        'location_correct': False,
        'confidence': 0.0,
        'address_match': False,
        'reason': 'Endereço não corresponde ao resultado da busca'
    }


def process_batch_1_validation():
    """Processa validação do lote 1 com resultados reais da busca web"""
    print("="*70)
    print("PROCESSAMENTO DE VALIDAÇÃO - LOTE 1")
    print("="*70)
    print()
    
    # Resultados da busca web para os primeiros 5 hospitais
    validation_results = {
        '0000027': {  # Casa De Saude Santa Helena
            'existence': '''Casa de Saude Santa Helena localizada em Avenida Presidente Getulio Vargas, 428, Centro, Cabo de Santo Agostinho, PE. 
            Telefone: (81) 3521-0975. Especialidades: ginecologia e obstetrícia, pediatria, ortopedia, neurologia, cardiologia.''',
            'location': '''Avenida Presidente Getulio Vargas, 428, Centro, Cabo de Santo Agostinho, PE 54505-560. 
            Waze mostra localização no endereço correto.'''
        },
        '0000035': {  # Hospital Mendo Sampaio
            'existence': '''Hospital Mendo Sampaio localizado em BR 101 Sul KM 34, Charneca, Cabo de Santo Agostinho, PE. 
            Telefones: (81) 3524-9181 / 3524-9182. Serviços: urgência, internação, cirurgia geral, exames diagnósticos.''',
            'location': '''BR 101 Sul KM 34, Charneca, Cabo de Santo Agostinho. Endereço corresponde (KM 34 vs KM 33 no banco - pequena diferença).'''
        },
        '0000094': {  # Maternidade Padre Geraldo Leite Bastos
            'existence': '''Maternidade Padre Geraldo Leite Bastos localizada em BR 101 KM 23 - Ponte dos Carvalhos, Cabo de Santo Agostinho, PE. 
            Telefones: (81) 3521-6784 / 3521-6243. Serviços: partos normais, cesáreas, urgências obstétricas.''',
            'location': '''BR 101 KM 23 - Ponte dos Carvalhos. Endereço corresponde exatamente.'''
        },
        '0000183': {  # Hospital Samaritano
            'existence': '''Hospital Samaritano localizado em Rua Severino Bezerra Marques, 40 - Centro, Cabo de Santo Agostinho, PE 54510-460. 
            Telefone: (81) 3521-0109. Hospital dedicado a servir clientes com atenção, eficiência e respeito.''',
            'location': '''Rua Severino Bezerra Marques, 40 - Centro, Cabo de Santo Agostinho, PE 54510-460. Endereço corresponde exatamente.'''
        },
        '0000221': {  # Hospital Sao Sebastiao
            'existence': '''Hospital São Sebastião localizado em Avenida Presidente Getúlio Vargas, 864, Centro, Cabo de Santo Agostinho, PE 54505-560. 
            Telefone: (81) 3521-4150. Casa de Saúde e Maternidade. Especialidades: ginecologia/obstetrícia, pediatria, cardiologia.''',
            'location': '''Avenida Presidente Getúlio Vargas, 864, Centro, Cabo de Santo Agostinho, PE 54505-560. Endereço corresponde exatamente.'''
        }
    }
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    confirmed = []
    ghost_companies = []
    location_issues = []
    
    for cnes_id, results in validation_results.items():
        # Buscar dados do hospital
        cursor.execute("""
            SELECT fantasy_name, name, address, lat, long
            FROM hospitals_cache
            WHERE cnes_id = ?
        """, (cnes_id,))
        row = cursor.fetchone()
        
        if not row:
            continue
        
        name = row['fantasy_name'] or row['name'] or 'Sem nome'
        address = row['address'] or ''
        
        # Analisar existência
        existence_analysis = analyze_existence_result(
            results.get('existence', ''),
            name,
            address
        )
        
        # Analisar localização
        location_analysis = analyze_location_result(
            results.get('location', ''),
            name,
            address,
            row['lat'],
            row['long']
        )
        
        print(f"\n{name} (CNES: {cnes_id})")
        print(f"   Existência: {'✅ EXISTE' if existence_analysis['exists'] else '❌ NÃO EXISTE'}")
        print(f"   Confiança: {existence_analysis['confidence']:.0%}")
        print(f"   Localização: {'✅ CORRETA' if location_analysis['location_correct'] else '⚠️ VERIFICAR'}")
        print(f"   Endereço: {'✅ CORRESPONDE' if location_analysis['address_match'] else '❌ NÃO CORRESPONDE'}")
        
        if existence_analysis['is_ghost']:
            ghost_companies.append({
                'cnes_id': cnes_id,
                'name': name,
                'reason': existence_analysis['reason']
            })
        elif existence_analysis['exists']:
            confirmed.append({
                'cnes_id': cnes_id,
                'name': name,
                'location_correct': location_analysis['location_correct'],
                'address_match': location_analysis['address_match']
            })
            
            if not location_analysis['location_correct']:
                location_issues.append({
                    'cnes_id': cnes_id,
                    'name': name,
                    'reason': location_analysis['reason']
                })
    
    # Remover empresas fantasmas
    if ghost_companies:
        print("\n" + "="*70)
        print("REMOVENDO EMPRESAS FANTASMAS")
        print("="*70)
        
        cnes_ids = [h['cnes_id'] for h in ghost_companies]
        placeholders = ','.join(['?' for _ in cnes_ids])
        cursor.execute(f"""
            UPDATE hospitals_cache
            SET has_maternity = 0
            WHERE cnes_id IN ({placeholders})
        """, cnes_ids)
        removed = cursor.rowcount
        print(f"[OK] {removed} empresas fantasmas removidas")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*70)
    print("RESUMO")
    print("="*70)
    print(f"✅ Confirmados: {len(confirmed)}")
    print(f"❌ Empresas Fantasmas: {len(ghost_companies)}")
    print(f"⚠️ Problemas de Localização: {len(location_issues)}")
    
    return {
        'confirmed': confirmed,
        'ghost_companies': ghost_companies,
        'location_issues': location_issues
    }


if __name__ == "__main__":
    results = process_batch_1_validation()
