# Reset de senha

## Rotas

- **POST /api/forgot-password**  
  Body: `{ "email": "..." }`  
  Sempre retorna `{ ok: true }` (não revela se o e-mail existe). Se existir usuário, envia e-mail com link de reset (expira em 1h).

- **GET /reset-password?token=...**  
  Página HTML com formulário para definir uma nova senha. Exibe aviso se o token parecer inválido.

- **POST /api/reset-password**  
  JSON ou form: `{ "token": "...", "password": "..." }`  
  Valida token e troca a senha. Mantém sessão logada após o reset.

## Templates dos e-mails

- backend/templates/email/reset.html e reset.txt

## Config

- **FRONTEND_BASE_URL** (opcional): base para montar o link do e-mail.
- **SECRET_KEY**: obrigatório para assinar/verificar tokens.
- Envio de e-mail: SENDGRID_API_KEY ou SMTP_* (ver EMAIL_VERIFICATION.md).

## Validação rápida (dev)

1. Crie usuário (register/verify) e faça forgot:  
   `curl -sS -X POST http://127.0.0.1:5000/api/forgot-password -H "Content-Type: application/json" -d "{\"email\":\"seu@email.com\"}"`
2. Veja no log o link /reset-password?token=... e abra no navegador.
3. Defina nova senha no formulário.
4. Faça login com a senha nova.

## Notas

- O store é JSON (backend/static/data/users.json); em produção, substitua por DB conforme necessário.
- O endpoint sempre retorna ok no forgot para evitar enumeração de e-mails.
