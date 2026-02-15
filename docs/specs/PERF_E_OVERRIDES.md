# Performance e Overrides do CNES – uso, cache e diagnóstico

## O que é

`cnes_overrides.py` aplica **Público/Privado/Filantrópico**, **Aceita Cartão SUS** e **convênios** direto do CNES sem reprocessar o dataset.

- **Lazy boot**: nada carrega na importação do app. O primeiro uso chama `ensure_boot()` (e usa cache `.pkl` se os CSVs não mudaram).

## Arquivos e cache

**CSVs procurados** (por `SNAPSHOT=YYYYMM`):

- `tbEstabelecimentoYYYYMM.csv` (obrigatório)
- `tbEstabPrestConvYYYYMM.csv` (opcional)

**Locais buscados:** `data/`, `data/raw/YYMM/`, `BASE_DE_DADOS_CNES_YYYYMM/`

**Cache:** `data/cache/cnes_overrides_<hash>.pkl` (hash = snapshot + mtime dos CSVs)

## Variáveis de ambiente

| Variável | Descrição |
|----------|-----------|
| `SNAPSHOT=YYYYMM` | Mês alvo (ex.: `202512`). Se ausente ou CSV não existir, autodetect. |
| `PERF_LOG=on\|off` | Logs de performance (import do app, boot dos overrides, primeira request). |
| `STRICT_OBST=on\|off` | Filtro obstétrico estrito no search (exclui psicologia/fono/fisio etc.). |
| `OVERRIDES_BOOT=lazy\|background` | **lazy** (default): carrega no primeiro uso. **background**: carrega em thread ao subir (não bloqueia). |
| `OVERRIDES_CONVENIOS=on\|off` | **on** (default): carrega convênios. **off**: pula leitura de convênios para start ultra-rápido. |
| `PERF_EXPOSE=on\|off` | **on** (default): expõe bloco `perf` em `GET /api/v1/health`. |
| `PERF_LOG=on\|off` | Logs de performance no console (import, boot, primeira request). |

### Segurança (endpoints /debug/*)

- **ADMIN_DEBUG=on|off**: se **off**, todos os endpoints `/api/v1/debug/*` retornam 404 (disabled). Em produção pública use **ADMIN_DEBUG=off**.
- **ADMIN_TOKEN**: se definido, exige header **X-Admin-Token** (ou query **admin_token**) igual ao valor. Em staging/dev defina um token forte.
- **ADMIN_ALLOWED_IPS**: lista de IPs permitidos (ex.: `127.0.0.1,::1` ou o /32 da VPN). Se vazio, não restringe por IP (só por token, se houver).

**Badge admin:** no `index.html` (somente em dev) você pode definir:  
`<script> window.SOPHIA_ADMIN = true; window.ADMIN_TOKEN = 'seu_token_apenas_local'; </script>`  
Assim o badge envia o token nos fetches para refresh, quick_check e qa/list.

