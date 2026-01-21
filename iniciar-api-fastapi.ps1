# Script para iniciar API FastAPI - Localizador Puerperal
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "🚀 Iniciando API FastAPI" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se banco existe
$dbPath = "backend\cnes_cache.db"
if (-not (Test-Path $dbPath)) {
    Write-Host "⚠️ Banco de dados não encontrado!" -ForegroundColor Yellow
    Write-Host "💡 Execute primeiro: python backend/etl/seed_data.py" -ForegroundColor Yellow
    Write-Host ""
    $continuar = Read-Host "Deseja continuar mesmo assim? (s/n)"
    if ($continuar -ne 's' -and $continuar -ne 'S') {
        exit
    }
}

# Iniciar servidor
Write-Host "📡 Iniciando servidor na porta 5000..." -ForegroundColor Cyan
Write-Host "📚 Documentação: http://localhost:5000/docs" -ForegroundColor Cyan
Write-Host "🔍 Health Check: http://localhost:5000/api/v1/facilities/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pressione Ctrl+C para parar o servidor" -ForegroundColor Gray
Write-Host ""

python -m uvicorn backend.api.main:app --reload --host 0.0.0.0 --port 5000
