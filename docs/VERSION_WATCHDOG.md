# Version Watchdog

## O que é

- Um script leve que consulta `/version.json` (sem cache). Se a versão mudar:
  - atualiza o Service Worker,
  - limpa caches de assets (.js/.css e URLs com `?v=`),
  - grava a nova versão em `localStorage.app_version`,
  - recarrega a página.

## Onde está

- `backend/static/js/version-watchdog.js`
- Injetado na index, conteudos, reset_password, páginas de erro e legais.

## Como define a versão

- `BUILD_VERSION` (env) — recomendado no CI/CD — ou arquivo `VERSION` na raiz do repo.
- Sem nada definido, usa timestamp do processo (muda a cada restart).

## Validação

- Altere `BUILD_VERSION` no ambiente (ou o arquivo `VERSION`) e publique.
- As páginas devem recarregar sozinhas na próxima checagem (até 5 minutos) ou imediatamente com `?refresh=1`.

## Notas

Junto com:

- SW: assets network-first e /api/* network-first (0061),
- HTML no-store,
- e o desativador de autologin,

a UI não fica "presa" em versões antigas.
