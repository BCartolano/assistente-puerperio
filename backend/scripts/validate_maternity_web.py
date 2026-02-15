#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validação Web de Hospitais com Ala da Maternidade
Purpose: Verificar via web se hospitais realmente têm Ala da Maternidade
"""

import os
import sys
import sqlite3
import time
from typing import Dict, List, Optional, Tuple

# Configuração de encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'cnes_cache.db')

# Termos de busca para confirmar maternidade
MATERNITY_KEYWORDS = [
    'maternidade', 'obstetrícia', 'obstetricia', 'parto', 'pré-natal', 'pre-natal',
    'ginecologia', 'ginecología', 'neonatologia', 'neonatología',
    'centro obstétrico', 'centro obstetrico', 'ala da maternidade',
    'atendimento obstétrico', 'atendimento obstetrico'
]

# Termos que indicam NÃO tem maternidade
NO_MATERNITY_KEYWORDS = [
    'não realiza parto', 'nao realiza parto', 'sem maternidade',
    'especializado em', 'apenas', 'somente'
]


def get_hospitals_batch(limit: int = 10, offset: int = 0) -> List[Dict]:
    """Obtém um lote de hospitais para validação"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT cnes_id, name, fantasy_name, address, city, state, telefone
        FROM hospitals_cache
        WHERE has_maternity = 1
        AND tipo_unidade IN ('05', '07', 'HOSPITAL')
        ORDER BY cnes_id
        LIMIT ? OFFSET ?
    """, (limit, offset))
    
    hospitals = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return hospitals


def build_search_query(hospital: Dict) -> str:
    """Constrói query de busca para o hospital"""
    name = hospital.get('fantasy_name') or hospital.get('name') or ''
    city = hospital.get('city') or ''
    state = hospital.get('state') or ''
    
    # Construir query: nome do hospital + cidade + estado + "maternidade"
    query_parts = [name]
    if city:
        query_parts.append(city)
    if state:
        query_parts.append(state)
    query_parts.append('maternidade')
    
    return ' '.join(filter(None, query_parts))


def validate_maternity_web_batch(hospitals: List[Dict], batch_num: int) -> Dict:
    """
    Valida um lote de hospitais via busca web
    
    Returns:
        Dict com estatísticas do lote
    """
    print(f"\n{'='*70}")
    print(f"VALIDAÇÃO WEB - LOTE {batch_num}")
    print(f"{'='*70}")
    print(f"Processando {len(hospitals)} hospitais...\n")
    
    confirmed = []
    not_confirmed = []
    errors = []
    
    for i, hospital in enumerate(hospitals, 1):
        cnes_id = hospital.get('cnes_id')
        name = hospital.get('fantasy_name') or hospital.get('name') or 'Sem nome'
        
        print(f"[{i}/{len(hospitals)}] Verificando: {name} (CNES: {cnes_id})")
        
        try:
            # Construir query de busca
            search_query = build_search_query(hospital)
            print(f"   Busca: '{search_query}'")
            
            # NOTA: Esta função será chamada externamente via web_search tool
            # Por enquanto, apenas estrutura a busca
            # A busca real será feita pelo agente usando web_search
            
            # Simular resultado (será substituído pela busca real)
            # Por enquanto, marcar como "pendente" para busca manual
            print(f"   [PENDENTE] Aguardando busca web...")
            
            # Estrutura para resultado
            result = {
                'cnes_id': cnes_id,
                'name': name,
                'search_query': search_query,
                'status': 'pending'  # pending, confirmed, not_confirmed, error
            }
            
            # Adicionar delay para não sobrecarregar
            time.sleep(0.5)
            
        except Exception as e:
            print(f"   [ERRO] {str(e)}")
            errors.append({
                'cnes_id': cnes_id,
                'name': name,
                'error': str(e)
            })
    
    return {
        'batch_num': batch_num,
        'total': len(hospitals),
        'confirmed': confirmed,
        'not_confirmed': not_confirmed,
        'errors': errors
    }


def get_total_hospitals() -> int:
    """Retorna total de hospitais com has_maternity=1"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM hospitals_cache
        WHERE has_maternity = 1
        AND tipo_unidade IN ('05', '07', 'HOSPITAL')
    """)
    
    total = cursor.fetchone()[0]
    conn.close()
    
    return total


def main():
    """Função principal - estrutura para validação web"""
    print("="*70)
    print("VALIDAÇÃO WEB DE HOSPITAIS COM ALA DA MATERNIDADE")
    print("="*70)
    print()
    
    total = get_total_hospitals()
    print(f"[INFO] Total de hospitais para validar: {total}")
    print(f"[INFO] Processando em lotes de 10 hospitais")
    print()
    
    # Obter primeiro lote para exemplo
    batch_size = 10
    hospitals = get_hospitals_batch(limit=batch_size, offset=0)
    
    if not hospitals:
        print("[AVISO] Nenhum hospital encontrado para validação")
        return
    
    print(f"[LOTE 1] Preparando {len(hospitals)} hospitais para validação web...")
    print()
    
    # Mostrar exemplos de queries que serão usadas
    print("EXEMPLOS DE QUERIES DE BUSCA:")
    for i, hospital in enumerate(hospitals[:5], 1):
        query = build_search_query(hospital)
        name = hospital.get('fantasy_name') or hospital.get('name') or 'Sem nome'
        print(f"   {i}. {name}")
        print(f"      Query: '{query}'")
    
    print()
    print("[INFO] Use web_search tool para buscar informações sobre cada hospital")
    print("[INFO] Verifique se há menção a 'maternidade', 'obstetrícia', 'parto', etc.")
    print()
    print("[PRÓXIMOS PASSOS]")
    print("1. Para cada hospital, fazer busca web com a query gerada")
    print("2. Analisar resultados para confirmar presença de maternidade")
    print("3. Atualizar has_maternity no banco baseado nos resultados")
    print("4. Gerar relatório de validação")


if __name__ == "__main__":
    main()
