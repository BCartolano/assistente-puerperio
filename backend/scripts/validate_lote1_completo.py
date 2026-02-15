#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validação Completa Lote 1 - Todos os 10 Hospitais
Purpose: Processar resultados de busca web e atualizar banco
"""

import os
import sys
import sqlite3

# Configuração de encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'cnes_cache.db')

# Resultados da busca web (primeiros 10 hospitais)
WEB_VALIDATION_RESULTS = {
    '0000027': {  # Casa De Saude Santa Helena
        'confirmed': True,
        'confidence': 1.0,
        'evidence': ['maternidade', 'obstetrícia', 'parto', 'sala de parto'],
        'notes': 'Múltiplas unidades confirmadas com maternidade'
    },
    '0000035': {  # Hospital Mendo Sampaio
        'confirmed': True,
        'confidence': 1.0,
        'evidence': ['maternidade', 'partos normais', 'partos cesarianos', 'urgências obstétricas'],
        'notes': 'Confirmado: oferece partos normais e cesarianos'
    },
    '0000094': {  # Maternidade Padre Geraldo Leite Bastos
        'confirmed': True,
        'confidence': 1.0,
        'evidence': ['maternidade', 'partos', 'urgências obstétricas'],
        'notes': 'Confirmado: é uma maternidade'
    },
    '0000183': {  # Hospital Samaritano
        'confirmed': True,
        'confidence': 1.0,
        'evidence': ['centro materno fetal', 'sala ppps', 'uti neonatal', 'maternidade'],
        'notes': 'Confirmado: Centro de Excelência Materno Fetal'
    },
    '0000221': {  # Hospital Sao Sebastiao
        'confirmed': True,
        'confidence': 1.0,
        'evidence': ['casa de parto', 'obstetrícia', 'partos normais'],
        'notes': 'Confirmado: Casa de Parto especializada'
    },
    '0000396': {  # Hospital Das Clinicas
        'confirmed': True,
        'confidence': 1.0,
        'evidence': ['centro obstétrico', 'maternidade', 'emergência obstétrica', 'parto'],
        'notes': 'Confirmado: Centro Obstétrico e Maternidade'
    },
    '0000418': {  # Hospital Agamenon Magalhaes
        'confirmed': True,
        'confidence': 1.0,
        'evidence': ['maternidade de alto risco', 'obstetrícia', 'neonatologia', '230 partos/mês'],
        'notes': 'Confirmado: Maternidade de alto risco, 230 partos/mês'
    },
    '0000426': {  # Hospital Otavio De Freitas
        'confirmed': False,
        'confidence': 0.0,
        'evidence': [],
        'notes': 'Não encontradas informações sobre maternidade'
    },
    '0000434': {  # Imip
        'confirmed': False,
        'confidence': 0.3,
        'evidence': [],
        'notes': 'Resultados genéricos sobre parto, não específicos do hospital'
    },
    '0000477': {  # Hospital Oswaldo Cruz
        'confirmed': False,
        'confidence': 0.0,
        'evidence': [],
        'notes': 'Hospital não listou obstetrícia/maternidade entre especialidades'
    }
}


def analyze_and_update():
    """Analisa resultados e atualiza banco de dados"""
    print("="*70)
    print("VALIDAÇÃO WEB - LOTE 1 COMPLETO")
    print("="*70)
    print()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    confirmed = []
    not_confirmed = []
    
    for cnes_id, validation in WEB_VALIDATION_RESULTS.items():
        # Buscar nome do hospital
        cursor.execute("""
            SELECT fantasy_name, name
            FROM hospitals_cache
            WHERE cnes_id = ?
        """, (cnes_id,))
        row = cursor.fetchone()
        
        if not row:
            continue
        
        name = row['fantasy_name'] or row['name'] or 'Sem nome'
        
        if validation['confirmed']:
            confirmed.append({
                'cnes_id': cnes_id,
                'name': name,
                'confidence': validation['confidence'],
                'evidence': validation['evidence']
            })
            print(f"✅ {name} (CNES: {cnes_id})")
            print(f"   Confiança: {validation['confidence']:.0%}")
            print(f"   Evidências: {', '.join(validation['evidence'][:3])}")
        else:
            not_confirmed.append({
                'cnes_id': cnes_id,
                'name': name,
                'reason': validation['notes']
            })
            print(f"❌ {name} (CNES: {cnes_id})")
            print(f"   Razão: {validation['notes']}")
    
    print()
    print("="*70)
    print("ATUALIZANDO BANCO DE DADOS")
    print("="*70)
    
    # Remover has_maternity=1 de hospitais não confirmados
    if not_confirmed:
        cnes_ids = [h['cnes_id'] for h in not_confirmed]
        placeholders = ','.join(['?' for _ in cnes_ids])
        cursor.execute(f"""
            UPDATE hospitals_cache
            SET has_maternity = 0
            WHERE cnes_id IN ({placeholders})
        """, cnes_ids)
        removed = cursor.rowcount
        print(f"[OK] {removed} hospitais não confirmados removidos da busca de maternidades")
    
    conn.commit()
    conn.close()
    
    print()
    print("="*70)
    print("RESUMO")
    print("="*70)
    print(f"✅ Confirmados: {len(confirmed)}")
    print(f"❌ Não Confirmados: {len(not_confirmed)}")
    print(f"📊 Taxa de Confirmação: {len(confirmed)/(len(confirmed)+len(not_confirmed))*100:.1f}%")
    
    return {
        'confirmed': confirmed,
        'not_confirmed': not_confirmed
    }


if __name__ == "__main__":
    results = analyze_and_update()
