# Aplicar e validar 0005-fix-eslint.patch

**Patch na raiz:** `0005-fix-eslint.patch` (fix ESLint: duplicatas, loadChatHistoryFromServer, dicasContainer, prefixos _).

**Base do patch (opcional):** preencha com o SHA/branch onde ele foi gerado se quiser reduzir rejeições por drift.

> **Comunicado pro time:** Se já estiverem em árvore fixada, o patch não aplica — usem um branch/backup unfixed ou tratem o patch como referência.

---

## Aplicar em uma árvore "unfixed" (antes do fix)

Se algum passo falhar, veja [Se o apply rejeitar (fallback)](#se-o-apply-rejeitar-fallback).

```bash
git checkout -b apply-0005
git apply --check 0005-fix-eslint.patch
git apply 0005-fix-eslint.patch
git add -A && git commit -m "fix(eslint): remover duplicatas, renomear loadChatHistoryFromServer, declarar dicasContainer e prefixos _"
npm run lint
npm run check:js
```

**Teste em clone limpo (recomendado):** `git clone` → checkout no branch unfixed → `git apply --check 0005-fix-eslint.patch` → siga o doc. Garante que o fluxo está blindado contra drift.

---

## Validação rápida

### ESLint (.eslintrc.cjs)

- `grep -n "varsIgnorePattern: '^_'" .eslintrc.cjs`
- `grep -n "argsIgnorePattern: '^_'" .eslintrc.cjs`

### api-client.js

- `grep -n "cancelAll(" backend/static/js/api-client.js`  
  **Esperado:** apenas uma definição restante. Se aparecerem chamadas além da definição, abra o arquivo para confirmar que só há 1 método `cancelAll()`.

### chat.js

- `grep -n "async loadChatHistoryFromServer" backend/static/js/chat.js` (esperado: 1)
- `grep -n "this.loadChatHistoryFromServer(" backend/static/js/chat.js` (esperado: ≥1, ex.: initMainApp)
- `grep -n "this.loadChatHistory()" backend/static/js/chat.js` (esperado: chamadas para anônimos; tipicamente 2)  
  **Dica:** para evitar confundir com FromServer: `grep -n "this.loadChatHistory()" backend/static/js/chat.js | grep -v FromServer`

### mobile-navigation.js

- `grep -n "loadVideosLazy()" backend/static/js/mobile-navigation.js` (confirma a função)
- `grep -n "const dicasContainer" backend/static/js/mobile-navigation.js`
- `grep -n "const dicasContainer" backend/static/js/mobile-navigation.js | wc -l` (esperado: 1, sem redeclarações)

### device-detector.js e vaccination-timeline.js

- `grep -n "const _deviceType" backend/static/js/device-detector.js` (esperado: 1)
- `grep -n "_vaccineDate" backend/static/js/vaccination-timeline.js` (esperado: 1)
- `grep -n "const _today" backend/static/js/vaccination-timeline.js` (esperado: 1)

### Lint e checks

- `npm run lint` (esperado: sucesso; sem warnings se configurado com `--max-warnings 0`)
- `npm run check:js`

**CI:** para travar lint no pipeline, adicione `--max-warnings 0` no script ou job de lint (e mantenha o `varsIgnorePattern: '^_'` no `.eslintrc.cjs` como garantia extra).

---

## Se o apply rejeitar (fallback)

1. **Verifique primeiro:**  
   `git apply --check 0005-fix-eslint.patch`

2. **Se falhar, tente com rejeições e whitespace:**  
   `git apply --reject --whitespace=fix 0005-fix-eslint.patch`

3. **Investigue rejeições:**  
   `find . -name "*.rej" -print`  
   Abra os `.rej` e aplique manualmente as mudanças nos arquivos correspondentes.

4. **Se ainda travar:** envie **arquivo + número do hunk** (ou 2–3 linhas de contexto acima/abaixo do bloco que falhou) para reancorarmos o patch.

**Notas:**

- Se a sua árvore já estiver “fixada” (com essas mudanças aplicadas), o patch não vai aplicar — use um branch/backup “unfixed” ou trate o patch como referência.
- **Windows/CRLF:** em caso de rejeições de whitespace, use o fallback acima e, se necessário, aplique com `core.autocrlf` desativado temporariamente:  
  `git config core.autocrlf false` (ou `input` em ambientes mixed) → aplique o patch → depois restaure sua config.
