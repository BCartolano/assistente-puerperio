# Script para resolver TODOS os problemas e alertas do PowerShell e Git
# Uso: .\resolver-tudo.ps1
# Este script configura tudo necessário para remover alertas do Cursor IDE

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RESOLVER TUDO - CONFIGURACAO COMPLETA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$erros = @()
$sucessos = @()

# ========================================
# 1. CONFIGURAR ENCODING UTF-8
# ========================================
Write-Host "[1/5] Configurando encoding UTF-8..." -ForegroundColor Yellow
try {
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    [Console]::InputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding = [System.Text.Encoding]::UTF8
    chcp 65001 | Out-Null
    $env:PYTHONIOENCODING = "utf-8"
    $env:PYTHONLEGACYWINDOWSSTDIO = "0"
    $sucessos += "Encoding UTF-8 configurado"
    Write-Host "  ✓ Encoding UTF-8 configurado" -ForegroundColor Green
} catch {
    $erros += "Erro ao configurar encoding: $_"
    Write-Host "  ✗ Erro ao configurar encoding" -ForegroundColor Red
}
Write-Host ""

# ========================================
# 2. CONFIGURAR GIT
# ========================================
Write-Host "[2/5] Configurando Git..." -ForegroundColor Yellow
if (Get-Command git -ErrorAction SilentlyContinue) {
    try {
        # Configura credential helper (essencial para o Cursor IDE)
        git config --global credential.helper manager-core 2>&1 | Out-Null
        Write-Host "  ✓ Credential helper configurado (manager-core)" -ForegroundColor Green
        
        # Configura UTF-8 no Git
        git config --global core.quotepath false 2>&1 | Out-Null
        git config --global i18n.commitencoding utf-8 2>&1 | Out-Null
        git config --global i18n.logoutputencoding utf-8 2>&1 | Out-Null
        Write-Host "  ✓ Git UTF-8 configurado" -ForegroundColor Green
        
        # Configura autocrlf (importante para Windows)
        git config --global core.autocrlf true 2>&1 | Out-Null
        Write-Host "  ✓ Git autocrlf configurado" -ForegroundColor Green
        
        # Verifica se user.name e user.email estão configurados
        $gitUser = git config --global user.name 2>&1
        $gitEmail = git config --global user.email 2>&1
        
        if (-not $gitUser -or $gitUser -match "error") {
            Write-Host "  ! Git user.name não configurado (opcional)" -ForegroundColor Yellow
            Write-Host "    Configure com: git config --global user.name 'Seu Nome'" -ForegroundColor Gray
        } else {
            Write-Host "  ✓ Git user.name: $gitUser" -ForegroundColor Green
        }
        
        if (-not $gitEmail -or $gitEmail -match "error") {
            Write-Host "  ! Git user.email não configurado (opcional)" -ForegroundColor Yellow
            Write-Host "    Configure com: git config --global user.email 'seu@email.com'" -ForegroundColor Gray
        } else {
            Write-Host "  ✓ Git user.email: $gitEmail" -ForegroundColor Green
        }
        
        $sucessos += "Git configurado corretamente"
    } catch {
        $erros += "Erro ao configurar Git: $_"
        Write-Host "  ✗ Erro ao configurar Git" -ForegroundColor Red
    }
} else {
    Write-Host "  ! Git não encontrado (opcional)" -ForegroundColor Yellow
    Write-Host "    Instale de: https://git-scm.com/download/win" -ForegroundColor Gray
    Write-Host "    O alerta do Cursor IDE pode persistir sem o Git instalado" -ForegroundColor Yellow
}
Write-Host ""

# ========================================
# 3. VERIFICAR PYTHON
# ========================================
Write-Host "[3/5] Verificando Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Python encontrado: $pythonVersion" -ForegroundColor Green
        $sucessos += "Python instalado: $pythonVersion"
    } else {
        $erros += "Python não encontrado"
        Write-Host "  ✗ Python não encontrado" -ForegroundColor Red
    }
} catch {
    $erros += "Python não está instalado"
    Write-Host "  ✗ Python não encontrado" -ForegroundColor Red
    Write-Host "    Instale Python 3.8+ de: https://www.python.org/downloads/" -ForegroundColor Yellow
}
Write-Host ""