**Produção:** deixe **ADMIN_DEBUG=off** e **PERF_EXPOSE=off** para não expor perf nem /debug/* publicamente.

### Race / lock

`ensure_boot()` usa `threading.Lock` para evitar boot duplo na primeira requisição (condição de corrida).

### Gunicorn (multi-workers)

- **preload_app=True** (em `gunicorn.conf.py`): o master carrega o app uma vez; workers herdam páginas (copy-on-write). Overrides em memória tendem a ser compartilhados; com cache `.pkl` o boot por worker é rápido.
- Sem `preload_app`: cada worker chama `ensure_boot()` uma vez; com `.pkl` em disco o boot é da ordem de milissegundos.

### Endpoint admin – refresh (sem reiniciar)

- **POST /api/v1/debug/overrides/refresh** – recarrega overrides do CNES (usa `SNAPSHOT` do `.env`). Resposta: `{ "ok": true, "snapshot": "...", "count": N }`.

### Quick-check (área do usuário, sem logs)

- **GET /api/v1/debug/overrides/quick_check?lat=&lon=&radius_km=25** – cobertura de override na área (até 30 estabelecimentos no raio). Resposta: `{ "ok", "total", "override_hits", "coverage_pct" }`. Protegido por `_admin_allowed`.

### Health curto (LB/probe)

- **GET /api/v1/health/short** – health mínimo para load balancer/uptime: `{ "status": "ok", "dataset": { "present": true/false }, "version": "sophia-emergency-v2" }`. **Não** é protegido por admin.

### QA – listar e baixar CSVs

- **GET /api/v1/debug/qa/list** – lista CSVs de QA em `reports/` (qa_publico_vs_privado.csv, qa_ambulatorial_vazando.csv, qa_maternidade_nao_marcada.csv). Protegido por `_admin_allowed`.
- **GET /api/v1/debug/qa/download?name=...** – download do CSV. Protegido por `_admin_allowed`.

## Comandos úteis

### Cobertura do override

- `GET /api/v1/debug/overrides/coverage` → `{ "total_loaded", "snapshot_usado" }`
- `GET /api/v1/emergency/search?...&debug=true` → por item: `override_hit` (true/false), `override_reason` (`"applied"` \| `"no_match"` \| `"not_applied"`). O body inclui `override_coverage_pct` no meta.

### Trocar o snapshot (sem reiniciar tudo)

1. `.env`: `SNAPSHOT=202511` (ou copie CSVs 202511 para o nome 202512).
2. Reinicie o Flask. Logs:
   - `[CNES/OVR] usando .../tbEstabelecimentoYYYYMM.csv`
   - `[CNES/OVR] overrides prontos: N CNES (snapshot=YYYYMM)`

### Invalidação do cache

Apague `data/cache/cnes_overrides_*.pkl` **ou** altere os CSVs (mtime muda) → o próximo boot reconstrói.

**CLI (sem reiniciar o app):**

```bash
python scripts/overrides_cache.py clear
```

## Troubleshooting

| Sintoma | Ação |
|--------|------|
| `total_loaded=0` ou `snapshot_usado` estranho | SNAPSHOT não encontra CSV; ajuste o `.env` ou copie CSVs. |
| `override_reason="no_match"` em muitos itens | O CSV não tem os CNES do dataset (períodos diferentes); sincronize SNAPSHOT. |
| “Privado” indevido com `override_hit=true` | Front em cache; Ctrl+F5. Se persistir, mande o item para ajuste de nome/regex. |

## Perf logs (com PERF_LOG=on)

```
[PERF] import backend.app: 420 ms
[PERF] overrides boot: 850 ms (snapshot=202511, count=5800)
[PERF] first request GET /api/v1/emergency/search -> 200 in 120 ms
```

Com `OVERRIDES_BOOT=background`:

```
[PERF] import backend.app: 420 ms
[PERF] overrides boot (bg) ok: snapshot=202511 count=5800
```

## Exemplo: CLI overrides_cache.py

```bash
# Status (carrega lazy se ainda não carregou)
python scripts/overrides_cache.py status

# Pré-aquecer e forçar snapshot
python scripts/overrides_cache.py warm --snapshot 202512

# Limpar cache em disco (próximo boot reconstrói do CSV)
python scripts/overrides_cache.py clear
```

Saída típica de `status` / `warm`:

```json
{
  "snapshot": "202512",
  "count": 598661,
  "cache_files": ["cnes_overrides_abc123def456.pkl"]
}
```

---

## Perf summary no /health

Com **PERF_EXPOSE=on** (default), `GET /api/v1/health` inclui o bloco `perf`:

- **startup_ms**: tempo de import do `backend.app` (ms).
- **first_request_ms** / **first_request_at**: tempo da primeira resposta servida.
- **overrides.boot_ms** / **boot_at**: tempo do boot dos overrides (lazy ou background).
- **overrides.snapshot**, **overrides.count**, **overrides.mode**: snapshot, quantidade e modo (lazy/background).

Exemplo:

```json
"perf": {
  "startup_ms": 420,
  "first_request_ms": 115,
  "first_request_at": "2025-02-02T12:00:00.000Z",
  "overrides": {
    "boot_ms": 820,
    "boot_at": "2025-02-02T12:00:00.500Z",
    "snapshot": "202512",
    "count": 598661,
    "mode": "background"
  }
}
```

---

## perf_probe no orquestrador

O script **scripts/perf_probe.py** consulta `/api/v1/health` (ou sobe um Flask temporário com `--spawn`), extrai as métricas de perf, aplica thresholds e pode injetar em **reports/run_summary.json** com `--update-run-summary`.

**Variáveis de ambiente:**

- **PERF_PROBE_BASE_URL**: URL base (default `http://localhost:5000`).
- **PERF_PROBE_SPAWN**: se `true`, sobe servidor temporário na porta `--port`.
- **PERF_MAX_STARTUP_MS**, **PERF_MAX_OVR_BOOT_MS**, **PERF_MAX_FIRST_REQ_MS**: thresholds (default 2500, 2000, 1500 ms).

**Uso:**

```bash
python scripts/perf_probe.py --base-url http://localhost:5000
python scripts/perf_probe.py --spawn --update-run-summary
```

No orquestrador, defina **RUN_PERF_PROBE=true** para rodar o probe antes de gravar o run_summary; o resultado fica em **perf_summary**, **perf_warnings**, **perf_errors** no run_summary.

Opcional: **QC_LAT**, **QC_LON**, **QC_RADIUS** para anexar **override_quick_check** ao run_summary (API já de pé, ex.: após perf_probe --spawn).

---

## Super badge admin (?admin=1)

Com **?admin=1** (ou `window.SOPHIA_ADMIN=true`), a UI exibe um único badge com:

- **[perf]** start • boot • first
- **[geo]** coords • tel • conf
- **[qc]** overrides hits/total (coverage) na área (usa última posição ou QC_LAT/QC_LON)
- Botão **↻** para recarregar overrides e refazer quick-check
- Botão **×** para fechar

Para atualizar o badge quando o usuário fizer uma busca por GPS, chame no fluxo de geolocalização ou ao final da busca:

```js
if (window.sophiaAdminBadgeUpdatePos) window.sophiaAdminBadgeUpdatePos(lat, lon);
```

Thresholds (opcional no `index.html`): `window.PERF_T_STARTUP`, `PERF_T_BOOT`, `PERF_T_FIRST`, `GEO_T_COORDS`, `GEO_T_PHONE`, `QC_LAT`, `QC_LON`, `QC_RADIUS`.

---

## Go / No-Go (checklist final de produção)

| Check | Critério |
|-------|----------|
| **/health perf** | `perf.startup_ms` &lt; 2500; `overrides.boot_ms` &lt; 2000; `first_request_ms` &lt; 1500 |
| **/health geo** | `geo_health.coord_coverage_pct` ≥ 0.85; `phone_coverage_pct` ≥ 0.85 |
| **/search?debug=true** | `override_coverage_pct` alto; badges "Público" / "Aceita Cartão SUS" corretos |
| **qa_hints** | `público_vs_privado_pct_uf` ≤ 0.5% |
| **UI ?admin=1** | Badge [geo] + [perf] + [qc] ok; botão ↻ funcionando |
