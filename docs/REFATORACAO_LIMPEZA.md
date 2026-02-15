# Refatoração e limpeza – Projeto Sophia

Documento de análise para otimizar a estrutura, remover redundâncias e preparar para novas funcionalidades.

---

## 1. Código morto identificado

### Backend

- **app.py**: As funções estão ligadas a rotas (`@app.route`), a `before_request`/`after_request`, ou são usadas internamente (ex.: `carregar_dados`, `send_email`). Não foi encontrada função definida em `app.py` que nunca seja chamada. O arquivo é muito grande (~7k linhas); a próxima melhoria é **modularizar em Blueprints** (ver seção 6).
- **routes.py (api)** e **routes_hospitais.py**: Rotas registradas nos blueprints e usadas pelo frontend. Nenhuma rota óbvia sem uso.
- **auth/routes.py**: Rotas de login, logout, registro, etc. Em uso.

Conclusão: não há “dead code” claro em rotas; o principal ganho é **quebrar app.py em blueprints** (chat, auth, saúde, etc.).

### Frontend – arquivos JS não referenciados no `index.html`

| Arquivo | Situação | Recomendação |
|--------|----------|--------------|
| **remove-app-update-wire.js** | Não referenciado. Restinho de aviso de atualização. | **Removido** (checkpoint aprovado). |
| **hospitals-searchlog-wire.js** | Não referenciado. Painel debug "Detalhes da busca". | **Removido** (checkpoint aprovado). |
| **login-forgot-wire.js** | Não referenciado. Adiciona o botão "Esqueci minha senha" no formulário de login e chama `/api/forgot-password`. | **Recomendado incluir** em `index.html` (uma linha) para a funcionalidade de recuperação de senha; ou remover se não for usada. |

Demais arquivos `.js` em `static/js` estão referenciados em `index.html`, em `emergencia.html`, em `sw.js` (importScripts) ou são injetados por outros scripts (ex.: `auth/login.js` na página de login via template).

### CSS

- Todos os CSS em `static/css` são usados: seja por `index.html` (link direto), seja injetados por scripts (ex.: `theme-polish-wire.js` → `fonts.css`, `a11y-polish.css`; `edu-cards-wire.js` e skeletons → `skeleton.css`), ou em outras páginas (`conteudos.html`, `reset_password.html` → `a11y-polish.css`). Nenhum arquivo CSS óbvio como morto.

---

## 2. Lista de arquivos para você confirmar antes de deletar

**Regra:** nada será apagado sem sua confirmação. Abaixo, apenas a lista sugerida.

### 2.1 Scripts JS (código morto)

- `backend/static/js/remove-app-update-wire.js` – não referenciado.
- `backend/static/js/hospitals-searchlog-wire.js` – não referenciado.

(Se quiser manter o comportamento de “Esqueci minha senha”, **não** apague `login-forgot-wire.js` e inclua-o no `index.html`.)

### 2.2 Base de dados e cache (`/data/`)

- O repositório atual **não** contém CSVs antigos nem `.pkl` versionados (pastas como `data/cache/`, `data/raw/` estão vazias ou no `.gitignore`).
- O `.gitignore` já cobre: `data/raw/`, `data/*202*.csv`, `data/geo/` (exceto um parquet), `reports/`, `logs/`, `BASE_DE_DADOS_CNES_*/`.
- **Se** na sua máquina existirem arquivos como `data/tbEstabelecimento202410.csv` ou `data/cache/cnes_overrides_*.pkl` de meses anteriores a 202512, pode removê-los manualmente após backup; não estão no repo.
- **Logs antigos:** a pasta `logs/` está no `.gitignore`. Se houver `logs/*.log` ou `logs/search_events.jsonl` no disco, pode apagar após conferir. Não deletamos nada automaticamente.

### 2.3 Resumo – confirme antes de deletar

- [x] ~~`backend/static/js/remove-app-update-wire.js`~~ (removido)
- [x] ~~`backend/static/js/hospitals-searchlog-wire.js`~~ (removido)
- (Opcional) `backend/static/js/login-forgot-wire.js` – só se não for usar “Esqueci minha senha”.

---

## 3. Consolidação de estáticos (bundling manual)

Há muitos arquivos pequenos (vários `*-wire.js`, `debug-guard.js`, `version-watchdog.js`, etc.). Duas frentes:

### 3.1 Proposta de bundles

- **wire-bundle.js** (carregar no head, antes do resto):
  - `storage-namespace.js`, `debug-guard.js`, `flags-override-wire.js`, `version-watchdog.js`, `disable-autologin.js`, `fetch-deduped.js`, `login-forgot-wire.js`, `emergency-headers-wire.js`, `nearby-headers-wire.js`, `hospitals-hud-wire.js`, `hospitals-offline-wire.js`, `kill-searchlog-wire.js`, `kill-gps-refresh-wire.js`, `debug-drawer.js`
