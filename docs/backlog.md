# Backlog – Localizador de Emergência Obstétrica

Backlog priorizado por épicos, alinhado aos OKRs e às user stories.

---

## Épicos (ordem de prioridade)

1. **Dados** – Snapshot CNES, códigos, dicionário, ETL.
2. **Classificação** – Regras, pesos, has_maternity, score, evidence.
3. **Geolocalização** – Lat/long CNES, geocoder, cache offline.
4. **API** – Endpoints emergência e estabelecimento, contratos, health/version.
5. **Emergência** – Fluxo UI, cards, Ligar/Rotas, filtro SUS, 192.
6. **Auditoria** – Revisão “Provável”, gates QA, relatórios.

---

## Itens priorizados (resumo)

| # | Item | Épico | Prioridade |
|---|------|--------|------------|
| 1 | Snapshot CNES em data/raw/<snapshot>/ e config/cnes_codes.json | Dados | P0 |
| 2 | ETL: ingest, normalização, validação (DB/Parquet) | Dados | P0 |
| 3 | Classificador: scoring.yaml + cnes_codes.json → has_maternity, evidence | Classificação | P0 |
| 4 | Geocoding: CNES + cache; interface geocoder (Nominatim/Google/Mapbox) | Geolocalização | P0 |
| 5 | API: GET /v1/emergency/search, GET /v1/establishments/{cnes_id}, GET /v1/establishments/{cnes_id}/evidence | API | P0 |
| 6 | Health/version; contratos JSON Schema; respostas com telefone_formatado, phone_e164 e evidence | API | P0 |
| 7 | UI: fluxo emergência, cards (Ligar, Rotas), disclaimer 192 | Emergência | P0 |
| 8 | Filtro “Atende SUS” e microcopy aprovado | Emergência | P1 |
| 9 | Ranking: top-N por emergência obstétrica (tempo, SUS, telefone) | API | P0 |
| 10 | Lista/painel “Provável” para admin; gate 0,4–0,59 | Auditoria | P1 |
| 11 | Testes automatizados (classificador, API, contrato, data quality) | Auditoria | P0 |
| 12 | Snapshot mensal (script) e data_versions.md | Dados | P1 |

---

## Definition of Done (por tipo)

- **Código:** Revisão mín. 1 aprovação; testes passando; sem regressão em contratos; endpoints retornando telefone_formatado, phone_e164 e evidence conforme contratos.
- **Dados:** Validação de tipos e cobertura mínima; data_version registrado.
- **Copy:** Aprovado por PO; disclaimer e 192 conforme user_stories.md.

---

## Alinhamento

- OKRs: `docs/okrs.md`
- User Stories: `docs/user_stories.md`
- Riscos: `docs/risks.md`
- Arquitetura: `docs/architecture_emergency.md`

---

**Versão:** 1.0  
**Data:** 2025-02  
**Autor:** PO Agent (BMAD)
