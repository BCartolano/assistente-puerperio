#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validação Automática Contínua de Hospitais de Maternidade
Purpose: Rodar em modo autônomo, validar e corrigir hospitais automaticamente
Modo: Automático com tratamento de erros de internet
"""

import os
import sys
import sqlite3
import json
import time
import re
from typing import Dict, List, Optional
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'cnes_cache.db')
LOG_FILE = os.path.join(BASE_DIR, 'backend', 'scripts', 'auto_validation_log.json')
STATE_FILE = os.path.join(BASE_DIR, 'backend', 'scripts', 'auto_validation_state.json')

# Padrões que indicam NÃO maternidade
NON_MATERNITY_PATTERNS = [
    r'PSIQUIATR[IA|ICO]', r'SAUDE MENTAL', r'SAÚDE MENTAL', r'CVV',
    r'DEPENDENCIA', r'DEPENDÊNCIA', r'QUIMICA', r'QUÍMICA', r'ADICCAO', r'ADICÇÃO',
    r'ALCOOLISMO', r'DROGADICCAO', r'DROGADIÇÃO',
    r'ORTOPED[IA|ICO|ISTA]', r'TRAUMATOLOGIA', r'FRATURA', r'OSSO', r'OSSOS',
    r'VIS[ÃO|AO]', r'VISUAL', r'OFTA', r'OFTALMO', r'OLHO', r'OLHOS',
    r'CARDIOLOG[IA|ICO]', r'CARDIACO', r'CORAÇÃO', r'CORACAO',
    r'ONCOLOG[IA|ICO]', r'CANCER', r'CÂNCER',
    r'HOSPITAL INFANTIL', r'INFANTIL$', r'PEDIATR[IA|ICO|ICA]',
    r'CIRURGIA PLASTICA', r'CIRURGIA PLÁSTICA', r'PLASTICA', r'PLÁSTICA',
    r'ESTETICA', r'ESTÉTICA',
    r'^CLINICA ', r'^CLÍNICA ', r'CLINICA DE ', r'CLÍNICA DE ',
    r'CLINICA DR ', r'CLÍNICA DR ', r'CLINICA TERAPEUTICA',
    r'CLÍNICA TERAPÊUTICA', r'CLINICA DE REPOUSO', r'CLÍNICA DE REPOUSO',
    r'CLINICA DE ACIDENT', r'CLINICA DE DESOSPITALIZACAO',
    r'REABILITACAO', r'FISIOTERAPIA', r'TERAPIA OCUPACIONAL',
    r'OTORRINOLARINGOLOG', r'OTORRINO',
    r'COVID 19', r'COVID-19', r'CORONAVIRUS', r'CORONA', r'PANDEMIA',
    r'CAMPANHA', r'HOSPITAL DE CAMPANHA', r'HOSPITAL CAMPANHA',
    r'RETAGUARDA', r'UNIDADE DE INTERNACAO', r'CENTRO DE INTERNACAO',
]

MATERNITY_PATTERNS = [
    r'MATERNIDADE', r'MATERNO', r'OBSTETRIC[IA|ICO]', r'OBSTETR[ÍI]C[IA|ICO]',
    r'GINECOLOG[IA|ICO]', r'GINECOLOGISTA', r'NEONATAL', r'NEONATOLOGIA',
    r'PARTO', r'NASCIMENTO', r'PR[ÉE]-NATAL', r'POS-PARTO', r'PÓS-PARTO',
]

def load_state():
    """Carrega estado da última execução"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'last_cnes_id': '', 'processed_count': 0, 'fixed_count': 0}

def save_state(state):
    """Salva estado da execução"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def log_action(action: str, details: Dict):
    """Registra ação no log"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': action,
        'details': details
    }
    
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    else:
        logs = []
    
    logs.append(log_entry)
    # Manter apenas últimos 1000 logs
    if len(logs) > 1000:
        logs = logs[-1000:]
    
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

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
    """Verifica se é um "Hospital das Clínicas" (hospital geral)"""
    name_upper = (name or '').upper()
    return 'HOSPITAL' in name_upper and ('DAS CLINICAS' in name_upper or 'DE CLINICAS' in name_upper)

def analyze_hospital_local(hospital: dict) -> Optional[str]:
    """Analisa hospital localmente (sem internet)"""
    name = hospital.get('name', '')
    fantasy_name = hospital.get('fantasy_name', '')
    full_name = f"{name} {fantasy_name}".strip()
    
    # Se é "Hospital das Clínicas", assumir válido
    if is_hospital_das_clinicas(full_name):
        return None  # Válido
    
    # Verificar padrões de NÃO maternidade
    if matches_pattern(full_name, NON_MATERNITY_PATTERNS):
        return 'Contém padrão não-maternidade'
    
    # Se tem padrão de maternidade, assumir válido
    if matches_pattern(full_name, MATERNITY_PATTERNS):
        return None  # Válido
    
    # Sem padrões claros - requer validação (mas não remove automaticamente)
    return 'Sem padrões claros - requer validação'

