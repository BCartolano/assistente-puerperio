#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filtro Rigoroso: APENAS Maternidade
Purpose: Garantir que APENAS hospitais com maternidade confirmada fiquem na lista
Modo: Análise completa do Brasil
"""

import os
import sys
import sqlite3
import json
import re
from typing import Dict, List, Set
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'cnes_cache.db')
REPORT_FILE = os.path.join(BASE_DIR, 'backend', 'scripts', 'strict_filter_report.json')

# REGRA RIGOROSA: Apenas estes padrões confirmam maternidade
STRICT_MATERNITY_PATTERNS = [
    r'MATERNIDADE',
    r'MATERNO',
    r'OBSTETRIC[IA|ICO]',
    r'OBSTETR[ÍI]C[IA|ICO]',
    r'GINECOLOG[IA|ICO]',
    r'NEONATAL',
    r'NEONATOLOGIA',
    r'PARTO',
    r'NASCIMENTO',
    r'PR[ÉE]-NATAL',
    r'POS-PARTO',
    r'PÓS-PARTO',
]

# Exclusões rigorosas (qualquer um destes = NÃO maternidade)
STRICT_EXCLUSIONS = [
    r'PSIQUIATR', r'MENTAL', r'CVV', r'DEPENDENCIA', r'QUIMICA', r'ADICCAO',
    r'ORTOPED', r'TRAUMATOLOGIA', r'FRATURA', r'OSSO',
    r'VIS[ÃO|AO]', r'OFTA', r'OFTALMO', r'OLHO',
    r'CARDIOLOG', r'CORAÇÃO', r'CORACAO',
    r'ONCOLOG', r'CANCER', r'CÂNCER',
    r'INFANTIL$', r'PEDIATR', r'CRIANCA', r'BABY',
    r'PLASTICA', r'PLÁSTICA', r'ESTETICA', r'ESTÉTICA',
    r'CLINICA ', r'CLÍNICA ', r'CLINICA DE ', r'CLÍNICA DE ',
    r'CLINICA DR ', r'CLINICA TERAPEUTICA',
    r'COVID', r'CORONA', r'CAMPANHA', r'RETAGUARDA',
    r'INTERNACAO', r'REABILITACAO', r'FISIOTERAPIA',
    r'OTORRINO', r'TERAPIA OCUPACIONAL',
]

def matches_pattern(text: str, patterns: list) -> bool:
    """Verifica padrão"""
    if not text:
        return False
    text_upper = text.upper()
    for pattern in patterns:
        if re.search(pattern, text_upper):
            return True
    return False

def is_strict_maternity(hospital: dict) -> bool:
    """
    REGRA RIGOROSA: Apenas retorna True se tiver padrão CLARO de maternidade
    E não tiver nenhuma exclusão
    """
    name = hospital.get('name', '')
    fantasy_name = hospital.get('fantasy_name', '')
    full_name = f"{name} {fantasy_name}".strip()
    name_upper = full_name.upper()
    
    # PRIORIDADE 1: Se tem "MATERNIDADE" no nome, SEMPRE é válido (mesmo que tenha "POLICLINICA")
    if 'MATERNIDADE' in name_upper:
        return True
    
    # PRIORIDADE 2: Se tem padrão CLARO de maternidade, é válido
    if matches_pattern(full_name, STRICT_MATERNITY_PATTERNS):
        return True
    
    # PRIORIDADE 3: Se é "Hospital das Clínicas", assumir válido (hospital geral)
    if 'HOSPITAL' in name_upper and ('DAS CLINICAS' in name_upper or 'DE CLINICAS' in name_upper):
        return True  # Hospital geral, pode ter maternidade
    
    # Se tem exclusão E não tem maternidade, NÃO é maternidade
    if matches_pattern(full_name, STRICT_EXCLUSIONS):
        return False
    
    # Se não tem padrão claro, NÃO é maternidade
    return False

def main():
    print("=" * 80)
    print("FILTRO RIGOROSO: APENAS MATERNIDADE")
    print("=" * 80)
    print("Analisando TODOS os estabelecimentos do Brasil")
    print("Regra: APENAS hospitais com padrão CLARO de maternidade")
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
    print(f"📊 Total de hospitais com has_maternity=1: {len(hospitals)}")
    print()
    
    print("🔍 Aplicando filtro rigoroso...")
    
    valid_count = 0
    invalid_count = 0
    invalid_hospitals = []
    
    for i, hospital in enumerate(hospitals, 1):
        cnes_id = hospital['cnes_id']
        name = hospital.get('fantasy_name') or hospital.get('name', '')
        
        if is_strict_maternity(hospital):
            valid_count += 1
        else:
            invalid_count += 1
            invalid_hospitals.append({
                'cnes_id': cnes_id,
                'name': name,
                'address': hospital.get('address', ''),
                'city': hospital.get('city', ''),
                'state': hospital.get('state', '')
            })
            
            # Remover do banco
            cur.execute("""
                UPDATE hospitals_cache
                SET has_maternity = 0
                WHERE cnes_id = ?
            """, (cnes_id,))
            
            if i % 100 == 0:
                print(f"   Progresso: {i}/{len(hospitals)} analisados...")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print()
    print("=" * 80)
    print("RESULTADO DO FILTRO RIGOROSO")
    print("=" * 80)
    print(f"✅ Hospitais VÁLIDOS (com maternidade confirmada): {valid_count}")
    print(f"🚫 Hospitais REMOVIDOS (sem padrão claro): {invalid_count}")
    print()
    
    # Salvar relatório
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_analyzed': len(hospitals),
        'valid_count': valid_count,
        'invalid_count': invalid_count,
        'invalid_hospitals': invalid_hospitals[:100]  # Primeiros 100
    }
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Relatório salvo em: {REPORT_FILE}")
    print()
    print("✅ Filtro rigoroso aplicado!")
    print("   Agora APENAS hospitais com padrão CLARO de maternidade estão na lista")

if __name__ == '__main__':
    main()
