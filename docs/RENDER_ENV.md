# Variáveis de ambiente no Render

No **Render** → seu Web Service → **Environment** → **Add Environment Variable**, configure:

## Obrigatórias

| Variável    | Exemplo / Descrição |
|------------|----------------------|
| **SECRET_KEY** | Uma string longa e aleatória (sessões Flask, login, tokens). Ex.: gere com `python -c "import secrets; print(secrets.token_hex(32))"` |

## Recomendadas (email e links)

| Variável    | Exemplo / Descrição |
|------------|----------------------|
| **BASE_URL** | URL pública do app. Ex.: `https://assistente-puerperio.onrender.com` (sem barra no final). Usado em links de verificação de email e recuperação de senha. |
| **RESEND_API_KEY** | Chave da API do [Resend](https://resend.com) (3.000 emails/mês grátis). Necessária para envio de email de verificação e “esqueci minha senha”. |
| **RESEND_FROM** | (Opcional) Remetente. Ex.: `Sophia <noreply@seudominio.com>`. Se não definir, usa `onboarding@resend.dev` (só envia para o email da sua conta Resend). |

## Chat com IA (padrão: Groq)

O app usa **AI_PROVIDER=groq** por padrão. Para o chat com IA funcionar, defina:

| Variável    | Exemplo / Descrição |
|------------|----------------------|
| **GROQ_API_KEY** | Chave da API da [Groq](https://console.groq.com) (grátis). Sem ela, o log mostra "GROQ_API_KEY não está definido" e o chat usa só respostas locais (fallback). |

Se não configurar, o site sobe mas as respostas do chat vêm do fallback local, não da IA.

## Opcionais

- **FLASK_ENV** = `production` (Render costuma definir)
- **SESSION_SECURE** = `1` para cookies seguros em HTTPS
- **MAIL_*** — use só se **não** for usar Resend (Gmail SMTP): `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_DEFAULT_SENDER`, etc. (ver `env.example`)

---

**Resumo rápido para colar no Render:**

- `SECRET_KEY` = (gere uma chave segura)
- `BASE_URL` = `https://assistente-puerperio.onrender.com`
- `GROQ_API_KEY` = (sua chave Groq para o chat com IA)
- `RESEND_API_KEY` = (sua chave do Resend, se for usar email)
