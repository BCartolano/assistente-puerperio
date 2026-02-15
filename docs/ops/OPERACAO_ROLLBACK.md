# Operação e Rollback - Sophia Emergency v2

## Operação Contínua

### Monitoração Diária

**Checks automáticos (cron ou CI/CD):**
```bash
# Health check básico
curl -sf https://SEU_APP/api/v1/health/short || alert "Health check falhou"

# Smoke test
python scripts/smoke_prod.py --base-url https://SEU_APP --lat -23.19 --lon -45.79 --radius 25 || alert "Smoke falhou"
```

**Métricas a monitorar:**
- `/api/v1/health/short` → status 200, `dataset.present: true`
- Latência P95 do `/api/v1/emergency/search` → < 2s
- Taxa de erro do `/api/v1/chat/intent` → < 5%

### Rotinas Mensais

**1. Atualização de Snapshot CNES:**
```bash
# 1. Baixar novo snapshot do CNES (tbEstabelecimentoYYYYMM.csv)
# 2. Copiar para data/ ou data/raw/YYYYMM/

# 3. Rodar orquestrador
RELEASE_UF=SP RUN_PERF_PROBE=true python scripts/run_orchestrator.py --snapshot YYYYMM

# 4. Verificar gates
cat reports/run_summary.json | jq ".qa_hints.publico_vs_privado_pct_uf"
# Aceite: <= 0.5%

# 5. Se passar, fazer deploy
```

**2. Análise de Eventos:**
```bash
# Analisar eventos de busca
python scripts/analyze_search_events.py

# Verificar métricas:
# - expanded_pct (deve estar estável)
# - hitA_pct (confirmados, deve estar alto)
# - override_coverage_pct (deve estar >= 90%)
```

**3. QA Mismatches:**
```bash
# Verificar inconsistências
python scripts/qa_mismatches.py

# Verificar CSVs:
# - qa_publico_vs_privado.csv (deve estar vazio)
# - qa_ambulatorial_vazando.csv (deve estar vazio)
```

### Alertas e Ações

| Alerta | Ação |
|--------|------|
| `health_short != 200` | Verificar logs, dataset, restart se necessário |
| `expanded_pct ↑` muito | Verificar se novos dados estão corretos |
| `hitA_pct ↓` muito | Verificar SNAPSHOT e CSVs do CNES |
| `qa_publico_vs_privado_pct_uf > 0.5%` | Bloquear release, revisar overrides |
| `override_coverage_pct < 90%` | Verificar SNAPSHOT e CSVs do CNES |

---

## Rollback

### Cenário 1: Dados Incorretos

**Sintomas:**
- Muitos "Privado" quando deveria ser "Público"
- `override_reason="no_match"` em muitos itens
- `qa_publico_vs_privado_pct_uf > 0.5%`

**Ação:**
```bash
# 1. Restaurar parquet anterior
cp backups/hospitals_geo.min.parquet.YYYYMMDD data/geo/hospitals_geo.min.parquet

# 2. Recarregar overrides (se SNAPSHOT mudou)
curl -X POST https://SEU_APP/api/v1/debug/overrides/refresh \
  -H "X-Admin-Token: SEU_TOKEN"

# 3. Verificar
python scripts/smoke_prod.py --base-url https://SEU_APP --lat -23.19 --lon -45.79 --radius 25
```

### Cenário 2: Problema no Frontend

**Sintomas:**
- Cards mostram "Privado" mas API envia "Público"
- Console mostra erros JavaScript

**Ação:**
```bash
# 1. Cache bust (deploy)
# Trocar querystring do JS: <script src=".../chat.js?v=YYYYMMDDHHMMSS"></script>

# 2. Usuário: Ctrl+F5 ou janela anônima

# 3. Verificar console do navegador
# Deve mostrar [DIAGNÓSTICO] Payload da API com esfera="Público"
```

### Cenário 3: Problema de Performance

**Sintomas:**
- `startup_ms > 2500ms`
- `overrides_boot_ms > 2000ms`
- `first_request_ms > 1500ms`

