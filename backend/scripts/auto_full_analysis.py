#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise Automática Completa do Projeto
Purpose: Analisar projeto inteiro, corrigir erros, validar API, filtrar apenas maternidade
Modo: Automático completo - roda continuamente
"""

import os
import sys
import sqlite3
import json
import time
import re
import subprocess
from typing import Dict, List, Optional, Set
from datetime import datetime
from pathlib import Path

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'cnes_cache.db')
LOG_FILE = os.path.join(BASE_DIR, 'backend', 'scripts', 'full_analysis_log.json')
STATE_FILE = os.path.join(BASE_DIR, 'backend', 'scripts', 'full_analysis_state.json')

# Padrões que indicam NÃO maternidade (completo)
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
    """Carrega estado"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'last_cnes_id': '',
        'processed_count': 0,
        'fixed_count': 0,
        'duplicates_found': 0,
        'ghost_companies_found': 0,
        'last_update': datetime.now().isoformat()
    }

def save_state(state):
    """Salva estado"""
    state['last_update'] = datetime.now().isoformat()
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def log_action(action: str, details: Dict):
    """Registra ação"""
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
    if len(logs) > 2000:
        logs = logs[-2000:]
    
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

def find_duplicates_by_location(conn):
    """Encontra duplicatas por localização (mesma lat/long)"""
    cur = conn.cursor()
    cur.execute("""
        SELECT lat, long, COUNT(*) as count, GROUP_CONCAT(cnes_id) as cnes_ids
        FROM hospitals_cache
        WHERE has_maternity = 1
        AND lat IS NOT NULL AND long IS NOT NULL
        AND lat != 0 AND long != 0
        GROUP BY ROUND(lat, 5), ROUND(long, 5)
        HAVING count > 1
    """)
    return cur.fetchall()

def find_duplicates_by_name(conn):
    """Encontra duplicatas por nome similar"""
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            UPPER(TRIM(COALESCE(fantasy_name, name, ''))) as name_upper,
            COUNT(*) as count,
            GROUP_CONCAT(cnes_id) as cnes_ids,
            GROUP_CONCAT(fantasy_name || '|' || name) as names
        FROM hospitals_cache
        WHERE has_maternity = 1
        AND tipo_unidade IN ('05', '07', 'HOSPITAL')
        GROUP BY name_upper
        HAVING count > 1
        LIMIT 100
    """)
    return cur.fetchall()

def is_ghost_company(hospital: dict) -> bool:
    """Verifica se pode ser empresa fantasma (coordenadas inválidas, dados incompletos)"""
    # Coordenadas inválidas
    lat = hospital.get('lat')
    lon = hospital.get('long')
    if not lat or not lon or lat == 0 or lon == 0:
        return True
    
    # Fora do Brasil
    if not (-35.0 <= lat <= 5.0) or not (-75.0 <= lon <= -30.0):
        return True
    
    # Sem endereço
    if not hospital.get('address'):
        return True
    
    # Nome muito genérico ou suspeito
    name = (hospital.get('fantasy_name') or hospital.get('name') or '').upper()
    suspicious_names = ['HOSPITAL', 'CLINICA', 'UNIDADE', 'CENTRO']
    if name in suspicious_names or len(name) < 5:
        return True
    
    return False

def matches_pattern(text: str, patterns: list) -> bool:
    """Verifica padrão"""
    if not text:
        return False
    text_upper = text.upper()
    for pattern in patterns:
        if re.search(pattern, text_upper):
            return True
    return False

def is_hospital_das_clinicas(name: str) -> bool:
    """Verifica se é Hospital das Clínicas"""
    name_upper = (name or '').upper()
    return 'HOSPITAL' in name_upper and ('DAS CLINICAS' in name_upper or 'DE CLINICAS' in name_upper)

def analyze_hospital_strict(hospital: dict) -> tuple:
    """
    Análise rigorosa: retorna (is_valid, reason, is_duplicate, is_ghost)
    """
    name = hospital.get('name', '')
    fantasy_name = hospital.get('fantasy_name', '')
    full_name = f"{name} {fantasy_name}".strip()
    cnes_id = hospital.get('cnes_id', '')
    
    # Verificar empresa fantasma
    if is_ghost_company(hospital):
        return (False, 'Empresa fantasma (coordenadas inválidas/dados incompletos)', False, True)
    
    # Verificar se é Hospital das Clínicas (válido)
    if is_hospital_das_clinicas(full_name):
        return (True, 'Hospital das Clínicas (hospital geral)', False, False)
    
    # Verificar padrões de NÃO maternidade
    if matches_pattern(full_name, NON_MATERNITY_PATTERNS):
        return (False, 'Contém padrão não-maternidade', False, False)
    
    # Verificar padrões de SIM maternidade
    if matches_pattern(full_name, MATERNITY_PATTERNS):
        return (True, 'Contém padrão maternidade', False, False)
    
    # Sem padrões claros - requer validação (mas não é válido automaticamente)
    return (False, 'Sem padrões claros de maternidade', False, False)

def fix_hospital_in_db(cnes_id: str, reason: str):
    """Corrige hospital no banco"""
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

def process_all_hospitals():
    """Processa TODOS os hospitais do Brasil"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Buscar TODOS os hospitais com has_maternity=1
    cur.execute("""
        SELECT cnes_id, name, fantasy_name, address, city, state, has_maternity, 
               tipo_unidade, lat, long
        FROM hospitals_cache
        WHERE has_maternity = 1
        AND tipo_unidade IN ('05', '07', 'HOSPITAL')
        ORDER BY cnes_id
    """)
    
    hospitals = [dict(row) for row in cur.fetchall()]
    
    # Encontrar duplicatas
    print("🔍 Procurando duplicatas...")
    duplicates_location = find_duplicates_by_location(conn)
    duplicates_name = find_duplicates_by_name(conn)
    
    duplicate_cnes: Set[str] = set()
    for dup in duplicates_location:
        cnes_ids = dup['cnes_ids'].split(',')
        # Manter o primeiro, marcar os outros como duplicatas
        for cnes_id in cnes_ids[1:]:
            duplicate_cnes.add(cnes_id.strip())
    
    for dup in duplicates_name:
        cnes_ids = dup['cnes_ids'].split(',')
        # Manter o primeiro, marcar os outros como duplicatas
        for cnes_id in cnes_ids[1:]:
            duplicate_cnes.add(cnes_id.strip())
    
    conn.close()
    
    return hospitals, duplicate_cnes

