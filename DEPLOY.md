# Deploy da Sophia

> Este arquivo é guia interno de deploy. Não aparece no README de vitrine.

A Sophia foi reescrita em Next.js + Prisma com **PostgreSQL como banco padrão** (substituiu SQLite por escolha de produção). Em dev, o Postgres roda via Docker; em prod, recomenda-se [Neon](https://neon.tech) (free tier generoso, serverless, integra com Vercel) ou Vercel Postgres.

---

## Dev local — primeira vez

Pré-requisitos: Node 20+, npm, Docker Desktop.

```bash
# 1. Sobe o Postgres local (porta 5432, dados em volume nomeado)
npm run db:up

# 2. Copia env example e preenche
cp .env.example .env
# Os valores padrão de .env.example já apontam pro Postgres local.
# Só precisa preencher JWT_SECRET (gere com o comando que está nos comentários)
# e RESEND_API_KEY (opcional em dev — sem ele, e-mails não chegam).

# 3. Gera o cliente Prisma e roda a primeira migration
npm run prisma:generate
npm run prisma:migrate
# Quando perguntar o nome da migration, escreva: init

# 4. Sobe a app
npm run dev
```

App em <http://localhost:3000>.

### Dev local — comandos do dia a dia

| Comando | O que faz |
|---|---|
| `npm run dev` | Sobe o Next em watch mode |
| `npm run db:up` | Sobe o Postgres (já configurado) |
| `npm run db:down` | Para o Postgres (mantém dados) |
| `npm run db:reset` | **Apaga** o banco e recria do zero |
| `npm run prisma:studio` | Abre o GUI do Prisma para ver/editar dados |
| `npm run prisma:migrate` | Cria nova migration a partir de mudanças no schema |

---

## Produção — Vercel + Neon

### Passo 1: criar banco no Neon

1. Vá em [console.neon.tech](https://console.neon.tech) e crie conta (login com GitHub recomendado).
2. **Create Project** → escolha região (`AWS us-east-1` é a mesma da Vercel default).
3. Nome: `sophia`.
4. Copie a **connection string** (algo como `postgresql://user:pass@ep-xxx.us-east-1.aws.neon.tech/sophia?sslmode=require`).

### Passo 2: criar conta no Resend (e-mails transacionais)

1. [resend.com](https://resend.com) → criar conta.
2. Pegue a API key em **API Keys → Create API Key** com permissão `Sending access`.
3. Em dev, pode usar `onboarding@resend.dev` como remetente. Em prod sério, **adicione um domínio próprio** em Resend e configure os registros DNS (SPF, DKIM).

### Passo 3: deploy na Vercel

1. [vercel.com](https://vercel.com) → criar conta com login do GitHub.
2. **Add New → Project** → importe `BCartolano/assistente-puerperio` (ou o nome novo, se você renomear).
3. Vercel detecta Next.js automaticamente. **Não mude** Framework Preset, Build Command nem Output Directory — o `vercel.json` na raiz já cuida disso (rodando `prisma generate && prisma migrate deploy && next build`).
4. **Environment Variables** (clicar em "Environment Variables" antes de "Deploy"):

   | Nome | Valor |
   |---|---|
   | `DATABASE_URL` | (a connection string do Neon do passo 1) |
   | `JWT_SECRET` | (uma string aleatória de 64+ caracteres — gere com `node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"`) |
   | `RESEND_API_KEY` | (a API key do Resend do passo 2) |
   | `RESEND_FROM_EMAIL` | `Sophia <onboarding@resend.dev>` (ou o domínio próprio quando configurado) |
   | `APP_BASE_URL` | `https://sophia-puerperio.vercel.app` (ou o domínio custom — atualiza depois) |

5. **Deploy**. Build leva 2-4 min na primeira vez (instala deps, gera cliente Prisma, roda migration, builda Next).

6. Quando estiver `Ready`, abra a URL. Se a tela branca → checa os logs em **Deployments → \[último deploy\] → Build Logs**.

### Passo 4: domínio próprio (opcional)

Em **Project → Settings → Domains** pode adicionar `sophia.seudominio.com` ou comprar um direto na Vercel. SSL é automático.

Lembra de atualizar `APP_BASE_URL` em **Settings → Environment Variables** depois (e fazer um redeploy).

---

## Decisões técnicas relevantes

### Por que Postgres em dev (e não SQLite)?

- **Paridade dev/prod.** Bug que aparece em prod com Postgres dificilmente aparece em dev com SQLite. Várias features (timezones, transações, índices, JSON) se comportam diferente.
- **Migrations confiáveis.** Migration gerada para SQLite tem sintaxe diferente da gerada para Postgres. Manter dois sets de migration é dor de cabeça.
- **Custo zero.** Docker é grátis e Postgres roda em 50 MB de RAM em modo dev.

### Por que Neon (e não Vercel Postgres direto)?

- **Compute scales to zero.** Free tier do Neon dorme depois de 5 min sem queries — 0 custo no início.
- **Branches de banco.** Cada branch Git pode ter um banco isolado (útil pra preview deployments).
- **Serverless driver.** Conexão sob demanda, não precisa pool warm-up.
- Vercel Postgres é ótimo também — equivalente, ligeiramente mais integrado, mas menos generoso no free tier.

### Por que Resend (e não SendGrid/Mailgun)?

- API moderna, latência baixa.
- Free tier generoso (100/dia, 3000/mês).
- DX excelente — mesma equipe que faz `react-email`.

---

## Checklist pós-deploy

- [ ] Cadastro de teste recebe o e-mail de verificação
- [ ] Reset de senha recebe e-mail
- [ ] Login persiste sessão (cookie httpOnly funcionando)
- [ ] `prisma migrate deploy` rodou sem erro nos build logs
- [ ] `APP_BASE_URL` está apontando pra URL real (afeta links nos e-mails)
- [ ] Healthcheck básico: `/login` carrega sem erro 500
- [ ] Atualizar o repo da Sophia no `index.html` do Portfólio com link da demo (`https://...vercel.app`)
