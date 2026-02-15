# Arquitetura "Mansão" – Modularização em Blueprints (Sophia)

Plano para preparar o projeto para crescer sem que o `app.py` exploda e sem que um erro em um módulo quebre os outros.

---

## Objetivo

- Criar a pasta **`backend/blueprints/`** e separar as rotas do `app.py` em Blueprints por domínio.
- Cada Blueprint fica em um arquivo isolado: **auth**, **chat**, **health**, **edu**.
- O `app.py` passa a ser um “orquestrador” que cria o Flask, carrega config e registra os Blueprints.

---

## Estrutura proposta

```
backend/
  app.py                    # Só: criar app, config, carregar .env, registrar blueprints
  blueprints/
    __init__.py             # Opcional: exporta todos os blueprints
    auth_routes.py          # Login, Cadastro, Esqueci Senha, Verificação email, Logout
    chat_routes.py          # Interação com a IA, Histórico, /api/chat, limpar memória
    health_routes.py        # CNES, Hospitais, Vacinação, /api/v1/emergency, /api/nearby, facilities
    edu_routes.py           # Cards educativos, /api/educational, página /conteudos
```

---

## Separação por Blueprint

### 1. **auth_routes.py** (Blueprint `auth_bp`)

- Rotas de **login** (GET/POST), **logout**, **cadastro** (registro), **esqueci senha**, **verificação de email**, **reset de senha**.
- Tudo que hoje está em `app.py` relacionado a `/auth/login`, `/api/login`, `/api/register`, `/api/forgot-password`, `/api/verify-email`, reset de senha, e em `backend/auth/routes.py` (se já existir um auth_bp, pode ser consolidado aqui ou o auth/ vira um wrapper que importa do blueprints).
- Templates: login, forgot_password, reset_password, verificação.
- Dependências: `init_db`, `load_user`, `send_email`, modelos de usuário (podem ficar em `app.py` ou em um `models.py` compartilhado).

### 2. **chat_routes.py** (Blueprint `chat_bp`)

- Rotas de **chat com a IA**: `/api/chat`, histórico (`/api/historico`, limpar memória), detecção de risco, etc.
- Toda a lógica do `ChatbotPuerperio`, busca local, chamadas a OpenAI/Gemini/Groq, `carregar_dados` / `BASE_CONHECIMENTO` (podem ser importados de um módulo `backend/knowledge.py` ou permanecer carregados no app e passados ao blueprint).
- Rotas de histórico e limpeza de memória da Sophia.

### 3. **health_routes.py** (Blueprint `health_bp`)

- Tudo relacionado a **CNES, hospitais, vacinação**:
  - `/api/v1/emergency/search`, `/api/v1/emergency/health`, `/api/nearby`, `/api/v1/facilities/search`
  - Rotas de vacinação (se houver), integração com overrides CNES, geo, OSRM, etc.
- Pode importar e registrar também os blueprints já existentes (`geo_bp`, `hospitais_bp` da API) ou consolidar as rotas aqui.
- Dependências: `backend/startup/cnes_overrides`, `backend/services/spatial_search_service`, `backend/api/routes.py` (FastAPI) ou equivalente em Flask.

### 4. **edu_routes.py** (Blueprint `edu_bp`)

- **Cards educativos** e conteúdo estático:
  - `/api/educational`, página **/conteudos**
  - Dados de guias, vacinas (mãe/bebê), cuidados (gestação, pós-parto), etc., se forem servidos por rotas próprias.
- Mantém o repositório de conteúdo em JSONs externos (já é assim); o blueprint só expõe as rotas e lê os dados.

---

## Ordem de execução sugerida (para a próxima interação)

1. **Criar** `backend/blueprints/` e `__init__.py`.
2. **Extrair auth**: criar `auth_routes.py`, mover rotas e funções de login/cadastro/esqueci senha/verificação do `app.py` para o blueprint; registrar no `app.py`.
3. **Extrair edu**: criar `edu_routes.py`, mover `/api/educational` e `/conteudos`; registrar.
4. **Extrair health**: criar `health_routes.py`, mover rotas de emergency, nearby, facilities; integrar com blueprints existentes (geo, hospitais) se fizer sentido; registrar.
5. **Extrair chat**: criar `chat_routes.py`, mover `/api/chat`, histórico, limpar memória e toda a lógica do chatbot; registrar.
6. **Limpar app.py**: deixar só criação do app, config, middlewares (CORS, cache, before/after_request globais), registro de blueprints e o que for compartilhado (ex.: `load_user`, `init_db` se ficarem no app).

---

## Dica de “peso” (repositório leve)

- **Vídeos:** usar links do **YouTube** ou **Vimeo**; não colocar arquivos de vídeo no repositório.
- **Imagens** (fotos, ilustrações educativas): usar **Cloudinary**, **Imgur** ou outro CDN; não subir gigabytes de mídia para o repo.
- Isso mantém o repositório leve e o Cursor rápido.

---

## Comando sugerido para a próxima interação

> Cursor, vamos executar o plano de Blueprints da Sophia. Siga o documento `docs/ARQUITETURA_BLUEPRINTS_SOPHIA.md`: crie `backend/blueprints/` e os arquivos `auth_routes.py`, `chat_routes.py`, `health_routes.py`, `edu_routes.py`. Migre as rotas do `app.py` para cada blueprint na ordem sugerida (auth → edu → health → chat) e registre os blueprints no `app.py`. Ao final, o `app.py` deve conter apenas criação do app, config e registro de blueprints.

Quando estiver pronto para executar, use o comando acima (ou uma variação) para a IA implementar o plano passo a passo.

---

## Fase 1 concluída (edu_bp)

- **Estrutura criada:** `backend/blueprints/` com `__init__.py`, `edu_routes.py`, `auth_routes.py`, `health_routes.py`, `chat_routes.py`.
- **edu_bp ativo:** Rotas `/conteudos` e `/api/educational` migradas para `edu_routes.py` e registradas em `app.py` com `url_prefix=""` (URLs inalteradas).
- **Referência atualizada:** `backend/auth/routes.py` passou a usar `url_for("edu.conteudos_page")` em vez de `url_for("conteudos_page")`.
- **auth_bp, health_bp, chat_bp:** Arquivos criados como stubs (sem rotas); a lógica continua em `app.py`. Migração em fases seguintes para evitar import circular e quebrar o app.

**Próximas fases:** Migrar health (emergency, facilities, health endpoints), depois auth (com extração de helpers para `current_app.config["DB_PATH"]`, User, email), depois chat (com instância do chatbot/BASE_CONHECIMENTO via módulo compartilhado ou `current_app`).