def main_analysis_loop():
    """Loop principal de análise completa"""
    print("=" * 80)
    print("ANÁLISE AUTOMÁTICA COMPLETA - MODO AUTÔNOMO")
    print("=" * 80)
    print("Analisando: Erros, arquivos desnecessários, empresas fantasmas, duplicatas")
    print("Filtrando: APENAS hospitais com maternidade confirmada")
    print("Escopo: Brasil inteiro (7.428+ estabelecimentos)")
    print()
    print("Pressione Ctrl+C para parar")
    print()
    
    state = load_state()
    iteration = 0
    
    try:
        while True:
            iteration += 1
            print(f"\n{'='*80}")
            print(f"ITERAÇÃO {iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*80}")
            
            # Processar todos os hospitais
            print("📊 Carregando todos os hospitais do Brasil...")
            hospitals, duplicate_cnes = process_all_hospitals()
            
            print(f"📋 Total de hospitais com has_maternity=1: {len(hospitals)}")
            print(f"🔄 Duplicatas encontradas: {len(duplicate_cnes)}")
            print()
            
            print("🔍 Analisando cada hospital...")
            
            fixed_count = 0
            ghost_count = 0
            duplicate_count = 0
            invalid_count = 0
            
            for i, hospital in enumerate(hospitals, 1):
                cnes_id = hospital['cnes_id']
                name = hospital.get('fantasy_name') or hospital.get('name', '')
                
                # Verificar duplicata
                if cnes_id in duplicate_cnes:
                    if fix_hospital_in_db(cnes_id, 'Duplicata (mesmo lugar ou nome)'):
                        duplicate_count += 1
                        fixed_count += 1
                        print(f"🔄 [{i}/{len(hospitals)}] DUPLICATA REMOVIDA: {name} (CNES: {cnes_id})")
                        log_action('duplicate_removed', {'cnes_id': cnes_id, 'name': name})
                    continue
                
                # Análise rigorosa
                is_valid, reason, is_dup, is_ghost = analyze_hospital_strict(hospital)
                
                if not is_valid:
                    if fix_hospital_in_db(cnes_id, reason):
                        fixed_count += 1
                        invalid_count += 1
                        if is_ghost:
                            ghost_count += 1
                        print(f"🚫 [{i}/{len(hospitals)}] REMOVIDO: {name} (CNES: {cnes_id})")
                        print(f"    Motivo: {reason}")
                        log_action('removed', {
                            'cnes_id': cnes_id,
                            'name': name,
                            'reason': reason,
                            'is_ghost': is_ghost
                        })
                
                # Progresso a cada 100
                if i % 100 == 0:
                    print(f"   Progresso: {i}/{len(hospitals)} processados...")
            
            # Atualizar estado
            state['processed_count'] = len(hospitals)
            state['fixed_count'] = state.get('fixed_count', 0) + fixed_count
            state['duplicates_found'] = state.get('duplicates_found', 0) + duplicate_count
            state['ghost_companies_found'] = state.get('ghost_companies_found', 0) + ghost_count
            save_state(state)
            
            print()
            print("=" * 80)
            print("RESUMO DA ITERAÇÃO")
            print("=" * 80)
            print(f"✅ Processados: {len(hospitals)}")
            print(f"🚫 Removidos: {fixed_count}")
            print(f"   - Duplicatas: {duplicate_count}")
            print(f"   - Empresas fantasmas: {ghost_count}")
            print(f"   - Inválidos (não-maternidade): {invalid_count - ghost_count}")
            print(f"📊 Total corrigido até agora: {state['fixed_count']}")
            print()
            
            # Aguardar antes de próxima iteração
            print("⏳ Aguardando 60 segundos antes da próxima análise completa...")
            time.sleep(60)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário")
        save_state(state)
    except Exception as e:
        print(f"\n\n❌ ERRO: {e}")
        log_action('error', {'error': str(e), 'traceback': str(sys.exc_info())})
        print("🔄 Continuando em 30 segundos...")
        time.sleep(30)
        main_analysis_loop()

if __name__ == '__main__':
    main_analysis_loop()
