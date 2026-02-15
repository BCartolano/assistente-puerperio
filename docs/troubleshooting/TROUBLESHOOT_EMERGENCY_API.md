# Troubleshooting – 5000 (404) e 8000 (connection refused)

Quando o log mostra:
- **5000: 404** → o processo na porta 5000 **não** é o Flask com `/api/v1/emergency/search`.
- **8000: connection refused** → o FastAPI não está rodando.

---

## Passo 1 — Testa 5000 direto (sem UI)

**Health:**
```bash
curl -i "http://localhost:5000/api/v1/health"
```
Esperado: **200**.

**Search:**
```bash
curl -i "http://localhost:5000/api/v1/emergency/search?lat=-23.1931904&lon=-45.7965568&radius_km=25&expand=true&limit=20&min_results=12&debug=true"
```
Esperado: **200** com JSON (ou **503** se dataset ausente → rode `python backend/pipelines/geocode_ready.py --mode copy`).

---

## Passo 2 — Se a página não está no mesmo host/porta

Se a UI roda em outra origem (ex.: `http://localhost:5173`), ative CORS no Flask.

No **.env**:
```env
ALLOW_ORIGINS=http://localhost:5173,http://localhost:5000
```

**Teste CORS com curl (simula origem Vite):**
```bash
curl -i -H "Origin: http://localhost:5173" "http://localhost:5000/api/v1/health"
```
A resposta deve ter `Access-Control-Allow-Origin: http://localhost:5173`.

---

## Passo 3 — Log de requisições no Flask

O app já registra REQ/RES no logger `sophia.api`. No terminal do Flask você verá:
```text
REQ GET /api/v1/health?
RES GET /api/v1/health -> 200
REQ GET /api/v1/emergency/search?lat=...
RES GET /api/v1/emergency/search -> 200
```
Quando a UI chamar, você verá exatamente se chegou, qual rota e o status (200/404/500).

**Debug na UI:** no console do navegador, cada tentativa de base mostra:
```text
[MAPS DEBUG] http://localhost:5000/api/v1/emergency/search?... -> 200 OK
```
Se aparecer `-> 500` ou `-> 404`, o problema está no backend; se `Failed to fetch`, é CORS/rede.

---

## Diagnóstico rápido (o que significa cada caso)

| Situação | Significado | Ação |
|----------|-------------|------|
| **200** no curl e **200** no Network | OK. Se a UI ainda falhar, é código do card/conversão; mande o payload da response. | |
| **503** | Dataset ausente | `python backend/pipelines/geocode_ready.py --mode copy` |
| **404** | Rota não carregou | `flask --app backend.app --debug run -p 5000` e confira `/__debug/routes` |
| **500** | Erro no servidor | Veja o stack no terminal do Flask (quase sempre NameError/KeyError); mande a linha para o fix. |
| **Failed to fetch** / **mixed-content** | Página em HTTPS e API em HTTP, ou CORS bloqueando | Sirva a UI pelo mesmo host/HTTPS (Nginx/Traefik) ou ative CORS e use mesma origem. |

Para fechar o diagnóstico, envie:
- **Status da 5000** (200/503/404/500) na aba Network.
- Um trecho do **Response** (ou só o campo `debug` do JSON).

---

## Subir o servidor

Use **um único comando** (na raiz do projeto):

```bash
python start.py
```

Isso sobe o Flask na porta 5000 (chat, API e localizador). Detalhes: [COMO_INICIAR_SERVIDOR.md](COMO_INICIAR_SERVIDOR.md).

Se precisar só do Flask sem o script de checagens: `python -m flask --app backend.app run -p 5000`.

---

## Passo 2 — Conferir as rotas no 5000

- **Listar rotas:** http://localhost:5000/__debug/routes  
  Deve listar `GET /api/v1/emergency/search`.

- **Testar direto:**  
  http://localhost:5000/api/v1/emergency/search?lat=-23.1931904&lon=-45.7965568&radius_km=25&expand=true&limit=20&min_results=12&debug=true  
  Esperado: **200** + JSON com `debug`.

---

## Tentar de novo na UI

Abra o modal de hospitais. No console você deve ver:
```text
[MAPS DEBUG] http://localhost:5000/api/v1/emergency/search?... -> 200 OK
```
Se a UI falhar no 5000 e cair no 8000, tudo bem (desde que o uvicorn esteja ativo).

**Patch debug (forçar same-origin):** na console do navegador, antes de abrir o modal:
```javascript
window.SOPHIA_API_BASE = window.location.origin;  // temporário: usa só a origem da página
```
Recarregue e tente de novo; a primeira base será a mesma origem (evita CORS quando a UI está em 5000).

---

## Se continuar 404 no 5000

Outro app está ocupando a porta. Mate e suba o certo:

1. **PowerShell:** `netstat -ano | findstr :5000` → anote o **PID**.
2. **Gerenciador de Tarefas** → Finalizar o processo com esse PID (ou feche o terminal que está rodando o app errado).
3. Suba de novo: `python -m flask --app backend.app --debug run -p 5000` (com `$env:FLASK_APP="backend.app:app"` já definido).

---

## Se der CORS ao falar com 8000

No `.env` (ou variáveis do FastAPI), garanta:
```env
ALLOW_ORIGINS=*
```
(ou o origin exato da sua UI). Reinicie o uvicorn.

---

## Ordem de tentativa na UI (chat.js)

O front já tenta, nesta ordem:
1. **Same-origin** (`window.location.origin`) — quando a UI está no mesmo host/porta do backend.
2. **SOPHIA_API_BASE** (se definido no `window`).
3. **http://localhost:5000**
4. **http://localhost:8000**
5. **http://127.0.0.1:8000**

Ou seja, se a UI estiver em `http://localhost:5000`, a primeira requisição já vai para o Flask na 5000.

---

## Checklist rápido

| Item | OK? |
|------|-----|
| `/api/v1/health` no 5000 responde? | |
| `/__debug/routes` lista `/api/v1/emergency/search`? | |
| UI volta a listar hospitais (Confirmados + Prováveis) sem erro? | |

---

## Se algo fugir disso

Envie:
1. A resposta de **http://localhost:5000/__debug/routes**
2. A resposta de **http://localhost:5000/api/v1/health**

Com isso dá para apontar o ajuste exato (entrypoint errado, prefixo, etc.).
