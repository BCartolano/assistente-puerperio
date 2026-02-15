#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validação Web - Lote 1
Purpose: Validar primeiro lote de hospitais via busca web
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'backend', 'scripts'))

from process_web_validation import analyze_web_result, update_database_from_validation, process_validation_results

# Resultados da busca web para os primeiros 5 hospitais
BATCH_1_RESULTS = {
    'hospitals': [
        {
            'cnes_id': '0000027',
            'name': 'Casa De Saude Santa Helena',
            'search_results': {
                'maternidade': '''Maternidade Santa Helena encerra atividades em Florianópolis. 
                Hospital e Maternidade Santa Helena em São Bernardo do Campo oferece serviços de maternidade.
                Hospital e Maternidade Santa Helena em Aracaju opera 24 horas com maternidade.''',
                'obstetricia': '''Hospital e Maternidade Santa Helena oferece serviços de obstetrícia.
                Maternidade com atendimento obstétrico completo.''',
                'parto': '''Hospital e Maternidade Santa Helena oferece partos normais e cesáreas.
                Sala de parto equipada.'''
            }
        },
        {
            'cnes_id': '0000035',
            'name': 'Hospital Mendo Sampaio',
            'search_results': {
                'maternidade': '''Hospital Mendo Sampaio em Cabo de Santo Agostinho oferece serviços de maternidade.
                Partos normais e cesarianos. Urgências obstétricas.'''
            }
        },
        {
            'cnes_id': '0000094',
            'name': 'Maternidade Padre Geraldo Leite Bastos',
            'search_results': {
                'maternidade': '''Maternidade Padre Geraldo Leite Bastos oferece partos normais e cesáreas.
                Urgências obstétricas. Exames laboratoriais.'''
            }
        },
        {
            'cnes_id': '0000183',
            'name': 'Hospital Samaritano',
            'search_results': {
                'maternidade': '''Hospital Samaritano possui Centro de Excelência Materno Fetal Infantil.
                Sala PPPs (pré-parto, parto e pós-parto). UTI Neonatal. Maternidade com enfermaria.'''
            }
        },
        {
            'cnes_id': '0000221',
            'name': 'Hospital Sao Sebastiao',
            'search_results': {
                'maternidade': '''Casa de Parto de São Sebastião oferece atendimento em obstetrícia.
                Partos normais de baixo risco. Atendimento durante pré-parto, parto e puerpério.'''
            }
        }
    ]
}

def validate_batch_1():
    """Valida primeiro lote de hospitais"""
    print("="*70)
    print("VALIDAÇÃO WEB - LOTE 1 (Primeiros 5 Hospitais)")
    print("="*70)
    print()
    
    from process_web_validation import process_validation_results
    
    # Processar resultados
    results = process_validation_results(BATCH_1_RESULTS)
    
    print(f"[RESULTADOS]")
    print(f"   Confirmados: {len(results['confirmed'])}")
    print(f"   Não Confirmados: {len(results['not_confirmed'])}")
    print(f"   Incertos: {len(results['uncertain'])}")
    print()
    
    if results['confirmed']:
        print("[CONFIRMADOS]")
        for hosp in results['confirmed']:
            print(f"   ✅ {hosp['name']} (CNES: {hosp['cnes_id']})")
            print(f"      Confiança: {hosp['confidence']:.0%}")
            print(f"      Evidências: {', '.join(set(hosp['evidence']))}")
    
    if results['not_confirmed']:
        print("\n[NÃO CONFIRMADOS]")
        for hosp in results['not_confirmed']:
            print(f"   ❌ {hosp['name']} (CNES: {hosp['cnes_id']})")
            print(f"      Razão: {hosp['reason']}")
    
    if results['uncertain']:
        print("\n[INCERTOS - Requerem mais investigação]")
        for hosp in results['uncertain']:
            print(f"   ⚠️  {hosp['name']} (CNES: {hosp['cnes_id']})")
            print(f"      Razão: {hosp['reason']}")
    
    # Atualizar banco de dados
    if results['not_confirmed']:
        print("\n[ATUALIZANDO BANCO DE DADOS]")
        update_database_from_validation(results)
    
    return results

if __name__ == "__main__":
    validate_batch_1()
