# Resgate do login e blindagem contra parse error

## Hotfix aplicado

### 1. Parse error em chat.js (~linha 5780)
- **Causa:** Template literal aninhado no `cardHtml` (FASE 3 – avisos de dados incompletos). O backtick interno fechava o template externo e gerava "missing ) after argument list".
- **Correção:** Bloco reescrito com IIFE que retorna string montada por concatenação (sem backticks aninhados). Sintaxe validada com `node --check backend/static/js/chat.js`.

### 2. Code-splitting: login não carrega chat.js
- **Já existente:** `data-page="{{ page|default('app') }}"` no `<html>`; rota define `page='login'` quando usuário não autenticado.
- **Scripts na tela de login:** Apenas `boot.js`, que carrega `auth/login.js`. **chat.js não é carregado** na página de login — parse error em chat.js não quebra login.
- **Scripts no app:** device-detector, api-client, toast, sidebar, vaccination-timeline, mobile-navigation, badges, chat.js.

### 3. Form com fallback sem JS
- **Form de login:** `action="/auth/login"` e `method="POST"`. Se o JS cair, o submit vai para o servidor e o login continua funcionando.
- **Com JS:** `auth/login.js` intercepta submit, chama `fetch('/api/login', ...)` e redireciona em caso de sucesso.

### 4. Service Worker
- Se houver SW cacheando a página de login, desabilitar para `/login` e `/auth` no SW (evitar JS antigo em cache).
- Em dev: `navigator.serviceWorker.getRegistrations().then(rs => rs.forEach(r => r.unregister()));` e hard reload.

---

## Blindagem para não quebrar de novo

### Verificação de sintaxe antes de commit
- **Node:** `node --check backend/static/js/chat.js` (e outros .js críticos).
- **ESLint (opcional):** `eslint . --max-warnings 0` em pre-commit (ex.: Husky + lint-staged).

### Pre-commit (Husky + lint-staged)
Exemplo de configuração para rodar em todo commit:
- **Husky:** hook `pre-commit` que chama `lint-staged`.
- **lint-staged:** para `backend/static/js/*.js`: `node --check` e (se quiser) `eslint --fix`.
- Assim, "missing )" e outros erros de parse não entram no repo.

### Teste de fumaça do login (E2E)
- Abrir `/` (ou rota de login).
- Preencher e-mail e senha (fake).
- Clicar Entrar.
- Verificar request e/ou redirecionamento (Playwright/Cypress).
- Rodar em CI/pre-push; se a IA quebrar algo, o merge bloqueia.

### Mapa de owners e sandbox para IA
- **Pastas protegidas:** `auth/`, `backend/static/js/auth/` (e opcionalmente core) com CODEOWNERS exigindo review humano.
- **Sandbox:** pasta `ai-sandbox/` para experimentos sem tocar em login/core.
- **README:** trecho curto tipo "Não editar estes arquivos sem review: auth, boot, login.js, chat.js (bloco displayHospitals)."

### Delegação de eventos (opcional)
- Botões com `data-action="foo"` e um único listener em `document.body` que despacha para `actions[el.dataset.action]`. Botão sem action registrada gera warning e não vira peso morto.

---

## Como enxugar o projeto (referência)

- **Onde está o peso:** `du -h -d 2` (mac/linux) ou WinDirStat no Windows; ver também `.git` com `du -sh .git`.
- **Limpeza:** remover `node_modules`, `dist`, `build`, `.cache`, `.next`, `coverage`; usar `pnpm` para reduzir tamanho de `node_modules`.
- **.git:** `git filter-repo` ou BFG para remover blobs grandes da história; binários em LFS ou storage externo.
- **Assets:** WebP/AVIF, não subir PSD/originais; docs em wiki ou índice enxuto.

---

## Comandos úteis

```bash
# Verificar sintaxe de chat.js
node --check backend/static/js/chat.js

# Limpar SW em dev (console do navegador)
navigator.serviceWorker.getRegistrations().then(rs => rs.forEach(r => r.unregister())); location.reload(true);
```
