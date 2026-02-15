# Checklist rápido (staging)

## Pré-requisitos
- Python 3.11+, pip
- Git
- (Opcional) Docker Desktop

## Variáveis de ambiente
Se ainda não tiver `.env`:
- **PowerShell:** `scripts\criar-env.ps1`
- ou: `copy env.example .env`
Edite o `.env` se quiser tempo de viagem (`TRAVEL_TIME=on` e `MAPBOX_TOKEN`).

## Dados CNES
Coloque os CSVs em `data/raw/<snapshot>` (ex.: `202512`).

## Preflight
```bash
python scripts/preflight.py
```
Esperado: **SUCESSO ✅**

## Golden set (opcional, melhora os gates)
```bash
python scripts/build_golden_set.py
```
Arquivo gerado: `data/golden/golden_set.json`  
Teste: `pytest tests/golden/test_golden_set.py -v`

## Testes unitários
```bash
pip install -r requirements.txt
pytest tests/unit -v
```

## Orquestrador
```bash
python scripts/run_orchestrator.py --snapshot 202512
```
Cheque `reports/run_summary.json`:
- `coord_coverage` ≥ 0.85
- `phone_coverage` ≥ 0.85
- `geocode_fail_rate` < 0.10
- `tests_passed` = true
- `golden_accuracy` ≥ 0.95 (se houver golden_set)

## API
```bash
uvicorn backend.api.main:app --reload --port 8000
```
Testes rápidos:
- http://localhost:8000/api/v1/version
- http://localhost:8000/api/v1/emergency/search?lat=-23.55&lon=-46.63&limit=3
- http://localhost:8000/api/v1/establishments/{CNES}/evidence

## Docker (opcional)
```bash
docker compose up api
docker compose --profile orchestrator up orchestrator
```

## Se algum gate falhar
- **coord < 0.85:** reprocessar geocode, revisar endereços/CEP, considerar provider com token.
- **phone < 0.85:** melhorar parser/normalização; buscar campos alternativos no CNES.
- **muitos "prováveis":** revisar `config/cnes_codes.json` e pesos em `config/scoring.yaml`; rodar pipeline novamente.
