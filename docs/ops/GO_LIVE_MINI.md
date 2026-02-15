# Go Live Mini – Emergência Obstétrica (Geo v2)

Checklist de validação final e dois upgrades para o selo "Ala de Maternidade".

**📚 Documentação completa:**
- `GO_LIVE_RUNBOOK.md` — Runbook completo de go live (build, deploy, pós-deploy)
- `OPERACAO_ROLLBACK.md` — Operação contínua e rollback

---

## Checklist de validação final

### Dataset
```bash
python backend/pipelines/geocode_ready.py
# até salvar data/geo/hospitals_geo.parquet

python scripts/diag_geo_v2.py --lat -23.55 --lon -46.63 --radius 25
# confirme muitos "Prováveis"
```

### API Flask (porta 5000)
```bash
curl "http://localhost:5000/api/v1/emergency/search?lat=-23.1931904&lon=-45.7965568&radius_km=25&expand=true&limit=20&min_results=8&debug=true"
```
- `debug.radius_used` deve bater com o chip da UI
- `found_B` alto; `found_A` pode estar 0 por enquanto

### UI
- Console: `[EMERGENCY] GET /api/v1/emergency/search?...` e `[EMERGENCY DEBUG] { … }`
- Lista com dezenas de resultados
- Chip "Resultados em raio expandido para X km" quando `debug.expanded=true`
- Cards: Nome, Esfera, Atende SUS, telefone, endereço, Rotas, `label_maternidade`

---

## Dois upgrades que valem ouro

### 1. Mapear códigos de leito (Prováveis → Confirmados / "Ala de Maternidade")
```bash
python scripts/inspect_leito_types.py --snapshot 202512
# abrir config/leito_codes_suggestion.json
# copiar leito_codes_obst e leito_codes_neonatal → config/cnes_codes.json

python backend/pipelines/prepare_geo_v2.py --snapshot 202512
python backend/pipelines/geocode_ready.py
```
- `diag_geo_v2` deve mostrar **Confirmados > 0**
- Os cards passam a exibir **"Ala de Maternidade"** onde for comprovado

### 2. Observabilidade de busca
- Cada busca no Flask é logada em **`logs/search_events.jsonl`** (um JSON por linha)
- Campos: `ts`, `lat`, `lon`, `radius_requested`, `radius_used`, `expanded`, `found_A`, `found_B`, `banner_192`, `sus`
- Ajuda a ver UFs onde falta dado e calibrar `radius`/`min_results`

---

## Go / No‑go

**OK se:**
- `curl` na 5000 retorna lista grande
- UI mostra dezenas, chip de raio quando expandiu, banner 192 quando completou com grupo C
- **Perf:** `startup_ms` &lt; 2500 ms, `overrides.boot_ms` &lt; 2000 ms, `first_request_ms` &lt; 1500 ms
- **Geo:** `coord_coverage_pct` ≥ 0.85; `phone_coverage_pct` ≥ 0.85
- **Search debug:** `override_coverage_pct` alto; "Público" / "Aceita Cartão SUS" corretos
- **qa_hints:** `público_vs_privado_pct_uf` ≤ 0.5%
- **UI ?admin=1:** badge [geo] + [perf] + [qc] ok; botão ↻ funcionando

**Não‑OK se:**
- **503** na 5000 → path do parquet (rode `geocode_ready` e verifique diretório)
- **Poucos resultados** → conferir `radius_km` e `expand=true` na URL da UI e se não tem filtro escondido no client

---

## Pequenos ajustes opcionais

- **Raio:** se a cidade for muito pequena, subir `radius_km` para 50 antes do primeiro expand (UI pode ter seletor "raio: 25/50/100").
- **extra_exclude_keywords:** se ainda pipocar serviço de apoio, adicione a palavra em `config/cnes_codes.json` e rode `prepare_geo_v2` de novo.
- **SUS:** quando o usuário marcar SUS, passar `sus=true` na query; se vier pouco resultado, mostrar "Tente remover o filtro SUS" com botão.
