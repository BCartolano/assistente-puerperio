# Runbook – Cache, Service Worker e Atualização

## Verificação rápida

### SW e cache
- **DevTools > Application:** Update / Skip waiting no Service Worker; depois **Ctrl+Shift+R** (duas vezes na primeira vez).
- **Network:** `index.html` com `Cache-Control: no-store`; `.js`/`.css` e `/api/*` vindo **"from network"**.

### Version handshake
- Abra `/version.json`.
- Faça um deploy (o CI grava `VERSION` com SHA curto). A página deve recarregar sozinha em até 5 min ou na hora com `?refresh=1`.

### Storage namespaced
- **Console:** `localStorage.getItem('current_user_id')` deve existir quando logado; chaves sensíveis (`user_name`, `baby_name`) só como `user:<uid>:user_name` etc.

### Autologin
- Não deve haver `POST /api/login` automático; login só quando o usuário envia o formulário.

---

## Se ainda travar em algum navegador

Cole no **Console** (apenas nessa aba) para limpeza total:

```javascript
(async () => {
  if ('caches' in window) { for (const k of await caches.keys()) await caches.delete(k); }
  if (navigator.serviceWorker?.getRegistration) { const r = await navigator.serviceWorker.getRegistration(); r && (await r.unregister()); }
  localStorage.clear(); sessionStorage.clear(); location.reload();
})();
```

---

## Diagnóstico rápido de versão

- **Header:** Todas as respostas do servidor incluem `X-Build-Version` (valor de `BUILD_VERSION` ou arquivo `VERSION`).
- **Console:** Na carga da página o script de version-watchdog loga `[APP] Build: <versão>`.
- **Menu:** Botão **"Atualizar app"** (sidebar) chama o fluxo do watchdog (atualiza SW, limpa caches de assets, recarrega).

---

## Backend – Cache do dataset de emergência (0069)

- **TTL opcional:** `EMERGENCY_CACHE_TTL_SECONDS` no ambiente: cache do parquet expira após N segundos e é recarregado na próxima busca.
- **Recarga sob demanda:** `POST /api/v1/emergency/reload` limpa o cache e força recarga na próxima busca (útil após atualizar a base sem reiniciar o processo).
- **Headers de resposta** em `GET /api/v1/emergency/search`: `X-Data-Source` (nome do arquivo) e `X-Data-Mtime` (timestamp) para ver se está lendo arquivo atualizado.

---

## Se algo ainda “prender” em build antigo

Envie:
1. **DevTools > Network:** headers da requisição do HTML e de um JS (ex.: `chat.js`); linha **"from …"** (ServiceWorker/disk ou network).
2. **2–3 linhas** do `addEventListener('fetch', …)` do seu `sw.js` atual.

Com isso dá para reancorar o bypass no fetch handler e ajustar headers se faltar algo.

---

## Campos da API e cards (0072 / 0073)

- **GET /api/v1/emergency/search:** retorna `results` e `nearby_confirmed` com `nome`, `endereco`, `logradouro`, `numero`, `bairro`, `cidade`, `estado`, `telefone`, `telefone_formatado`, `convenios`, `esfera`, `sus_badge`. O backend preenche `telefone_formatado` via `format_br_phone(telefone)` quando o parquet não traz o campo.
- **Front:** o mapeamento para `convertFacilitiesToHospitals` usa esses campos; há fallback de telefone a partir de `co_ddd` + `nu_telefone` se a API enviar. Os cards exibem endereço formatado (Rua, Número – Bairro – Cidade – Estado), telefone clicável, até 3 convênios (card azul) e badges de esfera/SUS.
- **GET /api/nearby:** schema reduzido (`name`, `address`, `lat`, `lon`, `public_private`, `accepts_sus`, `accepts_convenio`, `distance_km`). O **nearby-wire.js** normaliza cada item para o schema unificado (`normalizeNearbyToUnified`) e o card exibe convênios, endereço e telefone quando presentes, mantendo compatibilidade se no futuro o endpoint passar a devolver os mesmos campos do emergency/search.