**Ação:**
```bash
# 1. Verificar logs de perf
# Procurar por [PERF] no console/logs

# 2. Se overrides_boot_ms alto:
# - Verificar se cache .pkl existe
# - Verificar se OVERRIDES_CONVENIOS=off ajuda
# - Verificar se preload_app=True está ativo (Gunicorn)

# 3. Se startup_ms alto:
# - Verificar imports desnecessários
# - Verificar se NLTK está baixando dados
```

### Cenário 4: Problema Crítico (Health Down)

**Sintomas:**
- `/api/v1/health/short` retorna 500 ou timeout
- App não responde

**Ação:**
```bash
# 1. Verificar logs do App Service / Docker
# Procurar por erros de import, dataset não encontrado, etc.

# 2. Restart do serviço
# Azure: Restart via portal
# Docker: docker-compose restart

# 3. Se persistir, rollback completo:
# - Restaurar imagem anterior
# - Restaurar dados (parquet)
# - Verificar ENV
```

---

## Backup e Restauração

### Backup Automático

**Antes de cada deploy:**
```bash
# 1. Backup do parquet
cp data/geo/hospitals_geo.min.parquet backups/hospitals_geo.min.parquet.$(date +%Y%m%d)

# 2. Backup dos overrides (cache)
cp -r data/cache backups/cache.$(date +%Y%m%d)

# 3. Backup do run_summary
cp reports/run_summary.json backups/run_summary.$(date +%Y%m%d).json
```

### Restauração

**Restaurar dados:**
```bash
# 1. Restaurar parquet
cp backups/hospitals_geo.min.parquet.YYYYMMDD data/geo/hospitals_geo.min.parquet

# 2. Restaurar cache (opcional)
cp -r backups/cache.YYYYMMDD/* data/cache/

# 3. Recarregar overrides
curl -X POST https://SEU_APP/api/v1/debug/overrides/refresh \
  -H "X-Admin-Token: SEU_TOKEN"
```

---

## Troubleshooting Rápido

### "Privado" Indevido

**Diagnóstico:**
```javascript
// Console do navegador
fetch('/api/v1/emergency/search?lat=-23.19&lon=-45.79&radius_km=25&limit=3&expand=true&debug=true')
  .then(r=>r.json())
  .then(d => console.table(d.results.map(it => ({
    nome: it.nome,
    esfera: it.esfera,
    override_hit: it.override_hit,
    override_reason: it.override_reason
  }))));
```

**Soluções:**
- `override_reason="no_match"` → ajustar SNAPSHOT ou copiar CSVs
- `esfera="Público"` mas card mostra "Privado" → cache do frontend (Ctrl+F5)
- `esfera="Privado"` da API → verificar snapshot/caminho dos CSVs

### Performance Lenta

**Diagnóstico:**
```bash
# Verificar perf no /health (bastidor)
curl -s https://SEU_APP/api/v1/health | jq ".perf"
```

**Soluções:**
- `startup_ms` alto → verificar imports, NLTK
- `overrides_boot_ms` alto → verificar cache .pkl, OVERRIDES_CONVENIOS
- `first_request_ms` alto → verificar dataset, geocoding

### Health Check Falhando

**Diagnóstico:**
```bash
# Verificar health short
curl -s https://SEU_APP/api/v1/health/short | jq

# Verificar logs
# Azure: Logs do App Service
# Docker: docker-compose logs
```

**Soluções:**
- `dataset.present: false` → verificar se parquet existe
- Erro 500 → verificar logs para erro específico
- Timeout → verificar recursos do servidor

---

## Contatos e Escalação

**Níveis de severidade:**
- **Crítico:** Health down, dados incorretos em massa → Rollback imediato
- **Alto:** Performance degradada, alguns dados incorretos → Investigar e corrigir
- **Médio:** Alertas de QA, métricas fora do normal → Monitorar e agendar correção
- **Baixo:** Melhorias, otimizações → Backlog

**Ações imediatas:**
1. Verificar logs
2. Rodar smoke tests
3. Verificar métricas (perf, geo, QA)
4. Se crítico, rollback

**Última linha de defesa:** Rollback rápido (restaurar parquet + refresh overrides)
