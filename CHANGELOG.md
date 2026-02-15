# Changelog – Localizador de Emergência Obstétrica

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/).

---

## [Unreleased]

### A fazer

- Snapshot mensal automatizado e data_versions.md.
- Revisão de estabelecimentos “Provável” (admin).
- Opcional: tempo de viagem (rotas) e deep links.

---

## [1.0.0] – 2025-02 – R1

### Adicionado

- **Analyst:** config/cnes_codes.json com arrays de códigos CNES (leitos, serviços, classificações, tipos estab., keywords, SUS, esfera); docs/data_dictionary.md.
- **Architect:** docs/architecture_emergency.md (ETL → Classificador → Geocoding → API → UI); db/schema.sql (establishments, beds, services, habilitations, geocodes, classifications, views); config/scoring.yaml; backend/api/contracts/*.json (GET emergency/search, establishments/{id}, health/version).
- **PM:** docs/okrs.md, docs/roadmap.md, docs/risks.md.
- **PO:** docs/user_stories.md, docs/backlog.md.
- **UX:** docs/ux/cards_spec.md, docs/ux/flows.md (microcopy, acessibilidade AA, fluxo emergência).
- **SM:** docs/ways_of_working.md, docs/impediments_log.md.
- **Dev:** backend/pipelines/ingest.py, classify.py, geocode.py; backend/ranking/selector.py; GET /api/v1/emergency/search e GET /api/v1/establishments/{cnes_id}; ui/cards_templates.json; scripts/snapshot_update.sh e snapshot_update.ps1.
- **QA:** tests/conftest.py (fixtures); tests/unit/test_classifier.py, test_ranking.py, test_api_contracts.py; checks/data_quality.py (telefone, coordenadas, duplicidade).
- **BMAD Master:** docs/release_plan_R1.md, CHANGELOG.md.
- **Orchestrator:** reports/run_summary.json (estrutura); workflow e gates em release_plan e bmad-orchestrator.

### Existente (mantido)

- backend/etl/data_ingest.py, maternity_whitelist_pipeline.py; backend/services/facility_service.py; POST /api/v1/facilities/search; backend/database/schema.sql (hospitals_cache).

---

## [0.x] – Histórico anterior

- Chatbot Puerpério Sophia; integração WhatsApp; agendamento; base de conhecimento; alertas; vacinação.

---

[Unreleased]: https://github.com/.../compare/v1.0.0...HEAD
[1.0.0]: https://github.com/.../releases/tag/v1.0.0
