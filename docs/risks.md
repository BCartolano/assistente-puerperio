# Matriz de Riscos – Localizador de Emergência Obstétrica

Riscos identificados com planos de mitigação. Responsáveis atribuídos.

---

## R1: Dados CNES desatualizados

| Aspecto | Descrição |
|--------|-----------|
| **Risco** | Snapshot mensal atrasado ou incompleto; estabelecimentos fechados ou sem maternidade ainda listados. |
| **Impacto** | Alto (precisão e confiança do usuário). |
| **Probabilidade** | Média. |
| **Mitigação** | Atualização mensal automatizada (`scripts/snapshot_update.sh` ou equivalente); registro em `docs/data_versions.md`; disclaimer na UI: “Informações do CNES de <MM/AAAA>. Confirme por telefone.” |
| **Responsável** | Dev / Dados. |

---

## R2: Limites de geocoder (rate limit / indisponibilidade)

| Aspecto | Descrição |
|--------|-----------|
| **Risco** | Serviço externo (Nominatim/Google/Mapbox) indisponível ou com limite de requisições. |
| **Impacto** | Médio (estabelecimentos sem coordenadas; busca por proximidade incompleta). |
| **Probabilidade** | Média. |
| **Mitigação** | Priorizar lat/long do CNES; cache local (`data/geocache.sqlite` ou tabela `geocodes`); marcar “needs_review” se geocodificação falhar para >10%; modo offline documentado em `docs/architecture_emergency.md`. |
| **Responsável** | Dev. |

---

## R3: Convênios / rede credenciada incertos

| Aspecto | Descrição |
|--------|-----------|
| **Risco** | CNES não é fonte confiável para rede credenciada de planos de saúde. |
| **Impacto** | Alto (expectativa de usuária sobre “atende meu convênio”). |
| **Probabilidade** | Alta. |
| **Mitigação** | Exibir “Ligue para confirmar” para convênios; atende_sus baseado em dados oficiais (SUS); microcopy aprovado por PO (docs/ux). |
| **Responsável** | PO / UX. |

---

## R4: Cobertura de telefone < 85%

| Aspecto | Descrição |
|--------|-----------|
| **Risco** | Muitos estabelecimentos sem telefone no CNES; botão “Ligar” inútil. |
| **Impacto** | Médio (experiência e segurança). |
| **Probabilidade** | Média. |
| **Mitigação** | Gate no orquestrador: alertar se coverage de telefone < 85%; exibir “Telefone não informado” e manter botão Rotas; relatório em `reports/run_summary.json`. |
| **Responsável** | Analyst / Dev; alerta para PM. |

---

## R5: Alta proporção “Provável” sem revisão

| Aspecto | Descrição |
|--------|-----------|
| **Risco** | >10% dos resultados em faixa 0,4–0,59 sem revisão pendente; confusão na UI. |
| **Impacto** | Médio. |
| **Probabilidade** | Média. |
| **Mitigação** | Gate QA: reprovar se 0,4–0,59 > 10% sem revisão pendente; backlog de auditoria (admin); documentar em `docs/release_plan_R1.md`. |
| **Responsável** | QA / SM. |

---

## Aprovação

- Riscos atribuídos e documentados.
- Alinhado a `docs/okrs.md` e `docs/roadmap.md`.
- Revisão trimestral recomendada.

---

**Versão:** 1.0  
**Data:** 2025-02  
**Autor:** PM Agent (BMAD)
