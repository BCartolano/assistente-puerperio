# Checklist pós-rollout – Geo e selo "Ala de Maternidade"

## 1. Confirmar que o geo está fechado (5.786 linhas)

- **Verificar:** `data/geo/hospitals_geo.parquet` existe e tem **5.786** linhas (igual ao `hospitals_ready`).
- **Se precisar refazer na hora (sem geocodificar):**
  ```powershell
  python backend/pipelines/geocode_ready.py --mode copy
  ```
- **Conferência rápida:**
  ```powershell
  python -c "import pandas as pd; df=pd.read_parquet('data/geo/hospitals_geo.parquet'); print(len(df), 'linhas')"
  ```

## 2. Badge admin e CI – números devem bater com o diag

- **Badge (UI com `?admin=1`):** exibe `[geo] coords X% • tel Y% • conf Z`.
  - Esperado hoje: **coords 97%**, **tel 100%**, **conf 4.856** (ou próximo).
  - **Âmbar (warn):** se coords < 85% → rodar geocode completo ou revisar fonte de lat/lon.
- **CI (artifacts):** em `reports-<run_id>`:
  - `geo_health_summary.txt` → Total 5786, Confirmados 4856, coords 97%.
  - `run_summary.json` → deve ter blocos `geo_health` e `search_metrics` (se o orquestrador e o analyzer rodaram).
- **Diag local (referência):**
  ```powershell
  python scripts/diag_geo_v2.py --lat -23.55 --lon -46.63 --radius 25
  ```
  - Confirmados (has_maternity) no ready: 4856; no raio: 189 (SP). Os totais do healthcheck devem refletir isso.

## 3. Quando sair o LT 2512 (leitos dez/2025)

Repetir os comandos na ordem:

1. **Baixar e gerar CSV (FTP já tenta 2512):**
   ```powershell
   python scripts/download_rlEstabLeito.py --snapshot 202512
   ```
   → Gera `data/tbLeito202512.csv` (ou mantém o 202511 copiado até 2512 existir).

2. **Reprocessar pipeline:**
   ```powershell
   python backend/pipelines/prepare_geo_v2.py --snapshot 202512
   python backend/pipelines/geocode_ready.py --mode copy
   ```
   (Ou `--mode geocode` se quiser preencher coordenadas faltantes.)

3. **Validar:**
   ```powershell
   python scripts/check_geo_parquet.py --municipios --export-missing
   python scripts/diag_geo_v2.py --lat -23.55 --lon -46.63 --radius 25
   ```
   → Badge e `reports/geo_health_summary.txt` atualizam; Confirmados podem subir se 2512 tiver mais estabelecimentos com leito obst/neo.

## 4. Se pintar desvio

- **Badge em âmbar:** coords < 85% → ver `reports/geo_health_summary.txt` e `data/geo/` (geo vs ready); rodar `geocode_ready --mode geocode` se faltar geocodificar.
- **Poucos confirmados no raio:** conferir `leito_codes_obst` / `leito_codes_neonatal` em `config/cnes_codes.json`; rodar `scripts/check_leito_counts.py --snapshot 202512`.
- **run_summary sem geo_health ou search_metrics:**
  - `geo_health`: orquestrador chama `check_geo_parquet.py` e lê `reports/geo_health_summary.txt`; verificar se o script rodou e se o arquivo existe.
  - `search_metrics`: vêm de `logs/search_events.jsonl`; o orquestrador chama `quick_metrics_from_logs`; verificar se há buscas logadas e se o path está correto.

**Para debug rápido:** enviar:
1. A resposta de **`GET /api/v1/health`** (JSON completo), e  
2. O trecho de **`reports/run_summary.json`** com os blocos **`geo_health`** e **`search_metrics`**  

Com isso dá para apontar em minutos se o desvio é: coordenada, telefone, leitos, serviço/habilitação ou só raio/min_results.

---

## 5. Quando sair o LT 2512 – depois do reprocessamento

Seguir o item 3 deste checklist (downloader → prepare_geo_v2 → geocode_ready → validar). Se quiser conferir os números com alguém, mande a resposta de **`/api/v1/health`** depois do reprocessamento para bater os totais (coords, tel, conf) e confirmar que está tudo alinhado.
