# Script para verificar e diagnosticar problemas no PowerShell
# Uso: .\verificar-problemas-powershell.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VERIFICACAO DE PROBLEMAS - POWERSHELL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$problemas = @()
$avisos = @()
$sucessos = @()

# Verificacao 1: Politica de execucao
Write-Host "1. Verificando politica de execucao..." -ForegroundColor Yellow
$executionPolicy = Get-ExecutionPolicy
if ($executionPolicy -eq "Restricted") {
    $problemas += "Politica de execucao esta 'Restricted' - scripts nao podem ser executados"
    Write-Host "  X Politica: $executionPolicy" -ForegroundColor Red
    Write-Host "  Solucao: Execute como Administrador:" -ForegroundColor Yellow
    Write-Host "    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Gray
} elseif ($executionPolicy -eq "AllSigned") {
    $avisos += "Politica de execucao esta 'AllSigned' - apenas scripts assinados podem ser executados"
    Write-Host "  ! Politica: $executionPolicy" -ForegroundColor Yellow
} else {
    $sucessos += "Politica de execucao adequada: $executionPolicy"
    Write-Host "  OK Politica: $executionPolicy" -ForegroundColor Green
}
Write-Host ""

# Verificacao 2: Encoding
Write-Host "2. Verificando encoding UTF-8..." -ForegroundColor Yellow
$outputEncoding = [Console]::OutputEncoding
$inputEncoding = [Console]::InputEncoding

if ($outputEncoding.CodePage -eq 65001) {
    $sucessos += "OutputEncoding esta configurado para UTF-8 (65001)"
    Write-Host "  OK OutputEncoding: UTF-8 (65001)" -ForegroundColor Green
} else {
    $avisos += "OutputEncoding nao esta em UTF-8 (atual: $($outputEncoding.CodePage))"
    Write-Host "  ! OutputEncoding: $($outputEncoding.EncodingName) ($($outputEncoding.CodePage))" -ForegroundColor Yellow
    Write-Host "  Solucao: Execute [Console]::OutputEncoding = [System.Text.Encoding]::UTF8" -ForegroundColor Gray
}

if ($inputEncoding.CodePage -eq 65001) {
    $sucessos += "InputEncoding esta configurado para UTF-8 (65001)"
    Write-Host "  OK InputEncoding: UTF-8 (65001)" -ForegroundColor Green
} else {
    $avisos += "InputEncoding nao esta em UTF-8 (atual: $($inputEncoding.CodePage))"
    Write-Host "  ! InputEncoding: $($inputEncoding.EncodingName) ($($inputEncoding.CodePage))" -ForegroundColor Yellow
}
Write-Host ""

# Verificacao 3: Python
Write-Host "3. Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $sucessos += "Python esta instalado: $pythonVersion"
        Write-Host "  OK Python: $pythonVersion" -ForegroundColor Green
        
        # Verifica variavel de ambiente
        $pythonIOEncoding = $env:PYTHONIOENCODING
        if ($pythonIOEncoding -eq "utf-8") {
            $sucessos += "PYTHONIOENCODING esta configurado para utf-8"
            Write-Host "  OK PYTHONIOENCODING: utf-8" -ForegroundColor Green
        } else {
            $avisos += "PYTHONIOENCODING nao esta configurado (atual: $pythonIOEncoding)"
            Write-Host "  ! PYTHONIOENCODING: $pythonIOEncoding" -ForegroundColor Yellow
            Write-Host "  Solucao: Execute `$env:PYTHONIOENCODING = 'utf-8'" -ForegroundColor Gray
        }
    } else {
        $problemas += "Python nao encontrado ou com erro"
        Write-Host "  X Python nao encontrado" -ForegroundColor Red
    }
} catch {
    $problemas += "Python nao esta instalado ou nao esta no PATH"
    Write-Host "  X Python nao encontrado" -ForegroundColor Red
    Write-Host "  Solucao: Instale Python 3.8+ e adicione ao PATH" -ForegroundColor Yellow
}
Write-Host ""

# Verificacao 4: Arquivos necessarios
Write-Host "4. Verificando arquivos do projeto..." -ForegroundColor Yellow
$arquivosNecessarios = @("start.py", "verificar_config.py", "backend\app.py")
foreach ($arquivo in $arquivosNecessarios) {
    if (Test-Path $arquivo) {
        $sucessos += "Arquivo encontrado: $arquivo"
        Write-Host "  OK $arquivo" -ForegroundColor Green
    } else {
        $problemas += "Arquivo nao encontrado: $arquivo"
        Write-Host "  X $arquivo nao encontrado" -ForegroundColor Red
    }
}
Write-Host ""

# Verificacao 5: Scripts PowerShell
Write-Host "5. Verificando scripts PowerShell..." -ForegroundColor Yellow
$scriptsPS = @("iniciar-servidor.ps1", "iniciar-com-ngrok.ps1", "testar-encoding.ps1")
foreach ($script in $scriptsPS) {
    if (Test-Path $script) {
        $sucessos += "Script encontrado: $script"
        Write-Host "  OK $script" -ForegroundColor Green
    } else {
        $avisos += "Script nao encontrado: $script"
        Write-Host "  ! $script nao encontrado" -ForegroundColor Yellow
    }
}
Write-Host ""

# Verificacao 6: Teste de caracteres especiais
Write-Host "6. Testando exibicao de caracteres especiais..." -ForegroundColor Yellow
Write-Host "  Acentos: a e i o u a o c" -ForegroundColor White
Write-Host "  Maiusculas: A E I O U A O C" -ForegroundColor White
Write-Host "  Emojis: [OK] [ERRO] [AVISO] [INFO]" -ForegroundColor White
Write-Host "  Se os caracteres acima apareceram corretamente, o encoding esta funcionando!" -ForegroundColor Gray
Write-Host ""

# Resumo
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RESUMO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($sucessos.Count -gt 0) {
    Write-Host "OK Sucessos ($($sucessos.Count)):" -ForegroundColor Green
    foreach ($sucesso in $sucessos) {
        Write-Host "  - $sucesso" -ForegroundColor Gray
    }
    Write-Host ""
}

if ($avisos.Count -gt 0) {
    Write-Host "! Avisos ($($avisos.Count)):" -ForegroundColor Yellow
    foreach ($aviso in $avisos) {
        Write-Host "  - $aviso" -ForegroundColor Gray
    }
    Write-Host ""
}

if ($problemas.Count -gt 0) {
    Write-Host "X Problemas ($($problemas.Count)):" -ForegroundColor Red
    foreach ($problema in $problemas) {
        Write-Host "  - $problema" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "Acao necessaria: Corrija os problemas acima antes de continuar." -ForegroundColor Red
    exit 1
} else {
    Write-Host "OK Nenhum problema critico encontrado!" -ForegroundColor Green
    if ($avisos.Count -gt 0) {
        Write-Host "! Ha alguns avisos que podem ser corrigidos." -ForegroundColor Yellow
    }
    exit 0
}
