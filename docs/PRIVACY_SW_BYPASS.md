# Bypass de cache para rotas sensíveis (SW + Cache Storage)

## O que este patch faz (lado do cliente)

- Remove do Cache Storage qualquer resposta antiga de:  
  `/api/me`, `/api/user-data`, `/api/register`, `/api/login`, `/api/logout`, `/api/verify`, `/api/forgot-password`, `/api/reset-password`
- Força `fetch(..., { cache: "no-store", credentials: "include" })` nessas URLs.
- Envia `postMessage({ type: "AUTH_CACHE_BYPASS", patterns: [...] })` ao Service Worker ativo (se houver).

## Complemento ideal (Service Worker)

No arquivo do Service Worker, adicione:

```javascript
const AUTH_BYPASS = [/^\/api\/(?:me|user-data|register|login|logout|verify|forgot-password|reset-password)(\/|$)/i];
self.addEventListener('message', (ev) => {
  if (ev.data && ev.data.type === 'AUTH_CACHE_BYPASS' && Array.isArray(ev.data.patterns)) {
    try { /* opcional: atualizar AUTH_BYPASS dinamicamente */ } catch (e) {}
  }
});
self.addEventListener('fetch', (event) => {
  var url = new URL(event.request.url);
  if (['GET', 'HEAD'].indexOf(event.request.method) !== -1 && AUTH_BYPASS.some(function (rx) { return rx.test(url.pathname); })) {
    event.respondWith(fetch(event.request, { cache: 'no-store', credentials: 'include' }));
    return;
  }
  // ... resto do fetch
});
```

Se quiser, envie o caminho do seu Service Worker (e 2–3 linhas do `addEventListener('fetch'...)`) para receber um patch 0047a aplicando isso no arquivo.

## Lembrete

- Os endpoints sensíveis já recebem `Cache-Control: no-store` e `Vary: Cookie` pelo patch 0046.
- Após aplicar, faça hard reload e, se necessário, Unregister do Service Worker uma vez.
