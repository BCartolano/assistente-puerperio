# Ways of Working – Localizador de Emergência Obstétrica

Cerimônias, Definition of Done por tipo de item, política de branch/PR e board.

---

## 1. Cerimônias

| Cerimônia | Objetivo | Frequência |
|-----------|----------|------------|
| **Daily curta** | Alinhamento rápido; impedimentos. | Diária (time pequeno: async ou 15 min) |
| **Planning** | Priorizar backlog; compromisso da sprint/iteração. | Início da iteração |
| **Review** | Demonstrar entregas; aceite com PO. | Fim da iteração / quando houver entrega |
| **Retro** | Melhorar processo. | Fim da iteração |

---

## 2. Definition of Done (DoD) por tipo

| Tipo de item | DoD |
|--------------|-----|
| **Código** | Revisão mín. 1 aprovação; testes passando; sem quebra de contrato de API; documentação atualizada se necessário. |
| **Dados** | Validação de tipos e cobertura mínima; data_version registrado; sem duplicatas indevidas. |
| **Copy** | Aprovado por PO; alinhado a `docs/ux/cards_spec.md` e user_stories. |
| **Documentação** | Revisão técnica (Architect/SM); referências cruzadas corretas. |

---

## 3. Política de branch e PR

- **Branch:** feature/ ou fix/ a partir de main (ex.: `feature/emergency-search`, `fix/geocode-cache`).
- **PR:** Obrigatório para merge em main; **mínimo 1 aprovação** antes de merge.
- **Revisão:** Verificar DoD; testes; contratos; impacto em dados/UX quando aplicável.

---

## 4. Board (colunas)

| Coluna | Uso |
|--------|-----|
| **Backlog** | Itens priorizados; não iniciados. |
| **In Progress** | Em desenvolvimento; WIP limitado (ex.: máx. 2 por pessoa). |
| **In Review** | PR aberto; aguardando aprovação. |
| **QA** | Pronto para testes/validação. |
| **Done** | Entregue e aceito. |

**WIP:** Controlar itens “In Progress” para evitar sobrecarga; impedimentos registrados em `impediments_log.md`.

---

## 5. Impedimentos

- Registrar bloqueios em `docs/impediments_log.md`.
- SM e bmad-master atuam para remover impedimentos e reabrir tarefas se QA reprovar (com comentário de falha).

---

**Versão:** 1.0  
**Data:** 2025-02  
**Autor:** SM Agent (BMAD)
