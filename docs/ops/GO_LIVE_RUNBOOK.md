# Go Live Runbook - Sophia Emergency v2

## Modo Turbo (3 blocos)

### 1. Antes de Publicar (Local/CI)

#### Build e Dados

```bash
# 1. Preparar dados geo
python backend/pipelines/prepare_geo_v2.py --snapshot 202512

# 2. Geocode ready
python backend/pipelines/geocode_ready.py --mode copy

# 3. Criar versão min (otimizada)
python scripts/make_geo_min.py
```

**Verificar:**
- `data/geo/hospitals_geo.min.parquet` existe e tem tamanho razoável
- Logs não mostram erros críticos

#### Orquestrador (com Gates)

```bash
RELEASE_UF=SP RUN_PERF_PROBE=true python scripts/run_orchestrator.py --snapshot 202512
```

**Conferir `reports/run_summary.json`:**
```bash
cat reports/run_summary.json | jq ".perf_summary, .geo_health, .qa_hints"
```

**Aceite:**
- `perf_summary.startup_ms < 2500ms`
- `perf_summary.overrides_boot_ms < 2000ms`
- `perf_summary.first_request_ms < 1500ms`
- `geo_health.status == "ok"`
- `qa_hints.publico_vs_privado_pct_uf <= 0.5%`
- `qa_hints.ambulatorial_vazando == 0`

#### Smokes (Automáticos)

```bash
# Smoke da API de emergência
python scripts/smoke_prod.py --base-url http://localhost:5000 --lat -23.19 --lon -45.79 --radius 25

# Smoke do chatbot
bash scripts/smoke_chat.sh http://localhost:5000
```

**Aceite:** Ambos retornam exit code 0

---

### 2. Publicação (Prod)

#### Azure App Service (Single Container)

**Construir imagem:**
```bash
docker build -t sophia-emergency:v2 -f Dockerfile.prod .
docker tag sophia-emergency:v2 seu-registry.azurecr.io/sophia-emergency:v2
docker push seu-registry.azurecr.io/sophia-emergency:v2
```

**App Settings (ENV):**
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

**Deploy:**
- Configure build automático ou faça push manual
- Verifique logs do App Service após deploy

#### Traefik/Nginx (Docker Compose)

```bash
# Subir com compose prod
docker-compose -f docker-compose.prod.yml up -d

# Verificar health
curl -s http://localhost/api/v1/health/short | jq
```

**Verificar:**
- `/api/v1/health/short` retorna `200` e `dataset.present: true`
- Logs não mostram erros de startup

---

### 3. Pós-Deploy Imediato (5 Comandos)

```bash
# 1. Health check básico
curl -s https://SEU_APP/api/v1/health/short | jq

# 2. Smoke da API de emergência
python scripts/smoke_prod.py --base-url https://SEU_APP --lat -23.19 --lon -45.79 --radius 25

# 3. Smoke do chatbot
curl -s https://SEU_APP/api/v1/chat/ping | jq

# 4. Badge admin (bastidor)
# Abra: https://SEU_APP/?admin=1
# Verifique: badge [perf]+[geo]+[qc] e botão QA funcionando

# 5. QA CSVs (bastidor)
# Baixe os CSVs de QA pelo botão QA e confira se vazio/válido
```

**Aceite:**
- Todos os comandos retornam sucesso
- Badge admin mostra métricas corretas
- CSVs de QA estão vazios ou com valores esperados

---

## Toggles Finais de Produção (ENV)

```bash
# Segurança e Performance
ADMIN_DEBUG=off                    # Desabilita /debug/* publicamente
PERF_EXPOSE=off                    # Não expõe perf em /health (público)
PERF_LOG=off                       # Não loga perf no console

# Funcionalidade
STRICT_OBST=on                     # Filtro obstétrico estrito
OVERRIDES_BOOT=lazy                # ou background (pré-aquecimento)
OVERRIDES_CONVENIOS=on             # ou off (start ultra-rápido)

# CORS e Rate Limit
ALLOW_ORIGINS=https://seu-dominio.com
CHAT_RATE_MAX=120                  # req/min por IP

# Dados
SNAPSHOT=202512                    # ou auto-detect
```

---

## Monitoração e Rotinas

### Logs e Analytics

**Arquivos de log:**
- `logs/search_events.jsonl` — eventos de busca (com `analyze_search_events.py`)
- `logs/chat_events.jsonl` — eventos do chatbot (rotação automática 5MB x 5)

**Rotação:**
- `scripts/rotate_logs.py` — rotação mensal (já configurado)

### Jobs Mensais

