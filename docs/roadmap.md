# Roadmap – Localizador de Emergência Obstétrica (Trimestral)

**Horizonte:** 3 trimestres a partir do R1.

---

## T1 (R1 – Lançamento)

- **Dados:** Snapshot CNES em `data/raw/<snapshot>/`, `config/cnes_codes.json` e dicionário atualizados.
- **Classificador:** Regras e pesos em produção; has_maternity, score, evidence persistidos.
- **Geocoding:** Lat/long do CNES + cache local; opcional integração com geocoder externo.
- **API:** GET /v1/emergency/search e GET /v1/establishments/{cnes_id} estáveis; health/version.
- **UX:** Fluxo emergência (botão → GPS → 192 se graves → lista top 3); cards com Ligar/Rotas, disclaimer 192.
- **QA:** Testes automatizados e auditoria de amostra; gate de precisão “Ala de Maternidade”.
- **Release:** Pipeline executável pelo orquestrador; CHANGELOG e release_plan_R1.

---

## T2 (Consolidação e qualidade)

- Atualização mensal automatizada (snapshot_update) e registro em `docs/data_versions.md`.
- Revisão de estabelecimentos “Provável” (score 0,4–0,59) por admin/auditoria.
- Melhoria de cobertura: telefone ≥95%, coordenadas ≥90%; alertas se abaixo.
- Contratos de API e testes de contrato em CI.
- Acessibilidade (AA) e microcopy revisados (PO/UX).

---

## T3 (Escala e evolução)

- Opcional: integração com rotas (tempo de viagem real) e deep links consistentes.
- Opcional: painel admin para revisão de “Provável” e ajuste de evidências.
- Indicadores de sucesso (OKRs) monitorados; relatórios em `reports/run_summary.json`.
- Mitigações de riscos (dados desatualizados, limites de geocoder) aplicadas conforme `docs/risks.md`.

---

## Dependências entre épicos

- **Dados** → Classificação → Geocoding → API → Emergência (UI).
- **Auditoria** depende de Classificação e Dados estáveis.

---

**Versão:** 1.0  
**Data:** 2025-02  
**Autor:** PM Agent (BMAD)
