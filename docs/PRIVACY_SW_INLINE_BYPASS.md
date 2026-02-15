# SW – bypass inline para rotas sensíveis

## O que este snippet faz

- Força **network-only** (no-store) para:  
  `/api/me`, `/api/user-data`, `/api/register`, `/api/login`, `/api/logout`, `/api/verify`, `/api/forgot-password`, `/api/reset-password`
- Aceita atualização dinâmica dos padrões via **postMessage** do cliente (`AUTH_CACHE_BYPASS`).

## Como usar

1. Aplique o patch que cria **backend/static/js/sw-auth-bypass.js**.
2. No seu Service Worker, no topo:  
   `importScripts('/static/js/sw-auth-bypass.js');`
3. Faça “version bump” do SW (se usar `CACHE_VERSION`).
4. Atualize o SW em runtime (Update / SkipWaiting).

## Observações

- Já temos:
  - Headers no-store / Vary: Cookie nas respostas sensíveis (patch 0046).
  - **auth-cache-buster.js** (patch 0047) enviando o `AUTH_CACHE_BYPASS` ao SW e limpando o Cache Storage legado.
- Este snippet garante que mesmo um SW com estratégia cache-first não responda com dados de outra sessão.

## Validação

- DevTools > Application > Service Workers: atualize o SW e confira que **sw-auth-bypass.js** está carregado.
- Teste de troca de usuário no mesmo navegador (A → logout → B → logout → A): header/subtítulo e `/api/me` devem refletir sempre o usuário atual.
- No Network, as chamadas às rotas sensíveis devem aparecer sem “(from disk cache)” e com Cache-Control: no-store.

## Automação (0047b)

- Se enviar o caminho do arquivo do SW e 2–3 linhas que incluem `addEventListener('fetch', ...)`, pode ser gerado o 0047b para:
  - inserir automaticamente a linha `importScripts('/static/js/sw-auth-bypass.js');` no topo do SW;
  - opcionalmente, adicionar a lógica de bypass no bloco de fetch existente.
