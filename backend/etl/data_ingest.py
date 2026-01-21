#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Ingestão de Dados Reais do CNES
Purpose: Processar arquivo CSV oficial do DataSUS e popular banco local
Author: Dev Agent (baseado no mapeamento de colunas do CNES)
"""

import csv
import os
import sys
import sqlite3
from datetime import datetime
from typing import Dict, Optional

# Configuração de encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Caminhos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'backend', 'cnes_cache.db')
CSV_PATH = os.path.join(BASE_DIR, 'BASE_DE_DADOS_CNES_202512', 'tbEstabelecimento202512.csv.csv')


def create_schema(conn: sqlite3.Connection):
    """Cria/atualiza a estrutura da tabela hospitals_cache"""
    cursor = conn.cursor()
    
    # Criar tabela se não existir (usando estrutura existente)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hospitals_cache (
            cnes_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            fantasy_name TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            neighborhood TEXT,
            lat REAL NOT NULL,
            long REAL NOT NULL,
            has_maternity INTEGER NOT NULL DEFAULT 0,
            is_emergency_only INTEGER NOT NULL DEFAULT 0,
            is_sus INTEGER NOT NULL DEFAULT 0,
            management TEXT NOT NULL CHECK(management IN ('MUNICIPAL', 'ESTADUAL', 'FEDERAL', 'PRIVADO', 'DUPLA')),
            cnpj TEXT,
            tipo_unidade TEXT,
            natureza_juridica TEXT,
            codigo_servicos TEXT,
            last_updated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            data_source_date TEXT
        )
    ''')
    
    # Criar índices
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_hospitals_lat_long ON hospitals_cache (lat, long)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_hospitals_has_maternity ON hospitals_cache (has_maternity)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_hospitals_is_sus ON hospitals_cache (is_sus)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_hospitals_is_emergency_only ON hospitals_cache (is_emergency_only)')
    
    conn.commit()


def clean_name(name: str) -> str:
    """Converte nome para Title Case"""
    if not name:
        return ""
    cleaned = " ".join(name.strip().split())
    return cleaned.title()


def parse_float(value: str) -> Optional[float]:
    """Converte string para float, tratando vírgula como separador decimal"""
    if not value or value.strip() == '':
        return None
    try:
        # Trocar vírgula por ponto se necessário
        normalized = value.strip().replace(',', '.')
        return float(normalized)
    except (ValueError, TypeError):
        return None


# Blacklist de termos que devem ser excluídos
TERM_BLACKLIST = [
    "ODONTO", "DENTISTA", "ÓTICA", "OTICA", "LABORATORIO", "LABORATÓRIO",
    "ANALISES", "ANÁLISES", "FISIOTERAPIA", "PSICOLOGIA", "ESTETICA", "ESTÉTICA",
    "VETERINARIA", "VETERINÁRIA", "ACADEMIA", "FARMACIA", "FARMÁCIA", 
    "DROGARIA", "FUNERARIA", "FUNERÁRIA", "OFTALMO", "CLINICA DE OLHOS",
    "CLÍNICA DE OLHOS", "FISIOTERAPIA", "PSICOLOGO", "PSICÓLOGO"
]

def is_blacklisted(name: str) -> bool:
    """Verifica se o nome contém termos da blacklist"""
    if not name:
        return False
    name_upper = name.upper()
    return any(term in name_upper for term in TERM_BLACKLIST)


def map_tipo_unidade(codigo_tipo: str) -> Optional[str]:
    """
    Mapeia código de tipo de unidade (CO_TIPO_UNIDADE) para tipo legível
    
    Args:
        codigo_tipo: Código da coluna CO_TIPO_UNIDADE
        
    Returns:
        Tipo mapeado ou None se for irrelevante
    """
    if not codigo_tipo:
        return None
    
    codigo_clean = codigo_tipo.strip()
    
    # Hospitais
    if codigo_clean in ['05', '07', '15', '20', '21']:
        return 'HOSPITAL'
    
    # UPAs (Pronto Atendimento)
    if codigo_clean == '73':
        return 'UPA'
    
    # UBSs (Unidades Básicas de Saúde)
    if codigo_clean in ['01', '02', '32', '40', '50']:
        return 'UBS'
    
    # Outros tipos relevantes (pronto-socorro, etc)
    return 'OUTROS'


def is_upa(row: Dict[str, str], tipo_mapped: Optional[str] = None) -> bool:
    """Identifica se é UPA (Pronto Atendimento)"""
    # Verificar tipo mapeado
    if tipo_mapped == 'UPA':
        return True
    
    # Verificar código original
    tipo_unidade = row.get('CO_TIPO_UNIDADE', '').strip()
    if tipo_unidade == '73':
        return True
    
    # Buscar no nome
    nome_fantasia = row.get('NO_FANTASIA', '').upper()
    if 'UPA' in nome_fantasia or 'PRONTO ATENDIMENTO' in nome_fantasia:
        return True
    
    return False


def has_maternity_heuristic(row: Dict[str, str]) -> bool:
    """
    Identifica maternidade por heurística (nome e tipo)
    REGRA: Ser conservador - só marcar se houver evidência clara
    """
    nome_fantasia = row.get('NO_FANTASIA', '').upper()
    tipo_unidade = row.get('CO_TIPO_UNIDADE', '').strip()
    
    # Se for UPA, nunca tem maternidade
    if is_upa(row):
        return False
    
    # Buscar palavras-chave no nome
    keywords_maternity = ['MATERNIDADE', 'MATERNO', 'OBSTETRICIA', 'OBSTETRICO']
    if any(keyword in nome_fantasia for keyword in keywords_maternity):
        return True
    
    # Se for Hospital Especializado (07) ou Geral (05), verificar mais contexto
    # MAS: Ser conservador - não assumir que Geral sempre tem maternidade
    # Retornar False por padrão para evitar falsos positivos
    return False


def determine_is_sus(natureza_jur: str) -> bool:
    """Determina se hospital atende SUS pela Natureza Jurídica"""
    if not natureza_jur:
        return False
    
    natureza_clean = natureza_jur.strip()
    
    # Adm Pública (códigos que começam com 1)
    if natureza_clean.startswith('1'):
        return True
    
    # Associação Privada sem fins lucrativos / Santa Casa (3999)
    if natureza_clean == '3999':
        return True
    
    # Empresarial (códigos que começam com 2) = Privado
    if natureza_clean.startswith('2'):
        return False
    
    # Por padrão, assumir SUS se não for claramente privado
    return True


def map_management(tp_gestao: str) -> str:
    """Mapeia código de gestão para enum"""
    tp_clean = tp_gestao.strip().upper() if tp_gestao else ''
    
    mapping = {
        'M': 'MUNICIPAL',
        'E': 'ESTADUAL',
        'F': 'FEDERAL',
        'D': 'DUPLA',
        'S': 'ESTADUAL',  # S também é Estadual
    }
    
    return mapping.get(tp_clean, 'PRIVADO')


def process_row(row: Dict[str, str]) -> Optional[Dict]:
    """
    Processa uma linha do CSV e retorna dict pronto para inserção
    
    REGRA DE OURO: Se faltar lat/long, PULAR (continue)
    FILTRO CRÍTICO: Blacklist de termos (dentistas, óticas, etc.)
    """
    # 1. Validação obrigatória: CNES ID
    cnes_id = row.get('CO_CNES', '').strip()
    if not cnes_id:
        return None
    
    # 2. Mapear tipo de unidade (FILTRO DE RELEVÂNCIA)
    codigo_tipo = row.get('CO_TIPO_UNIDADE', '').strip()
    tipo_mapped = map_tipo_unidade(codigo_tipo)
    
    # Se não mapear para tipo relevante, pode ser irrelevante (mas não descartar ainda)
    
    # 3. Validação obrigatória: Latitude e Longitude (FILTRO DE QUALIDADE)
    lat = parse_float(row.get('NU_LATITUDE', ''))
    long = parse_float(row.get('NU_LONGITUDE', ''))
    
    if lat is None or long is None:
        return None  # PULA se não tiver coordenadas
    
    # 4. Nome (usar fantasia ou razão social)
    nome_fantasia = row.get('NO_FANTASIA', '').strip()
    nome_razao = row.get('NO_RAZAO_SOCIAL', '').strip()
    name = clean_name(nome_fantasia or nome_razao)
    if not name:
        return None  # PULA se não tiver nome
    
    # 5. FILTRO CRÍTICO: Blacklist (excluir dentistas, óticas, etc.)
    if is_blacklisted(nome_fantasia) or is_blacklisted(nome_razao):
        return None  # PULA se estiver na blacklist
    
    # 4. Endereço completo
    logradouro = row.get('NO_LOGRADOURO', '').strip()
    numero = row.get('NU_ENDERECO', '').strip()
    bairro = row.get('NO_BAIRRO', '').strip()
    
    address_parts = []
    if logradouro:
        address_parts.append(logradouro)
    if numero:
        address_parts.append(numero)
    if bairro:
        address_parts.append(bairro)
    
    address = ", ".join(address_parts) if address_parts else None
    
    # 5. Município (usar código por enquanto, ou deixar vazio)
    # CO_MUNICIPIO_GESTOR é código, não nome
    city = None  # Deixar vazio por enquanto (pode melhorar depois)
    
    # 6. Estado (usar código do gestor ou inferir)
    estado_gestor = row.get('CO_ESTADO_GESTOR', '').strip()
    state = estado_gestor[:2] if estado_gestor else None
    
    # 7. Classificação: UPA (usando tipo mapeado)
    is_emergency_only = is_upa(row, tipo_mapped)
    
    # 8. Classificação: Maternidade
    has_maternity = has_maternity_heuristic(row)
    
    # Se for UPA, garantir que não tem maternidade
    if is_emergency_only:
        has_maternity = False
    
    # 9. VALIDAÇÃO FINAL: Se tipo não for relevante E não for hospital/upa/ubs, considerar descartar
    # Mas vamos manter por enquanto para não ser muito restritivo
    
    # 10. Classificação: SUS vs Privado
    natureza_jur = row.get('CO_NATUREZA_JUR', '').strip()
    is_sus = determine_is_sus(natureza_jur)
    
    # 11. Gestão
    tp_gestao = row.get('TP_GESTAO', '').strip()
    management = map_management(tp_gestao)
    
    # 12. CNPJ
    cnpj = row.get('NU_CNPJ', '').strip() or None
    
    # 13. Tipo Unidade (SALVAR O TIPO MAPEADO, não o código)
    tipo_unidade = tipo_mapped or codigo_tipo or None
    
    # 13. Natureza Jurídica
    natureza_juridica = natureza_jur or None
    
    # 14. Data source
    data_source_date = datetime.now().strftime('%Y-%m-%d')
    
    return {
        'cnes_id': cnes_id,
        'name': name,
        'fantasy_name': name,  # Usar mesmo nome por enquanto
        'lat': lat,
        'long': long,
        'address': address,
        'city': city,
        'state': state,
        'neighborhood': bairro,
        'management': management,
        'is_sus': 1 if is_sus else 0,
        'has_maternity': 1 if has_maternity else 0,
        'is_emergency_only': 1 if is_emergency_only else 0,
        'cnpj': cnpj,
        'tipo_unidade': tipo_unidade,
        'natureza_juridica': natureza_juridica,
        'codigo_servicos': None,  # Não temos ainda
        'data_source_date': data_source_date
    }


def ingest_csv():
    """Processa CSV e insere no banco de dados"""
    print("=" * 80)
    print("🚀 INGESTÃO DE DADOS CNES - Processamento de Dados Reais")
    print("=" * 80)
    print()
    
    # Verificar se arquivo existe
    if not os.path.exists(CSV_PATH):
        print(f"❌ Arquivo CSV não encontrado: {CSV_PATH}")
        print(f"\n💡 Verifique se o arquivo está em:")
        print(f"   BASE_DE_DADOS_CNES_202512/tbEstabelecimento202512.csv.csv")
        return
    
    print(f"📁 Arquivo CSV: {CSV_PATH}")
    print(f"📊 Tamanho: {os.path.getsize(CSV_PATH) / (1024*1024):.2f} MB")
    print(f"💾 Banco de dados: {DB_PATH}")
    print()
    
    # Conectar ao banco
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Criar schema
    create_schema(conn)
    
    # LIMPAR TABELA ANTES DE COMEÇAR
    print("🗑️  Limpando tabela existente...")
    cursor.execute('DELETE FROM hospitals_cache')
    conn.commit()
    print("✅ Tabela limpa!\n")
    
    # Estatísticas
    total_lines = 0
    inserted = 0
    skipped_no_coords = 0
    skipped_no_name = 0
    skipped_no_cnes = 0
    errors = 0
    
    print("📖 Lendo CSV...")
    print("   Encoding: ISO-8859-1")
    print("   Separador: ;")
    print()
    
    try:
        with open(CSV_PATH, 'r', encoding='ISO-8859-1', errors='replace') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            for i, row in enumerate(reader, 1):
                total_lines = i
                
                # Mostrar progresso a cada 10.000 linhas
                if i % 10000 == 0:
                    print(f"   📊 Processadas {i:,} linhas... (Inseridos: {inserted:,}, Pulados: {skipped_no_coords + skipped_no_name + skipped_no_cnes:,})")
                
                try:
                    processed = process_row(row)
                    
                    if processed is None:
                        # Contar razões de skip
                        if not row.get('CO_CNES', '').strip():
                            skipped_no_cnes += 1
                        elif not row.get('NO_FANTASIA', '').strip() and not row.get('NO_RAZAO_SOCIAL', '').strip():
                            skipped_no_name += 1
                        else:
                            skipped_no_coords += 1
                        continue
                    
                    # Inserir no banco
                    cursor.execute('''
                        INSERT INTO hospitals_cache 
                        (cnes_id, name, fantasy_name, lat, long, address, city, state, neighborhood,
                         management, is_sus, has_maternity, is_emergency_only, 
                         cnpj, tipo_unidade, natureza_juridica, codigo_servicos, data_source_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        processed['cnes_id'],
                        processed['name'],
                        processed['fantasy_name'],
                        processed['lat'],
                        processed['long'],
                        processed['address'],
                        processed['city'],
                        processed['state'],
                        processed['neighborhood'],
                        processed['management'],
                        processed['is_sus'],
                        processed['has_maternity'],
                        processed['is_emergency_only'],
                        processed['cnpj'],
                        processed['tipo_unidade'],
                        processed['natureza_juridica'],
                        processed['codigo_servicos'],
                        processed['data_source_date']
                    ))
                    
                    inserted += 1
                    
                    # Commit a cada 5000 inserções para performance
                    if inserted % 5000 == 0:
                        conn.commit()
                
                except Exception as e:
                    errors += 1
                    if errors <= 10:  # Mostrar apenas primeiros 10 erros
                        print(f"   ⚠️  Erro na linha {i}: {e}")
            
            # Commit final
            conn.commit()
    
    except Exception as e:
        print(f"\n❌ Erro fatal ao processar CSV: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()
    
    # Resumo final
    print()
    print("=" * 80)
    print("✅ PROCESSAMENTO CONCLUÍDO!")
    print("=" * 80)
    print(f"📊 Estatísticas:")
    print(f"   • Total de linhas processadas: {total_lines:,}")
    print(f"   • ✅ Inseridos com sucesso: {inserted:,}")
    print(f"   • ⏭️  Pulados (sem coordenadas): {skipped_no_coords:,}")
    print(f"   • ⏭️  Pulados (sem nome): {skipped_no_name:,}")
    print(f"   • ⏭️  Pulados (sem CNES): {skipped_no_cnes:,}")
    print(f"   • ❌ Erros: {errors:,}")
    print()
    print(f"💾 Banco de dados atualizado: {DB_PATH}")
    print()
    print("🧪 Próximos passos:")
    print("   1. Reinicie o backend FastAPI")
    print("   2. Acesse o mapa no navegador")
    print("   3. Veja os hospitais reais do Brasil! 🌍📍")
    print("=" * 80)


if __name__ == '__main__':
    ingest_csv()
