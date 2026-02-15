-- Criação da tabela estabelecimentos_saude com PostGIS
-- Execute este script no Azure Database for PostgreSQL Flexible Server

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS estabelecimentos_saude (
    id SERIAL PRIMARY KEY,
    cnes VARCHAR(20) UNIQUE,
    nome_fantasia VARCHAR(255),
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    logradouro VARCHAR(255),
    bairro VARCHAR(100),
    municipio VARCHAR(100),
    uf CHAR(2),
    telefone VARCHAR(20),
    tem_maternidade BOOLEAN DEFAULT FALSE,
    tem_uti_neonatal BOOLEAN DEFAULT FALSE,
    aceita_sus BOOLEAN DEFAULT TRUE,
    convenio BOOLEAN DEFAULT FALSE,
    particular BOOLEAN DEFAULT FALSE,
    geom GEOMETRY(Point, 4326)
);

-- Índice espacial GIST para consultas rápidas de proximidade
CREATE INDEX IF NOT EXISTS idx_estabelecimentos_geom ON estabelecimentos_saude USING GIST(geom);

-- Índices adicionais para filtros comuns
CREATE INDEX IF NOT EXISTS idx_estabelecimentos_uf ON estabelecimentos_saude(uf);
CREATE INDEX IF NOT EXISTS idx_estabelecimentos_maternidade ON estabelecimentos_saude(tem_maternidade) WHERE tem_maternidade = TRUE;
CREATE INDEX IF NOT EXISTS idx_estabelecimentos_cnes ON estabelecimentos_saude(cnes);

-- Comentários para documentação
COMMENT ON TABLE estabelecimentos_saude IS 'Tabela de estabelecimentos de saúde do CNES com suporte a consultas espaciais via PostGIS';
COMMENT ON COLUMN estabelecimentos_saude.geom IS 'Geometria Point em WGS84 (SRID 4326) para consultas de proximidade';
COMMENT ON COLUMN estabelecimentos_saude.tem_maternidade IS 'Indica se o estabelecimento possui maternidade';
