#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análise do Arquivo tbLeito
Purpose: Entender estrutura e relação com estabelecimentos
"""

import os
import sys
import csv

# Configuração de encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

# Tentar diferentes caminhos
LEITO_PATHS = [
    os.path.join(BASE_DIR, 'data', 'tbLeito202512'),
    os.path.join(BASE_DIR, 'data', 'tbLeito202512.csv'),
]

LEITO_PATH = None
for path in LEITO_PATHS:
    if os.path.exists(path):
        LEITO_PATH = path
        break

def analyze_tbleito():
    """Analisa estrutura do arquivo tbLeito"""
    print("="*70)
    print("ANÁLISE DO ARQUIVO TBLEITO")
    print("="*70)
    print()
    
    if not LEITO_PATH:
        print("❌ Arquivo tbLeito não encontrado!")
        print("💡 Verifique se o arquivo está em um dos seguintes locais:")
        for path in LEITO_PATHS:
            print(f"   - {path}")
        return
    
    print(f"📁 Arquivo: {LEITO_PATH}")
    print()
    
    try:
        with open(LEITO_PATH, 'r', encoding='ISO-8859-1', errors='replace') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            # Ler primeiras linhas
            rows = []
            for i, row in enumerate(reader):
                rows.append(row)
                if i >= 10:  # Ler 10 linhas
                    break
            
            if not rows:
                print("❌ Arquivo vazio ou sem dados")
                return
            
            # Mostrar colunas
            print("[1] COLUNAS DISPONÍVEIS:")
            columns = list(rows[0].keys())
            for col in sorted(columns):
                print(f"   - {col}")
            
            print(f"\n[2] TOTAL DE LINHAS ANALISADAS: {len(rows)}")
            
            # Verificar se há CO_CNES ou relação com estabelecimento
            has_cnes = any('CNES' in col.upper() or 'ESTABELECIMENTO' in col.upper() for col in columns)
            print(f"\n[3] RELAÇÃO COM ESTABELECIMENTO:")
            if has_cnes:
                print("   ✅ Arquivo contém campo de relação com estabelecimento")
                cnes_cols = [col for col in columns if 'CNES' in col.upper() or 'ESTABELECIMENTO' in col.upper()]
                for col in cnes_cols:
                    print(f"      - {col}")
            else:
                print("   ⚠️  Arquivo NÃO contém campo de relação com estabelecimento")
                print("   💡 Pode ser uma tabela de referência (códigos de tipos de leitos)")
            
            # Verificar valores de TP_LEITO e DS_LEITO
            print(f"\n[4] VALORES DE TP_LEITO:")
            tp_leito_values = {}
            for row in rows:
                tp = row.get('TP_LEITO', '').strip()
                if tp:
                    tp_leito_values[tp] = tp_leito_values.get(tp, 0) + 1
            
            for tp, count in sorted(tp_leito_values.items()):
                print(f"   - TP_LEITO={tp}: {count} ocorrências")
            
            print(f"\n[5] VALORES DE DS_LEITO (primeiros 10):")
            ds_leito_values = set()
            for row in rows:
                ds = row.get('DS_LEITO', '').strip()
                if ds:
                    ds_leito_values.add(ds)
            
            for ds in sorted(list(ds_leito_values))[:10]:
                print(f"   - {ds}")
            
            # Verificar se há "OBSTETR" ou "02" (conforme especificação do usuário)
            print(f"\n[6] BUSCANDO LEITOS DE OBSTETRÍCIA:")
            obstet_leitos = []
            for row in rows:
                tp = row.get('TP_LEITO', '').strip()
                ds = row.get('DS_LEITO', '').strip().upper()
                if tp == '02' or 'OBSTETR' in ds:
                    obstet_leitos.append(row)
            
            if obstet_leitos:
                print(f"   ✅ Encontrados {len(obstet_leitos)} leitos de obstetrícia nas primeiras linhas")
                for leito in obstet_leitos[:3]:
                    print(f"      - TP_LEITO={leito.get('TP_LEITO')}, DS_LEITO={leito.get('DS_LEITO')}")
            else:
                print("   ⚠️  Nenhum leito de obstetrícia encontrado nas primeiras linhas")
                print("   💡 Pode ser necessário verificar mais linhas ou o arquivo pode ser apenas referência")
            
            # Mostrar exemplos
            print(f"\n[7] EXEMPLOS DE LINHAS:")
            for i, row in enumerate(rows[:3], 1):
                print(f"\n   Linha {i}:")
                for col in columns:
                    val = row.get(col, '').strip()
                    if val:
                        print(f"      {col}: {val}")
    
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_tbleito()
