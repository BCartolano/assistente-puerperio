#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise Contínua Completa - Processa Tudo Enquanto Você Dorme
Purpose: Rodar continuamente processando TODOS os hospitais, corrigindo tudo
Modo: Contínuo - processa tudo de uma vez, depois reinicia
"""

import os
import sys
import sqlite3
import json
import time
import re
from typing import Dict, List, Set
from datetime import datetime
from collections import defaultdict

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'cnes_cache.db')
STATE_FILE = os.path.join(BASE_DIR, 'backend', 'scripts', 'continuous_analysis_state.json')
LOG_FILE = os.path.join(BASE_DIR, 'backend', 'scripts', 'continuous_analysis_log.json')

STRICT_MATERNITY = [
    r'MATERNIDADE', r'MATERNO', r'OBSTETRIC[IA|ICO]', r'OBSTETR[ÍI]C[IA|ICO]',
    r'GINECOLOG[IA|ICO]', r'NEONATAL', r'NEONATOLOGIA', r'PARTO', r'NASCIMENTO',
    r'PR[ÉE]-NATAL', r'POS-PARTO', r'PÓS-PARTO',
]

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

def load_state():
    """Carrega estado"""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'iterations': 0,
        'total_processed': 0,
        'total_removed': 0,
        'last_completion': None
    }

def save_state(state):
    """Salva estado"""
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
    if len(logs) > 5000:
        logs = logs[-5000:]
    
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

def matches_pattern(text: str, patterns: list) -> bool:
    """Verifica padrão"""
    if not text:
        return False
    text_upper = text.upper()
    for pattern in patterns:
        if re.search(pattern, text_upper):
            return True
    return False

def is_valid_maternity(hospital: dict) -> bool:
    """Verifica se é maternidade válida"""
    name = hospital.get('name', '')
    fantasy_name = hospital.get('fantasy_name', '')
    full_name = f"{name} {fantasy_name}".strip()
    name_upper = full_name.upper()
    
    if 'MATERNIDADE' in name_upper:
        return True
    if matches_pattern(full_name, STRICT_MATERNITY):
        return True
    if 'HOSPITAL' in name_upper and ('DAS CLINICAS' in name_upper or 'DE CLINICAS' in name_upper):
        return True
    if matches_pattern(full_name, STRICT_EXCLUSIONS):
        return False
    return False

def is_ghost_company(hospital: dict) -> bool:
    """Verifica empresa fantasma"""
    lat = hospital.get('lat')
    lon = hospital.get('long')
    if not lat or not lon or lat == 0 or lon == 0:
        return True
    if not (-35.0 <= lat <= 5.0) or not (-75.0 <= lon <= -30.0):
        return True
    if not hospital.get('address'):
        return True
    return False

def normalize_name(name: str) -> str:
    """Normaliza nome"""
    if not name:
        return ''
    import unicodedata
    normalized = unicodedata.normalize('NFD', name.upper())
    normalized = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    normalized = ''.join(c for c in normalized if c.isalnum() or c.isspace())
    return ' '.join(normalized.split())

def process_all_hospitals():
    """Processa TODOS os hospitais"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    cur.execute("""
        SELECT cnes_id, name, fantasy_name, address, city, state, has_maternity, 
               tipo_unidade, lat, long, telefone
        FROM hospitals_cache
        WHERE has_maternity = 1
        AND tipo_unidade IN ('05', '07', 'HOSPITAL')
        ORDER BY cnes_id
    """)
    
    hospitals = [dict(row) for row in cur.fetchall()]
    
    # Identificar duplicatas
    by_name = defaultdict(list)
    by_location = defaultdict(list)
    
    for h in hospitals:
        name_norm = normalize_name(h.get('fantasy_name') or h.get('name', ''))
        if name_norm and len(name_norm) > 5:
            by_name[name_norm].append(h)
        
        lat = h.get('lat')
        lon = h.get('long')
        if lat and lon and lat != 0 and lon != 0:
            key = (round(float(lat), 4), round(float(lon), 4))
            by_location[key].append(h)
    
    duplicate_cnes = set()
    for name, hospitals_list in by_name.items():
        if len(hospitals_list) > 1:
            for h in hospitals_list[1:]:
                duplicate_cnes.add(h['cnes_id'])
    
    for loc, hospitals_list in by_location.items():
        if len(hospitals_list) > 1:
            for h in hospitals_list[1:]:
                if h['cnes_id'] not in duplicate_cnes:
                    duplicate_cnes.add(h['cnes_id'])
    
    # Processar cada hospital
    stats = {
        'valid': 0,
        'removed_duplicate': 0,
        'removed_ghost': 0,
        'removed_invalid': 0
    }
    
    for hospital in hospitals:
        cnes_id = hospital['cnes_id']
        name = hospital.get('fantasy_name') or hospital.get('name', '')
        
        should_remove = False
        reason = ''
        
        if cnes_id in duplicate_cnes:
            should_remove = True
            reason = 'Duplicata'
            stats['removed_duplicate'] += 1
        elif is_ghost_company(hospital):
            should_remove = True
            reason = 'Empresa fantasma'
            stats['removed_ghost'] += 1
        elif not is_valid_maternity(hospital):
            should_remove = True
            reason = 'Sem padrão claro de maternidade'
            stats['removed_invalid'] += 1
        else:
            stats['valid'] += 1
        
        if should_remove:
            cur.execute("""
                UPDATE hospitals_cache
                SET has_maternity = 0
                WHERE cnes_id = ?
            """, (cnes_id,))
            log_action('removed', {'cnes_id': cnes_id, 'name': name, 'reason': reason})
    
    conn.commit()
    cur.close()
    conn.close()
    
    return len(hospitals), stats

def main_loop():
    """Loop principal contínuo"""
    print("=" * 80)
    print("ANÁLISE CONTÍNUA COMPLETA - PROCESSANDO TUDO")
    print("=" * 80)
    print("Este script processará TODOS os hospitais continuamente")
    print("Garantirá que APENAS hospitais com maternidade fiquem na lista")
    print("Rodará enquanto você dorme e deixará tudo arrumado")
    print()
    print("Pressione Ctrl+C para parar")
    print()
    
    state = load_state()
    
    try:
        while True:
            iteration = state['iterations'] + 1
            print(f"\n{'='*80}")
            print(f"ITERAÇÃO {iteration} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*80}")
            
            start_time = time.time()
            
            print("📊 Processando TODOS os hospitais...")
            total, stats = process_all_hospitals()
            
            elapsed = time.time() - start_time
            
            state['iterations'] = iteration
            state['total_processed'] = state.get('total_processed', 0) + total
            state['total_removed'] = state.get('total_removed', 0) + (
                stats['removed_duplicate'] + stats['removed_ghost'] + stats['removed_invalid']
            )
            state['last_completion'] = datetime.now().isoformat()
            save_state(state)
            
            print()
            print("=" * 80)
            print("RESULTADO DA ITERAÇÃO")
            print("=" * 80)
            print(f"📊 Total analisado: {total}")
            print(f"✅ Válidos mantidos: {stats['valid']}")
            print(f"🚫 Removidos: {stats['removed_duplicate'] + stats['removed_ghost'] + stats['removed_invalid']}")
            print(f"   - Duplicatas: {stats['removed_duplicate']}")
            print(f"   - Empresas fantasmas: {stats['removed_ghost']}")
            print(f"   - Sem padrão claro: {stats['removed_invalid']}")
            print(f"⏱️  Tempo: {elapsed:.2f} segundos")
            print()
            print(f"📊 Total processado (todas iterações): {state['total_processed']}")
            print(f"🚫 Total removido (todas iterações): {state['total_removed']}")
            print()
            
            # Verificar quantos restam
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("""
                SELECT COUNT(*) as total
                FROM hospitals_cache
                WHERE has_maternity = 1
                AND tipo_unidade IN ('05', '07', 'HOSPITAL')
            """)
            remaining = cur.fetchone()['total']
            cur.close()
            conn.close()
            
            print(f"📊 Hospitais restantes com has_maternity=1: {remaining}")
            print()
            
            if remaining == stats['valid']:
                print("✅ Todos os hospitais válidos! Sistema limpo.")
            else:
                print("🔄 Reiniciando análise em 30 segundos...")
                time.sleep(30)
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário")
        save_state(state)
    except Exception as e:
        print(f"\n\n❌ ERRO: {e}")
        log_action('error', {'error': str(e)})
        print("🔄 Continuando em 60 segundos...")
        time.sleep(60)
        main_loop()

if __name__ == '__main__':
    main_loop()
