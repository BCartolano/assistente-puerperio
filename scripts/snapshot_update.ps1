# Atualização mensal: coloca CSVs em data/raw/<snapshot>, roda pipeline completo.
# Uso: .\scripts\snapshot_update.ps1 [-Snapshot 202601]

param(
    [string]$Snapshot = (Get-Date -Format "yyyyMM")
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BaseDir = Split-Path -Parent $ScriptDir
$RawDir = Join-Path $BaseDir "data\raw\$Snapshot"

Write-Host "--- Snapshot update: $Snapshot ---"
New-Item -ItemType Directory -Force -Path $RawDir | Out-Null

# 1. Verificar CSVs em data/raw/<snapshot>
$estab = Get-ChildItem -Path $RawDir -Filter "*Estabelecimento*" -ErrorAction SilentlyContinue
if (-not $estab) {
    $alt = Join-Path $BaseDir "BASE_DE_DADOS_CNES_202512"
    if (Test-Path $alt) { $RawDir = $alt; Write-Host "Usando $alt" }
    else {
        Write-Host "AVISO: Coloque os CSVs do CNES em $RawDir (ou BASE_DE_DADOS_CNES_202512) e execute novamente."
        exit 1
    }
}

# 2. Ingest
Write-Host "Rodando ingest..."
Set-Location $BaseDir
try {
    python -m backend.pipelines.ingest --snapshot $Snapshot
} catch {
    python backend/etl/maternity_whitelist_pipeline.py
}

# 3. Classify
$GeoJson = Join-Path $BaseDir "backend\data\maternities_whitelist.geojson"
if (Test-Path $GeoJson) {
    Write-Host "Rodando classify..."
    python -m backend.pipelines.classify --input $GeoJson --output (Join-Path $BaseDir "backend\data\maternities_classified.json")
}

# 4. Registrar data_version
$VersionsMd = Join-Path $BaseDir "docs\data_versions.md"
Add-Content -Path $VersionsMd -Value $Snapshot -ErrorAction SilentlyContinue
Write-Host "Snapshot $Snapshot registrado em docs/data_versions.md"
Write-Host "--- Snapshot update concluído ---"
