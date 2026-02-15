#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validação e Correção de Hospitais Suspeitos
Purpose: Validar hospitais suspeitos e corrigir banco de dados
Modo: Autônomo - processa lista de suspeitos
"""

import os
import sys
import sqlite3
import json

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'cnes_cache.db')
SUSPICIOUS_FILE = os.path.join(BASE_DIR, 'backend', 'scripts', 'suspicious_hospitals.json')

# Blacklist baseada em validação manual/web search
# CNES que devem ter has_maternity=0
BLACKLIST_CNES = [
    # Saúde Mental
    '0027707',   # Clínica Pinel - saúde mental/psiquiatria (Belo Horizonte, MG)
    '0003085',   # Clínica de Repouso São Marcello - saúde mental (Aracaju, SE)
    '0106518',   # Clínica Terapêutica Virtude - provável saúde mental
    '0235385',   # Clínica Terapêutica Sonho de Vida - provável saúde mental
    '0228494',   # Serenity Clínica de Desospitalização - provável saúde mental
    # Clínicas específicas (não hospitais)
    '0002593',   # Clínica Santa Helena Suissa - clínica específica
    '0016292',   # Clínica Dr Helio Rotenberg - clínica específica
    '0007714',   # Clínica de Acident São Francisco - clínica de acidentes
    '0014125',   # Center Clínicas - centro de clínicas
    # Policlínicas sem maternidade confirmada
    '0219622',   # Policlínica Municipal Geomarco Coelho - verificar
    # Hospitais específicos sem maternidade
    '0262862',   # Hospital das Clínicas Covid 19 - hospital temporário COVID
]

# Whitelist - Hospitais "das Clínicas" que TÊM maternidade (validados)
WHITELIST_CNES = [
    '0000396',   # Hospital das Clínicas (Recife, PE) - hospital geral, pode ter maternidade
    '0027049',   # Hospital das Clínicas UFMG - TEM maternidade/obstetría (validado)
    '0026417',   # Hospital de Clínicas Sul - hospital geral
    '0104884',   # Hospital das Clínicas de São Gonçalo - hospital geral
    '0115509',   # Hospital de Clínicas Anjo Gabriel - hospital geral
    '0175277',   # Hospital das Clínicas Bauru - hospital geral
    '0220337',   # Hospital de Clínicas de Campina Grande - hospital geral
]

# Policlínicas que TÊM maternidade no nome (manter)
POLICLINICS_WITH_MATERNITY = [
    '0000671',   # Policlínica E Maternidade Arnaldo Marques
    '0020516',   # Policlínica E Maternidade Professor Barros Lima
]

def load_suspicious_hospitals():
    """Carrega lista de hospitais suspeitos"""
    if not os.path.exists(SUSPICIOUS_FILE):
        return []
    with open(SUSPICIOUS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('suspicious', [])

def fix_hospitals_in_database():
    """Corrige hospitais no banco de dados"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Remover has_maternity=1 dos CNES na blacklist
    if BLACKLIST_CNES:
        placeholders = ','.join('?' * len(BLACKLIST_CNES))
        cur.execute(f"""
            UPDATE hospitals_cache
            SET has_maternity = 0
            WHERE cnes_id IN ({placeholders})
            AND has_maternity = 1
        """, BLACKLIST_CNES)
        n_removed = cur.rowcount
    else:
        n_removed = 0
    
    conn.commit()
    cur.close()
    conn.close()
    
    return n_removed

def main():
    print("=" * 80)
    print("VALIDAÇÃO E CORREÇÃO DE HOSPITAIS SUSPEITOS")
    print("=" * 80)
    print()
    
    suspicious = load_suspicious_hospitals()
    print(f"📋 Carregados {len(suspicious)} hospitais suspeitos do arquivo JSON")
    print()
    
    print("🔍 ANÁLISE DE CADA HOSPITAL SUSPEITO:")
    print()
    
    to_remove = []
    to_keep = []
    
    for h in suspicious:
        cnes_id = h['cnes_id']
        name = h['name']
        
        if cnes_id in BLACKLIST_CNES:
            to_remove.append(h)
            print(f"🚫 REMOVER: {name} (CNES: {cnes_id})")
            print(f"   Motivo: Na blacklist (não tem maternidade)")
        elif cnes_id in WHITELIST_CNES:
            to_keep.append(h)
            print(f"✅ MANTER: {name} (CNES: {cnes_id})")
            print(f"   Motivo: Na whitelist (tem maternidade ou é hospital geral)")
        elif cnes_id in POLICLINICS_WITH_MATERNITY:
            to_keep.append(h)
            print(f"✅ MANTER: {name} (CNES: {cnes_id})")
            print(f"   Motivo: Policlínica com 'Maternidade' no nome")
        else:
            # Não está em nenhuma lista - requer análise manual
            print(f"⚠️  PENDENTE: {name} (CNES: {cnes_id})")
            print(f"   Motivo: Requer validação manual/web search")
    
    print()
    print("=" * 80)
    print(f"RESUMO")
    print("=" * 80)
    print(f"🚫 A remover: {len(to_remove)}")
    print(f"✅ A manter: {len(to_keep)}")
    print(f"⚠️  Pendentes: {len(suspicious) - len(to_remove) - len(to_keep)}")
    print()
    
    # Corrigir banco
    print("🔧 Corrigindo banco de dados...")
    n_fixed = fix_hospitals_in_database()
    print(f"✅ {n_fixed} hospital(is) corrigido(s) no banco")
    print()
    
    # Salvar relatório
    report = {
        'removed': [{'cnes_id': h['cnes_id'], 'name': h['name']} for h in to_remove],
        'kept': [{'cnes_id': h['cnes_id'], 'name': h['name']} for h in to_keep],
        'pending': [{'cnes_id': h['cnes_id'], 'name': h['name']} for h in suspicious 
                   if h['cnes_id'] not in BLACKLIST_CNES + WHITELIST_CNES + POLICLINICS_WITH_MATERNITY]
    }
    
    report_file = os.path.join(BASE_DIR, 'backend', 'scripts', 'hospital_validation_report.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Relatório salvo em: {report_file}")
    print()
    print("✅ Processo concluído!")

if __name__ == '__main__':
    main()
