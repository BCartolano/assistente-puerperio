# -*- coding: utf-8 -*-
"""
Script de Setup e Importação de Dados CNES (Cadastro Nacional de Estabelecimentos de Saúde)
Integração com DATASUS para identificar hospitais SUS, Privados ou Mistos

Autor: Dev Agent
Data: 2025-01-19
"""

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime
import requests
from pathlib import Path
import argparse

# Adiciona o diretório backend ao path para imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from utils.db_connection import get_db_connection

# Caminho do banco de dados (usando o mesmo do app principal)
DB_PATH = os.path.join(backend_dir, "users.db")


def create_cnes_table(db_path=None):
    """
    Cria a tabela hospitais_oficiais no banco de dados SQLite.
    
    Args:
        db_path: str - Caminho do banco de dados (default: backend/users.db)
    """
    if db_path is None:
        db_path = DB_PATH
    
    print(f"[CNES SETUP] Criando tabela hospitais_oficiais em: {db_path}")
    
    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        
        # Cria a tabela hospitais_oficiais
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hospitais_oficiais (
                cnes_id TEXT PRIMARY KEY,
                nome_fantasia TEXT NOT NULL,
                razao_social TEXT,
                municipio TEXT NOT NULL,
                uf TEXT NOT NULL,
                codigo_municipio TEXT,
                codigo_uf TEXT,
                cep TEXT,
                endereco TEXT,
                bairro TEXT,
                telefone TEXT,
                email TEXT,
                atende_sus INTEGER DEFAULT 0,
                natureza TEXT,
                tipo_unidade TEXT,
                codigo_natureza TEXT,
                data_atualizacao TEXT,
                ativo INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Cria índices para melhorar performance de busca
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_hospitais_nome 
            ON hospitais_oficiais(nome_fantasia)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_hospitais_municipio 
            ON hospitais_oficiais(municipio, uf)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_hospitais_cnes 
            ON hospitais_oficiais(cnes_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_hospitais_sus 
            ON hospitais_oficiais(atende_sus, natureza)
        """)
        
        conn.commit()
        conn.close()
        
        print(f"[CNES SETUP] OK - Tabela hospitais_oficiais criada com sucesso!")
        return True
        
    except Exception as e:
        print(f"[CNES SETUP] ERRO - Erro ao criar tabela: {e}")
        import traceback
        traceback.print_exc()
        return False


def download_cnes_csv(url=None, output_dir=None):
    """
    Baixa arquivo CSV do CNES do portal dados.gov.br ou DATASUS.
    
    Args:
        url: str - URL do arquivo CSV (se None, usa URL padrão do DATASUS)
        output_dir: str - Diretório para salvar o arquivo (default: backend/etl/data)
    
    Returns:
        str - Caminho do arquivo baixado ou None se falhar
    """
    if output_dir is None:
        output_dir = os.path.join(backend_dir, "etl", "data")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # URL do portal de Dados Abertos - Base CNES Estabelecimentos
    # Formato esperado: CSV com dados dos estabelecimentos de saúde
    if url is None:
        # URL exemplo - pode variar conforme atualização do DATASUS
        # Para produção, usar API do dados.gov.br ou FTP do DATASUS
        url = "https://dados.gov.br/dados/conjuntos-dados/base-de-dados-cnes---estabelecimentos"
        print(f"[CNES DOWNLOAD] AVISO: URL não especificada. Usando portal de dados abertos.")
        print(f"[CNES DOWNLOAD] AVISO: Para download automático, especifique a URL do CSV direto.")
        return None
    
    try:
        print(f"[CNES DOWNLOAD] Baixando arquivo de: {url}")
        
        # Headers para simular navegador (evitar bloqueio)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, stream=True, timeout=300)
        response.raise_for_status()
        
        # Extrai nome do arquivo da URL ou usa nome padrão
        filename = url.split('/')[-1] or "tbEstabelecimento.csv"
        if not filename.endswith('.csv'):
            filename = "tbEstabelecimento.csv"
        
        filepath = os.path.join(output_dir, filename)
        
        # Baixa o arquivo em chunks
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        print(f"[CNES DOWNLOAD] Tamanho do arquivo: {total_size / (1024*1024):.2f} MB")
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\r[CNES DOWNLOAD] Progresso: {progress:.1f}%", end='')
        
        print(f"\n[CNES DOWNLOAD] OK - Arquivo baixado: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"[CNES DOWNLOAD] ERRO - Erro ao baixar arquivo: {e}")
        import traceback
        traceback.print_exc()
        return None


def import_cnes_from_csv(csv_path, db_path=None, limit=None):
    """
    Importa dados do CNES de um arquivo CSV para o banco de dados.
    
    Args:
        csv_path: str - Caminho do arquivo CSV
        db_path: str - Caminho do banco de dados (default: backend/users.db)
        limit: int - Limite de registros para importar (None = todos)
    
    Returns:
        int - Número de registros importados
    """
    if db_path is None:
        db_path = DB_PATH
    
    if not os.path.exists(csv_path):
        print(f"[CNES IMPORT] ERRO - Arquivo não encontrado: {csv_path}")
        return 0
    
    print(f"[CNES IMPORT] Lendo arquivo CSV: {csv_path}")
    
    try:
        # Lê o CSV usando pandas (suporta encoding UTF-8 e ISO-8859-1)
        # O arquivo CNES pode vir com separador ';' ou ','
        encodings = ['utf-8', 'latin-1', 'iso-8859-1']
        separators = [';', ',']
        
        df = None
        for encoding in encodings:
            for sep in separators:
                try:
                    # Tenta ler apenas as primeiras linhas para verificar formato
                    df_test = pd.read_csv(csv_path, encoding=encoding, sep=sep, nrows=5)
                    if len(df_test.columns) > 3:  # Arquivo tem colunas suficientes
                        print(f"[CNES IMPORT] Usando encoding: {encoding}, separador: '{sep}'")
                        df = pd.read_csv(csv_path, encoding=encoding, sep=sep, low_memory=False)
                        break
                except:
                    continue
            if df is not None:
                break
        
        if df is None:
            print(f"[CNES IMPORT] ERRO - Não foi possível ler o arquivo CSV com os encodings/separadores testados")
            return 0
        
        print(f"[CNES IMPORT] Linhas no CSV: {len(df)}")
        print(f"[CNES IMPORT] Colunas encontradas: {list(df.columns)[:10]}...")  # Primeiras 10 colunas
        
        # Aplica limite se especificado
        if limit:
            df = df.head(limit)
            print(f"[CNES IMPORT] Limite aplicado: importando {limit} registros")
        
        # Normaliza nomes de colunas (remove espaços, converte para minúscula)
        df.columns = df.columns.str.strip().str.lower()
        
        # Mapeia colunas do CNES para nossa tabela
        # A estrutura do CSV pode variar, então usamos mapeamento flexível
        column_mapping = {
            'cnes_id': ['co_cnes', 'cnes', 'id_cnes'],
            'nome_fantasia': ['no_fantasia', 'fantasia', 'nome_fantasia'],
            'razao_social': ['no_razao_social', 'razao_social'],
            'municipio': ['no_municipio', 'municipio'],
            'uf': ['co_uf', 'uf', 'sg_uf'],
            'codigo_municipio': ['co_municipio', 'codigo_municipio'],
            'codigo_uf': ['co_uf', 'codigo_uf'],
            'cep': ['co_cep', 'cep'],
            'endereco': ['no_logradouro', 'endereco', 'logradouro'],
            'bairro': ['no_bairro', 'bairro'],
            'telefone': ['nu_telefone', 'telefone', 'nu_fax'],
            'email': ['no_email', 'email'],
            'atende_sus': ['co_motivo_desab', 'atende_sus'],  # Lógica inversa: se motivo_desab = null, atende SUS
            'natureza': ['tp_gestao', 'natureza', 'tp_natureza'],
            'tipo_unidade': ['tp_unidade', 'tipo_unidade'],
            'codigo_natureza': ['co_natureza_jur', 'codigo_natureza']
        }
        
        # Mapeia colunas do CSV para nossa estrutura
        mapped_data = []
        for _, row in df.iterrows():
            hospital = {}
            
            # Busca cada campo no mapeamento
            for our_field, possible_names in column_mapping.items():
                value = None
                for col_name in possible_names:
                    if col_name in df.columns:
                        value = row[col_name]
                        if pd.notna(value):
                            break
                hospital[our_field] = value if value is not None else ''
            
            # Lógica especial para atende_sus
            # Se não encontrou coluna direta, tenta inferir de outras colunas
            if not hospital.get('atende_sus') or hospital['atende_sus'] == '':
                # Se tp_gestao é 'Público' ou similar, provavelmente atende SUS
                natureza = str(hospital.get('natureza', '')).upper()
                if 'PUBLICO' in natureza or 'ESTADUAL' in natureza or 'MUNICIPAL' in natureza or 'FEDERAL' in natureza:
                    hospital['atende_sus'] = 1
                elif 'PRIVADO' in natureza:
                    hospital['atende_sus'] = 0  # Pode ser misto ou não, usa 0 por padrão
                else:
                    hospital['atende_sus'] = 0
            
            # Converte atende_sus para inteiro
            try:
                hospital['atende_sus'] = int(hospital['atende_sus']) if hospital['atende_sus'] else 0
            except:
                hospital['atende_sus'] = 0
            
            # Data de atualização
            hospital['data_atualizacao'] = datetime.now().strftime('%Y-%m-%d')
            hospital['ativo'] = 1
            
            # Garante que cnes_id e nome_fantasia existam (campos obrigatórios)
            if hospital.get('cnes_id') and hospital.get('nome_fantasia'):
                mapped_data.append(hospital)
        
        print(f"[CNES IMPORT] Registros mapeados: {len(mapped_data)}")
        
        # Insere no banco de dados
        if not mapped_data:
            print(f"[CNES IMPORT] AVISO - Nenhum registro válido para importar")
            return 0
        
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        
        inserted = 0
        updated = 0
        errors = 0
        
        for hospital in mapped_data:
            try:
                # Verifica se já existe
                cursor.execute("""
                    SELECT cnes_id FROM hospitais_oficiais WHERE cnes_id = ?
                """, (str(hospital['cnes_id']),))
                
                exists = cursor.fetchone()
                
                if exists:
                    # Atualiza registro existente
                    cursor.execute("""
                        UPDATE hospitais_oficiais 
                        SET nome_fantasia = ?, razao_social = ?, municipio = ?, uf = ?,
                            codigo_municipio = ?, codigo_uf = ?, cep = ?, endereco = ?,
                            bairro = ?, telefone = ?, email = ?, atende_sus = ?,
                            natureza = ?, tipo_unidade = ?, codigo_natureza = ?,
                            data_atualizacao = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE cnes_id = ?
                    """, (
                        hospital.get('nome_fantasia', ''),
                        hospital.get('razao_social', ''),
                        hospital.get('municipio', ''),
                        hospital.get('uf', ''),
                        hospital.get('codigo_municipio', ''),
                        hospital.get('codigo_uf', ''),
                        hospital.get('cep', ''),
                        hospital.get('endereco', ''),
                        hospital.get('bairro', ''),
                        hospital.get('telefone', ''),
                        hospital.get('email', ''),
                        hospital.get('atende_sus', 0),
                        hospital.get('natureza', ''),
                        hospital.get('tipo_unidade', ''),
                        hospital.get('codigo_natureza', ''),
                        hospital.get('data_atualizacao', ''),
                        str(hospital['cnes_id'])
                    ))
                    updated += 1
                else:
                    # Insere novo registro
                    cursor.execute("""
                        INSERT INTO hospitais_oficiais (
                            cnes_id, nome_fantasia, razao_social, municipio, uf,
                            codigo_municipio, codigo_uf, cep, endereco, bairro,
                            telefone, email, atende_sus, natureza, tipo_unidade,
                            codigo_natureza, data_atualizacao, ativo
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        str(hospital['cnes_id']),
                        hospital.get('nome_fantasia', ''),
                        hospital.get('razao_social', ''),
                        hospital.get('municipio', ''),
                        hospital.get('uf', ''),
                        hospital.get('codigo_municipio', ''),
                        hospital.get('codigo_uf', ''),
                        hospital.get('cep', ''),
                        hospital.get('endereco', ''),
                        hospital.get('bairro', ''),
                        hospital.get('telefone', ''),
                        hospital.get('email', ''),
                        hospital.get('atende_sus', 0),
                        hospital.get('natureza', ''),
                        hospital.get('tipo_unidade', ''),
                        hospital.get('codigo_natureza', ''),
                        hospital.get('data_atualizacao', ''),
                        hospital.get('ativo', 1)
                    ))
                    inserted += 1
                
            except Exception as e:
                errors += 1
                if errors <= 5:  # Mostra apenas os primeiros 5 erros
                    print(f"[CNES IMPORT] AVISO - Erro ao inserir registro {hospital.get('cnes_id')}: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"[CNES IMPORT] OK - Importação concluída!")
        print(f"[CNES IMPORT]   - Novos registros: {inserted}")
        print(f"[CNES IMPORT]   - Registros atualizados: {updated}")
        print(f"[CNES IMPORT]   - Erros: {errors}")
        
        return inserted + updated
        
    except Exception as e:
        print(f"[CNES IMPORT] ERRO - Erro ao importar dados: {e}")
        import traceback
        traceback.print_exc()
        return 0


def seed_sample_data(db_path=None):
    """
    Cria dados de exemplo (seed) com principais hospitais das capitais e SJC.
    Útil para MVP quando o download completo não está disponível.
    
    Args:
        db_path: str - Caminho do banco de dados (default: backend/users.db)
    
    Returns:
        int - Número de registros inseridos
    """
    if db_path is None:
        db_path = DB_PATH
    
    print(f"[CNES SEED] Criando dados de exemplo (seed)...")
    
    # Dados de exemplo - principais hospitais das capitais e SJC
    sample_hospitals = [
        {
            'cnes_id': 'SEED001',
            'nome_fantasia': 'Hospital das Clínicas - FMUSP',
            'razao_social': 'Hospital das Clínicas da Faculdade de Medicina da Universidade de São Paulo',
            'municipio': 'São Paulo',
            'uf': 'SP',
            'codigo_municipio': '3550308',
            'codigo_uf': '35',
            'atende_sus': 1,
            'natureza': 'Público',
            'tipo_unidade': 'Hospital Geral'
        },
        {
            'cnes_id': 'SEED002',
            'nome_fantasia': 'Hospital Municipal São José dos Campos',
            'razao_social': 'Hospital Municipal de São José dos Campos',
            'municipio': 'São José dos Campos',
            'uf': 'SP',
            'codigo_municipio': '3549904',
            'codigo_uf': '35',
            'atende_sus': 1,
            'natureza': 'Público',
            'tipo_unidade': 'Hospital Geral'
        },
        {
            'cnes_id': 'SEED003',
            'nome_fantasia': 'Hospital Albert Einstein',
            'razao_social': 'Sociedade Beneficente Israelita Brasileira Albert Einstein',
            'municipio': 'São Paulo',
            'uf': 'SP',
            'codigo_municipio': '3550308',
            'codigo_uf': '35',
            'atende_sus': 0,
            'natureza': 'Privado',
            'tipo_unidade': 'Hospital Geral'
        },
        {
            'cnes_id': 'SEED004',
            'nome_fantasia': 'Hospital Samaritano',
            'razao_social': 'Hospital Samaritano Paulista',
            'municipio': 'São Paulo',
            'uf': 'SP',
            'codigo_municipio': '3550308',
            'codigo_uf': '35',
            'atende_sus': 0,
            'natureza': 'Privado',
            'tipo_unidade': 'Hospital Geral'
        },
        {
            'cnes_id': 'SEED005',
            'nome_fantasia': 'Santa Casa de Misericórdia de São José dos Campos',
            'razao_social': 'Santa Casa de Misericórdia de São José dos Campos',
            'municipio': 'São José dos Campos',
            'uf': 'SP',
            'codigo_municipio': '3549904',
            'codigo_uf': '35',
            'atende_sus': 1,
            'natureza': 'Misto',
            'tipo_unidade': 'Hospital Geral'
        },
        {
            'cnes_id': 'SEED006',
            'nome_fantasia': 'Hospital do Coração - HCor',
            'razao_social': 'Hospital do Coração',
            'municipio': 'São Paulo',
            'uf': 'SP',
            'codigo_municipio': '3550308',
            'codigo_uf': '35',
            'atende_sus': 0,
            'natureza': 'Privado',
            'tipo_unidade': 'Hospital Especializado'
        }
    ]
    
    try:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        
        inserted = 0
        for hospital in sample_hospitals:
            try:
                # Verifica se já existe
                cursor.execute("SELECT cnes_id FROM hospitais_oficiais WHERE cnes_id = ?", 
                             (hospital['cnes_id'],))
                
                if cursor.fetchone():
                    continue  # Já existe, pula
                
                # Insere novo registro
                cursor.execute("""
                    INSERT INTO hospitais_oficiais (
                        cnes_id, nome_fantasia, razao_social, municipio, uf,
                        codigo_municipio, codigo_uf, atende_sus, natureza,
                        tipo_unidade, data_atualizacao, ativo
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    hospital['cnes_id'],
                    hospital['nome_fantasia'],
                    hospital.get('razao_social', ''),
                    hospital['municipio'],
                    hospital['uf'],
                    hospital['codigo_municipio'],
                    hospital['codigo_uf'],
                    hospital['atende_sus'],
                    hospital['natureza'],
                    hospital['tipo_unidade'],
                    datetime.now().strftime('%Y-%m-%d'),
                    1
                ))
                inserted += 1
            except Exception as e:
                print(f"[CNES SEED] AVISO - Erro ao inserir {hospital['nome_fantasia']}: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"[CNES SEED] OK - {inserted} registros de exemplo inseridos!")
        return inserted
        
    except Exception as e:
        print(f"[CNES SEED] ERRO - Erro ao criar seed: {e}")
        import traceback
        traceback.print_exc()
        return 0


def main():
    """
    Função principal - executa setup completo do CNES.
    """
    parser = argparse.ArgumentParser(description='Setup e importação de dados CNES/DATASUS')
    parser.add_argument('--action', '-a', choices=['create', 'seed', 'import'], 
                       help='Ação a executar: create (apenas tabela), seed (dados exemplo), import (CSV)')
    parser.add_argument('--csv', '-c', type=str, help='Caminho do arquivo CSV para importar')
    parser.add_argument('--limit', '-l', type=int, help='Limite de registros para importar')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Modo interativo (pergunta ao usuário)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("CNES SETUP - Integração DATASUS")
    print("=" * 60)
    
    # 1. Cria tabela
    if not create_cnes_table():
        print("ERRO - Falha ao criar tabela. Abortando.")
        return
    
    # 2. Executa ação baseada em argumentos ou modo interativo
    if args.interactive or not args.action:
        # Modo interativo
        print("\nEscolha uma opção:")
        print("1. Importar dados de um arquivo CSV")
        print("2. Criar dados de exemplo (seed) para MVP")
        print("3. Apenas criar a tabela (não importar dados)")
        
        try:
            choice = input("\nDigite o número da opção (1, 2 ou 3): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nOperação cancelada.")
            return
        
        if choice == '1':
            csv_path = input("Digite o caminho do arquivo CSV: ").strip()
            if os.path.exists(csv_path):
                limit_input = input("Limite de registros para importar (Enter = todos): ").strip()
                limit = int(limit_input) if limit_input.isdigit() else None
                import_cnes_from_csv(csv_path, limit=limit)
            else:
                print(f"ERRO - Arquivo não encontrado: {csv_path}")
        
        elif choice == '2':
            seed_sample_data()
        
        elif choice == '3':
            print("OK - Tabela criada. Nenhum dado importado.")
        
        else:
            print("ERRO - Opção inválida.")
    
    else:
        # Modo não-interativo (argumentos de linha de comando)
        if args.action == 'create':
            print("OK - Tabela criada. Nenhum dado importado.")
        
        elif args.action == 'seed':
            seed_sample_data()
        
        elif args.action == 'import':
            if not args.csv:
                print("ERRO - É necessário especificar o caminho do CSV com --csv")
                return
            
            if not os.path.exists(args.csv):
                print(f"ERRO - Arquivo não encontrado: {args.csv}")
                return
            
            import_cnes_from_csv(args.csv, limit=args.limit)
    
    print("\n" + "=" * 60)
    print("Setup concluído!")
    print("=" * 60)


if __name__ == "__main__":
    main()
