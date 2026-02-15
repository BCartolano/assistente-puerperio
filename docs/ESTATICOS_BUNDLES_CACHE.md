# Estáticos: cache e sugestão de bundles

## Cache (já aplicado)

- **STATIC_CACHE_MAX_AGE** (segundos): controla o `Cache-Control` de arquivos em `/static/`.
  - Ex.: `STATIC_CACHE_MAX_AGE=60` em dev (1 minuto).
  - Ex.: `STATIC_CACHE_MAX_AGE=3600` (1 hora) ou `31536000` (1 ano) em produção.
  - `STATIC_CACHE_MAX_AGE=0`: desativa cache (`no-store`).
- Recursos com `?v=` ou extensão `.css`/`.js`/imagens usam esse valor (limitado a 1 ano).
- Em produção, use versionamento na query string (`?v=...`) e valor alto para reduzir requisições.

## Sugestão de bundles (opcional)

Há muitos arquivos JS pequenos carregados na mesma página (ex.: `debug-guard.js`, `version-watchdog.js`, `flags-override-wire.js`, etc.). Duas abordagens:

### 1. Bundle “wire” (recomendado para dev)

- Concatenar em um único arquivo, por exemplo:
  - **wire-bundle.js**: `storage-namespace.js`, `debug-guard.js`, `flags-override-wire.js`, `version-watchdog.js`, `disable-autologin.js`, `fetch-deduped.js`, `emergency-headers-wire.js`, `nearby-headers-wire.js`, etc.
- No `index.html`, trocar a lista de `<script src="...">` por um único `<script src="/static/js/wire-bundle.js">`.
- Build manual (script) ou com ferramenta (esbuild, rollup) em modo “concat”.

### 2. Manter arquivos separados e cache agressivo

- Manter os scripts separados e usar **STATIC_CACHE_MAX_AGE** alto em produção (ex.: 3600 ou 86400).
- Assim o navegador reutiliza os arquivos e não refaz dezenas de requisições a cada reload.

Ambas reduzem requisições: bundle reduz o número de arquivos; cache alto reduz requisições repetidas.
