# Health da base de emergência – detalhes

## Endpoints

- **GET /api/v1/emergency/health** — status `"ok"` e detalhes quando disponíveis.
- **GET /api/v1/emergency/health/details** — sempre tenta retornar detalhes.

## Modo estrito (fail-fast opcional)

- Env `EMERGENCY_HEALTH_MIN_COUNT` (ex.: 100) e `EMERGENCY_HEALTH_MAX_AGE_HOURS` (ex.: 24).
- `/api/v1/emergency/health` retorna **503** com `{"status":"degraded"|"stale","reason":"..."}` quando a contagem está abaixo do mínimo ou o arquivo está "velho".
- O CI já falha nesse caso (os steps de smoke usam `-sf` e exigem HTTP 200).

## Integrações detectadas automaticamente

- Tenta `backend.api.geo_info.get_geo_data_info()` (módulo auxiliar que introspecta routes sem editar).
- Se existir `backend.api.routes.get_geo_data_info()`, usa como fallback.
- Aceita retorno em **dict** (preferido) ou **tupla** `(source, mtime)` – compatível com a sua função atual.

## Campos de detalhes (se presentes)

- **count:** itens carregados na base.
- **source:** arquivo/fonte (caminho).
- **mtime** / **mtime_iso:** última modificação do arquivo.
- **loaded_at:** quando foi carregado (timestamp).
- **ttl_seconds** / **ttl_remaining:** TTL configurado e tempo restante em cache.

## Validação (local)

```bash
curl -s http://localhost:5000/api/v1/emergency/health
curl -s http://localhost:5000/api/v1/emergency/health/details
```

**Exponha os envs e confira:**
- `EMERGENCY_HEALTH_MIN_COUNT=100` → retorna 503 se `count<100`
- `EMERGENCY_HEALTH_MAX_AGE_HOURS=24` → retorna 503 se `age>24h`

## O que esperar no CI

- Os passos "Smoke emergency health" continuam iguais (`curl -sf …`); se `/health` vier 503, o job falha rápido.
- Os passos "Print emergency health details" mostram o payload (útil para diagnóstico imediato).

**Dicas:**
- Ligue o health estrito só em staging (valida a base antes de swap) e mantenha "ok" em produção — é só ajustar os envs por slot no App Service.
- Ou plugue um alerta mais caprichado (com payload do details no Slack/Teams/Discord).

## CI/CD

- Os workflows imprimem os detalhes após o deploy (passo "Print emergency health details"; não falha se o endpoint não existir).
- Em caso de falha do job, um passo opcional "Notify on failure" envia notificação para Slack/Teams/Discord, se os secrets `SLACK_WEBHOOK_URL`, `TEAMS_WEBHOOK_URL` e/ou `DISCORD_WEBHOOK_URL` estiverem definidos.
