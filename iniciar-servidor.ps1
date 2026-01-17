# Script PowerShell para iniciar o servidor
# Uso: .\iniciar-servidor.ps1

# Configura encoding UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
chcp 65001 | Out-Null

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Iniciando Assistente Puerperio" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Define caminho do Python do ambiente virtual (tenta múltiplos locais)
$venvPython = $null

# Tenta encontrar o venv em diferentes locais
if (Test-Path "backend\venv\Scripts\python.exe") {
    $venvPython = "backend\venv\Scripts\python.exe"
    Write-Host "Ambiente virtual encontrado em backend\venv" -ForegroundColor Green
}
elseif (Test-Path "venv\Scripts\python.exe") {
    $venvPython = "venv\Scripts\python.exe"
    Write-Host "Ambiente virtual encontrado em venv" -ForegroundColor Green
}
else {
    Write-Host "AVISO: Ambiente virtual nao encontrado!" -ForegroundColor Yellow
    Write-Host "Tentando usar Python global..." -ForegroundColor Yellow
    
    # Tenta usar Python global
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCmd) {
        $venvPython = "python"
        Write-Host "Usando Python global: $($pythonCmd.Source)" -ForegroundColor Yellow
    }
    else {
        Write-Host "ERRO: Python nao encontrado!" -ForegroundColor Red
        Write-Host "Execute: python -m venv backend\venv" -ForegroundColor Yellow
        exit 1
    }
}

# Inicia o servidor
if ($venvPython) {
    Write-Host "Iniciando servidor Flask..." -ForegroundColor Yellow
    Write-Host ""
    & $venvPython start.py
}
