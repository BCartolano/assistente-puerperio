# Limpeza do repositório (4GB → enxuto)

Produção usa só `data/geo/hospitals_geo.min.parquet` (ou `hospitals_geo.parquet`) + configs. O resto pode ser ignorado ou removido.

## O que pode apagar/ignorar sem dor

| Alvo | Descrição |
|------|-----------|
| `BASE_DE_DADOS_CNES_*/` | Dumps originais CNES |
| `data/raw/**` | CSV/DBC originais |
| `data/tb*.csv` | Mantendo só `data/geo/hospitals_geo.parquet` (e `data/golden` se quiser) |
| `*.dbc`, `*.dbf`, `*.sqlite`, `*.db` | Exceto geocache se quiser |
| `reports/**` e `logs/**` antigos | Já tem rotate e artifacts no CI |
| `__pycache__`, `.pytest_cache`, `.venv`, `node_modules` | Caches e ambientes |

## Scripts seguros

### Relatório de tamanho

```bash
python scripts/size_report.py
```

Mostra os top 20 diretórios/arquivos por tamanho (ignora `.git`, `__pycache__`, `node_modules`, `.venv`, `logs`, `reports`).

### Limpeza (dry-run por padrão)

```bash
# Simulado — só lista o que seria removido
python scripts/clean_workspace.py

# Executar remoção
python scripts/clean_workspace.py --no-dry-run
```

Protegidos (nunca apagados): `data/geo/hospitals_geo.parquet`, `data/geo/hospitals_geo.min.parquet`, `config/cnes_codes.json`, `config/scoring.yaml`.

## Se os arquivos grandes já foram commitados

### Remover do índice e manter local

```bash
git rm -r --cached BASE_DE_DADOS_CNES_* data/raw reports logs 2>/dev/null || true
git commit -m "chore: stop tracking dumps/raw/reports/logs"
```

### Reduzir histórico (opcional, pesado)

Requer `git-filter-repo` (ou BFG):

```bash
pipx install git-filter-repo
git filter-repo --path data/raw --path-glob "BASE_DE_DADOS_CNES_*" --invert-paths
git gc --aggressive --prune=now
```

Depois da limpeza, rode `python scripts/size_report.py` e envie o "Top diretórios/arquivos por tamanho" para apontar onde enxugar mais.
