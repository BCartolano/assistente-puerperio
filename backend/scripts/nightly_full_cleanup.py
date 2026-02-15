#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Limpeza Completa Noturna
Purpose: Processar TODOS os hospitais, remover inválidos, garantir apenas maternidade
Modo: Execução completa - processa tudo de uma vez
"""

import os
import sys
import sqlite3
import json
import re
import time
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
REPORT_FILE = os.path.join(BASE_DIR, 'backend', 'scripts', 'nightly_cleanup_report.json')

# Padrões rigorosos
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
    
    # PRIORIDADE 1: Se tem "MATERNIDADE" no nome, SEMPRE válido
    if 'MATERNIDADE' in name_upper:
        return True
    
    # PRIORIDADE 2: Se tem padrão claro de maternidade
    if matches_pattern(full_name, STRICT_MATERNITY):
        return True
    
    # PRIORIDADE 3: Hospital das Clínicas (hospital geral)
    if 'HOSPITAL' in name_upper and ('DAS CLINICAS' in name_upper or 'DE CLINICAS' in name_upper):
        return True
    
    # Se tem exclusão, NÃO é maternidade
    if matches_pattern(full_name, STRICT_EXCLUSIONS):
        return False
    
    # Se não tem padrão claro, NÃO é maternidade
    return False

def is_ghost_company(hospital: dict) -> bool:
    """Verifica empresa fantasma"""
    lat = hospital.get('lat')
    lon = hospital.get('long')
    
    # Coordenadas inválidas
    if not lat or not lon or lat == 0 or lon == 0:
        return True
    
    # Fora do Brasil
    if not (-35.0 <= lat <= 5.0) or not (-75.0 <= lon <= -30.0):
        return True
    
    # Sem endereço
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
    normalized = ' '.join(normalized.split())
    return normalized

def main():
    print("=" * 80)
    print("LIMPEZA COMPLETA NOTURNA - PROCESSANDO TUDO")
    print("=" * 80)
    print("Este script processará TODOS os hospitais do Brasil")
    print("Removerá inválidos, duplicatas e empresas fantasmas")
    print("Garantirá que APENAS hospitais com maternidade fiquem na lista")
    print()
    
    start_time = time.time()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # Buscar TODOS os hospitais com has_maternity=1
    print("📊 Carregando todos os hospitais...")
    cur.execute("""
        SELECT cnes_id, name, fantasy_name, address, city, state, has_maternity, 
               tipo_unidade, lat, long, telefone
        FROM hospitals_cache
        WHERE has_maternity = 1
        AND tipo_unidade IN ('05', '07', 'HOSPITAL')
        ORDER BY cnes_id
    """)
    
    hospitals = [dict(row) for row in cur.fetchall()]
    print(f"   Total encontrado: {len(hospitals)} hospitais")
    print()
    
    stats = {
        'total_analyzed': len(hospitals),
        'valid': 0,
        'removed_invalid': 0,
        'removed_ghost': 0,
        'removed_duplicate': 0,
        'removed_no_pattern': 0
    }
    
    removed_cnes = []
    
    # FASE 1: Identificar duplicatas
    print("🔍 FASE 1: Identificando duplicatas...")
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
    
    print(f"   Duplicatas encontradas: {len(duplicate_cnes)}")
    print()
    
    # FASE 2: Analisar cada hospital
    print("🔍 FASE 2: Analisando cada hospital...")
    
    for i, hospital in enumerate(hospitals, 1):
        cnes_id = hospital['cnes_id']
        name = hospital.get('fantasy_name') or hospital.get('name', '')
        
        should_remove = False
        reason = ''
        
        # Verificar duplicata
        if cnes_id in duplicate_cnes:
            should_remove = True
            reason = 'Duplicata'
            stats['removed_duplicate'] += 1
        
        # Verificar empresa fantasma
        elif is_ghost_company(hospital):
            should_remove = True
            reason = 'Empresa fantasma (coordenadas/dados inválidos)'
            stats['removed_ghost'] += 1
        
        # Verificar se é maternidade válida
        elif not is_valid_maternity(hospital):
            should_remove = True
            reason = 'Sem padrão claro de maternidade'
            stats['removed_no_pattern'] += 1
        
        if should_remove:
            cur.execute("""
                UPDATE hospitals_cache
                SET has_maternity = 0
                WHERE cnes_id = ?
            """, (cnes_id,))
            removed_cnes.append({'cnes_id': cnes_id, 'name': name, 'reason': reason})
            stats['removed_invalid'] += 1
        else:
            stats['valid'] += 1
        
        if i % 500 == 0:
            print(f"   Progresso: {i}/{len(hospitals)} analisados...")
    
    conn.commit()
    
    # Verificar resultado final
    cur.execute("""
        SELECT COUNT(*) as total
        FROM hospitals_cache
        WHERE has_maternity = 1
        AND tipo_unidade IN ('05', '07', 'HOSPITAL')
    """)
    final_count = cur.fetchone()['total']
    
    cur.close()
    conn.close()
    
    elapsed = time.time() - start_time
    
    print()
    print("=" * 80)
    print("RESULTADO DA LIMPEZA COMPLETA")
    print("=" * 80)
    print(f"📊 Total analisado: {stats['total_analyzed']}")
    print(f"✅ Hospitais válidos mantidos: {stats['valid']}")
    print(f"🚫 Hospitais removidos: {stats['removed_invalid']}")
    print(f"   - Duplicatas: {stats['removed_duplicate']}")
    print(f"   - Empresas fantasmas: {stats['removed_ghost']}")
    print(f"   - Sem padrão claro: {stats['removed_no_pattern']}")
    print()
    print(f"📊 Total final no banco: {final_count} hospitais com has_maternity=1")
    print(f"⏱️  Tempo de processamento: {elapsed:.2f} segundos")
    print()
    
    # Salvar relatório
    report = {
        'timestamp': datetime.now().isoformat(),
        'stats': stats,
        'final_count': final_count,
        'elapsed_seconds': elapsed,
        'removed_samples': removed_cnes[:200]  # Primeiros 200
    }
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Relatório salvo em: {REPORT_FILE}")
    print()
    print("✅ Limpeza completa concluída!")
    print("   Agora APENAS hospitais com maternidade confirmada estão na lista")

if __name__ == '__main__':
    main()
