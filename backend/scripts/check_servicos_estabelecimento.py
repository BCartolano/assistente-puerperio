#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar Serviços no tbEstabelecimento
Purpose: Verificar se há campo CO_SERVICO e valores relacionados a obstetrícia
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
ESTAB_PATHS = [
    os.path.join(BASE_DIR, 'data', 'tbEstabelecimento202512'),
    os.path.join(BASE_DIR, 'data', 'tbEstabelecimento202512.csv'),
]

ESTAB_PATH = None
for path in ESTAB_PATHS:
    if os.path.exists(path):
        ESTAB_PATH = path
        break

def check_servicos():
    """Verifica serviços no arquivo tbEstabelecimento"""
    print("="*70)
    print("VERIFICAÇÃO DE SERVIÇOS NO TBESTABELECIMENTO")
    print("="*70)
    print()
    
    if not ESTAB_PATH:
        print("❌ Arquivo tbEstabelecimento não encontrado!")
        return
    
    print(f"📁 Arquivo: {ESTAB_PATH}")
    print()
    
    try:
        with open(ESTAB_PATH, 'r', encoding='ISO-8859-1', errors='replace') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            # Ler primeira linha
            row = next(reader)
            
            # Buscar colunas relacionadas a serviços
            servico_cols = [k for k in row.keys() if 'SERV' in k.upper()]
            
            print("[1] COLUNAS RELACIONADAS A SERVIÇOS:")
            if servico_cols:
                for col in servico_cols:
                    print(f"   - {col}")
            else:
                print("   ⚠️  Nenhuma coluna de serviços encontrada")
            
            # Buscar todas as colunas
            all_cols = list(row.keys())
            print(f"\n[2] TOTAL DE COLUNAS: {len(all_cols)}")
            print(f"[3] PRIMEIRAS 30 COLUNAS:")
            for i, col in enumerate(sorted(all_cols)[:30], 1):
                print(f"   {i:2d}. {col}")
            
            # Verificar se há CO_SERVICO
            if 'CO_SERVICO' in all_cols:
                print(f"\n[4] ✅ CO_SERVICO encontrado!")
                # Ler algumas linhas para ver valores
                f.seek(0)
                reader = csv.DictReader(f, delimiter=';')
                servicos_141 = []
                for i, r in enumerate(reader):
                    servico = r.get('CO_SERVICO', '').strip()
                    if '141' in servico or servico == '141':
                        cnes = r.get('CO_CNES', '').strip()
                        nome = r.get('NO_FANTASIA', '').strip() or r.get('NO_RAZAO_SOCIAL', '').strip()
                        servicos_141.append((cnes, nome, servico))
                        if len(servicos_141) >= 5:
                            break
                
                if servicos_141:
                    print(f"   ✅ Encontrados estabelecimentos com CO_SERVICO=141 (Obstetrícia):")
                    for cnes, nome, serv in servicos_141:
                        print(f"      - CNES: {cnes}, Nome: {nome[:50]}, Serviços: {serv}")
                else:
                    print("   ⚠️  Nenhum estabelecimento com CO_SERVICO=141 encontrado nas primeiras linhas")
            else:
                print(f"\n[4] ⚠️  CO_SERVICO NÃO encontrado nas colunas")
                print("   💡 Pode estar com nome diferente ou em outro arquivo")
    
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_servicos()
