# Sophia — Companheira no Puerpério

> Assistente virtual de apoio educativo e acolhimento emocional para mães no puerpério, com conteúdo curado a partir de fontes oficiais (Ministério da Saúde, OMS, FEBRASGO).

**Status:** em desenvolvimento ativo · deploy público planejado para Vercel + Neon Postgres.

---

## O que é

Sophia é uma aplicação web que combina **conversa acolhedora** com **biblioteca de conteúdo curado** sobre puerpério, gestação, parto, cuidados com o bebê e saúde emocional materna.

A proposta é simples: o pós-parto é um período de muita vulnerabilidade, e a maioria das mães não tem onde tirar dúvidas no meio da madrugada sem cair em fórum desorganizado ou em conselho médico genérico de chatbot. A Sophia ocupa esse espaço — não substituindo profissional de saúde, mas oferecendo presença e informação confiável até o próximo encontro com a equipe que cuida da mãe.

---

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

---

## Stack

| Camada | Tecnologia |
|---|---|
| Framework | Next.js 16 (App Router) + React 19 |
| Linguagem | TypeScript |
| Estilo | Tailwind CSS + design system próprio |
| Banco | Prisma ORM + PostgreSQL (Docker em dev · Neon em prod) |
| Auth | JWT em cookie httpOnly + bcrypt + verificação por código de e-mail |
| E-mail | Resend |
| Validação | Zod |

---

## Funcionalidades

### Conversa (`/conversar`)
- Chat com Sophia, respostas curadas por intenção
- Sugestões rápidas ("Estou cansada", "Tô feliz hoje", "Preciso desabafar"...)
- Disclaimer médico permanente
- Cards de conteúdo recomendado dentro da própria conversa
- Cartão de cuidado quando detecta queixa de saúde
- Protocolo de crise com encaminhamento direto para CVV/SAMU

### Biblioteca de conteúdo curado
- 30+ tópicos sobre puerpério, gestação, parto, cuidados do bebê, saúde emocional, dicas e guias práticos
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
- Páginas dedicadas de privacidade, termos e aviso legal
- **Direito ao esquecimento** com fluxo de exclusão de conta (`/excluir-meus-dados`) e cascade no banco

---

## Identidade visual

A Sophia foi desenhada para ser **acolhedora, calma e digna** — sem o visual hospitalar frio, sem o infantilizado pastel forçado.

- **Tipografia:** Playfair Display (títulos, serif elegante) + Inter (corpo, sans-serif moderna)
- **Detalhes:** linhas botânicas SVG sutis no fundo, sombras macias em rosa, cards com bordas arredondadas (até 28px)

### Paleta

| Token | Cor | Uso |
|---|---|---|
| `--rosa` | `#f0b8c4` | Principal (botões, destaques) |
| `--rosa-suave` | `#fbe5ea` | Fundos de hover |
| `--rosa-deep` | `#a85975` | Títulos e estados ativos |
| `--verde` | `#a9bda1` | Acento secundário (sálvia) |
| `--verde-forte` | `#6f8a68` | Status positivo, mensagens da usuária |
| `--dourado` | `#d4a574` | Avisos de transparência (banner IA, disclaimers) |
| `--fundo` | `#fef7f3` | Fundo creme quente da app |
| `--texto` | `#3d2c34` | Texto principal (alto contraste mas suave) |

### Componentes visuais característicos
- **Hero da conversa:** avatar circular grande da Sophia, gradiente rosa-creme, frase introdutória
- **Sidebar sticky** com logo redondo, nav rosada e seções tipográficas hierárquicas
- **Cards de cuidado** (mood, conteúdo recomendado, lembretes) com hover suave que eleva
- **Banner de transparência IA** dourado, com borda esquerda destacada
- **Storybook de consentimento LGPD** em modal, com progress dots e ilustrações próprias

---

## Compliance e segurança

- **Lei do Ato Médico (Lei 12.842/2013):** Sophia nunca diagnostica, nunca prescreve, nunca substitui consulta. Linguagem reforçada em todas as superfícies sensíveis.
- **LGPD:** consentimento granular versionado, gestor revisitável, direito ao esquecimento implementado de ponta a ponta.
- **Senhas:** bcryptjs com sal automático.
- **Sessões:** JWT em cookie `httpOnly` + `Secure` + `SameSite=Lax`.
- **Validação:** todas as entradas de API passam por schemas Zod.
- **Crise:** detecção determinística com encaminhamento imediato para CVV (188) e SAMU (192).

---

## Roadmap

- [x] Autenticação completa com verificação de e-mail
- [x] Biblioteca de conteúdo curado (30+ tópicos)
- [x] Motor de conversa rule-based com detecção de crise
- [x] Fluxo LGPD (consentimento + exclusão)
- [x] Design system próprio (rosa-pó + verde-sálvia + dourado)
- [ ] Diário da jornada com persistência
- [ ] Lembretes contextuais (vacinas do bebê, retornos pós-parto)
- [ ] Modo offline para conteúdo
- [ ] Deploy público (Vercel + Neon Postgres)
- [ ] App mobile (Expo)

---

## Disclaimer

Sophia é uma ferramenta de **apoio educativo e acolhimento**. Não substitui consulta médica, atendimento de urgência, nem acompanhamento psicológico ou psiquiátrico profissional.

- Emergência médica: **SAMU 192**
- Apoio emocional 24h: **CVV 188**

---

© 2026 Bruno Cartolano dos Santos. Projeto pessoal em desenvolvimento.