```bash
# 1. Snapshot mensal
RELEASE_UF=SP RUN_PERF_PROBE=true python scripts/run_orchestrator.py --snapshot YYYYMM

# 2. Análise de eventos
python scripts/analyze_search_events.py

# 3. QA mismatches
python scripts/qa_mismatches.py
```

### Alertas Práticos

**Monitorar:**
- `expanded_pct ↑` e `hitA_pct ↓` (queda de confirmados) → revisar overrides/SNAPSHOT
- `qa_publico_vs_privado_pct_uf > 0.5%` → gate de release (bloquear se passar)
- `/api/v1/health/short != 200` → problema crítico

**Ações:**
- Se `expanded_pct` subir muito → verificar se novos dados estão corretos
- Se `hitA_pct` cair → verificar SNAPSHOT e CSVs do CNES
- Se `health_short` falhar → verificar logs e dataset

---

## Rollback Simples (Dois Botões)

### Dados

```bash
# 1. Restaurar hospitals_geo.min.parquet "bom"
cp backups/hospitals_geo.min.parquet.YYYYMMDD data/geo/hospitals_geo.min.parquet

# 2. Recarregar overrides
curl -X POST https://SEU_APP/api/v1/debug/overrides/refresh \
  -H "X-Admin-Token: SEU_TOKEN"
```

### Frontend

```bash
# 1. Limpar cache (usuário)
# Ctrl+F5 ou janela anônima

# 2. Cache bust (deploy)
# Trocar querystring do JS: <script src=".../chat.js?v=YYYYMMDDHHMMSS"></script>
```

---

## Segurança

### Endpoints Protegidos

- `/api/v1/debug/*` — protegido por `ADMIN_DEBUG`, `ADMIN_TOKEN`, `ADMIN_ALLOWED_IPS`
- **Produção pública:** `ADMIN_DEBUG=off` (retorna 404)

### Rate Limiting

- `/api/v1/chat/intent` — rate limit por IP (`CHAT_RATE_MAX` req/min)
- **Se publicar muito:** considere recaptcha/turnstile no frontend

### CORS

- `ALLOW_ORIGINS` — lista de origens permitidas (separadas por vírgula)
- **Produção:** apenas seu domínio principal

---

## Diagnóstico Express

### Verificar Override Coverage

```javascript
// No console do navegador
fetch('/api/v1/emergency/search?lat=-23.19&lon=-45.79&radius_km=25&limit=20&expand=true&debug=true')
  .then(r=>r.json())
  .then(d => {
    console.table(d.results.slice(0,5).map(it => ({
      nome: it.nome,
      cnes_id: it.cnes_id,
      esfera: it.esfera,
      sus_badge: it.sus_badge,
      override_hit: it.override_hit,
      override_reason: it.override_reason
    })));
  });
```

**Interpretação:**
- `override_reason="no_match"` → ajuste SNAPSHOT/CSV
- `override_reason="applied"` → override funcionando
- `esfera="Privado"` quando deveria ser "Público" → verificar snapshot/caminho dos CSVs

### Verificar "Privado" Indevido

**Se aparecer "Privado" quando deveria ser "Público":**

1. **Verificar payload da API:**
   ```javascript
   fetch('/api/v1/emergency/search?...&debug=true')
     .then(r=>r.json())
     .then(d => console.table(d.results.slice(0,3).map(it => ({
       nome: it.nome, esfera: it.esfera, override_hit: it.override_hit
     }))));
   ```

2. **Se `esfera` vem "Público" da API mas card mostra "Privado":**
   - Problema no frontend (cache ou código)
   - Solução: Ctrl+F5 ou verificar `chat.js` (mapEsfera)

3. **Se `esfera` vem "Privado" da API:**
   - Problema no backend (override não aplicado)
   - Solução: verificar SNAPSHOT, CSVs do CNES, ou `override_reason`

---

## Checklist Final

- [ ] Build e dados preparados (`hospitals_geo.min.parquet` existe)
- [ ] Orquestrador passou (perf, geo, QA ok)
- [ ] Smokes passaram (API e chat)
- [ ] ENV configurado (ADMIN_DEBUG=off, PERF_EXPOSE=off, etc.)
- [ ] Deploy realizado
- [ ] Pós-deploy validado (health, smoke, badge admin, QA CSVs)
- [ ] Monitoração configurada (logs, alertas)
- [ ] Rollback testado (restaurar dados e refresh overrides)

---

## Contatos de Emergência

- **Problemas críticos:** verificar logs do App Service / Docker
- **Dados incorretos:** verificar SNAPSHOT e CSVs do CNES
- **Frontend:** verificar cache e console do navegador

**Última linha de defesa:** Rollback rápido (restaurar parquet + refresh overrides)
