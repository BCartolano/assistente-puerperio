# Script de Monitoramento - Tags de Cansaço Extremo
# Filtra apenas as tags cansaço_extremo e cansaço_extremo_critico do context_metrics.log

Write-Host "🔍 Monitorando tags de cansaço_extremo..." -ForegroundColor Cyan
Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Yellow
Write-Host ""

$logFile = "logs\context_metrics.log"

if (-not (Test-Path $logFile)) {
    Write-Host "⚠️ Arquivo $logFile não encontrado. Criando..." -ForegroundColor Yellow
    New-Item -ItemType File -Path $logFile -Force | Out-Null
}

Get-Content $logFile -Wait -Tail 50 | Where-Object { 
    $_ -match 'cansaço_extremo|cansaço_extremo_critico' 
} | ForEach-Object {
    $color = if ($_ -match 'critico') { "Red" } else { "Yellow" }
    Write-Host $_ -ForegroundColor $color
}
