#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Seed Data - Dados de Teste para Validação Visual
Purpose: Popular banco com dados fictícios mas realistas para testar frontend
Author: Dev Agent (baseado em QA scenarios)
"""

import os
import sys
import sqlite3
from datetime import datetime

# Configuração de encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Caminho do banco de dados
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'cnes_cache.db')

# Coordenadas base (Centro de São Paulo)
BASE_LAT = -23.5505
BASE_LON = -46.6333

# Dados de teste conforme especificação QA
TEST_HOSPITALS = [
    {
        'cnes_id': '9990001',
        'name': 'Hospital das Clínicas',
        'fantasy_name': 'Hospital das Clínicas (Simulado)',
        'address': 'Av. Dr. Enéas de Carvalho Aguiar, 255',
        'city': 'São Paulo',
        'state': 'SP',
        'neighborhood': 'Cerqueira César',
        'lat': BASE_LAT + 0.01,  # ~1.1km norte
        'long': BASE_LON - 0.01,  # ~1.1km oeste
        'has_maternity': 1,
        'is_emergency_only': 0,
        'is_sus': 1,
        'management': 'ESTADUAL',
        'cnpj': '12345678000100',
        'tipo_unidade': '05',
        'natureza_juridica': 'ADMINISTRACAO PUBLICA ESTADUAL',
        'codigo_servicos': '065,066,067',  # Obstetrícia + outros
        'description': 'Hospital Estadual SUS com Maternidade (deve aparecer AZUL)'
    },
    {
        'cnes_id': '9990002',
        'name': 'Maternidade Santa Joana',
        'fantasy_name': 'Maternidade Santa Joana (Simulada)',
        'address': 'Rua Dr. Enéas de Carvalho Aguiar, 155',
        'city': 'São Paulo',
        'state': 'SP',
        'neighborhood': 'Cerqueira César',
        'lat': BASE_LAT - 0.01,  # ~1.1km sul
        'long': BASE_LON + 0.01,  # ~1.1km leste
        'has_maternity': 1,
        'is_emergency_only': 0,
        'is_sus': 0,
        'management': 'PRIVADO',
        'cnpj': '98765432000100',
        'tipo_unidade': '07',
        'natureza_juridica': 'ENTIDADE EMPRESARIAL',
        'codigo_servicos': '065',  # Apenas Obstetrícia
        'description': 'Hospital Privado com Maternidade (deve aparecer VERDE)'
    },
    {
        'cnes_id': '9990003',
        'name': 'UPA 24h Vergueiro',
        'fantasy_name': 'UPA 24h Vergueiro',
        'address': 'Rua Vergueiro, 1000',
        'city': 'São Paulo',
        'state': 'SP',
        'neighborhood': 'Vila Mariana',
        'lat': BASE_LAT - 0.015,  # ~1.7km sul
        'long': BASE_LON + 0.005,  # ~0.6km leste
        'has_maternity': 0,  # CRÍTICO: UPA não tem maternidade
        'is_emergency_only': 1,  # CRÍTICO: UPA é emergência apenas
        'is_sus': 1,
        'management': 'MUNICIPAL',
        'cnpj': '11122233000100',
        'tipo_unidade': '73',  # CRÍTICO: Tipo 73 = UPA
        'natureza_juridica': 'ADMINISTRACAO PUBLICA MUNICIPAL',
        'codigo_servicos': '',  # UPA não tem código 065
        'description': 'UPA Municipal (deve aparecer AMARELO com aviso - não faz parto)'
    },
    {
        'cnes_id': '9990004',
        'name': 'UBS República',
        'fantasy_name': 'UBS República',
        'address': 'Rua Barão de Itapetininga, 200',
        'city': 'São Paulo',
        'state': 'SP',
        'neighborhood': 'República',
        'lat': BASE_LAT + 0.005,  # ~0.6km norte
        'long': BASE_LON - 0.005,  # ~0.6km oeste
        'has_maternity': 0,
        'is_emergency_only': 0,
        'is_sus': 1,
        'management': 'MUNICIPAL',
        'cnpj': '22233344000100',
        'tipo_unidade': '02',  # UBS
        'natureza_juridica': 'ADMINISTRACAO PUBLICA MUNICIPAL',
        'codigo_servicos': '',  # UBS não tem maternidade
        'description': 'UBS Municipal (NÃO deve aparecer se filtro for "Apenas Maternidade")'
    },
    {
        'cnes_id': '9990005',
        'name': 'Hospital Misto Modelo',
        'fantasy_name': 'Hospital Misto Modelo',
        'address': 'Av. Paulista, 1000',
        'city': 'São Paulo',
        'state': 'SP',
        'neighborhood': 'Bela Vista',
        'lat': BASE_LAT + 0.008,  # ~0.9km norte
        'long': BASE_LON + 0.008,  # ~0.9km leste
        'has_maternity': 1,
        'is_emergency_only': 0,
        'is_sus': 1,
        'management': 'DUPLA',
        'cnpj': '33344455000100',
        'tipo_unidade': '05',
        'natureza_juridica': 'FILANTROPICA',
        'codigo_servicos': '065,066',  # Obstetrícia
        'description': 'Hospital Misto SUS com Maternidade (deve aparecer AZUL/Misto)'
    }
]


def create_schema_if_needed(conn):
    """Cria schema se não existir"""
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hospitals_cache (
            cnes_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            fantasy_name TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            neighborhood TEXT,
            lat REAL,
            long REAL,
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
    
    conn.commit()


def seed_database():
    """Popula banco com dados de teste"""
    print("=" * 60)
    print("🌱 SEED DATA - Dados de Teste para Validação Visual")
    print("=" * 60)
    print()
    
    # Conectar ao banco
    conn = sqlite3.connect(DB_PATH)
    create_schema_if_needed(conn)
    
    cursor = conn.cursor()
    
    # Limpar tabela (para recriar dados limpos)
    print("🗑️  Limpando tabela existente...")
    cursor.execute('DELETE FROM hospitals_cache WHERE cnes_id LIKE "999%"')
    conn.commit()
    print("✅ Tabela limpa (apenas dados de seed removidos)")
    print()
    
    # Inserir dados de teste
    print("📝 Inserindo dados de teste...")
    print()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    for hospital in TEST_HOSPITALS:
        try:
            cursor.execute('''
                INSERT INTO hospitals_cache 
                (cnes_id, name, fantasy_name, address, city, state, neighborhood,
                 lat, long, has_maternity, is_emergency_only, is_sus, management,
                 cnpj, tipo_unidade, natureza_juridica, codigo_servicos, data_source_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                hospital['cnes_id'],
                hospital['name'],
                hospital['fantasy_name'],
                hospital['address'],
                hospital['city'],
                hospital['state'],
                hospital['neighborhood'],
                hospital['lat'],
                hospital['long'],
                hospital['has_maternity'],
                hospital['is_emergency_only'],
                hospital['is_sus'],
                hospital['management'],
                hospital['cnpj'],
                hospital['tipo_unidade'],
                hospital['natureza_juridica'],
                hospital['codigo_servicos'],
                today
            ))
            
            print(f"✅ {hospital['fantasy_name']}")
            print(f"   📍 {hospital['address']}")
            print(f"   🎨 {hospital['description']}")
            print()
            
        except Exception as e:
            print(f"❌ Erro ao inserir {hospital['fantasy_name']}: {e}")
            print()
    
    conn.commit()
    conn.close()
    
    print("=" * 60)
    print("✅ SEED CONCLUÍDO!")
    print("=" * 60)
    print()
    print("📊 Resumo dos dados inseridos:")
    print(f"   • Total: {len(TEST_HOSPITALS)} estabelecimentos")
    print(f"   • Localização base: {BASE_LAT}, {BASE_LON} (Centro de SP)")
    print()
    print("🧪 PRÓXIMOS PASSOS PARA TESTE:")
    print("   1. Inicie o backend: uvicorn backend.api.main:app --reload")
    print("   2. Inicie o frontend: cd frontend && npm run dev")
    print("   3. Acesse: http://localhost:3000")
    print("   4. Permita geolocalização (ou use coordenadas de SP)")
    print()
    print("📋 TESTES SUGERIDOS:")
    print("   • Filtro SUS + Maternidade: Deve mostrar Hospital das Clínicas e Misto")
    print("   • Filtro Privado: Deve mostrar apenas Santa Joana (VERDE)")
    print("   • Desmarcar Maternidade: Deve mostrar UPA (AMARELO com aviso)")
    print("   • Botão Emergência: Deve mostrar TODOS (ignora filtros)")
    print("=" * 60)


if __name__ == '__main__':
    try:
        seed_database()
    except Exception as e:
        print(f"❌ Erro ao executar seed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
