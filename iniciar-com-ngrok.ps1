# Script PowerShell para iniciar o servidor com ngrok e encoding UTF-8 correto
# Uso: .\iniciar-com-ngrok.ps1

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
Write-Host "Iniciando Assistente Puerpério com ngrok" -ForegroundColor Cyan
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

# Procura o ngrok
$ngrokPath = $null

# Verifica se ngrok está no PATH
try {
    $ngrokVersion = ngrok version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $ngrokPath = "ngrok"
        Write-Host "✓ ngrok encontrado no PATH" -ForegroundColor Green
    }
} catch {
    # Continua procurando
}

# Verifica na pasta do projeto
if (-not $ngrokPath) {
    if (Test-Path "ngrok.exe") {
        $ngrokPath = ".\ngrok.exe"
        Write-Host "✓ ngrok encontrado na pasta do projeto" -ForegroundColor Green
    }
}

# Verifica na pasta Downloads
if (-not $ngrokPath) {
    $downloadsPath = Join-Path $env:USERPROFILE "Downloads\ngrok.exe"
    if (Test-Path $downloadsPath) {
        $ngrokPath = $downloadsPath
        Write-Host "✓ ngrok encontrado na pasta Downloads" -ForegroundColor Green
    }
}

# Se não encontrou, mostra erro
if (-not $ngrokPath) {
    Write-Host ""
    Write-Host "✗ ERRO: ngrok não encontrado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Por favor, instale o ngrok:" -ForegroundColor Yellow
    Write-Host "1. Baixe de: https://ngrok.com/download" -ForegroundColor Yellow
    Write-Host "2. Extraia o ngrok.exe" -ForegroundColor Yellow
    Write-Host "3. Coloque o ngrok.exe nesta pasta OU adicione ao PATH" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Veja o guia completo em: COMO_INSTALAR_NGROK.md" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

Write-Host ""
Write-Host "Iniciando o servidor Flask..." -ForegroundColor Yellow

# Inicia Flask em uma nova janela
Start-Process python -ArgumentList "start.py" -WindowStyle Normal

Write-Host "Aguardando o Flask iniciar (5 segundos)..." -ForegroundColor Gray
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Iniciando ngrok..." -ForegroundColor Cyan
Write-Host "O link público será exibido abaixo:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 COPIAR O LINK: Procure por 'Forwarding' abaixo" -ForegroundColor Yellow
Write-Host "   O link será algo como: https://xxxxx.ngrok.io" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  Para parar: Pressione Ctrl+C aqui" -ForegroundColor Yellow
Write-Host "   Depois feche a janela do 'Flask Server'" -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Inicia o ngrok
& $ngrokPath http 5000
