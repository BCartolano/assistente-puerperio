#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificação Final: Apenas Hospitais com Maternidade
Purpose: Verificar se não há hospitais de Visão, Ortopedia, Infantis, etc.
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

def verify_maternity_only():
    """Verifica se apenas hospitais com maternidade estão marcados"""
    print("="*70)
    print("VERIFICAÇÃO FINAL: APENAS HOSPITAIS COM MATERNIDADE")
    print("="*70)
    print()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Todos os termos que devem ser excluídos
    excluded_terms = {
        'Visão/Oftalmologia': ['VISÃO', 'VISAO', 'VISUAL', 'OFTA', 'OFTALMO', 'OLHO', 'OLHOS', 'RETINA', 'CÓRNEA', 'CORNEA', 'CATARATA', 'GLAUCOMA'],
        'Ortopedia': ['ORTO', 'ORTOD', 'ORTOPED', 'ORTOPÉD', 'TRAUMATO', 'FRATURA', 'OSSO', 'OSSOS', 'COLUNA', 'JOELHO', 'QUADRIL', 'OMBRO', 'ORTHO', 'ORTHOPEDIC'],
        'Infantil/Pediátrico': ['INFANTIL', 'PEDIATRIA', 'PEDIATRICO', 'PEDIATRICA', 'PEDIATRIC', 'CRIANCA', 'CRIANÇA', 'BABY', 'BEBE', 'BEBÊ'],
        'Cardiologia': ['CARDIOL', 'CARDIAC', 'CORAÇÃO', 'CORACAO', 'CIRURGIA CARDIACA'],
        'Oncologia': ['ONCO', 'CANCER', 'CÂNCER', 'TRATAMENTO CANCER', 'INSTITUTO DO CANCER'],
        'Psiquiatria': ['PSIQUIATR', 'MENTAL'],
        'Outros': ['REABILITACAO', 'FISIOTERAPIA', 'CIRURGIA PLASTICA', 'ESTETICA']
    }
    
    total_problemas = 0
    
    print("[VERIFICAÇÃO] Buscando hospitais não relacionados a maternidade...")
    print()
    
    for categoria, terms in excluded_terms.items():
        conditions = []
        params = []
        
        for term in terms:
            conditions.append("(UPPER(COALESCE(name, '')) LIKE ? OR UPPER(COALESCE(fantasy_name, '')) LIKE ?)")
            params.extend([f'%{term}%', f'%{term}%'])
        
        if conditions:
            cursor.execute(f"""
                SELECT COUNT(*) as count
                FROM hospitals_cache
                WHERE has_maternity = 1
                AND tipo_unidade IN ('05', '07', 'HOSPITAL')
                AND ({' OR '.join(conditions)})
            """, params)
            
            count = cursor.fetchone()['count']
            
            if count > 0:
                print(f"   ❌ {categoria}: {count} hospitais encontrados")
                total_problemas += count
                
                # Mostrar exemplos
                cursor.execute(f"""
                    SELECT cnes_id, name, fantasy_name
                    FROM hospitals_cache
                    WHERE has_maternity = 1
                    AND tipo_unidade IN ('05', '07', 'HOSPITAL')
                    AND ({' OR '.join(conditions)})
                    LIMIT 3
                """, params)
                
                exemplos = cursor.fetchall()
                for hosp in exemplos:
                    nome = hosp['fantasy_name'] or hosp['name'] or 'Sem nome'
                    print(f"      - {nome} (CNES: {hosp['cnes_id']})")
            else:
                print(f"   ✅ {categoria}: 0 hospitais encontrados")
    
    # Contar total de hospitais com maternidade
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM hospitals_cache
        WHERE has_maternity = 1
        AND tipo_unidade IN ('05', '07', 'HOSPITAL')
    """)
    total_maternidade = cursor.fetchone()['total']
    
    conn.close()
    
    print("\n" + "="*70)
    print("RESUMO")
    print("="*70)
    print(f"Total de hospitais com maternidade: {total_maternidade}")
    print(f"Total de problemas encontrados: {total_problemas}")
    
    if total_problemas == 0:
        print("\n✅ [SUCESSO] Apenas hospitais com Ala da Maternidade estão marcados!")
        return True
    else:
        print(f"\n❌ [ATENÇÃO] {total_problemas} hospitais não relacionados ainda estão marcados como maternidade")
        return False

if __name__ == "__main__":
    success = verify_maternity_only()
    sys.exit(0 if success else 1)
