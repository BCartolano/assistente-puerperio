-- QA Queries para auditoria (PostgreSQL preferido; inclui alternativas simplificadas para SQLite)
-- Pré-requisito: db/schema.sql aplicado e views v_establishments_core e v_maternity_status disponíveis.
-- Se usar apenas hospitals_cache (SQLite), adapte: substitua v_establishments_core por hospitals_cache e v_maternity_status por hospitals_cache (colunas: cnes_id, name, fantasy_name, address, city, state, telefone, lat, long, has_maternity, is_sus, management, data_source_date).

-- 1) Distribuição por classe (confirmado/provável/não listado)
SELECT
  m.has_maternity,
  CASE
    WHEN m.score >= 0.6 THEN 'confirmado'
    WHEN m.score BETWEEN 0.4 AND 0.59 THEN 'provavel'
    ELSE 'nao_listado'
  END AS classe,
  COUNT(*) AS total
FROM v_maternity_status m
GROUP BY m.has_maternity, classe
ORDER BY classe, m.has_maternity;

-- 2) Lista de "prováveis" para revisão manual
SELECT
  e.cnes_id, e.nome, e.telefone, e.municipio, e.uf,
  m.score, m.evidence
FROM v_maternity_status m
JOIN v_establishments_core e USING (cnes_id)
WHERE m.score BETWEEN 0.4 AND 0.59
ORDER BY m.score DESC;

-- 3) Telefone faltante ou inválido
-- Postgres (regex com operador !~)
SELECT cnes_id, nome, telefone
FROM v_establishments_core
WHERE telefone IS NULL
   OR telefone !~ '^\+?55?\s?\(?\d{2}\)?\s?\d{4,5}-?\d{4}$';

-- SQLite (fallback simplificado sem regex nativo):
-- SELECT cnes_id, name, telefone
-- FROM hospitals_cache
-- WHERE telefone IS NULL
--    OR LENGTH(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(telefone,'-',''),' ',''),')',''),'(',''),'+',''),'.','')) NOT IN (10,11);

-- 4) Coordenadas fora do Brasil (sanidade geográfica)
SELECT cnes_id, nome, lat, lon
FROM v_establishments_core
WHERE NOT (lat BETWEEN -34.0 AND 5.5 AND lon BETWEEN -74.5 AND -32.0);

-- 5) Duplicidade por CNPJ/INE
SELECT cnpj, COUNT(*) AS qtd
FROM v_establishments_core
GROUP BY cnpj
HAVING COUNT(*) > 1
ORDER BY qtd DESC;

-- 6) Top por UF (quantidade de estabelecimentos com maternidade)
SELECT
  e.uf,
  SUM(CASE WHEN m.has_maternity THEN 1 ELSE 0 END) AS maternidades,
  COUNT(*) AS total_estabelecimentos
FROM v_maternity_status m
JOIN v_establishments_core e USING (cnes_id)
GROUP BY e.uf
ORDER BY maternidades DESC, e.uf;
