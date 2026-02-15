# Diagnóstico e Correção Rápida: Esfera "Desconhecido"

## A) Diagnóstico Relâmpago (2 comandos)

### 1. Verificar se overrides carregaram

```bash
curl http://localhost:5000/api/v1/debug/overrides/coverage
```

**Esperado:**
```json
{
  "total_loaded": 50000,
  "snapshot_usado": "202512"
}
```

**Se `total_loaded = 0` ou `snapshot_usado` não bate com seus CSVs:**
- Overrides não foram carregados
- Verifique `SNAPSHOT` no `.env`
- Verifique se os CSVs existem em `data/`

### 2. Cobertura nos cards (com debug)

Cole no console do navegador:

```javascript
fetch('/api/v1/emergency/search?lat=-23.1931904&lon=-45.7965568&radius_km=25&limit=20&expand=true&debug=true')
  .then(r=>r.json())
  .then(d=>console.table((d.results||[]).map(it=>({
    nome:it.nome,
    cnes:it.cnes_id,
    esfera:it.esfera,
    sus:it.sus_badge,
    hit:it.override_hit,
    reason:it.override_reason
  }))));
```

**Interpretação:**
- Se `override_reason = "no_match"` em quase todos → CSV/snapshot errado
- Se aparece `esfera: Público/Filantrópico/Privado` para vários → payload correto
- Se `override_hit = true` na maioria → overrides funcionando

## B) Corrigir o Override (1 minuto)

### Opção 1: Ajustar SNAPSHOT no .env

```bash
# No .env, defina:
SNAPSHOT=202512
```

### Opção 2: Copiar CSVs para snapshot atual

**Windows:**
```powershell
copy data\tbEstabelecimento202511.csv data\tbEstabelecimento202512.csv
copy data\tbEstabPrestConv202511.csv data\tbEstabPrestConv202512.csv
```

**Linux/Mac:**
```bash
cp data/tbEstabelecimento202511.csv data/tbEstabelecimento202512.csv
cp data/tbEstabPrestConv202511.csv data/tbEstabPrestConv202512.csv
```

### Recarregar overrides sem reiniciar

```bash
# Via curl
curl -X POST http://localhost:5000/api/v1/debug/overrides/refresh

# Ou no console do navegador
fetch('/api/v1/debug/overrides/refresh', {method:'POST'})
```

### Confirmar

```bash
curl http://localhost:5000/api/v1/debug/overrides/coverage
```

Faça a busca com debug de novo; `override_hit` deve virar `true` na maioria.

## C) Martelo: Aplica em Massa no Parquet (100%)

**Mesmo que o override ainda esteja capenga, este script reescreve esfera/sus_badge no Parquet.**

```bash
python scripts/apply_overrides_to_geo.py
```

**O que faz:**
1. Lê `data/geo/hospitals_geo.parquet` (ou `.min`)
2. Carrega overrides do CNES
3. Aplica a TODOS os CNES, normalizando esfera e SUS
4. Salva de volta `.parquet` e `.min`

**Depois:**
```bash
# Garantir mtime atualizado (opcional)
python backend/pipelines/geocode_ready.py --mode copy

# Limpar cache do navegador
Ctrl+F5 no navegador
```

**Resultado:** Os 17 cartões viram de uma vez! ✅

## D) Script de Diagnóstico Automático

```bash
python scripts/diag_override_coverage.py
```

Mostra:
- Total de overrides carregados
- Snapshot usado
- Instruções de diagnóstico
- Comando para testar no console

## Resumo Rápido

1. **Diagnóstico:**
   ```bash
   python scripts/diag_override_coverage.py
   ```

2. **Corrigir snapshot/CSVs:**
   - Ajuste `SNAPSHOT` no `.env` OU copie CSVs
   - `POST /api/v1/debug/overrides/refresh`

3. **Aplicar em massa (garantido):**
   ```bash
   python scripts/apply_overrides_to_geo.py
   ```

4. **Limpar cache:**
   - Ctrl+F5 no navegador

## Se Ainda Estiver Errado

Envie:
1. **2 linhas do diagnóstico** (payload da API com debug):
   ```json
   {
     "nome": "...",
     "cnes_id": "...",
     "esfera": "...",
     "override_hit": true/false,
     "override_reason": "..."
   }
   ```

2. **Coverage endpoint:**
   ```bash
   curl http://localhost:5000/api/v1/debug/overrides/coverage
   ```

Com isso identificamos exatamente: "é snapshot X", ou "é CSV em Y", ou "é o front segurando".
