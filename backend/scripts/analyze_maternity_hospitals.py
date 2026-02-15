#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise Sistemática de Hospitais de Maternidade
Purpose: Identificar hospitais que não existem ou não têm maternidade/obstetría
Modo: Autônomo (YOLO) - análise em lote
"""

import os
import sys
import sqlite3
import json
from typing import Dict, List, Tuple

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'cnes_cache.db')

# Termos que indicam NÃO maternidade (expansão completa)
NON_MATERNITY_KEYWORDS = [
    # Saúde Mental
    'PSIQUIATRIA', 'PSIQUIATRICO', 'MENTAL', 'SAUDE MENTAL', 'SAÚDE MENTAL',
    'CVV', 'VALORIZACAO', 'VALORIZAÇÃO', 'DEPENDENCIA', 'DEPENDÊNCIA',
    'QUIMICA', 'QUÍMICA', 'ADICCAO', 'ADICÇÃO', 'ALCOOLISMO', 'DROGADICCAO',
    # Ortopedia
    'ORTOPEDIA', 'ORTOPEDICO', 'ORTOPEDISTA', 'TRAUMATOLOGIA', 'FRATURA',
    'OSSO', 'OSSOS', 'COLUNA', 'JOELHO', 'QUADRIL', 'OMBRO',
    # Oftalmologia
    'VISÃO', 'VISAO', 'VISUAL', 'OFTA', 'OFTALMO', 'OLHO', 'OLHOS',
    'RETINA', 'CÓRNEA', 'CORNEA', 'CATARATA', 'GLAUCOMA',
    # Cardiologia
    'CARDIOLOGIA', 'CARDIACO', 'CORAÇÃO', 'CORACAO', 'CIRURGIA CARDIACA',
    # Oncologia
    'ONCOLOGIA', 'ONCOLOGICO', 'CANCER', 'CÂNCER', 'INSTITUTO DO CANCER',
    # Pediatria (hospitais infantis, não maternidade)
    'INFANTIL', 'PEDIATRIA', 'PEDIATRICO', 'PEDIATRICA', 'CRIANCA', 'CRIANÇA',
    'BABY', 'BEBE', 'BEBÊ', 'HOSPITAL INFANTIL',
    # Cirurgia plástica/estética
    'CIRURGIA PLASTICA', 'CIRURGIA PLÁSTICA', 'PLASTICA', 'PLÁSTICA',
    'ESTETICA', 'ESTÉTICA', 'CIRURGIA ESTETICA',
    # Outras especialidades
    'REABILITACAO', 'FISIOTERAPIA', 'TERAPIA OCUPACIONAL',
    'OTORRINOLARINGOLOG', 'OTORRINO', 'PSICOLOGIA',
    # Instituições não-hospitalares (mas NÃO excluir "Hospital das Clínicas" que são hospitais gerais)
    'GRUPAMENTO', 'CENTRO OCUPACIONAL', 'CENTRO DE TREINAMENTO',
    'DIVISÃO', 'DIVISAO',
    # Clínicas específicas (mas não "Hospital das Clínicas")
    'CLINICA DE', 'CLÍNICA DE', 'CLINICA DR', 'CLÍNICA DR', 'CLINICA TERAPEUTICA',
    'CLÍNICA TERAPÊUTICA', 'CLINICA DE REPOUSO', 'CLÍNICA DE REPOUSO',
    # UPA (já filtrado, mas garantir)
    'UPA', 'UNIDADE DE PRONTO ATENDIMENTO',
]

# Termos que indicam SIM maternidade
MATERNITY_KEYWORDS = [
    'MATERNIDADE', 'MATERNO', 'OBSTETRICIA', 'OBSTETRICO', 'OBSTETRÍCIA',
    'GINECOLOGIA', 'GINECOLOGICO', 'GINECOLÓGICO', 'GINECOLOGISTA',
    'NEONATOLOGIA', 'NEONATAL', 'PARTO', 'NASCIMENTO',
    'PRÉ-NATAL', 'PRE-NATAL', 'POS-PARTO', 'PÓS-PARTO',
    'CENTRO OBSTETRICO', 'CENTRO OBSTETRÍCICO',
]

def analyze_hospital_name(name: str, fantasy_name: str) -> Tuple[bool, str]:
    """
    Analisa nome do hospital e retorna se parece ter maternidade
    Returns: (has_maternity_likely, reason)
    """
    name_upper = (name or '').upper()
    fantasy_upper = (fantasy_name or '').upper()
    full_name = f"{name_upper} {fantasy_upper}".strip()
    
    # Verificar termos de NÃO maternidade
    for keyword in NON_MATERNITY_KEYWORDS:
        if keyword in full_name:
            return False, f"Contém termo não-maternidade: {keyword}"
    
    # Verificar termos de SIM maternidade
    for keyword in MATERNITY_KEYWORDS:
        if keyword in full_name:
            return True, f"Contém termo maternidade: {keyword}"
    
    # Se não tem termos específicos, assumir que pode ter (será validado depois)
    return True, "Sem termos específicos - requer validação"

def get_hospitals_to_validate(limit: int = 100) -> List[Dict]:
    """Busca hospitais marcados como tendo maternidade para validação"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("""
        SELECT cnes_id, name, fantasy_name, address, city, state, has_maternity, tipo_unidade
        FROM hospitals_cache
        WHERE has_maternity = 1
        AND tipo_unidade IN ('05', '07', 'HOSPITAL')
        ORDER BY cnes_id
        LIMIT ?
    """, (limit,))
    
    rows = cur.fetchall()
    hospitals = [dict(row) for row in rows]
    conn.close()
    
    return hospitals

def analyze_all_hospitals():
    """Análise sistemática de todos os hospitais com maternidade"""
    print("=" * 80)
    print("ANÁLISE SISTEMÁTICA DE HOSPITAIS DE MATERNIDADE")
    print("=" * 80)
    print()
    
    hospitals = get_hospitals_to_validate(limit=500)  # Analisar até 500
    print(f"📊 Analisando {len(hospitals)} hospitais marcados como tendo maternidade...\n")
    
    suspicious = []  # Hospitais suspeitos (não têm maternidade)
    valid = []       # Hospitais válidos
    
    for i, hospital in enumerate(hospitals, 1):
        cnes_id = hospital['cnes_id']
        name = hospital.get('name', '')
        fantasy_name = hospital.get('fantasy_name', '')
        address = hospital.get('address', '')
        city = hospital.get('city', '')
        state = hospital.get('state', '')
        
        # Análise do nome
        has_maternity_likely, reason = analyze_hospital_name(name, fantasy_name)
        
        if not has_maternity_likely:
            suspicious.append({
                'cnes_id': cnes_id,
                'name': fantasy_name or name,
                'address': address,
                'city': city,
                'state': state,
                'reason': reason
            })
            print(f"🚫 [{i}/{len(hospitals)}] SUSPEITO: {fantasy_name or name}")
            print(f"    CNES: {cnes_id} | Motivo: {reason}")
            if address:
                print(f"    Endereço: {address}")
            print()
        else:
            valid.append(cnes_id)
    
    print("=" * 80)
    print(f"RESUMO DA ANÁLISE")
    print("=" * 80)
    print(f"✅ Hospitais válidos: {len(valid)}")
    print(f"🚫 Hospitais suspeitos: {len(suspicious)}")
    print()
    
    if suspicious:
        print("HOSPITAIS SUSPEITOS (requerem validação manual ou web search):")
        print()
        for h in suspicious:
            print(f"CNES: {h['cnes_id']}")
            print(f"  Nome: {h['name']}")
            print(f"  Endereço: {h['address']}")
            print(f"  Cidade: {h['city']}, Estado: {h['state']}")
            print(f"  Motivo: {h['reason']}")
            print()
    
    # Salvar resultados em JSON para análise posterior
    results_file = os.path.join(BASE_DIR, 'backend', 'scripts', 'suspicious_hospitals.json')
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_analyzed': len(hospitals),
            'valid': len(valid),
            'suspicious': suspicious
        }, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Resultados salvos em: {results_file}")
    print()
    print("PRÓXIMOS PASSOS:")
    print("1. Validar hospitais suspeitos via web search")
    print("2. Criar blacklist de CNES inválidos")
    print("3. Executar script de correção no banco")
    
    return suspicious

if __name__ == '__main__':
    analyze_all_hospitals()
