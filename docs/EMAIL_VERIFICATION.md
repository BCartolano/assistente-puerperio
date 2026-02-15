# Verificação de e-mail (Auth)

## Rotas

- **POST /api/register** { name, email, password } → cria usuário (users.json), envia e-mail de verificação, retorna { ok: true, need_verify: true }
- **GET /api/verify?token=...** → valida token, marca verified=true e redireciona para /
- **POST /api/login** { email, password } → { ok: true, user } (se verificado). Se não verificado, reenvia link e retorna { ok: false, error: "unverified", resent: true }
- **GET /api/me** → {} se não autenticado; { user, verified } se autenticado
- **POST /api/logout** → { ok: true }

## Envio de e-mail

- **SendGrid:** defina SENDGRID_API_KEY e SMTP_FROM.
- **SMTP:** SMTP_HOST, SMTP_PORT (padrão 587), SMTP_USER, SMTP_PASS, SMTP_SSL (true/false), SMTP_FROM.
- Sem config: faz log no console (modo dev).

## Tokens

- Assinados via HMAC (SECRET_KEY) com expiração (3 dias em /register e /login reenvio).

## Aviso

- É um store JSON simples para funcionar já. Se você tiver DB, adapte a persistência em backend/auth/routes.py.
