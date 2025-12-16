# Perfil PowerShell para o projeto Chatbot Puerpério
# Este arquivo configura automaticamente o terminal ao abrir
# Para usar: Copie este arquivo para seu perfil PowerShell

# Localização do perfil PowerShell:
# $PROFILE (execute 'echo $PROFILE' no PowerShell para ver o caminho)

# Configura encoding UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null
$env:PYTHONIOENCODING = "utf-8"

# Configura Git (se estiver instalado) - ESSENCIAL para remover alerta do Cursor IDE
if (Get-Command git -ErrorAction SilentlyContinue) {
    # Configura credential helper (manager-core é necessário para o Cursor IDE)
    git config --global credential.helper manager-core 2>&1 | Out-Null
    
    # Configura UTF-8 no Git
    git config --global core.quotepath false 2>&1 | Out-Null
    git config --global i18n.commitencoding utf-8 2>&1 | Out-Null
    git config --global i18n.logoutputencoding utf-8 2>&1 | Out-Null
    
    # Configura autocrlf para Windows
    git config --global core.autocrlf true 2>&1 | Out-Null
}

# Função para navegar para o projeto
function Go-Project {
    Set-Location "C:\Users\Cartolano\Documents\chatbot-puerperio"
}

# Função para iniciar o servidor
function Start-Server {
    & "C:\Users\Cartolano\Documents\chatbot-puerperio\iniciar-servidor.ps1"
}

# Função para iniciar com ngrok
function Start-ServerNgrok {
    & "C:\Users\Cartolano\Documents\chatbot-puerperio\iniciar-com-ngrok.ps1"
}

# Função para verificar problemas
function Test-Project {
    & "C:\Users\Cartolano\Documents\chatbot-puerperio\verificar-problemas-powershell.ps1"
}

# Mensagem de boas-vindas (apenas se estiver no diretório do projeto)
if ((Get-Location).Path -like "*chatbot-puerperio*") {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Chatbot Puerpério - Ambiente Configurado" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Encoding: UTF-8" -ForegroundColor Green
    Write-Host "Git: Configurado" -ForegroundColor Green
    Write-Host ""
    Write-Host "Comandos úteis:" -ForegroundColor Yellow
    Write-Host "  Start-Server      - Inicia o servidor Flask" -ForegroundColor Gray
    Write-Host "  Start-ServerNgrok - Inicia servidor + ngrok" -ForegroundColor Gray
    Write-Host "  Test-Project      - Verifica problemas" -ForegroundColor Gray
    Write-Host "  Go-Project        - Navega para o projeto" -ForegroundColor Gray
    Write-Host ""
}