def fix_hospital_in_db(cnes_id: str, reason: str):
    """Corrige hospital no banco (remove has_maternity=1)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            UPDATE hospitals_cache
            SET has_maternity = 0
            WHERE cnes_id = ?
            AND has_maternity = 1
        """, (cnes_id,))
        n = cur.rowcount
        conn.commit()
        cur.close()
        conn.close()
        return n > 0
    except Exception as e:
        log_action('error', {'cnes_id': cnes_id, 'error': str(e)})
        return False

def process_hospitals_batch(batch_size: int = 50, start_from: str = ''):
    """Processa lote de hospitais"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Buscar próximo lote
    if start_from:
        cur.execute("""
            SELECT cnes_id, name, fantasy_name, address, city, state, has_maternity, tipo_unidade
            FROM hospitals_cache
            WHERE has_maternity = 1
            AND tipo_unidade IN ('05', '07', 'HOSPITAL')
            AND cnes_id > ?
            ORDER BY cnes_id
            LIMIT ?
        """, (start_from, batch_size))
    else:
        cur.execute("""
            SELECT cnes_id, name, fantasy_name, address, city, state, has_maternity, tipo_unidade
            FROM hospitals_cache
            WHERE has_maternity = 1
            AND tipo_unidade IN ('05', '07', 'HOSPITAL')
            ORDER BY cnes_id
            LIMIT ?
        """, (batch_size,))
    
    hospitals = [dict(row) for row in cur.fetchall()]
    conn.close()
    
    return hospitals

def main_loop():
    """Loop principal de validação automática"""
    print("=" * 80)
    print("MODO AUTOMÁTICO: VALIDAÇÃO CONTÍNUA DE HOSPITAIS")
    print("=" * 80)
    print("Pressione Ctrl+C para parar")
    print()
    
    state = load_state()
    batch_size = 50
    processed_total = state.get('processed_count', 0)
    fixed_total = state.get('fixed_count', 0)
    last_cnes = state.get('last_cnes_id', '')
    
    iteration = 0
    
    try:
        while True:
            iteration += 1
            print(f"\n{'='*80}")
            print(f"ITERAÇÃO {iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*80}")
            print(f"📊 Processados até agora: {processed_total} | Corrigidos: {fixed_total}")
            print()
            
            # Processar lote
            hospitals = process_hospitals_batch(batch_size, last_cnes)
            
            if not hospitals:
                print("✅ Todos os hospitais foram processados!")
                print("🔄 Reiniciando do início...")
                last_cnes = ''
                time.sleep(60)  # Aguardar 1 minuto antes de reiniciar
                continue
            
            print(f"📋 Processando lote de {len(hospitals)} hospitais...")
            
            batch_fixed = 0
            for i, hospital in enumerate(hospitals, 1):
                cnes_id = hospital['cnes_id']
                name = hospital.get('fantasy_name') or hospital.get('name', '')
                
                # Análise local (não requer internet)
                reason = analyze_hospital_local(hospital)
                
                if reason and ('não-maternidade' in reason or 'requer validação' in reason):
                    # Para "requer validação", verificar se é hospital de campanha/retaguarda
                    name_upper = name.upper()
                    if 'CAMPANHA' in name_upper or 'RETAGUARDA' in name_upper or 'INTERNACAO' in name_upper:
                        reason = 'Contém padrão não-maternidade (campanha/retaguarda/internação)'
                    
                if reason and 'não-maternidade' in reason:
                    # Remover automaticamente
                    if fix_hospital_in_db(cnes_id, reason):
                        batch_fixed += 1
                        fixed_total += 1
                        print(f"🚫 [{i}/{len(hospitals)}] REMOVIDO: {name} (CNES: {cnes_id})")
                        print(f"    Motivo: {reason}")
                        log_action('removed', {
                            'cnes_id': cnes_id,
                            'name': name,
                            'reason': reason
                        })
                elif reason and 'requer validação' in reason:
                    # Apenas logar, não remover automaticamente
                    print(f"⚠️  [{i}/{len(hospitals)}] PENDENTE: {name} (CNES: {cnes_id})")
                    print(f"    Motivo: {reason}")
                    log_action('pending', {
                        'cnes_id': cnes_id,
                        'name': name,
                        'reason': reason
                    })
                else:
                    # Válido
                    pass
                
                last_cnes = cnes_id
                processed_total += 1
                
                # Pequena pausa para não sobrecarregar
                time.sleep(0.1)
            
            # Salvar estado
            state = {
                'last_cnes_id': last_cnes,
                'processed_count': processed_total,
                'fixed_count': fixed_total,
                'last_update': datetime.now().isoformat()
            }
            save_state(state)
            
            print()
            print(f"✅ Lote processado: {len(hospitals)} hospitais | {batch_fixed} removidos")
            print(f"📊 Total: {processed_total} processados | {fixed_total} corrigidos")
            
            # Pausa entre lotes
            time.sleep(5)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário")
        print(f"📊 Estado salvo: {processed_total} processados | {fixed_total} corrigidos")
        save_state(state)
    except Exception as e:
        print(f"\n\n❌ ERRO: {e}")
        log_action('error', {'error': str(e), 'traceback': str(sys.exc_info())})
        print("🔄 Continuando em 10 segundos...")
        time.sleep(10)
        main_loop()  # Reiniciar loop

if __name__ == '__main__':
    main_loop()
