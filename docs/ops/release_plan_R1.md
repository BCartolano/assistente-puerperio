# Plano de Release R1 – Localizador de Emergência Obstétrica

Cronograma, riscos e rollback. Pipeline completo executável pelo orquestrador.

---

## Fases do release

| Fase | Entregas | DoD |
|------|----------|-----|
| **Data** | data/raw/<snapshot>, config/cnes_codes.json, ETL (ingest) | CSVs carregados; data_version registrado; sem duplicatas indevidas. |
| **Classifier** | config/scoring.yaml, pipelines/classify.py, has_maternity/score/evidence | Evidências persistidas por cnes_id; regras documentadas. |
| **Geocode** | pipelines/geocode.py, cache local (data/geocache.sqlite) | Lat/long do CNES ou cache; >85% com coordenadas (gate). |
| **API** | GET /v1/emergency/search, GET /v1/establishments/{cnes_id}, health, version | Contratos JSON Schema atendidos; P95 < 300ms em consulta local. |
| **UX** | Fluxo emergência, cards (Ligar, Rotas), disclaimer 192 | Protótipo navegável; textos aprovados por PO. |
| **QA** | pytest (classificador, ranking, API), contract tests, data quality | Gates passando; recall/precisão em amostra conforme critérios. |
| **Release** | CHANGELOG, artefatos (docs, config, container opcional) | Pipeline executável sem passos manuais além de fornecer CSVs. |

---

## Cronograma (exemplo)

- **Semana 1–2:** Data + Classifier + Geocode (pipelines).
- **Semana 2–3:** API (endpoints + contratos) + Ranking.
- **Semana 3–4:** UX (cards, fluxo, microcopy) + QA (testes + gates).
- **Semana 4:** Release R1 (documentação, CHANGELOG, orquestrador).

---

## Riscos e mitigação

- **Dados desatualizados:** Snapshot mensal; disclaimer na UI (docs/risks.md).
- **Geocoder indisponível:** Cache local; modo offline (docs/architecture_emergency.md).
- **Cobertura telefone < 85%:** Gate alerta; exibir “Telefone não informado” (docs/risks.md).
- **Provável > 10% sem revisão:** Gate QA reprova; backlog de auditoria (docs/risks.md).

---

## Rollback

- Reverter deploy para versão anterior (container/commit).
- Desativar TRAVEL_TIME (env TRAVEL_TIME=off) e usar Haversine; voltar para snapshot anterior (re-rodar ingest).
- Banco: manter backup pré-release; migrações reversíveis quando aplicável.
- Feature flags: desabilitar “emergência” na UI se necessário.

---

## Checklist bloqueantes

- [ ] config/cnes_codes.json e config/scoring.yaml presentes.
- [ ] data/raw/<snapshot> ou caminho alternativo com CSVs.
- [ ] pipelines/ingest → classify → geocode executáveis.
- [ ] API GET /v1/emergency/search e GET /v1/establishments/{cnes_id} e GET /v1/establishments/{cnes_id}/evidence respondendo.
- [ ] Contratos (api/contracts/*.json) validados por testes.
- [ ] Data quality: coord ≥ 0.85, phone ≥ 0.85, geocode_fail < 0.10; tests_passed=true; golden_accuracy ≥ 0.95 quando houver.
- [ ] QA: nenhum contrato quebrado; gate 0.4–0.59 conforme política.

---

## Checklist por arquivo (por agente)

| Agente | Arquivo | Entregue |
|--------|---------|----------|
| Analyst | config/cnes_codes.json | [ ] |
| Analyst | docs/data_dictionary.md | [ ] |
| Architect | docs/architecture_emergency.md | [ ] |
| Architect | db/schema.sql | [ ] |
| Architect | config/scoring.yaml | [ ] |
| Architect | backend/api/contracts/get_emergency_search.json | [ ] |
| Architect | backend/api/contracts/get_establishment_by_id.json | [ ] |
| Architect | backend/api/contracts/get_evidence.json | [ ] |
| Architect | backend/api/contracts/healthcheck_version.json | [ ] |
| Dev | backend/utils/env.py | [ ] |
| Dev | backend/utils/phone.py | [ ] |
| Dev | backend/utils/travel_time.py | [ ] |
| Dev | backend/pipelines/ingest.py, classify.py, geocode.py | [ ] |
| Dev | backend/ranking/selector.py | [ ] |
| Dev | backend/api/routes.py (emergency/search, establishments, evidence, version, health) | [ ] |
| Dev | ui/cards_templates.json | [ ] |
| Dev | env.example, Dockerfile, .dockerignore, docker-compose.yml | [ ] |
| Orchestrator | scripts/run_orchestrator.py | [ ] |
| Orchestrator | .github/workflows/snapshot.yml | [ ] |
| QA | tests/unit/test_classifier.py, test_ranking.py, test_api_contracts.py, test_phone.py | [ ] |
| QA | tests/golden/test_golden_set.py | [ ] |
| QA | checks/data_quality.py | [ ] |
| QA | sql/qa_queries.sql | [ ] |
| PM | docs/okrs.md, docs/roadmap.md, docs/risks.md | [ ] |
| PO | docs/user_stories.md, docs/backlog.md | [ ] |
| SM | docs/ways_of_working.md, docs/impediments_log.md | [ ] |
| UX | docs/ux/cards_spec.md, docs/ux/flows.md, ui/cards_templates.json | [ ] |
| BMAD Master | docs/release_plan_R1.md, CHANGELOG.md, docs/data_versions.md | [ ] |

---

**Versão:** 1.0  
**Data:** 2025-02  
**Autor:** BMAD Master (BMAD)
