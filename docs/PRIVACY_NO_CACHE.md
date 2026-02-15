# Privacidade: no-cache em dados do usuário

## Por que endpoints personalizados não devem ser cacheados

Respostas de `/api/me` e `/api/user-data` dependem do cookie de sessão. Se forem cacheadas (por Cache Storage, Service Worker ou CDN), um usuário pode ver dados de outro que usou o mesmo navegador. Isso causa vazamento de privacidade (ex.: nome do bebê ou da mãe no header).

## O que foi adicionado

- **Backend (auth):** Todas as respostas de `/api/me`, `/api/user-data` (override), `/api/register`, `/api/login`, `/api/logout`, `/api/verify`, `/api/forgot-password` e `/api/reset-password` enviam:
  - `Cache-Control: no-store, no-cache, must-revalidate, max-age=0`
  - `Pragma: no-cache`
  - `Vary: Cookie`
- **Frontend (privacy-storage-guard.js):**
  - Chama `/api/me` com `cache: 'no-store'` e `credentials: 'include'`.
  - Remove do `localStorage` chaves globais que podem vazar entre usuários (`user_name`, `baby_name`, `header_subtitle`, etc.) quando não estão namespacadas por `user:`.
  - Define `current_user_id` como âncora da sessão atual.

## Inclusão

Inclua o script após os outros wires:  
`<script src="/static/js/privacy-storage-guard.js" defer></script>`
