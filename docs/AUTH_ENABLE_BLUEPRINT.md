# Ativando o auth (e-mail) sem apagar rotas antigas

## Como funciona

- O blueprint **auth_bp** já registra: `/api/register`, `/api/verify`, `/api/login`, `/api/me`, `/api/logout`.
- Se seu **app.py** também tiver essas rotas legadas, elas podem conflitar.
- Este patch sobrescreve os “view functions” das URLs legadas para apontarem para as do blueprint (sem apagar código antigo).

## O que foi adicionado

- Em **backend/app.py**, após registrar **auth_bp**, a função `_override_route(path, src_endpoint)` percorre as regras e reatribui o `app.view_functions` das URLs:
  - `/api/register` → auth.api_register
  - `/api/login` → auth.api_login
  - `/api/logout` → auth.api_logout
  - `/api/me` → auth.api_me
  - `/api/verify` → auth.api_verify

## Validação rápida

- **Registro:** POST /api/register { name, email, password } → { ok: true, need_verify: true } e e-mail enviado (ou logado no console)
- **Verificação:** GET /api/verify?token=... → redireciona para /
- **Login:** POST /api/login { email, password } → { ok: true, user } (se verificado)
- **Sessão:** GET /api/me → {} (anônimo) ou { user, verified: true }

Quando quiser, pode remover as rotas legadas com calma — o override já garante que as URLs usam o fluxo novo.
