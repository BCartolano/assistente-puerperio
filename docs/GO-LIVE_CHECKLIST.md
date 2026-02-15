# Go‑Live Checklist (Azure App Service)

Objetivo: publicar com segurança e previsibilidade. Tudo abaixo é rápido de validar.

## 1) Pré‑deploy local (uma vez por release)

- **Lint e checagens**
  - `npm run lint`
  - `npm run check:js`
- **Índices/dados**
  - `python scripts/build_hospitals_index.py`
  - `python scripts/validate_educational.py`
- **Teste local rápido**
  - `gunicorn -w 2 -k gthread -t 120 -b 127.0.0.1:5000 backend.app:app`
  - `scripts/smoke-tests.sh http://127.0.0.1:5000` (ou o PS1)

## 2) Azure App Service (Linux, Python 3.11)

- **Startup Command**
  - `gunicorn -w 2 -k gthread -t 120 -b 0.0.0.0:8000 backend.app:app`
- **App Settings (variáveis)**
  - SCM_DO_BUILD_DURING_DEPLOYMENT=true
  - WEBSITES_PORT=8000
  - FLASK_ENV=production
  - SECRET_KEY=valor aleatório
  - GROQ_API_KEY=…
  - HOSPITALS_INDEX_PATH=/home/site/wwwroot/backend/static/data/hospitais_index.json
  - (se usar e‑mail de confirmação) SMTP/SendGrid (host, user, senha, remetente)
- **Geral**
  - Always On: enabled
  - Logs de aplicação: enabled (tiers/retention conforme necessidade)

## 3) Segurança e privacidade

- **CSP** (já incluída no _csp_meta.html)
  - Ajuste connect-src se o backend/API estiver em outro domínio.
- **Cookies de sessão**
  - httpOnly, Secure (em https), SameSite=Lax (ou Strict)
- **Service Worker**
  - Bump de versão (CACHE_VERSION), skipWaiting + clients.claim
  - Hard reload após deploy
- **Rate‑limit** no login/recuperação (se aplicável)
- **Logs:** sem dados sensíveis/PII
- **HSTS** (opcional): ative no front escolhido (CDN/App Gateway)

## 4) Geolocalização (prioridade)

- Índice gerado e versionado: backend/static/data/hospitais_index.json
- **/api/nearby**
  - GET /api/nearby?lat=-23.55&lon=-46.63&radius_km=10&limit=5
  - Esperado: 200, JSON com items e distance_km
  - Filtros: accepts_sus=true/false, accepts_convenio=true/false, public_private=Público|Privado|Filantrópico
  - ETag presente nas respostas do índice
- **UI**
  - “Perto de você” exibe cards com SUS/Convênio e Público/Privado corretos
  - Sem badge “Privado” indevido (somente quando canônico)

## 5) Conteúdos educativos e UX

- **/api/educational**
  - 200, JSON com items, ETag/Cache‑Control: public, max‑age=60
- **Cards na home**
  - Shimmer inicial (600 ms min), ícones certos (fita rosa / mamadeiras)
  - “Leitura X min”, CTA abre gov.br em nova aba
  - Link “Ver todos” aponta para /conteudos
- **/conteudos**
  - Lista itens do educational.json

## 6) Chatbot “Sophia”

- **Prompt/guardrails**
  - Não diagnostica; mensagens de segurança; recursos 188/192/190/180
  - Antirrepetição ligada; tom acolhedor
- **Integração Groq**
  - GROQ_API_KEY setado; timeout/backoff (robustFetch) ativo
  - Respostas moderadas (temperature 0.5–0.7; frequency_penalty 0.6)

## 7) Performance

- Head com preconnect/dns‑prefetch (_perf_head_links.html)
- Prefetch em idle de /api/educational (perf‑prefetch.js)
- Fonts com display:swap (fonts.css) e preconnect (fonts.googleapis/gstatic)
- Skeletons com tempo mínimo e prefers‑reduced‑motion respeitado

## 8) Pós‑deploy

- Hard reload e, se houver Service Worker, Unregister uma vez
- Monitorar logs 15–30 min (erros 4xx/5xx, tempo de resposta)
- **Scripts de smoke test no ambiente**
  - bash: `scripts/smoke-tests.sh https://SEUAPP.azurewebsites.net`
  - PowerShell: `.\scripts\SMOKE_TESTS.ps1 -Base https://SEUAPP.azurewebsites.net`

## 9) Rollback simples

- Reverter o commit anterior e deixar a Action de deploy publicar
- Manter tag/branch “last‑good” para recovery rápido

## 10) Anotações úteis

- **CORS:** se o front estiver em domínio diferente, liste os origins permitidos
- **CDN/Cache:** invalide conteúdo estático se usar CDN
- **Logs** preservados (retention) e alerta básico em erros 5xx (App Service)

---

## Anexos

- scripts/smoke-tests.sh (bash)
- scripts/SMOKE_TESTS.ps1 (PowerShell)

### Smokes esperados (resumo)

- / → 200
- /conteudos → 200
- /api/educational → 200 (JSON) + ETag + Cache‑Control
- /api/nearby?lat=-23.55&lon=-46.63&radius_km=10&limit=5 → 200 (items>=0)
- Sem erros CSP no console
- Skeleton → conteúdo real (sem “colar”)

Se algo falhar, anote: endpoint + status + payload de erro (sem chaves/PII). Corrija, rode novamente os smokes e siga.
