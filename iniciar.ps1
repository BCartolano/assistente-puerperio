# Script simples para iniciar o servidor
# Uso: .\iniciar.ps1

$venvPython = "backend\venv\Scripts\python.exe"

if (Test-Path $venvPython) {
    Write-Host "Iniciando servidor..." -ForegroundColor Green
    & $venvPython start.py
} else {
    Write-Host "ERRO: Ambiente virtual nao encontrado!" -ForegroundColor Red
    Write-Host "Execute: python -m venv backend\venv" -ForegroundColor Yellow
    exit 1
}