# ========================================
# 4. VERIFICAR ARQUIVOS DO PROJETO
# ========================================
Write-Host "[4/5] Verificando arquivos do projeto..." -ForegroundColor Yellow
$arquivos = @("start.py", "backend\app.py")
$todosArquivosOk = $true
foreach ($arquivo in $arquivos) {
    if (Test-Path $arquivo) {
        Write-Host "  ✓ $arquivo encontrado" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $arquivo não encontrado" -ForegroundColor Red
        $todosArquivosOk = $false
        $erros += "Arquivo não encontrado: $arquivo"
    }
}
if ($todosArquivosOk) {
    $sucessos += "Todos os arquivos do projeto encontrados"
}
Write-Host ""

# ========================================
# 5. TESTAR CONFIGURAÇÕES
# ========================================
Write-Host "[5/5] Testando configurações..." -ForegroundColor Yellow
Write-Host "  Testando caracteres especiais: á é í ó ú ã õ ç" -ForegroundColor White
Write-Host "  Testando emojis: ✓ ✗ ⚠️ ℹ️ 🚀" -ForegroundColor White
if ([Console]::OutputEncoding.CodePage -eq 65001) {
    Write-Host "  ✓ Encoding está funcionando corretamente" -ForegroundColor Green
    $sucessos += "Encoding testado e funcionando"
} else {
    Write-Host "  ✗ Encoding pode não estar funcionando corretamente" -ForegroundColor Yellow
}
Write-Host ""

# ========================================
# RESUMO E INSTRUÇÕES
# ========================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RESUMO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($sucessos.Count -gt 0) {
    Write-Host "✓ Sucessos ($($sucessos.Count)):" -ForegroundColor Green
    foreach ($sucesso in $sucessos) {
        Write-Host "  - $sucesso" -ForegroundColor Gray
    }
    Write-Host ""
}

if ($erros.Count -gt 0) {
    Write-Host "✗ Erros encontrados ($($erros.Count)):" -ForegroundColor Red
    foreach ($erro in $erros) {
        Write-Host "  - $erro" -ForegroundColor Gray
    }
    Write-Host ""
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PRÓXIMOS PASSOS PARA REMOVER O ALERTA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para remover o alerta do Cursor IDE sobre Git:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. FECHE ESTE TERMINAL" -ForegroundColor White
Write-Host "   (Feche a janela do terminal atual)" -ForegroundColor Gray
Write-Host ""
Write-Host "2. NO CURSOR IDE:" -ForegroundColor White
Write-Host "   - Clique no botão 'Reiniciar Terminal' no alerta" -ForegroundColor Gray
Write-Host "   - OU: Terminal > Novo Terminal" -ForegroundColor Gray
Write-Host "   - OU: Terminal > Reiniciar Terminal" -ForegroundColor Gray
Write-Host ""
Write-Host "3. O ALERTA DEVE DESAPARECER" -ForegroundColor Green
Write-Host "   Após reiniciar, o Git estará configurado e o alerta não aparecerá mais" -ForegroundColor Gray
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CONFIGURAÇÃO PERMANENTE (OPCIONAL)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para configurar automaticamente toda vez que abrir o terminal:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Execute:" -ForegroundColor White
Write-Host "  .\instalar-perfil-powershell.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "Isso instalará um perfil que configura tudo automaticamente." -ForegroundColor Gray
Write-Host ""

if ($erros.Count -eq 0) {
    Write-Host "✅ TUDO CONFIGURADO COM SUCESSO!" -ForegroundColor Green
    Write-Host "   Agora reinicie o terminal no Cursor IDE para remover o alerta." -ForegroundColor Gray
    exit 0
} else {
    Write-Host "⚠️  Alguns erros foram encontrados. Corrija-os antes de continuar." -ForegroundColor Yellow
    exit 1
}
