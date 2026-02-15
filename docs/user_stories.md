# User Stories – Localizador de Emergência Obstétrica

Histórias priorizadas e alinhadas aos OKRs (`docs/okrs.md`). Critérios de aceite claros.

---

## US1: Puérpera em emergência – Top 3 com maternidade

**Como** puérpera em situação de emergência,  
**quero** ver os 3 hospitais mais rápidos COM maternidade para chegar,  
**para** ser atendida o mais rápido possível em local adequado.

| Critério de aceite |
|--------------------|
| A lista exibe no máximo 3 estabelecimentos. |
| Ordenação prioriza: (1) has_maternity true, (2) tempo/distância, (3) atende SUS se filtrado, (4) telefone disponível. |
| Cada card mostra nome, endereço, distância/tempo estimado, telefone (ou “Telefone não informado”) e selo “Ala de Maternidade” (Sim/Provável/Não listado). |
| Botão “Rotas” disponível mesmo sem telefone. |
| Disclaimer 192 e informação de fonte (CNES <MM/AAAA>) visíveis. |

**Prioridade:** Must. **Épico:** Emergência.

---

## US2: Acompanhante – Botão “Ligar” visível

**Como** acompanhante,  
**quero** um botão “Ligar” visível no card,  
**para** confirmar vagas e convênio por telefone.

| Critério de aceite |
|--------------------|
| O card sempre mostra o botão “Ligar” quando há telefone. |
| Se telefone ausente: exibir “Telefone não informado” e manter botão “Rotas” ativo. |
| Telefone formatado (ex.: (11) 1234-5678) quando disponível. |

**Prioridade:** Must. **Épico:** Emergência.

---

## US3: Usuária do SUS – Filtrar por atendimento SUS

**Como** usuária do SUS,  
**quero** filtrar por “Atende SUS”,  
**para** ver apenas estabelecimentos que atendem pelo SUS.

| Critério de aceite |
|--------------------|
| Filtro “Atende SUS” retorna apenas estabelecimentos com atende_sus = Sim (dados CNES). |
| Card exibe “Atende SUS: Sim/Não/Desc.” no subtítulo. |
| Convênios: exibir “Ligue para confirmar” (CNES não é confiável para rede credenciada). |

**Prioridade:** Should. **Épico:** Emergência.

---

## US4: Admin – Revisar estabelecimentos “Provável”

**Como** administrador(a),  
**quero** revisar estabelecimentos classificados como “Provável” (score 0,4–0,59),  
**para** melhorar precisão da flag “Ala de Maternidade”.

| Critério de aceite |
|--------------------|
| Existe lista ou painel de estabelecimentos com maternity_status = “Provável”. |
| Evidências (tipo, código, fonte) visíveis por cnes_id. |
| Gate QA: reprovar se >10% em 0,4–0,59 sem revisão pendente (conforme risks.md). |

**Prioridade:** Should. **Épico:** Auditoria.

---

## Textos oficiais (disclaimer e 192)

- **Disclaimer:** “Informações do CNES de <MM/AAAA>. Confirme convênios por telefone. Em emergência, ligue 192.”
- **192 (sintomas graves):** “Sintomas graves detectados. Ligue 192 (SAMU) agora.”
- **Precisão maternidade:** Só afirmar “Sim” com evidência CNES (leito/serviço/habilitação/tipo); caso contrário “Provável” ou “Não listado”.

---

**Versão:** 1.0  
**Data:** 2025-02  
**Autor:** PO Agent (BMAD)
