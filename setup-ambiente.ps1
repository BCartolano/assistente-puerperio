# ============================================
# Script de Setup Automático - Chatbot Puerpério
# ============================================
# Este script automatiza a instalação e configuração
# de todo o ambiente necessário para o projeto.
# ============================================

# Configuração de encoding UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  SETUP AUTOMÁTICO - CHATBOT PUERPÉRIO" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Função para verificar se um comando existe
function Test-Command {
    param([string]$Command)
    $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

# Função para verificar versão do Python
function Test-PythonVersion {
    Write-Host "[1/7] Verificando Python..." -ForegroundColor Yellow
    
    # Tenta diferentes formas de chamar Python
    $pythonCommands = @("python", "python3", "py")
    $pythonPath = $null
    $pythonVersion = $null
    
    foreach ($cmd in $pythonCommands) {
        if (Test-Command $cmd) {
            try {
                $versionOutput = & $cmd --version 2>&1
                if ($LASTEXITCODE -eq 0 -or $versionOutput -match "Python") {
                    $pythonPath = $cmd
                    $pythonVersion = $versionOutput
                    break
                }
            } catch {
                continue
            }
        }
    }
    
    if ($pythonPath) {
        Write-Host "  ✅ Python encontrado: $pythonVersion" -ForegroundColor Green
        Write-Host "  📍 Comando: $pythonPath" -ForegroundColor Gray
        return @{ Success = $true; Command = $pythonPath; Version = $pythonVersion }
    } else {
        Write-Host "  ❌ Python NÃO encontrado!" -ForegroundColor Red
        Write-Host ""
        Write-Host "  📥 Para instalar Python 3.11:" -ForegroundColor Yellow
        Write-Host "     1. Acesse: https://www.python.org/downloads/" -ForegroundColor Cyan
        Write-Host "     2. Baixe Python 3.11.x (Windows installer 64-bit)" -ForegroundColor Cyan
        Write-Host "     3. Durante instalação, MARQUE 'Add Python to PATH'" -ForegroundColor Yellow
        Write-Host "     4. Execute este script novamente após instalar" -ForegroundColor Cyan
        Write-Host ""
        return @{ Success = $false; Command = $null; Version = $null }
    }
}

# Função para verificar pip
function Test-PipVersion {
    param([string]$PythonCommand)
    
    Write-Host "[2/7] Verificando pip..." -ForegroundColor Yellow
    
    try {
        $pipVersion = & $PythonCommand -m pip --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ pip encontrado: $pipVersion" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "  ⚠️ pip não encontrado, tentando instalar..." -ForegroundColor Yellow
        try {
            & $PythonCommand -m ensurepip --upgrade
            Write-Host "  ✅ pip instalado com sucesso!" -ForegroundColor Green
            return $true
        } catch {
            Write-Host "  ❌ Erro ao instalar pip" -ForegroundColor Red
            return $false
        }
    }
    
    return $false
}

# Função para criar ambiente virtual
function New-VirtualEnvironment {
    param([string]$PythonCommand)
    
    Write-Host "[3/7] Configurando ambiente virtual..." -ForegroundColor Yellow
    
    $venvPath = Join-Path $PSScriptRoot "backend\venv"
    
    if (Test-Path $venvPath) {
        Write-Host "  ℹ️ Ambiente virtual já existe em: $venvPath" -ForegroundColor Cyan
        Write-Host "  🔄 Deseja recriar? (s/n): " -NoNewline -ForegroundColor Yellow
        $response = Read-Host
        if ($response -match "^[sS]") {
            Write-Host "  🗑️ Removendo ambiente virtual antigo..." -ForegroundColor Yellow
            Remove-Item -Path $venvPath -Recurse -Force -ErrorAction SilentlyContinue
        } else {
            Write-Host "  ✅ Usando ambiente virtual existente" -ForegroundColor Green
            return $true
        }
    }
    
    Write-Host "  📦 Criando ambiente virtual..." -ForegroundColor Yellow
    try {
        & $PythonCommand -m venv $venvPath
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ Ambiente virtual criado com sucesso!" -ForegroundColor Green
            return $true
        } else {
            Write-Host "  ❌ Erro ao criar ambiente virtual" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "  ❌ Erro: $_" -ForegroundColor Red
        return $false
    }
}

# Função para instalar dependências
function Install-Dependencies {
    param([string]$PythonCommand)
    
    Write-Host "[4/7] Instalando dependências Python..." -ForegroundColor Yellow
    
    $venvPath = Join-Path $PSScriptRoot "backend\venv"
    $pipPath = Join-Path $venvPath "Scripts\pip.exe"
    $requirementsPath = Join-Path $PSScriptRoot "requirements.txt"
    
    if (-not (Test-Path $requirementsPath)) {
        Write-Host "  ❌ Arquivo requirements.txt não encontrado!" -ForegroundColor Red
        return $false
    }
    
    if (Test-Path $pipPath) {
        Write-Host "  📦 Usando pip do ambiente virtual..." -ForegroundColor Cyan
        $pipCommand = $pipPath
    } else {
        Write-Host "  📦 Usando pip do sistema..." -ForegroundColor Cyan
        $pipCommand = "$PythonCommand -m pip"
    }
    
    Write-Host "  ⏳ Instalando pacotes (isso pode levar alguns minutos)..." -ForegroundColor Yellow
    Write-Host ""
    
    try {
        if (Test-Path $pipPath) {
            & $pipPath install --upgrade pip
            & $pipPath install -r $requirementsPath
        } else {
            & $PythonCommand -m pip install --upgrade pip
            & $PythonCommand -m pip install -r $requirementsPath
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "  ✅ Dependências instaladas com sucesso!" -ForegroundColor Green
            return $true
        } else {
            Write-Host ""
            Write-Host "  ⚠️ Alguns erros podem ter ocorrido. Verifique acima." -ForegroundColor Yellow
            return $false
        }
    } catch {
        Write-Host ""
        Write-Host "  ❌ Erro ao instalar dependências: $_" -ForegroundColor Red
        return $false
    }
}

# Função para baixar dados do NLTK
function Install-NLTKData {
    param([string]$PythonCommand)
    
    Write-Host "[5/7] Configurando NLTK (opcional)..." -ForegroundColor Yellow
    
    $venvPath = Join-Path $PSScriptRoot "backend\venv"
    $pythonPath = Join-Path $venvPath "Scripts\python.exe"
    
    if (-not (Test-Path $pythonPath)) {
        $pythonPath = $PythonCommand
    }
    
    try {
        Write-Host "  📥 Baixando dados do NLTK (punkt tokenizer)..." -ForegroundColor Cyan
        & $pythonPath -c "import nltk; nltk.download('punkt', quiet=True)" 2>&1 | Out-Null
        Write-Host "  ✅ NLTK configurado!" -ForegroundColor Green
        return $true
    } catch {
        Write-Host "  ⚠️ NLTK não disponível (opcional, não crítico)" -ForegroundColor Yellow
        return $true  # Não é crítico
    }
}

# Função para configurar arquivo .env
function Setup-EnvironmentFile {
    Write-Host "[6/7] Configurando arquivo .env..." -ForegroundColor Yellow
    
    $envPath = Join-Path $PSScriptRoot ".env"
    $envExamplePath = Join-Path $PSScriptRoot "env_example.txt"
    
    if (Test-Path $envPath) {
        Write-Host "  ℹ️ Arquivo .env já existe" -ForegroundColor Cyan
        Write-Host "  🔄 Deseja recriar a partir do template? (s/n): " -NoNewline -ForegroundColor Yellow
        $response = Read-Host
        if ($response -notmatch "^[sS]") {
            Write-Host "  ✅ Mantendo arquivo .env existente" -ForegroundColor Green
            return $true
        }
    }
    
    if (Test-Path $envExamplePath) {
        Copy-Item -Path $envExamplePath -Destination $envPath -Force
        Write-Host "  ✅ Arquivo .env criado a partir do template!" -ForegroundColor Green
        Write-Host ""
        Write-Host "  ⚠️ IMPORTANTE: Edite o arquivo .env e configure:" -ForegroundColor Yellow
        Write-Host "     - OPENAI_API_KEY (obrigatório para IA)" -ForegroundColor Cyan
        Write-Host "     - SECRET_KEY (gere uma chave segura)" -ForegroundColor Cyan
        Write-Host "     - Configurações de email (opcional)" -ForegroundColor Cyan
        Write-Host ""
        return $true
    } else {
        Write-Host "  ⚠️ Arquivo env_example.txt não encontrado" -ForegroundColor Yellow
        Write-Host "  📝 Criando arquivo .env básico..." -ForegroundColor Cyan
        
        $envContent = @"
# Configurações do Chatbot Puerpério
OPENAI_API_KEY=sua_chave_openai_aqui
USE_AI=true

# Configurações do Flask
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=sua-chave-secreta-super-segura-mude-isso-em-producao

# Porta do servidor
PORT=5000

# URL base do aplicativo
BASE_URL=http://localhost:5000
"@
        Set-Content -Path $envPath -Value $envContent -Encoding UTF8
        Write-Host "  ✅ Arquivo .env criado!" -ForegroundColor Green
        return $true
    }
}

# Função para verificar configuração final
function Test-FinalConfiguration {
    param([string]$PythonCommand)
    
    Write-Host "[7/7] Verificando configuração final..." -ForegroundColor Yellow
    
    $venvPath = Join-Path $PSScriptRoot "backend\venv"
    $pythonPath = Join-Path $venvPath "Scripts\python.exe"
    
    if (-not (Test-Path $pythonPath)) {
        $pythonPath = $PythonCommand
    }
    
    $checks = @{
        "Python" = $false
        "Flask" = $false
        "OpenAI" = $false
        "Arquivo .env" = $false
    }
    
    # Verifica Python
    try {
        $version = & $pythonPath --version 2>&1
        if ($version -match "Python") {
            $checks["Python"] = $true
        }
    } catch {}
    
    # Verifica Flask
    try {
        $flaskVersion = & $pythonPath -c "import flask; print(flask.__version__)" 2>&1
        if ($flaskVersion -match "^\d+\.\d+") {
            $checks["Flask"] = $true
        }
    } catch {}
    
    # Verifica OpenAI
    try {
        $openaiVersion = & $pythonPath -c "import openai; print(openai.__version__)" 2>&1
        if ($openaiVersion -match "^\d+\.\d+") {
            $checks["OpenAI"] = $true
        }
    } catch {}
    
    # Verifica .env
    $envPath = Join-Path $PSScriptRoot ".env"
    if (Test-Path $envPath) {
        $checks["Arquivo .env"] = $true
    }
    
    Write-Host ""
    Write-Host "  📊 Resumo da Verificação:" -ForegroundColor Cyan
    foreach ($check in $checks.GetEnumerator()) {
        $status = if ($check.Value) { "✅" } else { "❌" }
        $color = if ($check.Value) { "Green" } else { "Red" }
        Write-Host "     $status $($check.Key)" -ForegroundColor $color
    }
    
    return $checks
}

# ============================================
# EXECUÇÃO PRINCIPAL
# ============================================

Write-Host "Iniciando processo de setup..." -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Python
$pythonCheck = Test-PythonVersion
if (-not $pythonCheck.Success) {
    Write-Host ""
    Write-Host "❌ SETUP INTERROMPIDO: Python não está instalado." -ForegroundColor Red
    Write-Host "   Instale Python 3.11 e execute este script novamente." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Pressione Enter para sair"
    exit 1
}

$pythonCommand = $pythonCheck.Command

# 2. Verificar pip
if (-not (Test-PipVersion -PythonCommand $pythonCommand)) {
    Write-Host ""
    Write-Host "❌ SETUP INTERROMPIDO: pip não está disponível." -ForegroundColor Red
    Write-Host ""
    Read-Host "Pressione Enter para sair"
    exit 1
}

# 3. Criar ambiente virtual
if (-not (New-VirtualEnvironment -PythonCommand $pythonCommand)) {
    Write-Host ""
    Write-Host "❌ SETUP INTERROMPIDO: Erro ao criar ambiente virtual." -ForegroundColor Red
    Write-Host ""
    Read-Host "Pressione Enter para sair"
    exit 1
}

# 4. Instalar dependências
if (-not (Install-Dependencies -PythonCommand $pythonCommand)) {
    Write-Host ""
    Write-Host "⚠️ AVISO: Alguns erros ocorreram durante a instalação." -ForegroundColor Yellow
    Write-Host "   Verifique as mensagens acima e tente novamente se necessário." -ForegroundColor Yellow
    Write-Host ""
}

# 5. Configurar NLTK
Install-NLTKData -PythonCommand $pythonCommand | Out-Null

# 6. Configurar .env
Setup-EnvironmentFile | Out-Null

# 7. Verificação final
$finalCheck = Test-FinalConfiguration -PythonCommand $pythonCommand

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  SETUP CONCLUÍDO!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verifica se tudo está OK
$allOk = $finalCheck.Values | Where-Object { $_ -eq $true } | Measure-Object
if ($allOk.Count -eq $finalCheck.Count) {
    Write-Host "✅ Todas as verificações passaram!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 PRÓXIMOS PASSOS:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Edite o arquivo .env e configure:" -ForegroundColor Cyan
    Write-Host "   - OPENAI_API_KEY (obrigatório)" -ForegroundColor White
    Write-Host "   - SECRET_KEY (gere uma chave segura)" -ForegroundColor White
    Write-Host ""
    Write-Host "2. Para iniciar o servidor, execute:" -ForegroundColor Cyan
    Write-Host "   .\iniciar-servidor.ps1" -ForegroundColor White
    Write-Host "   OU" -ForegroundColor Gray
    Write-Host "   python start.py" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "⚠️ Algumas verificações falharam. Revise os erros acima." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Pressione Enter para sair..." -ForegroundColor Gray
Read-Host
