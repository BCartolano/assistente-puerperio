# Geolocalização – Índice e API

## Arquivos

- `scripts/build_hospitals_index.py` – gera `backend/static/data/hospitais_index.json`
- `backend/geo/indexer.py` – normaliza e deduplica dados (CNES + data/)
- `backend/geo/nearby.py` – endpoint `/api/nearby`

## Variáveis de ambiente (opcional)

- `CNES_BASE_DIR` – diretório com BASE_DE_DADOS_CNES_202512
- `DATA_DIR` – diretório com data
- `HOSPITALS_INDEX_PATH` – caminho do JSON gerado
- `GEO_REINDEX_TOKEN` – token para POST `/api/geo/reindex` (opcional)

## Gerar índice

1. `python scripts/build_hospitals_index.py`
2. Verifique `backend/static/data/hospitais_index.json`

## Usar a API

- `GET /api/nearby?lat=-23.55&lon=-46.63&radius_km=10&limit=20`
- Filtros: `accepts_sus=true|false`, `accepts_convenio=true|false`, `public_private=Público|Privado|Filantrópico`

## Notas

- Ownership: se SUS=True e não há “gestão”, assume Público.
- Sem lat/lon: registro não entra no raio.
- ETag e Cache-Control leves para performance.
