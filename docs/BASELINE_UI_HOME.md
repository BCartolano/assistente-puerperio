# Baseline de UI da Home — Sophia

**Ponto de restauração:** commit `481392f` (branch `auto/fix-geo-docs-sophia`).

Use este commit para reverter regressões visuais ou de comportamento responsivo na Home:

```bash
git checkout 481392f -- backend/static/css/style.css backend/static/css/educational-cards.css backend/static/js/edu-cards-wire.js backend/templates/index.html
```

---

## Instruções críticas para futuras iterações

### 1. Respeito à Baseline

- **Obrigatório:** Antes de alterar layout ou estilos da Home, consultar os comentários de manutenção em:
  - `backend/static/css/style.css`
  - `backend/static/css/educational-cards.css`

### 2. Linting e padronização

- **edu-cards-wire.js:** Manter o padrão de funções internas não usadas com **prefixo `_`** (ex.: `_norm`, `_addReadBadge`, `_createCard`) para conformidade com ESLint (`no-unused-vars`).

### 3. Layout persistente (não alterar sem aprovação)

| Regra | Detalhe |
|------|--------|
| **Conteúdos Educativos** | Não reverter a seção para carrossel horizontal. Manter lista vertical (grid 1 col mobile / 2 col desktop). |
| **Aviso Médico (mobile)** | Não aumentar o tamanho da fonte de `.medical-disclaimer-end` no mobile acima de **0.7rem** (botão) e **0.65rem** (corpo do texto). |
| **Perguntas rápidas** | Manter a especificidade **`!important`** no fundo branco da seção "Não sabe por onde começar?" (classe `quick-questions-section-white`, `background: #ffffff !important`). |

### 4. Regressões

- Se uma nova funcionalidade causar regressão visual ou no comportamento responsivo da Home, **restaurar a partir do commit 481392f** nos arquivos listados acima e reaplicar apenas as mudanças necessárias, respeitando esta baseline.
