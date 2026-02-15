# "Conexão Falha" / Request ID — Diagnóstico rápido

Quando aparecer **"Conexão Falha"** ou erro ao falar com a Sophia, normalmente é rede/timeout/CORS/cache. Use este checklist (2–5 min).

## 1. Linha/porta (PowerShell)

```powershell
Test-NetConnection api.groq.com -Port 443
```

Se falhar: rede/firewall/DNS.

## 2. Chave e CORS

```powershell
curl.exe -sS -D - https://api.groq.com/openai/v1/models -H "Authorization: Bearer YOUR_GROQ_API_KEY"
```

- **200** = internet e chave ok
- **401** = chave inválida
- **403/5xx/timeout** = auth, rota ou rede

## 3. Browser (se o erro veio do front)

- **Ctrl+Shift+R** (hard reload)
- **DevTools > Application > Service Workers** → Unregister ou Update, depois tente de novo
- **DevTools > Network**: veja status (CORS, 401, 429, 5xx, aborted)

## 4. Backend

- Logs do endpoint que chama a Groq: stack, status, tempo.
- Cada chamada Groq gera um **request_id** (UUID). Em falha após retries, o backend devolve `request_id` na resposta (fallback) e loga `[GROQ] request_id=... fail ...`.
- Ao reportar o problema, informe: **onde quebrou (front/back)**, **código/stack**, **status HTTP**, **request_id** (se tiver), e se o request no DevTools mostra **(from ServiceWorker)**.

## O que foi implementado (resiliência)

- **Backend**: retry com backoff (3 tentativas, 800 ms base) na chamada à Groq; `request_id` em todos os logs e na resposta em caso de fallback.
- **Frontend**: `logNetworkError(context, err)` no api-client — no console aparece `[NET] endpoint offline=... name=... code=... message=...`.
- **Service Worker**: versão `v13`, `skipWaiting` + `clients.claim`; cache antigo é limpo no activate. Rota `/sw.js` com `Cache-Control: no-cache`.
- **Resposta de fallback**: quando a Groq falha, a resposta exibida inclui o ID para suporte (copiar e enviar ao dev).
