#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script temporário para inspecionar estrutura do CSV do CNES
Purpose: Ler cabeçalhos do arquivo CSV para identificar nomes das colunas
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

# Possíveis caminhos do arquivo CSV
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
POSSIBLE_PATHS = [
    os.path.join(BASE_DIR, 'BASE_DE_DADOS_CNES_202512', 'tbEstabelecimento202512.csv.csv'),
    os.path.join(BASE_DIR, 'BASE_DE_DADOS_CNES_202512', 'tbEstabelecimento202512.csv'),
    os.path.join(BASE_DIR, 'data', 'tbEstabelecimento202512.csv'),
    os.path.join(BASE_DIR, 'tbEstabelecimento202512.csv'),
]

def find_csv_file():
    """Procura o arquivo CSV em locais possíveis"""
    # Primeiro tenta caminhos específicos
    for path in POSSIBLE_PATHS:
        if os.path.exists(path):
            return path
    
    # Se não encontrou, procura por arquivos que começam com tbEstabelecimento na pasta BASE_DE_DADOS
    base_db_dir = os.path.join(BASE_DIR, 'BASE_DE_DADOS_CNES_202512')
    if os.path.exists(base_db_dir):
        import glob
        csv_files = glob.glob(os.path.join(base_db_dir, 'tbEstabelecimento*.csv*'))
        if csv_files:
            return csv_files[0]  # Retorna o primeiro encontrado
    
    return None

def inspect_csv_headers():
    """Lê apenas a primeira linha do CSV para obter os cabeçalhos"""
    
    print("=" * 80)
    print("🔍 INSPETOR DE CSV - CNES")
    print("=" * 80)
    
    # Procurar arquivo CSV
    CSV_PATH = find_csv_file()
    
    if not CSV_PATH:
        print(f"\n❌ ERRO: Arquivo CSV não encontrado!")
        print(f"\n📂 Procurou nos seguintes locais:")
        for path in POSSIBLE_PATHS:
            exists = "✅" if os.path.exists(path) else "❌"
            print(f"   {exists} {path}")
        
        print(f"\n💡 INSTRUÇÕES:")
        print(f"   1. Baixe o arquivo tbEstabelecimento202512.csv do DataSUS")
        print(f"   2. Coloque o arquivo em uma das pastas acima")
        print(f"   3. Ou atualize o caminho no script")
        print(f"\n🔗 Fonte dos dados: https://dados.gov.br/dados/conjuntos-dados/cadastro-nacional-de-estabelecimentos-de-saude-cnes")
        return
    
    print(f"✅ Arquivo encontrado!")
    print(f"📊 Tamanho: {os.path.getsize(CSV_PATH) / (1024*1024):.2f} MB")
    print("\n" + "=" * 80)
    
    # Ler primeira linha (cabeçalhos)
    try:
        with open(CSV_PATH, 'r', encoding='ISO-8859-1') as f:
            # Ler primeira linha
            first_line = f.readline()
            
            # Parse do CSV com separador ;
            reader = csv.reader([first_line], delimiter=';')
            headers = next(reader)
            
            print(f"\n📋 COLUNAS ENCONTRADAS ({len(headers)} colunas):\n")
            print("=" * 80)
            
            # Listar todas as colunas com índice
            for i, header in enumerate(headers, 1):
                # Limpar espaços em branco
                header_clean = header.strip()
                print(f"{i:3d}. {header_clean}")
            
            print("=" * 80)
            print(f"\n✅ Total: {len(headers)} colunas\n")
            
            # Buscar colunas importantes
            print("🔎 COLUNAS IMPORTANTES (buscando...)\n")
            
            important_cols = {
                'latitude': ['NU_LATITUDE', 'LATITUDE', 'VL_LATITUDE', 'CO_LATITUDE'],
                'longitude': ['NU_LONGITUDE', 'LONGITUDE', 'VL_LONGITUDE', 'CO_LONGITUDE'],
                'nome': ['NO_FANTASIA', 'NO_FANTASIA_FANTASIA', 'NM_FANTASIA', 'NO_ESTABELECIMENTO'],
                'cnes': ['CO_CNES', 'CNES', 'NU_CNES', 'CO_UNIDADE'],
                'endereco': ['NO_LOGRADOURO', 'DS_ENDERECO', 'NO_ENDERECO'],
                'municipio': ['NO_MUNICIPIO', 'NO_CIDADE', 'MUNICIPIO'],
                'uf': ['CO_UF', 'UF', 'SG_UF'],
                'tipo': ['CO_TIPO_UNIDADE', 'TP_UNIDADE', 'CO_TIPO'],
                'natureza': ['CO_NATUREZA_JURIDICA', 'NATUREZA_JURIDICA', 'CO_NATUREZA'],
            }
            
            found_cols = {}
            for key, variants in important_cols.items():
                for variant in variants:
                    if variant in headers:
                        found_cols[key] = variant
                        break
            
            if found_cols:
                print("✅ Colunas importantes encontradas:\n")
                for key, col_name in found_cols.items():
                    idx = headers.index(col_name) + 1
                    print(f"   • {key.upper():12s} → {col_name:30s} (coluna #{idx})")
                print()
            else:
                print("⚠️ Nenhuma coluna importante encontrada com nomes esperados.")
                print("   Verifique manualmente a lista acima.\n")
            
    except UnicodeDecodeError as e:
        print(f"❌ ERRO de encoding: {e}")
        print("   Tentando com UTF-8...")
        try:
            with open(CSV_PATH, 'r', encoding='utf-8') as f:
                first_line = f.readline()
                reader = csv.reader([first_line], delimiter=';')
                headers = next(reader)
                print(f"\n✅ Funcionou com UTF-8! ({len(headers)} colunas)")
        except Exception as e2:
            print(f"❌ Também falhou com UTF-8: {e2}")
    except Exception as e:
        print(f"❌ ERRO ao ler arquivo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    inspect_csv_headers()
