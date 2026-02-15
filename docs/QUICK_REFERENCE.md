# Quick Reference - Sophia Emergency v2

## Comandos Essenciais

### Build e Dados
```bash
python backend/pipelines/prepare_geo_v2.py --snapshot 202512
python backend/pipelines/geocode_ready.py --mode copy
python scripts/make_geo_min.py
```

### Orquestrador (com Gates)
```bash
RELEASE_UF=SP RUN_PERF_PROBE=true python scripts/run_orchestrator.py --snapshot 202512
cat reports/run_summary.json | jq ".perf_summary, .geo_health, .qa_hints"
```

### Smokes
```bash
python scripts/smoke_prod.py --base-url http://localhost:5000 --lat -23.19 --lon -45.79 --radius 25
bash scripts/smoke_chat.sh http://localhost:5000
```

### Pós-Deploy
```bash
curl -s https://SEU_APP/api/v1/health/short | jq
python scripts/smoke_prod.py --base-url https://SEU_APP --lat -23.19 --lon -45.79 --radius 25
curl -s https://SEU_APP/api/v1/chat/ping | jq
```

---

## ENV Produção

```bash
ADMIN_DEBUG=off
PERF_EXPOSE=off
PERF_LOG=off
STRICT_OBST=on
ALLOW_ORIGINS=https://seu-dominio.com
SNAPSHOT=202512
OVERRIDES_BOOT=lazy
OVERRIDES_CONVENIOS=on
CHAT_RATE_MAX=120
```

---

## Diagnóstico Rápido

### Verificar Override Coverage
```javascript
fetch('/api/v1/emergency/search?lat=-23.19&lon=-45.79&radius_km=25&limit=20&expand=true&debug=true')
  .then(r=>r.json())
  .then(d => console.table(d.results.slice(0,5).map(it => ({
    nome: it.nome, esfera: it.esfera, override_hit: it.override_hit, override_reason: it.override_reason
  }))));
```

### Verificar "Privado" Indevido
```javascript
fetch('/api/v1/emergency/search?lat=-23.19&lon=-45.79&radius_km=25&limit=3&expand=true&debug=true')
  .then(r=>r.json())
  .then(d => console.table(d.results.map(it => ({
    nome: it.nome, esfera: it.esfera, override_hit: it.override_hit, override_reason: it.override_reason
  }))));
```

**Interpretação:**
- `override_reason="no_match"` → ajustar SNAPSHOT/CSV
- `esfera="Público"` mas card mostra "Privado" → cache frontend (Ctrl+F5)
- `esfera="Privado"` da API → verificar snapshot/caminho dos CSVs

---

## Rollback Rápido

### Dados
```bash
cp backups/hospitals_geo.min.parquet.YYYYMMDD data/geo/hospitals_geo.min.parquet
curl -X POST https://SEU_APP/api/v1/debug/overrides/refresh -H "X-Admin-Token: SEU_TOKEN"
```

### Frontend
```bash
# Cache bust: trocar querystring do JS (?v=timestamp)
# Usuário: Ctrl+F5 ou janela anônima
```

---

## Alertas

| Métrica | Threshold | Ação |
|---------|-----------|------|
| `health_short` | != 200 | Verificar logs, restart |
| `expanded_pct` | ↑ muito | Verificar novos dados |
| `hitA_pct` | ↓ muito | Verificar SNAPSHOT/CSVs |
| `qa_publico_vs_privado_pct_uf` | > 0.5% | Bloquear release |
| `override_coverage_pct` | < 90% | Verificar SNAPSHOT/CSVs |

---

## Links Úteis

- **Runbook completo:** `docs/GO_LIVE_RUNBOOK.md`
- **Operação/Rollback:** `docs/OPERACAO_ROLLBACK.md`
- **Performance/Overrides:** `docs/PERF_E_OVERRIDES.md`
- **Chatbot Router:** `docs/CHATBOT_ROUTER.md`
- **Release Checklist:** `docs/RELEASE_CHECKLIST.md`
