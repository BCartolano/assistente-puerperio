-- Schema para Pipeline de Emergência Obstétrica (CNES)
-- Tabelas: establishments, beds, services, habilitations, geocodes, classifications
-- Views: v_establishments_core, v_maternity_status
-- Sem chaves órfãs; índices em cnes_id e geospatial

-- establishments: dados essenciais do estabelecimento (CNES)
CREATE TABLE IF NOT EXISTS establishments (
    cnes_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255),
    fantasy_name VARCHAR(255),
    tipo_unidade VARCHAR(10),
    tp_gestao VARCHAR(5),
    co_natureza_jur VARCHAR(20),
    co_esfera_admin VARCHAR(5),
    nu_cnpj VARCHAR(18),
    no_logradouro TEXT,
    nu_endereco VARCHAR(20),
    no_bairro VARCHAR(100),
    co_municipio VARCHAR(10),
    co_uf VARCHAR(2),
    nu_telefone VARCHAR(30),
    data_atualizacao DATE,
    data_version VARCHAR(10)
);

CREATE INDEX IF NOT EXISTS idx_establishments_tipo ON establishments(tipo_unidade);
CREATE INDEX IF NOT EXISTS idx_establishments_uf ON establishments(co_uf);
CREATE INDEX IF NOT EXISTS idx_establishments_municipio ON establishments(co_municipio);

-- beds: leitos por estabelecimento (rlEstabLeito)
CREATE TABLE IF NOT EXISTS beds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cnes_id VARCHAR(20) NOT NULL,
    co_leito VARCHAR(10) NOT NULL,
    qt_existente INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (cnes_id) REFERENCES establishments(cnes_id)
);

CREATE INDEX IF NOT EXISTS idx_beds_cnes ON beds(cnes_id);
CREATE INDEX IF NOT EXISTS idx_beds_co_leito ON beds(co_leito);

-- services: serviços por estabelecimento (rlEstabServClass - serviço)
CREATE TABLE IF NOT EXISTS services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cnes_id VARCHAR(20) NOT NULL,
    co_servico VARCHAR(10) NOT NULL,
    FOREIGN KEY (cnes_id) REFERENCES establishments(cnes_id)
);

CREATE INDEX IF NOT EXISTS idx_services_cnes ON services(cnes_id);
CREATE INDEX IF NOT EXISTS idx_services_co ON services(co_servico);

-- classifications: classificações por estabelecimento (rlEstabServClass - classificação)
CREATE TABLE IF NOT EXISTS classifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cnes_id VARCHAR(20) NOT NULL,
    co_classificacao VARCHAR(10) NOT NULL,
    FOREIGN KEY (cnes_id) REFERENCES establishments(cnes_id)
);

CREATE INDEX IF NOT EXISTS idx_classifications_cnes ON classifications(cnes_id);
CREATE INDEX IF NOT EXISTS idx_classifications_co ON classifications(co_classificacao);

-- habilitations: habilitações obstétricas/neonatais (quando disponível no CNES)
CREATE TABLE IF NOT EXISTS habilitations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cnes_id VARCHAR(20) NOT NULL,
    co_habilitacao VARCHAR(10) NOT NULL,
    FOREIGN KEY (cnes_id) REFERENCES establishments(cnes_id)
);

CREATE INDEX IF NOT EXISTS idx_habilitations_cnes ON habilitations(cnes_id);

-- geocodes: lat/long e cache de geocodificação (modo offline)
CREATE TABLE IF NOT EXISTS geocodes (
    cnes_id VARCHAR(20) PRIMARY KEY,
    lat REAL NOT NULL,
    lon REAL NOT NULL,
    address_normalized TEXT,
    source VARCHAR(20) DEFAULT 'cnes',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cnes_id) REFERENCES establishments(cnes_id)
);

CREATE INDEX IF NOT EXISTS idx_geocodes_spatial ON geocodes(lat, lon);

-- maternity_classification: saída do classificador (score e evidências)
CREATE TABLE IF NOT EXISTS maternity_classification (
    cnes_id VARCHAR(20) PRIMARY KEY,
    has_maternity INTEGER NOT NULL DEFAULT 0,
    score REAL NOT NULL DEFAULT 0.0,
    evidence TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (cnes_id) REFERENCES establishments(cnes_id)
);

CREATE INDEX IF NOT EXISTS idx_maternity_classification_has ON maternity_classification(has_maternity) WHERE has_maternity = 1;
CREATE INDEX IF NOT EXISTS idx_maternity_classification_score ON maternity_classification(score);

-- v_establishments_core: dados essenciais para API/cards
CREATE VIEW IF NOT EXISTS v_establishments_core AS
SELECT
    e.cnes_id,
    COALESCE(e.fantasy_name, e.name) AS display_name,
    e.name,
    e.fantasy_name,
    e.tipo_unidade,
    e.tp_gestao,
    e.co_natureza_jur,
    e.nu_telefone,
    e.no_logradouro,
    e.nu_endereco,
    e.no_bairro,
    e.co_municipio,
    e.co_uf,
    g.lat,
    g.lon,
    g.address_normalized,
    e.data_version
FROM establishments e
LEFT JOIN geocodes g ON e.cnes_id = g.cnes_id;

-- v_maternity_status: has_maternity, score, evidence (classificador)
CREATE VIEW IF NOT EXISTS v_maternity_status AS
SELECT
    e.cnes_id,
    COALESCE(m.has_maternity, 0) AS has_maternity,
    COALESCE(m.score, 0.0) AS score,
    m.evidence AS evidence,
    m.updated_at AS classification_updated
FROM establishments e
LEFT JOIN maternity_classification m ON e.cnes_id = m.cnes_id;
