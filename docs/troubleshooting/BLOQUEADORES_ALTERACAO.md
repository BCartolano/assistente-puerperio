# Bloqueadores de alteração – o que foi verificado e corrigido

## Service Worker

- **Arquivo:** `backend/static/sw.js`
- **Correção:** `CACHE_VERSION = 'v13'`; em `activate`, `event.waitUntil(caches.keys().then(...).then(() => self.clients.claim()))` para atualização imediata.
- **Rota `/sw.js`:** header `Cache-Control: no-cache, no-store, must-revalidate` para o navegador não cachear o SW.

## Cache do servidor

- **HTML (rota `/`):** resposta com `Cache-Control: no-cache, no-store, must-revalidate`.
- **APIs:** não cachear corpo de POST; GET de dados pode usar cache curto conforme endpoint.

## Proteções de branch/CI

- Verificar em `.github/workflows/` se há branch protection que impeça push em `auto/fix-geo-docs-sophia`. Se sim, documentar e usar merge via PR.
- Nenhuma alteração foi feita em CI que bloqueie deploy; apenas uso do branch indicado.

## Build / artefatos versionados

- Frontend (Vite) gera hashes em nome de arquivo quando configurado; garantir que o HTML referencia os bundles corretos (ex.: `?v=timestamp` já usado no template).
- Nenhum artefato faltando foi encontrado que travasse atualização.

## Resumo

- SW: versionado (v13), skipWaiting + clients.claim, rota sem cache.
- HTML: no-cache.
- Rate limit no login para evitar brute force (10 tentativas por IP / 15 min).
