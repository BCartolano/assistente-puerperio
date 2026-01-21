-- Schema para Cache Híbrido CNES
-- Tabela: hospitals_cache
-- Purpose: Armazenar dados locais do CNES para Cache Híbrido
-- Source of Truth: DataSUS/CNES (com atualização mensal)

-- Criar tipo ENUM para gestão (PostgreSQL)
CREATE TYPE management_type AS ENUM ('MUNICIPAL', 'ESTADUAL', 'FEDERAL', 'PRIVADO', 'DUPLA');

-- Tabela principal de cache de hospitais
CREATE TABLE IF NOT EXISTS hospitals_cache (
    -- Identificação
    cnes_id VARCHAR(20) PRIMARY KEY,
    
    -- Informações básicas
    name VARCHAR(255) NOT NULL,
    fantasy_name VARCHAR(255),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(2),
    neighborhood VARCHAR(100),
    
    -- Geolocalização (necessário para busca por proximidade)
    lat DECIMAL(10, 8),
    long DECIMAL(11, 8),
    
    -- Classificação puerperal (CRÍTICO)
    has_maternity BOOLEAN NOT NULL DEFAULT FALSE,
    is_emergency_only BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Classificação financeira
    is_sus BOOLEAN NOT NULL DEFAULT FALSE,
    management management_type NOT NULL,
    
    -- Informações adicionais do CNES
    cnpj VARCHAR(18),
    tipo_unidade VARCHAR(10),
    natureza_juridica VARCHAR(100),
    codigo_servicos TEXT, -- Códigos separados por vírgula (ex: '065,066,067')
    
    -- Metadados de cache
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_source_date DATE, -- Data da base oficial (Mês/Ano)
    
    -- Índices para performance
    CONSTRAINT hospitals_cache_cnes_id_key UNIQUE (cnes_id)
);

-- Índices para consultas rápidas
CREATE INDEX IF NOT EXISTS idx_hospitals_cache_location ON hospitals_cache(lat, long);
CREATE INDEX IF NOT EXISTS idx_hospitals_cache_city_state ON hospitals_cache(city, state);
CREATE INDEX IF NOT EXISTS idx_hospitals_cache_maternity ON hospitals_cache(has_maternity) WHERE has_maternity = TRUE;
CREATE INDEX IF NOT EXISTS idx_hospitals_cache_sus ON hospitals_cache(is_sus) WHERE is_sus = TRUE;
CREATE INDEX IF NOT EXISTS idx_hospitals_cache_emergency_only ON hospitals_cache(is_emergency_only) WHERE is_emergency_only = TRUE;

-- Índice composto para busca comum: Maternidade + SUS + Localização
CREATE INDEX IF NOT EXISTS idx_hospitals_cache_maternity_sus_location 
ON hospitals_cache(has_maternity, is_sus, city, state) 
WHERE has_maternity = TRUE;

-- Comentários para documentação
COMMENT ON TABLE hospitals_cache IS 'Cache local de dados CNES para busca rápida e fallback quando API está offline';
COMMENT ON COLUMN hospitals_cache.has_maternity IS 'TRUE se possui serviço de Obstetrícia (Código 065)';
COMMENT ON COLUMN hospitals_cache.is_emergency_only IS 'TRUE se é UPA (Tipo 73) - apenas emergência, não faz parto';
COMMENT ON COLUMN hospitals_cache.is_sus IS 'TRUE se vinculado ao SUS';
COMMENT ON COLUMN hospitals_cache.data_source_date IS 'Data da base oficial CNES usada (para exibir no aviso de possível desatualização)';

-- Para SQLite (compatibilidade), usar versão simplificada:
-- SQLite não suporta ENUM nativamente, usar VARCHAR
/*
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
);

CREATE INDEX IF NOT EXISTS idx_hospitals_cache_location ON hospitals_cache(lat, long);
CREATE INDEX IF NOT EXISTS idx_hospitals_cache_maternity ON hospitals_cache(has_maternity) WHERE has_maternity = 1;
CREATE INDEX IF NOT EXISTS idx_hospitals_cache_sus ON hospitals_cache(is_sus) WHERE is_sus = 1;
*/
