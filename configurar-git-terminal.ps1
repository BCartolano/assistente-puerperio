# Script para configurar Git e resolver alerta do Cursor IDE
# Uso: .\configurar-git-terminal.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CONFIGURACAO GIT E TERMINAL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configura encoding UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null
$env:PYTHONIOENCODING = "utf-8"

Write-Host "✓ Encoding UTF-8 configurado" -ForegroundColor Green

# Verifica se Git está instalado
Write-Host ""
Write-Host "Verificando Git..." -ForegroundColor Yellow
try {
    $gitVersion = git --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Git encontrado: $gitVersion" -ForegroundColor Green
        
        # Verifica configuração do Git
        $gitUser = git config --global user.name 2>&1
        $gitEmail = git config --global user.email 2>&1
        
        if ($gitUser -and $gitUser -notmatch "error") {
            Write-Host "✓ Git user.name: $gitUser" -ForegroundColor Green
        } else {
            Write-Host "! Git user.name não configurado" -ForegroundColor Yellow
        }
        
        if ($gitEmail -and $gitEmail -notmatch "error") {
            Write-Host "✓ Git user.email: $gitEmail" -ForegroundColor Green
        } else {
            Write-Host "! Git user.email não configurado" -ForegroundColor Yellow
        }
        
        # Configura Git para usar credenciais do Windows (ESSENCIAL para Cursor IDE)
        Write-Host ""
        Write-Host "Configurando Git..." -ForegroundColor Yellow
        git config --global credential.helper manager-core 2>&1 | Out-Null
        Write-Host "✓ Credential helper configurado (manager-core)" -ForegroundColor Green
        
        # Configura Git para usar UTF-8
        git config --global core.quotepath false 2>&1 | Out-Null
        git config --global i18n.commitencoding utf-8 2>&1 | Out-Null
        git config --global i18n.logoutputencoding utf-8 2>&1 | Out-Null
        Write-Host "✓ Git UTF-8 configurado" -ForegroundColor Green
        
        # Configura autocrlf para Windows
        git config --global core.autocrlf true 2>&1 | Out-Null
        Write-Host "✓ Git autocrlf configurado" -ForegroundColor Green
        
    } else {
        Write-Host "✗ Git não encontrado" -ForegroundColor Red
        Write-Host "  Instale Git de: https://git-scm.com/download/win" -ForegroundColor Yellow
    }
} catch {
    Write-Host "✗ Erro ao verificar Git: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CONFIGURACAO CONCLUIDA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Git configurado corretamente!" -ForegroundColor Green
Write-Host ""
Write-Host "Para resolver o alerta do Cursor IDE:" -ForegroundColor Yellow
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
Write-Host "💡 DICA: Execute '.\instalar-perfil-powershell.ps1' para configurar" -ForegroundColor Cyan
Write-Host "   automaticamente toda vez que abrir um novo terminal." -ForegroundColor Gray
Write-Host ""
