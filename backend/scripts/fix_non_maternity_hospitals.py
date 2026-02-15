#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remover Hospitais Não de Maternidade
Purpose: Remover has_maternity=1 de hospitais de Visão, Ortopedia, etc.
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

def fix_non_maternity_hospitals():
    """Remove has_maternity=1 de hospitais não relacionados a maternidade"""
    print("="*70)
    print("CORREÇÃO: REMOVENDO HOSPITAIS NÃO DE MATERNIDADE")
    print("="*70)
    print()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Termos a excluir (especialidades não relacionadas a maternidade)
    excluded_terms = [
        # Visão/Oftalmologia
        'VISÃO', 'VISAO', 'VISUAL', 'OFTA', 'OFTALMO', 'OLHO', 'OLHOS',
        'RETINA', 'CÓRNEA', 'CORNEA', 'CATARATA', 'GLAUCOMA',
        # Ortopedia
        'ORTO', 'ORTOD', 'ORTOPED', 'ORTOPÉD', 'TRAUMATO', 'FRATURA',
        'OSSO', 'OSSOS', 'COLUNA', 'JOELHO', 'QUADRIL', 'OMBRO',
        # Outras especialidades
        'CARDIOL', 'CARDIAC', 'CORAÇÃO', 'CORACAO',
        'ONCO', 'CANCER', 'CÂNCER',
        'PSIQUIATR', 'MENTAL', 'PSICOLÓGICO', 'PSICOLOGICO',
        'CIRURGIA PLÁSTICA', 'CIRURGIA PLASTICA', 'ESTÉTICA', 'ESTETICA',
        'REABILITAÇÃO', 'REABILITACAO', 'FISIOTERAPIA',
        'ORTHO', 'ORTHOPEDIC',
    ]
    
    total_removidos = 0
    
    # Construir query para remover has_maternity=1
    conditions = []
    params = []
    
    for term in excluded_terms:
        conditions.append("(UPPER(COALESCE(name, '')) LIKE ? OR UPPER(COALESCE(fantasy_name, '')) LIKE ?)")
        params.extend([f'%{term}%', f'%{term}%'])
    
    if conditions:
        query = f"""
            UPDATE hospitals_cache
            SET has_maternity = 0
            WHERE has_maternity = 1
            AND tipo_unidade IN ('05', '07', 'HOSPITAL')
            AND ({' OR '.join(conditions)})
        """
        
        # Executar atualização
        cursor.execute(query, params)
        removidos = cursor.rowcount
        total_removidos = removidos
        
        print(f"[OK] {removidos} hospitais não relacionados a maternidade removidos")
        
        # Mostrar alguns exemplos
        cursor.execute(f"""
            SELECT cnes_id, name, fantasy_name
            FROM hospitals_cache
            WHERE has_maternity = 0
            AND tipo_unidade IN ('05', '07', 'HOSPITAL')
            AND ({' OR '.join(conditions)})
            LIMIT 10
        """, params)
        
        exemplos = cursor.fetchall()
        if exemplos:
            print("\n[EXEMPLOS] Alguns hospitais corrigidos:")
            for hosp in exemplos:
                nome = hosp['fantasy_name'] or hosp['name'] or 'Sem nome'
                print(f"   - {nome} (CNES: {hosp['cnes_id']})")
    else:
        print("[AVISO] Nenhum termo de exclusão definido")
    
    conn.commit()
    
    # Verificar se ainda há problemas
    print("\n[VERIFICAÇÃO] Verificando se ainda há hospitais não relacionados...")
    problemas_restantes = 0
    for term in ['VISÃO', 'VISAO', 'OFTA', 'ORTOPED']:
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM hospitals_cache
            WHERE has_maternity = 1
            AND tipo_unidade IN ('05', '07', 'HOSPITAL')
            AND (
                UPPER(COALESCE(name, '')) LIKE ?
                OR UPPER(COALESCE(fantasy_name, '')) LIKE ?
            )
        """, (f'%{term}%', f'%{term}%'))
        count = cursor.fetchone()['count']
        if count > 0:
            problemas_restantes += count
            print(f"   [AVISO] Ainda há {count} hospitais com '{term}' marcados como maternidade")
    
    conn.close()
    
    print("\n" + "="*70)
    print("CORREÇÃO CONCLUÍDA")
    print("="*70)
    print(f"[OK] Total de hospitais corrigidos: {total_removidos}")
    if problemas_restantes == 0:
        print("[OK] Nenhum hospital não relacionado restante encontrado!")
    
    return True

if __name__ == "__main__":
    success = fix_non_maternity_hospitals()
    sys.exit(0 if success else 1)
