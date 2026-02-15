#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise Profunda de Hospitais de Maternidade
Purpose: Análise sistemática completa para encontrar TODOS os hospitais inválidos
Modo: Autônomo - análise em lote de todos os hospitais
"""

import os
import sys
import sqlite3
import json
import re

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'cnes_cache.db')

# Padrões que indicam NÃO maternidade (mais específicos)
NON_MATERNITY_PATTERNS = [
    # Saúde Mental (já coberto, mas garantir)
    r'PSIQUIATR[IA|ICO]', r'SAUDE MENTAL', r'SAÚDE MENTAL', r'CVV',
    r'DEPENDENCIA', r'DEPENDÊNCIA', r'QUIMICA', r'QUÍMICA', r'ADICCAO', r'ADICÇÃO',
    r'ALCOOLISMO', r'DROGADICCAO', r'DROGADIÇÃO',
    # Ortopedia
    r'ORTOPED[IA|ICO|ISTA]', r'TRAUMATOLOGIA', r'FRATURA', r'OSSO', r'OSSOS',
    r'COLUNA', r'JOELHO', r'QUADRIL', r'OMBRO',
    # Oftalmologia
    r'VIS[ÃO|AO]', r'VISUAL', r'OFTA', r'OFTALMO', r'OLHO', r'OLHOS',
    r'RETINA', r'CÓRNEA', r'CORNEA', r'CATARATA', r'GLAUCOMA',
    # Cardiologia
    r'CARDIOLOG[IA|ICO]', r'CARDIACO', r'CORAÇÃO', r'CORACAO',
    # Oncologia
    r'ONCOLOG[IA|ICO]', r'CANCER', r'CÂNCER', r'INSTITUTO DO CANCER',
    # Pediatria (hospitais infantis)
    r'HOSPITAL INFANTIL', r'INFANTIL$', r'PEDIATR[IA|ICO|ICA]',
    r'CRIANCA', r'CRIANÇA', r'BABY', r'BEBE', r'BEBÊ',
    # Cirurgia plástica
    r'CIRURGIA PLASTICA', r'CIRURGIA PLÁSTICA', r'PLASTICA', r'PLÁSTICA',
    r'ESTETICA', r'ESTÉTICA', r'CIRURGIA ESTETICA',
    # Clínicas específicas (não "Hospital das Clínicas")
    r'^CLINICA ', r'^CLÍNICA ', r'CLINICA DE ', r'CLÍNICA DE ',
    r'CLINICA DR ', r'CLÍNICA DR ', r'CLINICA TERAPEUTICA',
    r'CLÍNICA TERAPÊUTICA', r'CLINICA DE REPOUSO', r'CLÍNICA DE REPOUSO',
    r'CLINICA DE ACIDENT', r'CLINICA DE DESOSPITALIZACAO',
    # Outros
    r'REABILITACAO', r'FISIOTERAPIA', r'TERAPIA OCUPACIONAL',
    r'OTORRINOLARINGOLOG', r'OTORRINO',
    # Temporários / específicos
    r'COVID 19', r'COVID-19', r'PANDEMIA',
]

# Padrões que indicam SIM maternidade
MATERNITY_PATTERNS = [
    r'MATERNIDADE', r'MATERNO', r'OBSTETRIC[IA|ICO]', r'OBSTETR[ÍI]C[IA|ICO]',
    r'GINECOLOG[IA|ICO]', r'GINECOLOGISTA', r'NEONATAL', r'NEONATOLOGIA',
    r'PARTO', r'NASCIMENTO', r'PR[ÉE]-NATAL', r'POS-PARTO', r'PÓS-PARTO',
]

def matches_pattern(text: str, patterns: list) -> bool:
    """Verifica se texto corresponde a algum padrão"""
    if not text:
        return False
    text_upper = text.upper()
    for pattern in patterns:
        if re.search(pattern, text_upper):
            return True
    return False

def is_hospital_das_clinicas(name: str) -> bool:
    """Verifica se é um "Hospital das Clínicas" (hospital geral, pode ter maternidade)"""
    name_upper = (name or '').upper()
    return 'HOSPITAL' in name_upper and ('DAS CLINICAS' in name_upper or 'DE CLINICAS' in name_upper)

def analyze_hospital(hospital: dict) -> dict:
    """Analisa um hospital e retorna resultado"""
    name = hospital.get('name', '')
    fantasy_name = hospital.get('fantasy_name', '')
    full_name = f"{name} {fantasy_name}".strip()
    cnes_id = hospital.get('cnes_id', '')
    
    result = {
        'cnes_id': cnes_id,
        'name': fantasy_name or name,
        'address': hospital.get('address', ''),
        'city': hospital.get('city', ''),
        'state': hospital.get('state', ''),
        'status': 'unknown',
        'reason': ''
    }
    
    # Se é "Hospital das Clínicas", assumir válido (hospital geral)
    if is_hospital_das_clinicas(full_name):
        result['status'] = 'valid'
        result['reason'] = 'Hospital das Clínicas (hospital geral)'
        return result
    
    # Verificar padrões de NÃO maternidade
    if matches_pattern(full_name, NON_MATERNITY_PATTERNS):
        result['status'] = 'suspicious'
        result['reason'] = 'Contém padrão não-maternidade'
        return result
    
    # Verificar padrões de SIM maternidade
    if matches_pattern(full_name, MATERNITY_PATTERNS):
        result['status'] = 'valid'
        result['reason'] = 'Contém padrão maternidade'
        return result
    
    # Se não tem padrões específicos, marcar como requer validação
    result['status'] = 'needs_validation'
    result['reason'] = 'Sem padrões específicos - requer validação'
    return result

def main():
    print("=" * 80)
    print("ANÁLISE PROFUNDA DE HOSPITAIS DE MATERNIDADE")
    print("=" * 80)
    print()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Buscar TODOS os hospitais com has_maternity=1
    cur.execute("""
        SELECT cnes_id, name, fantasy_name, address, city, state, has_maternity, tipo_unidade
        FROM hospitals_cache
        WHERE has_maternity = 1
        AND tipo_unidade IN ('05', '07', 'HOSPITAL')
        ORDER BY cnes_id
    """)
    
    hospitals = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    print(f"📊 Analisando {len(hospitals)} hospitais marcados como tendo maternidade...\n")
    
    results = {
        'valid': [],
        'suspicious': [],
        'needs_validation': []
    }
    
    for i, hospital in enumerate(hospitals, 1):
        analysis = analyze_hospital(hospital)
        results[analysis['status']].append(analysis)
        
        if analysis['status'] == 'suspicious':
            print(f"🚫 [{i}/{len(hospitals)}] SUSPEITO: {analysis['name']}")
            print(f"    CNES: {analysis['cnes_id']} | {analysis['reason']}")
    
    print()
    print("=" * 80)
    print("RESUMO DA ANÁLISE")
    print("=" * 80)
    print(f"✅ Hospitais válidos: {len(results['valid'])}")
    print(f"🚫 Hospitais suspeitos: {len(results['suspicious'])}")
    print(f"⚠️  Requerem validação: {len(results['needs_validation'])}")
    print()
    
    # Salvar resultados
    output_file = os.path.join(BASE_DIR, 'backend', 'scripts', 'deep_analysis_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Resultados salvos em: {output_file}")
    print()
    print("PRÓXIMOS PASSOS:")
    print(f"1. Validar {len(results['suspicious'])} hospitais suspeitos")
    print(f"2. Validar {len(results['needs_validation'])} hospitais sem padrões claros")
    print("3. Atualizar blacklist e corrigir banco")

if __name__ == '__main__':
    main()