- **ui-components.js** (lógica de UI / wires de categorias e esqueleto):
  - `theme-polish-wire.js`, `categories-cards-wire.js`, `categories-filters-wire.js`, `categories-skeleton-wire.js`, `nearby-skeleton-wire.js`, `hospitals-skeleton-wire.js`, `edu-cards-wire.js`, `card-ownership-integrated.js`, `nearby-wire.js`, `chat-header-offset.js`, `skeleton-toggle-dev.js` (ou manter condicional)
- Manter separados: `boot.js`, `chat.js`, `api-client.js`, `hospitals-ux-bundle.js`, `hospital-cards-emergency.js`, `vaccination-timeline.js`, `mobile-navigation.js`, etc., por tamanho e responsabilidade.

Implementação sugerida: um script de build (Node ou Python) que concatena os arquivos na ordem acima e gera `wire-bundle.js` e `ui-components.js`; no `index.html`, trocar a lista de `<script>` pelos dois (ou três) bundles. Isso reduz bastante o número de requisições na primeira carga.

### 3.2 Cache

- Já configurado: `STATIC_CACHE_MAX_AGE` para `/static/`. Em produção, use versionamento (`?v=...`) e valor alto para reduzir requisições repetidas.

---

## 4. Imports não utilizados (.py)

- Em arquivos muito grandes (ex.: `app.py`), a remoção automática de imports é arriscada. Recomendação: usar **ruff** ou **pyflakes** no CI, por exemplo:
  - `ruff check --select F401 .`
  - Isso lista imports não usados (F401). Você pode corrigir aos poucos.
- Em arquivos menores, vale a pena remover manualmente. Exemplo: em `app.py` há muitos `import`; alguns podem estar sem uso (ex.: `difflib`, `islice`). Sugestão: rodar `ruff check backend/app.py --select F401` e revisar cada caso.

Não foram removidos imports automaticamente neste passo para evitar quebrar o app; apenas documentamos a estratégia.

---

## 5. requirements.txt – dependências “fantasmas”

Comparando o que está em `requirements.txt` com o que é importado no projeto:

| Pacote | Uso real | Ação sugerida |
|--------|----------|----------------|
| **folium** | Não encontrado em nenhum `.py` (apenas em requirements). | **Remover** ou marcar como opcional (ex.: `# folium  # opcional – visualização de mapas, não usado no app atualmente`). |
| **geopy** | Usado em `scripts/geocodificar_enderecos.py` (scripts de pipeline). | Manter (uso em script). |
| **flask-compress** | Usado em `app.py` (Compress). | Manter. |
| **opencensus-ext-azure** | Usado em `backend/monitoring/appinsights.py` (opcional). | Manter. |
| **scikit-learn** | Usado em `backend/services/spatial_search_service.py` (BallTree). | Manter. |
| **tqdm, colorama, distro** | Transitive/dev; podem vir de outras libs. | Manter se não der erro ao remover. |

Alteração aplicada no repo: **folium** comentado ou removido do `requirements.txt` (conforme escolha abaixo), pois não é importado em nenhum módulo do app.

---

## 6. Dicas de arquitetura (para deixar o projeto mais leve)

- **Modularização (Blueprints):** Plano detalhado em **`docs/ARQUITETURA_BLUEPRINTS_SOPHIA.md`** – criação de `backend/blueprints/` com `auth_routes.py`, `chat_routes.py`, `health_routes.py`, `edu_routes.py`. Execute esse plano na próxima interação para que o `app.py` não exploda.
- **Externalização de dados:** Conteúdos educativos (cards, etc.) já estão em JSONs externos; manter assim e evitar hardcode no Python.
- **Mídia (peso do repo):** Não coloque vídeos/imagens pesados no repositório. Use **YouTube/Vimeo** para vídeos e **Cloudinary/Imgur** (ou CDN) para imagens; o Cursor e o clone do repo ficam leves.

---

## 7. Ações já realizadas neste passo

- **requirements.txt:** `folium` marcado como opcional/removido (conforme edição aplicada).
- **login-forgot-wire.js:** Adicionada referência no `index.html` para que o botão “Esqueci minha senha” funcione na tela de login (recomendado manter o arquivo).
- **Documento:** Este `docs/REFATORACAO_LIMPEZA.md` criado com toda a análise e a lista de arquivos para você confirmar antes de qualquer deleção física.

Nenhum arquivo físico foi deletado; apenas listados para sua confirmação.
