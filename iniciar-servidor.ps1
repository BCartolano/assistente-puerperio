# Script PowerShell para iniciar o servidor com encoding UTF-8 correto
# Uso: .\iniciar-servidor.ps1

# Configura encoding UTF-8 para o PowerShell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Configura code page do console para UTF-8
chcp 65001 | Out-Null

# Define variável de ambiente para Python
$env:PYTHONIOENCODING = "utf-8"

# Configura Git (se estiver instalado) para evitar alertas do Cursor IDE
if (Get-Command git -ErrorAction SilentlyContinue) {
    # Credential helper manager-core é ESSENCIAL para o Cursor IDE
    git config --global credential.helper manager-core 2>&1 | Out-Null
    git config --global core.quotepath false 2>&1 | Out-Null
    git config --global i18n.commitencoding utf-8 2>&1 | Out-Null
    git config --global i18n.logoutputencoding utf-8 2>&1 | Out-Null
    git config --global core.autocrlf true 2>&1 | Out-Null
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Iniciando Assistente Puerpério" -ForegroundColor Cyan
Write-Host "Encoding UTF-8 configurado" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verifica se está no diretório correto
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Verifica se Python está disponível
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python detectado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ ERRO: Python não encontrado!" -ForegroundColor Red
    Write-Host "Por favor, instale Python 3.8 ou superior" -ForegroundColor Yellow
    exit 1
}

# Verifica se o arquivo start.py existe
if (-not (Test-Path "start.py")) {
    Write-Host "✗ ERRO: Arquivo start.py não encontrado!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Iniciando servidor Flask..." -ForegroundColor Yellow
Write-Host "Pressione Ctrl+C para parar o servidor" -ForegroundColor Gray
Write-Host ""

# Inicia o servidor
python start.py
