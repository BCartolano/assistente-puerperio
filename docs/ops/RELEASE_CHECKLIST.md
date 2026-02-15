# Checklist de Release - Sophia Emergency v2

## Fechar Release (5 passos, 5 min)

### 1. Perf + Overrides

**PERF_PROBE:**
```bash
RUN_PERF_PROBE=true python scripts/run_orchestrator.py --snapshot 202512
cat reports/run_summary.json | jq ".perf_summary,.perf_warnings"
```

**Badge admin (`?admin=1`):**
- Ver `[perf]` start/boot/first
- Ver `[qc]` overrides hits/total atualizando com `↻`

**Aceite:**
- `startup_ms < 2500ms`
- `overrides_boot_ms < 2000ms`
- `first_request_ms < 1500ms`

### 2. QA (Maternidade e Esfera/SUS)

**QA orquestrador:**
- `run_summary.json` → `.qa_hints` (`publico_vs_privado_pct_uf ≤ 0.5%`)

**CSVs (baixar pelo botão QA ou local):**
- `reports/qa_publico_vs_privado.csv` deve estar **vazio**
- `reports/qa_ambulatorial_vazando.csv` deve estar **vazio**

### 3. Smoke da API (Prod ou Staging)

```bash
python scripts/smoke_prod.py --base-url https://SEU_APP --lat -23.19 --lon -45.79 --radius 25
```

**Aceite:**
- `/api/v1/health/short` → 200, `dataset.present: true`
- `/api/v1/emergency/search` → 200, pelo menos 1 resultado, campos corretos

### 4. Segurança Prod

**.env (prod):**
```bash
ADMIN_DEBUG=off
PERF_EXPOSE=off
```

**Se quiser manter em bastidor:**
```bash
ADMIN_DEBUG=on
ADMIN_TOKEN=token_forte_aqui
ADMIN_ALLOWED_IPS=IP_da_VPN
```

### 5. Go/No-Go

**`/health`:**
- `dataset.present: true`

**`/search?debug=true`:**
- `override_coverage_pct` alto (≥ 90%)
- "Público/Aceita Cartão SUS" corretos
- Sem clínicas ambulatoriais

**UI `?admin=1`:**
- Badge ok (perf + geo + qc)
- Botão QA lista/baixa CSVs

---

## Checks Automáticos (Console do Navegador)

### Check 1: Contar "Privado" quando API disse "Público" (residual)

Cole no console do navegador:

```javascript
fetch('/api/v1/emergency/search?lat=-23.19&lon=-45.79&radius_km=25&limit=50&expand=true&debug=true')
  .then(r=>r.json()).then(d=>{
    const mism = d.results.filter(it => it.esfera==="Público" && it.override_hit && it.override_reason==="applied");
    console.log("[CHECK] públicos na API:", mism.length);
    console.table(mism.map(it=>({nome:it.nome, esfera:it.esfera, sus:it.sus_badge})));
  });
```

**Aceite:** Todos os "Público" da API devem aparecer como "Público" no card.

### Check 2: Verificar se clínica ambulatorial vazou

Cole no console do navegador:

```javascript
fetch('/api/v1/emergency/search?lat=-23.19&lon=-45.79&radius_km=25&limit=50&expand=true')
  .then(r=>r.json()).then(d=>{
    const amb = (d.results||[]).filter(it=>{
      const n=(it.nome||"").toLowerCase();
      return /psicolog|fono|fisioter|terapia\s*ocup|nutri|consult[óo]rio|ambulat/.test(n);
    });
    console.log("[CHECK] ambulatoriais listadas:", amb.length);
    if (amb.length) console.table(amb.map(it=>({nome:it.nome, label:it.label_maternidade})));
  });
```

**Aceite:** `ambulatoriais listadas: 0`

---

## Se Aparecer Algo Estranho

Mande o `/search?debug=true` dos 3 primeiros itens:

```javascript
fetch('/api/v1/emergency/search?lat=-23.19&lon=-45.79&radius_km=25&limit=3&expand=true&debug=true')
  .then(r=>r.json()).then(d=>{
    console.table(d.results.map(it=>({
      nome: it.nome,
      cnes_id: it.cnes_id,
      esfera: it.esfera,
      sus_badge: it.sus_badge,
      override_hit: it.override_hit,
      override_reason: it.override_reason
    })));
  });
```

**Ajustes comuns:**
- `override_reason="no_match"` em muitos → ajuste `SNAPSHOT` no `.env` ou copie CSVs para o snapshot atual
- `esfera="Privado"` quando deveria ser "Público" → verifique snapshot/caminho dos CSVs do CNES

---

## Variáveis de Ambiente Recomendadas (Prod)

```bash
# Performance
PERF_LOG=off
PERF_EXPOSE=off
OVERRIDES_BOOT=background  # ou lazy
OVERRIDES_CONVENIOS=on

# Segurança
ADMIN_DEBUG=off
PERF_EXPOSE=off

# Snapshot CNES
SNAPSHOT=202512  # ou o mês mais recente disponível
```

---

## Pós-Deploy

1. Rodar smoke test:
   ```bash
   python scripts/smoke_prod.py --base-url https://SEU_APP --lat -23.19 --lon -45.79 --radius 25
   ```

2. Verificar logs:
   - `logs/chat_events.jsonl` (se chatbot ativo)
   - Logs do servidor para erros de startup

3. Monitorar métricas:
   - `/api/v1/health` (sem perf em público)
   - Badge admin em bastidor (`?admin=1` + token)
