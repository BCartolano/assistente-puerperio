# Service Worker: network-first para assets versionados

## Objetivo

Evitar que o SW sirva `chat.js` ou CSS antigos quando a URL tem cache-bust (`?v=...`). Assim, após deploy, o usuário recebe o novo JS/CSS na próxima carga.

## Mecânica

- **Arquivo:** `backend/static/js/sw-assets-bypass.js`
- **Regra:** Pedidos GET para `.js` / `.css` ou com `?v=` na query → **network-first** (fetch com `cache: 'no-store'`; se falhar, fallback para cache).
- **Inclusão:** No topo de `backend/static/sw.js`:  
  `importScripts('/static/js/sw-assets-bypass.js');`
- **Versão:** Bump de `CACHE_VERSION` no SW (ex.: v14 → v15) para forçar atualização do SW.

## Checklist pós-deploy

1. DevTools > Application > Service Workers: **Update** / **Skip waiting**
2. Opcional: **Unregister** uma vez e recarregar
3. **Clear site data** ou Hard reload 2x (Ctrl+Shift+R)
4. Aba Network: `chat.js` e CSS vindo da **rede**, não "(from ServiceWorker)" ou "from disk cache"
