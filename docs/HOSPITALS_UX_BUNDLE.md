# Hospitals UX Bundle (0075/0076/0077/0078/0083)

Inclui
- **Telefone:** vira `tel:+…` (clique para ligar) e formata +55 (12)… quando possível.
- **Endereço:** botão "Copiar"; "Rota" e "Ver no mapa" (lat/lon se houver; fallback por endereço).
- **Convênios:** mostra até 3 chips e "ver mais" para expandir; disclaimer "sujeito a confirmação".
- **Flags:** `/flags.json` usa env `SHOW_SUS_BADGES` e `SHOW_OWNERSHIP_BADGES` para exibir/ocultar badges SUS/esfera.
- **Debug:** `/?debugHosp=1` cria bloco com campos crus (cnes/lat/lon/end/telefone/convenios) em cada card.
- **Health:** `/api/v1/emergency/health` para smoke leve do endpoint de hospitais.

**Debug – Health nos cards (0084)**  
No modo `/?debugHosp=1`, o bundle busca `/api/v1/emergency/health/details` uma vez e injeta um resumo em cada bloco de debug:
- `__health`: { status, count, ttl_remaining, ttl_seconds, mtime_iso, source }
- source é o basename do arquivo.
- Ajuda a diagnosticar rapidamente base vazia/antiga diretamente na UI.

**Debug – Headers do emergency/search (0085)**  
O wire `emergency-headers-wire.js` intercepta a resposta de `/api/v1/emergency/search` e salva:
- `window.__EMERGENCY_HEADERS` = { url, x_data_source, x_data_mtime, fetched_at }
- O bundle injeta um resumo no bloco `__headers` (basename do source, mtime ISO, instante de captura).
- Útil para confirmar rapidamente se o front está consumindo uma base recém-carregada ou de fonte/mtime específicos.

**Tooltips (0086)**  
Além do debug, cada card passa a mostrar um botão "i" discreto na linha do título; ao passar o mouse (ou tocar), aparece um tooltip com:
- Fonte (basename do X-Data-Source)
- Mtime (ISO) convertido a partir do X-Data-Mtime
- Instante em que os headers foram capturados (fetched_at)

**Refresh on-demand (0086a)**  
Ao clicar no "i", refaz o request do `/api/v1/emergency/search` e atualiza o tooltip.

**Headers garantidos (0087)**  
O servidor sempre envia X-Data-Source e X-Data-Mtime no `/api/v1/emergency/search`, com Access-Control-Expose-Headers para cross-origin.

**HUD de saúde (0088)**  
`hospitals-hud-wire.js` exibe um selinho no topo da modal/lista: "Base OK • N itens • mtime • TTL". Verde/âmbar/vermelho conforme status.

**Log estruturado (0089)**  
No console, cada busca gera `[EMERGENCY] busca: count=… fonte=… mtime=… lat=… lon=… radius_km=…`

**Headers completos (0090)**  
`/api/v1/emergency/search` envia X-Data-Source, X-Data-Mtime, X-Data-Count, X-Query-Lat, X-Query-Lon, X-Query-Radius. Todos expostos via Access-Control-Expose-Headers. Console e tooltip leem tudo dos headers, sem parse do JSON.

**Banner base degradada/stale (0091)**  
Quando o health estrito indicar degraded/stale, o HUD mostra aviso: "Base desatualizada ou menor que o esperado. Tente novamente em instantes."

**Offline/timeout UX (0092)**  
`hospitals-offline-wire.js` escuta `emergency:fetch-error`; em falha de rede/timeout exibe banner vermelho com "Tentar novamente" e orientação para 192. Clique no botão dispara refresh; sucesso remove o banner.

**Painel de buscas (0093)**  
`hospitals-searchlog-wire.js` exibe "Detalhes da busca" no rodapé da modal; últimas 5 buscas com count, fonte, mtime, lat/lon/radius; botões Copiar e Copiar tudo.

**Telemetria (0094)**  
`log_emergency_search()` em appinsights.py; se APPINSIGHTS_CONNECTION_STRING estiver definida, cada busca gera log estruturado para Application Insights.

**Headers/Logs para /api/nearby (0095)**  
`nearby-headers-wire.js` captura headers do /api/nearby; tooltip e painel usam emergency ou nearby conforme o fluxo. Painel mostra tipo: emergency/nearby. "Copiar últimos parâmetros" copia {lat, lon, radius_km, type}.

## Como usar

- Exponha flags no ambiente:
  - `SHOW_SUS_BADGES=true` para mostrar
  - `SHOW_OWNERSHIP_BADGES=true` para mostrar  
  (Padrão: ambos falsos, mantendo decisão de esconder por ora.)
- Se quiser forçar flags sem rede, defina no `<body>`:
  `<body data-show-sus-badges="1" data-show-ownership-badges="1">`
- Debug: `https://seuapp/.../?debugHosp=1`

## Requisitos

Os cards dos hospitais devem ter estrutura mínima:
- telefone em `.hospital-phone` (ou `[data-role="phone"]`) ou `a[href^="tel:"]`
- endereço em `.hospital-address` (ou `[data-role="address"]`)
- botões (opcionais) `.btn-copy-address`, `.btn-route`, `.btn-map`, `.btn-call`
- contêiner de convênios (opcional): `.hospital-convenios` ou `[data-role="convenios"]`
- atributos (opcionais) `data-lat`, `data-lon`, `data-cnes`
- badges (opcionais): `[data-badge="sus"]`, `[data-badge="esfera"]`

## Validação

- Abra a modal/lista de hospitais com `?debugHosp=1`
- Em cada card, o bloco JSON deve incluir um `__health` com status, count, ttl_remaining/ttl_seconds, mtime_iso e source (quando /health/details expuser).
- `/api/v1/emergency/health/details` continua imprimindo os detalhes completos.
- Abra a lista/modal de hospitais normalmente; no topo de cada card, o botão "i" deve aparecer (assim que houver uma chamada bem-sucedida ao `/api/v1/emergency/search`).
- Passe o mouse/toque e verifique o tooltip com arquivo/tempo.
- Com `/?debugHosp=1`, o bloco JSON deve incluir e atualizar `__headers` também.

- Cards exibem telefone clicável, copiar endereço, rota/mapa.
- Convenios aparecem em chips; se >3, "ver mais".
- `SHOW_*` des/ativa badges sem tocar código.
- `/?debugHosp=1` mostra blocos com dados crus.
- `/api/v1/emergency/health` → 200 JSON.

## Instruções e notas

O bundle age por "wire": não altera o seu render original, apenas melhora e organiza o DOM.  
Se preferir integração direta na função de render (chat.js) no futuro, pode ser feito um patch cirúrgico com o contexto da função.

## Validação rápida (pós-apply)

1. Reinicie o backend; SW Update/Skip waiting; Ctrl+Shift+R
2. Toggle `SHOW_SUS_BADGES`/`SHOW_OWNERSHIP_BADGES` no App Service e confira efeito imediato (version-watchdog cuida do refresh).
3. Verifique telefone/rota/cópia end. e chips de convênios nos cards.

## Observações

- O botão "i" só aparece quando os headers já tiverem sido capturados (ou seja, depois da primeira chamada ao `/api/v1/emergency/search`).
- Se o header do card tiver outra classe, o bundle tenta cair em elementos próximos (hospital-header/hospital-name).

## O que ficou faltando (se quiser)
- Atalhos de "Ligar / Rota / Mapa" com ícone (tema já tem classes `.btn-soft`; o CSS foi minimalista).
