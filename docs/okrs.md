# OKRs – Localizador de Emergência Obstétrica

**Objetivo de produto:** Disponibilizar busca de emergência obstétrica com top 3 hospitais em menos de 2 cliques, com dados confiáveis e acessíveis.

---

## O1: Disponibilizar busca de emergência com top 3 em <2 cliques

| KR | Indicador | Meta | Responsável |
|----|-----------|------|-------------|
| **KR1** | % de hospitais com telefone e coordenada (lat/long) | ≥ 95% | Dev / Dados |
| **KR2** | Precisão da flag “Ala de Maternidade” em amostra auditada | ≥ 98% | QA / Analyst |
| **KR3** | Uptime da API (disponibilidade) | ≥ 99% | Infra / Dev |

---

## Definições

- **Top 3:** Os 3 estabelecimentos mais relevantes para emergência obstétrica (prioridade: has_maternity true > tempo/distância > atende SUS [se filtrado] > telefone disponível).
- **<2 cliques:** Usuária aciona “Emergência” e, após consentimento de localização (se necessário), vê a lista top 3 sem passo intermediário obrigatório.
- **Ala de Maternidade:** Classificação baseada em evidência CNES (leito/serviço/habilitação/tipo); “Provável” quando score 0,4–0,59 + keyword; “Não listado” caso contrário.
- **Amostra auditada:** Subconjunto representativo de estabelecimentos revisado manualmente ou por regras de consistência para medir recall/precisão.
- **API/UX:** Respostas da API incluem `telefone_formatado`, `phone_e164` e endpoint `/establishments/{cnes_id}/evidence` (has_maternity, score, evidence); refletidos em cards, backlog e DoD.

---

## Aprovação

- Documento alinhado ao backlog (PO) e à arquitetura (Architect).
- Riscos atribuídos em `docs/risks.md`.

---

**Versão:** 1.0  
**Data:** 2025-02  
**Autor:** PM Agent (BMAD)
