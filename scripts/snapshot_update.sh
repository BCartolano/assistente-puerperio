#!/usr/bin/env bash
# Atualização mensal: baixa/coloca CSVs em data/raw/<snapshot>, roda pipeline completo.
# Uso: ./scripts/snapshot_update.sh [snapshot]   # ex.: 202601

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SNAPSHOT="${1:-$(date +%Y%m)}"

echo "--- Snapshot update: $SNAPSHOT ---"
RAW_DIR="$BASE_DIR/data/raw/$SNAPSHOT"
mkdir -p "$RAW_DIR"

# 1. Colocar CSVs em data/raw/<snapshot> (manual ou download DataSUS)
#    Ex.: tbEstabelecimento, rlEstabLeito, rlEstabServClass
if [ ! -f "$RAW_DIR/tbEstabelecimento.csv" ] && [ ! -f "$RAW_DIR/tbEstabelecimento${SNAPSHOT}.csv" ]; then
  echo "AVISO: Coloque os CSVs do CNES em $RAW_DIR e execute novamente."
  echo "Arquivos esperados: tbEstabelecimento*, rlEstabLeito*, rlEstabServClass*"
  exit 1
fi

# 2. Ingest
echo "Rodando ingest..."
cd "$BASE_DIR"
python -m backend.pipelines.ingest --snapshot "$SNAPSHOT" || python backend/etl/maternity_whitelist_pipeline.py

# 3. Classify (se houver GeoJSON/JSON de estabelecimentos)
GEOJSON="$BASE_DIR/backend/data/maternities_whitelist.geojson"
if [ -f "$GEOJSON" ]; then
  echo "Rodando classify..."
  python -m backend.pipelines.classify --input "$GEOJSON" --output "$BASE_DIR/backend/data/maternities_classified.json"
fi

# 4. Registrar data_version
echo "$SNAPSHOT" >> "$BASE_DIR/docs/data_versions.md" 2>/dev/null || true
echo "Snapshot $SNAPSHOT registrado em docs/data_versions.md"

echo "--- Snapshot update concluído ---"
