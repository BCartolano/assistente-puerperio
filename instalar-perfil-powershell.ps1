# Script para instalar o perfil PowerShell automaticamente
# Uso: .\instalar-perfil-powershell.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INSTALACAO DE PERFIL POWERSHELL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verifica se o perfil existe
$profilePath = $PROFILE.CurrentUserAllHosts
$profileDir = Split-Path -Parent $profilePath

Write-Host "Perfil PowerShell: $profilePath" -ForegroundColor Gray
Write-Host ""

# Cria o diretório se não existir
if (-not (Test-Path $profileDir)) {
    Write-Host "Criando diretório do perfil..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $profileDir -Force | Out-Null
    Write-Host "✓ Diretório criado" -ForegroundColor Green
}

# Verifica se o perfil já existe
if (Test-Path $profilePath) {
    Write-Host "⚠️  Perfil já existe!" -ForegroundColor Yellow
    Write-Host ""
    $resposta = Read-Host "Deseja fazer backup e substituir? (S/N)"
    if ($resposta -eq "S" -or $resposta -eq "s") {
        $backupPath = "$profilePath.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
        Copy-Item $profilePath $backupPath
        Write-Host "✓ Backup criado: $backupPath" -ForegroundColor Green
    } else {
        Write-Host "Instalação cancelada." -ForegroundColor Yellow
        exit 0
    }
}

# Copia o perfil
$perfilProjeto = Join-Path $PSScriptRoot "perfil-powershell.ps1"
if (Test-Path $perfilProjeto) {
    Write-Host "Instalando perfil..." -ForegroundColor Yellow
    
    # Lê o conteúdo do perfil do projeto
    $conteudo = Get-Content $perfilProjeto -Raw
    
    # Se o perfil já existe, adiciona ao final
    if (Test-Path $profilePath) {
        $conteudoExistente = Get-Content $profilePath -Raw
        if ($conteudoExistente -notlike "*chatbot-puerperio*") {
            Add-Content -Path $profilePath -Value "`n`n# Perfil Chatbot Puerpério`n$conteudo"
            Write-Host "✓ Perfil adicionado ao perfil existente" -ForegroundColor Green
        } else {
            Write-Host "! Perfil do projeto já está instalado" -ForegroundColor Yellow
        }
    } else {
        # Cria novo perfil
        $conteudo | Out-File -FilePath $profilePath -Encoding UTF8
        Write-Host "✓ Perfil criado" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "INSTALACAO CONCLUIDA" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "O perfil foi instalado com sucesso!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Para aplicar as configurações:" -ForegroundColor Yellow
    Write-Host "1. Feche e reabra o terminal PowerShell" -ForegroundColor White
    Write-Host "2. Ou execute: . `$PROFILE" -ForegroundColor White
    Write-Host ""
    Write-Host "O perfil configurará automaticamente:" -ForegroundColor Gray
    Write-Host "  - Encoding UTF-8" -ForegroundColor Gray
    Write-Host "  - Git credential helper" -ForegroundColor Gray
    Write-Host "  - Funções úteis do projeto" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "✗ Arquivo perfil-powershell.ps1 não encontrado!" -ForegroundColor Red
    Write-Host "  Certifique-se de executar este script na pasta do projeto." -ForegroundColor Yellow
    exit 1
}
