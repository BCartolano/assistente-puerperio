# Sophia — Companheira no Puerpério

> Assistente virtual de apoio educativo e acolhimento emocional para mães no puerpério, com conteúdo informativo baseado em fontes oficiais (Ministério da Saúde, OMS).

**Status:** Em desenvolvimento ativo · roda em ambiente local · planejado para deploy público.

---

## O que é

Sophia é uma aplicação web que combina **conversa acolhedora** com **biblioteca de conteúdo curado** sobre puerpério, gestação, parto, cuidados com o bebê e saúde emocional materna.

A proposta é simples: o pós-parto é um período de muita vulnerabilidade, e a maioria das mães não tem onde tirar dúvidas no meio da madrugada sem cair em fórum desorganizado ou em conselho médico genérico de chatbot. A Sophia ocupa esse espaço — não substituindo profissional de saúde, mas oferecendo presença e informação confiável até o próximo encontro com a equipe que cuida da mãe.

## Por que rule-based (e não LLM)?

A Sophia **não usa OpenAI, Gemini ou qualquer LLM**. As respostas são geradas por um motor de regras com:

- **Detecção de intenção emocional** (cansaço, tristeza, ansiedade, culpa, solidão, sobrecarga, alegria) com respostas curadas para cada contexto.
- **Detecção de crise** (ideação suicida, automutilação) com encaminhamento imediato para CVV 188 e SAMU 192.
- **Detecção de queixas de saúde** com cartão de cuidado sugerindo UBS, obstetra ou pediatra — sem nunca dar diagnóstico ou indicar medicamento.
- **Recomendação contextual** de artigos da biblioteca a partir de palavras-chave.

Foi uma decisão de produto, não limitação técnica:

1. **Segurança clínica.** Em saúde materna, alucinação de LLM pode causar dano real. Resposta determinística, escrita por humano, é auditável.
2. **Tom consistente.** A voz da Sophia é construída — acolhedora, sem juízo, sem o tom robótico de "como assistente virtual eu não posso...".
3. **Custo zero por conversa.** Roda em qualquer hospedagem básica.
4. **LGPD mais simples.** Conteúdo das mensagens não sai do servidor.

## Stack

| Camada | Tecnologia |
|---|---|
| Framework | Next.js 16 (App Router) + React 19 |
| Linguagem | TypeScript |
| Estilo | Tailwind CSS + design system próprio (paleta rosa/dourado, tipografia Inter + Playfair Display) |
| Banco | Prisma ORM + SQLite (dev) |
| Auth | JWT em cookie httpOnly + bcrypt + verificação por código de e-mail |
| E-mail | Resend |
| Validação | Zod |

## Funcionalidades

### Conversa (`/conversar`)
- Chat com Sophia, respostas curadas por intenção
- Sugestões rápidas ("Estou cansada", "Tô feliz hoje", "Preciso desabafar"...)
- Disclaimer médico permanente
- Cards de conteúdo recomendado dentro da conversa
- Cartão de cuidado quando detecta queixa de saúde
- Protocolo de crise com encaminhamento para CVV/SAMU

### Biblioteca de conteúdo
- 30+ tópicos curados sobre puerpério, gestação, parto, cuidados do bebê, saúde emocional, dicas e guias práticos
- Cada tópico com seções, dica da Sophia, tópicos relacionados e referências oficiais
- Rotas: `/gestacao`, `/parto`, `/pos-parto`, `/cuidados-bebe`, `/saude-emocional`, `/dicas`, `/guias-praticos`, `/conteudo/[slug]`

### Conta da usuária
- Cadastro com verificação de e-mail por código
- Login com JWT em cookie httpOnly
- Esqueci/reset de senha por token
- Mudança de senha autenticada
- Reenvio de código de verificação
- Perfil, favoritos, jornada pessoal, configurações

### LGPD e privacidade
- Onboarding de consentimento granular (lembretes, conteúdos, rotinas, alertas, info municipal)
- Consentimento versionado (`sophia.consent.v1`) com data de aceite
- Gestor de consentimento revisitável (`/consentimento`)
- Página de privacidade, termos, aviso legal
- **Exclusão da conta** com fluxo dedicado (`/excluir-meus-dados`) e cascade no banco

## Estrutura

```
src/
├── app/                        # App Router — 28 rotas
│   ├── api/auth/               # 9 endpoints de autenticação
│   ├── conversar/              # chat principal
│   ├── conteudo/[slug]/        # biblioteca dinâmica
│   ├── consentimento/          # gestão LGPD
│   ├── excluir-meus-dados/     # direito ao esquecimento
│   └── ...
├── components/
│   ├── ChatSophia.tsx          # motor de conversa
│   ├── OnboardingConsent.tsx   # fluxo LGPD
│   ├── DeleteAccountFlow.tsx
│   └── ...
└── lib/
    ├── topicos.ts              # 1900+ linhas de conteúdo curado
    ├── auth.ts                 # helpers JWT
    ├── mailer.ts               # Resend wrapper
    └── referencias.ts          # bibliografia oficial
prisma/
└── schema.prisma               # User, VerifyToken, PasswordResetToken
```

## Como rodar localmente

Pré-requisitos: Node 20+, npm.

```bash
git clone <repo>
cd chatbot-puerperio
npm install

cp .env.example .env
# edite .env e preencha:
#   DATABASE_URL="file:./dev.db"
#   RESEND_API_KEY="<sua chave Resend>"
#   APP_BASE_URL="http://localhost:3000"
#   JWT_SECRET="<gere uma chave forte>"

npm run prisma:generate
npm run prisma:migrate

npm run dev
```

App em `http://localhost:3000` (redireciona para `/login`).

> Sem `RESEND_API_KEY` válida, o cadastro funciona mas o e-mail de verificação não chega — para testes, busque o token diretamente no banco.

## Roadmap

- [x] Autenticação completa com verificação de e-mail
- [x] Biblioteca de conteúdo curado
- [x] Motor de conversa rule-based com detecção de crise
- [x] Fluxo LGPD (consentimento + exclusão)
- [ ] Diário da jornada com persistência
- [ ] Lembretes contextuais (vacinas do bebê, retornos pós-parto)
- [ ] Modo offline para conteúdo
- [ ] Deploy público (Vercel + Turso)

## Disclaimer

Sophia é uma ferramenta de **apoio educativo e acolhimento**. Não substitui consulta médica, atendimento de urgência, nem acompanhamento psicológico ou psiquiátrico profissional.

- Emergência médica: **SAMU 192**
- Apoio emocional 24h: **CVV 188**

## Licença

Projeto pessoal em desenvolvimento. Direitos reservados.
