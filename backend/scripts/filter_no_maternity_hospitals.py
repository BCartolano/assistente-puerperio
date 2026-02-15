#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filtragem de Hospitais SEM Ala da Maternidade
Purpose: Identificar e remover has_maternity=1 de hospitais que não têm maternidade
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

def filter_no_maternity_hospitals():
    """Filtra hospitais que não têm Ala da Maternidade"""
    print("="*70)
    print("FILTRAGEM DE HOSPITAIS SEM ALA DA MATERNIDADE")
    print("="*70)
    print()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Termos que indicam que NÃO tem maternidade (lista completa)
    excluded_keywords = [
        # Especialidades específicas (não têm maternidade)
        'PSIQUIATRIA', 'PSIQUIATRICO', 'MENTAL',
        'ORTOPEDIA', 'ORTODOXIA', 'TRAUMATOLOGIA', 'ORTOPEDICO', 'ORTOPEDISTA',
        'ORTO', 'TRAUMATO', 'FRATURA', 'OSSO', 'OSSOS', 'COLUNA', 'JOELHO', 'QUADRIL', 'OMBRO',
        'ORTHO', 'ORTHOPEDIC',
        'VISÃO', 'VISAO', 'VISUAL', 'OFTA', 'OFTALMO', 'OLHO', 'OLHOS',
        'RETINA', 'CÓRNEA', 'CORNEA', 'CATARATA', 'GLAUCOMA',
        'CARDIOLOGIA', 'CARDIACO', 'CARDIAC', 'CORAÇÃO', 'CORACAO', 'CIRURGIA CARDIACA',
        'ONCOLOGIA', 'ONCOLOGICO', 'CANCER', 'CÂNCER', 'TRATAMENTO CANCER', 'INSTITUTO DO CANCER',
        'INFANTIL', 'PEDIATRIA', 'PEDIATRICO', 'PEDIATRICA', 'PEDIATRIC',
        'CRIANCA', 'CRIANÇA', 'BABY', 'BEBE', 'BEBÊ',
        'REABILITACAO', 'FISIOTERAPIA',
        'CIRURGIA PLASTICA', 'ESTETICA',
        # Outros termos que indicam ausência de maternidade
        'OTORRINOLARINGOLOG', 'OTORRINO',
        'TERAPIA OCUPACIONAL',
        'PSICOLOGIA', 'PSICÓLOGO', 'PSICÓLOGA',
        'GRUPAMENTO DE APOIO', 'GRUPAMENTO APOIO',
        'CENTRO OCUPACIONAL', 'CENTRO DE TREINAMENTO',
        'CENTRO OCUPACIONAL E DE TREINAMENTO',
        'CENTRO DE APOIO', 'CENTRO APOIO',
        'DIVISÃO', 'DIVISAO',
        'GRUPAMENTO',
        'CLINICA DE TERAPIA', 'CLÍNICA DE TERAPIA',
    ]
    
    total_removidos = 0
    
    print("[1] Buscando hospitais com has_maternity=1 que contêm termos excluídos...")
    
    # Construir condições para busca
    conditions = []
    params = []
    
    for term in excluded_keywords:
        conditions.append("(UPPER(COALESCE(name, '')) LIKE ? OR UPPER(COALESCE(fantasy_name, '')) LIKE ?)")
        params.extend([f'%{term}%', f'%{term}%'])
    
    if conditions:
        # Contar antes
        cursor.execute(f"""
            SELECT COUNT(*) as count
            FROM hospitals_cache
            WHERE has_maternity = 1
            AND tipo_unidade IN ('05', '07', 'HOSPITAL')
            AND ({' OR '.join(conditions)})
        """, params)
        
        count_before = cursor.fetchone()['count']
        
        if count_before > 0:
            print(f"   [ENCONTRADOS] {count_before} hospitais sem Ala da Maternidade")
            
            # Mostrar alguns exemplos
            cursor.execute(f"""
                SELECT cnes_id, name, fantasy_name, tipo_unidade
                FROM hospitals_cache
                WHERE has_maternity = 1
                AND tipo_unidade IN ('05', '07', 'HOSPITAL')
                AND ({' OR '.join(conditions)})
                LIMIT 10
            """, params)
            
            exemplos = cursor.fetchall()
            print("\n   [EXEMPLOS]:")
            for hosp in exemplos:
                nome = hosp['fantasy_name'] or hosp['name'] or 'Sem nome'
                print(f"      - {nome} (CNES: {hosp['cnes_id']}, Tipo: {hosp['tipo_unidade']})")
            
            # Remover has_maternity=1
            print(f"\n[2] Removendo has_maternity=1 destes hospitais...")
            cursor.execute(f"""
                UPDATE hospitals_cache
                SET has_maternity = 0
                WHERE has_maternity = 1
                AND tipo_unidade IN ('05', '07', 'HOSPITAL')
                AND ({' OR '.join(conditions)})
            """, params)
            
            removidos = cursor.rowcount
            total_removidos += removidos
            print(f"   [OK] {removidos} hospitais removidos da busca de maternidades")
        else:
            print("   [OK] Nenhum hospital com termos excluídos encontrado")
    
    # Verificar hospitais que são claramente especializados (não gerais)
    print("\n[3] Verificando hospitais especializados que não têm maternidade...")
    
    # Hospitais que são claramente especializados e não têm maternidade
    specialized_keywords = [
        'HOSPITAL DE TRAUMA', 'HOSPITAL TRAUMA',
        'HOSPITAL ORTOPEDICO', 'HOSPITAL ORTOPÉDICO',
        'HOSPITAL CARDIOLOGICO', 'HOSPITAL CARDÍACO',
        'HOSPITAL ONCOLOGICO', 'HOSPITAL ONCOLÓGICO',
        'HOSPITAL PSIQUIATRICO', 'HOSPITAL PSIQUIÁTRICO',
        'HOSPITAL DE OLHOS', 'HOSPITAL DOS OLHOS',
        'INSTITUTO DE OLHOS', 'INSTITUTO DOS OLHOS',
    ]
    
    specialized_conditions = []
    specialized_params = []
    
    for term in specialized_keywords:
        specialized_conditions.append("(UPPER(COALESCE(name, '')) LIKE ? OR UPPER(COALESCE(fantasy_name, '')) LIKE ?)")
        specialized_params.extend([f'%{term}%', f'%{term}%'])
    
    if specialized_conditions:
        cursor.execute(f"""
            SELECT COUNT(*) as count
            FROM hospitals_cache
            WHERE has_maternity = 1
            AND tipo_unidade IN ('05', '07', 'HOSPITAL')
            AND ({' OR '.join(specialized_conditions)})
        """, specialized_params)
        
        specialized_count = cursor.fetchone()['count']
        
        if specialized_count > 0:
            print(f"   [ENCONTRADOS] {specialized_count} hospitais especializados sem maternidade")
            
            cursor.execute(f"""
                UPDATE hospitals_cache
                SET has_maternity = 0
                WHERE has_maternity = 1
                AND tipo_unidade IN ('05', '07', 'HOSPITAL')
                AND ({' OR '.join(specialized_conditions)})
            """, specialized_params)
            
            specialized_removed = cursor.rowcount
            total_removidos += specialized_removed
            print(f"   [OK] {specialized_removed} hospitais especializados removidos")
        else:
            print("   [OK] Nenhum hospital especializado encontrado")
    
    conn.commit()
    
    # Verificação final
    print("\n[4] Verificação final...")
    cursor.execute("""
        SELECT COUNT(*) as total
        FROM hospitals_cache
        WHERE has_maternity = 1
        AND tipo_unidade IN ('05', '07', 'HOSPITAL')
    """)
    total_maternidade = cursor.fetchone()['total']
    
    conn.close()
    
    print("\n" + "="*70)
    print("FILTRAGEM CONCLUÍDA")
    print("="*70)
    print(f"[OK] Total de hospitais removidos: {total_removidos}")
    print(f"[INFO] Total de hospitais com maternidade restantes: {total_maternidade}")
    
    if total_removidos > 0:
        print(f"\n[SUCESSO] {total_removidos} hospitais sem Ala da Maternidade foram filtrados!")
    else:
        print("\n[INFO] Nenhum hospital adicional precisou ser removido")
    
    return True

if __name__ == "__main__":
    success = filter_no_maternity_hospitals()
    sys.exit(0 if success else 1)
