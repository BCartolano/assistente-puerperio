# ============================================
# Script de Verificação de Instalação
# ============================================
# Verifica se todas as dependências e configurações
# estão corretas para executar o projeto.
# ============================================

# Configuração de encoding UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  VERIFICAÇÃO DE INSTALAÇÃO" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

$errors = @()
$warnings = @()
$success = @()

# Função para verificar se um comando existe
function Test-Command {
    param([string]$Command)
    $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

# Função para verificar versão
function Test-Version {
    param(
        [string]$Name,
        [string]$Command,
        [string]$VersionPattern = ".*"
    )
    
    Write-Host "[$Name] " -NoNewline -ForegroundColor Yellow
    
    $pythonCommands = @("python", "python3", "py")
    $found = $false
    
    foreach ($cmd in $pythonCommands) {
        if (Test-Command $cmd) {
            try {
                if ($Command -eq "python") {
                    $output = & $cmd --version 2>&1
                } else {
                    $venvPath = Join-Path $PSScriptRoot "backend\venv"
                    $pythonPath = Join-Path $venvPath "Scripts\python.exe"
                    
                    if (Test-Path $pythonPath) {
                        $output = & $pythonPath -c $Command 2>&1
                    } else {
                        $output = & $cmd -c $Command 2>&1
                    }
                }
                
                if ($output -match $VersionPattern -or $LASTEXITCODE -eq 0) {
                    Write-Host "✅ $output" -ForegroundColor Green
                    $script:success += $Name
                    $found = $true
                    break
                }
            } catch {
                continue
            }
        }
    }
    
    if (-not $found) {
        Write-Host "❌ Não encontrado" -ForegroundColor Red
        $script:errors += $Name
    }
}

# 1. Verificar Python
Write-Host "1. Verificando Python..." -ForegroundColor Cyan
Test-Version -Name "Python" -Command "python" -VersionPattern "Python 3\.(8|9|10|11|12)"

# 2. Verificar pip
Write-Host "2. Verificando pip..." -ForegroundColor Cyan
$venvPath = Join-Path $PSScriptRoot "backend\venv"
$pipPath = Join-Path $venvPath "Scripts\pip.exe"

if (Test-Path $pipPath) {
    try {
        $pipVersion = & $pipPath --version 2>&1
        Write-Host "  ✅ pip encontrado: $pipVersion" -ForegroundColor Green
        $success += "pip"
    } catch {
        Write-Host "  ❌ pip não encontrado no ambiente virtual" -ForegroundColor Red
        $errors += "pip"
    }
} else {
    $pythonCommands = @("python", "python3", "py")
    $found = $false
    foreach ($cmd in $pythonCommands) {
        if (Test-Command $cmd) {
            try {
                $pipVersion = & $cmd -m pip --version 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "  ✅ pip encontrado: $pipVersion" -ForegroundColor Green
                    $success += "pip"
                    $found = $true
                    break
                }
            } catch {
                continue
            }
        }
    }
    if (-not $found) {
        Write-Host "  ❌ pip não encontrado" -ForegroundColor Red
        $errors += "pip"
    }
}

# 3. Verificar ambiente virtual
Write-Host "3. Verificando ambiente virtual..." -ForegroundColor Cyan
$venvPython = Join-Path $venvPath "Scripts\python.exe"
if (Test-Path $venvPython) {
    Write-Host "  ✅ Ambiente virtual encontrado em: backend\venv\" -ForegroundColor Green
    $success += "Ambiente Virtual"
} else {
    Write-Host "  ⚠️ Ambiente virtual não encontrado" -ForegroundColor Yellow
    Write-Host "     Execute: python -m venv backend\venv" -ForegroundColor Gray
    $warnings += "Ambiente Virtual"
}

# 4. Verificar dependências principais
Write-Host "4. Verificando dependências Python..." -ForegroundColor Cyan

$dependencies = @{
    "Flask" = "import flask; print(flask.__version__)"
    "OpenAI" = "import openai; print(openai.__version__)"
    "python-dotenv" = "import dotenv; print('OK')"
    "flask-login" = "import flask_login; print('OK')"
    "bcrypt" = "import bcrypt; print('OK')"
    "flask-mail" = "import flask_mail; print('OK')"
    "NLTK" = "import nltk; print('OK')"
    "flask-compress" = "import flask_compress; print('OK')"
}

$pythonPath = $venvPython
if (-not (Test-Path $pythonPath)) {
    $pythonCommands = @("python", "python3", "py")
    foreach ($cmd in $pythonCommands) {
        if (Test-Command $cmd) {
            $pythonPath = $cmd
            break
        }
    }
}

foreach ($dep in $dependencies.GetEnumerator()) {
    Write-Host "  [$($dep.Key)] " -NoNewline -ForegroundColor Yellow
    try {
        $output = & $pythonPath -c $dep.Value 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Instalado" -ForegroundColor Green
            $success += $dep.Key
        } else {
            Write-Host "❌ Não instalado" -ForegroundColor Red
            if ($dep.Key -eq "NLTK" -or $dep.Key -eq "flask-compress") {
                $warnings += $dep.Key
            } else {
                $errors += $dep.Key
            }
        }
    } catch {
        Write-Host "❌ Não instalado" -ForegroundColor Red
        if ($dep.Key -eq "NLTK" -or $dep.Key -eq "flask-compress") {
            $warnings += $dep.Key
        } else {
            $errors += $dep.Key
        }
    }
}

# 5. Verificar arquivo .env
Write-Host "5. Verificando arquivo .env..." -ForegroundColor Cyan
$envPath = Join-Path $PSScriptRoot ".env"
if (Test-Path $envPath) {
    Write-Host "  ✅ Arquivo .env encontrado" -ForegroundColor Green
    $success += ".env"
    
    # Verificar variáveis importantes
    $envContent = Get-Content $envPath -Raw
    $requiredVars = @("OPENAI_API_KEY", "SECRET_KEY")
    $missingVars = @()
    
    foreach ($var in $requiredVars) {
        if ($envContent -notmatch "$var\s*=" -or $envContent -match "$var\s*=\s*(sua_|sua-|your_)") {
            $missingVars += $var
        }
    }
    
    if ($missingVars.Count -gt 0) {
        Write-Host "  ⚠️ Variáveis não configuradas: $($missingVars -join ', ')" -ForegroundColor Yellow
        $warnings += "Variáveis .env"
    } else {
        Write-Host "  ✅ Variáveis importantes configuradas" -ForegroundColor Green
    }
} else {
    Write-Host "  ❌ Arquivo .env não encontrado" -ForegroundColor Red
    Write-Host "     Execute: Copy-Item .env.example .env" -ForegroundColor Gray
    $errors += ".env"
}

# 6. Verificar arquivo requirements.txt
Write-Host "6. Verificando requirements.txt..." -ForegroundColor Cyan
$requirementsPath = Join-Path $PSScriptRoot "requirements.txt"
if (Test-Path $requirementsPath) {
    Write-Host "  ✅ requirements.txt encontrado" -ForegroundColor Green
    $success += "requirements.txt"
} else {
    Write-Host "  ❌ requirements.txt não encontrado" -ForegroundColor Red
    $errors += "requirements.txt"
}

# 7. Verificar estrutura de diretórios
Write-Host "7. Verificando estrutura de diretórios..." -ForegroundColor Cyan
$requiredDirs = @("backend", "backend\templates", "backend\static", "dados")
$allDirsOk = $true

foreach ($dir in $requiredDirs) {
    $dirPath = Join-Path $PSScriptRoot $dir
    if (Test-Path $dirPath) {
        Write-Host "  ✅ $dir" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $dir não encontrado" -ForegroundColor Red
        $allDirsOk = $false
    }
}

if ($allDirsOk) {
    $success += "Estrutura de Diretórios"
} else {
    $errors += "Estrutura de Diretórios"
}

# Resumo
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  RESUMO DA VERIFICAÇÃO" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

if ($success.Count -gt 0) {
    Write-Host "✅ Verificações bem-sucedidas ($($success.Count)):" -ForegroundColor Green
    foreach ($item in $success) {
        Write-Host "   - $item" -ForegroundColor Gray
    }
    Write-Host ""
}

if ($warnings.Count -gt 0) {
    Write-Host "⚠️ Avisos ($($warnings.Count)):" -ForegroundColor Yellow
    foreach ($item in $warnings) {
        Write-Host "   - $item" -ForegroundColor Gray
    }
    Write-Host ""
}

if ($errors.Count -gt 0) {
    Write-Host "❌ Erros encontrados ($($errors.Count)):" -ForegroundColor Red
    foreach ($item in $errors) {
        Write-Host "   - $item" -ForegroundColor Gray
    }
    Write-Host ""
    Write-Host "Execute o script de setup para corrigir:" -ForegroundColor Yellow
    Write-Host "  .\setup-ambiente.ps1" -ForegroundColor Cyan
    Write-Host ""
    exit 1
} else {
    Write-Host "✅ Todas as verificações críticas passaram!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Você pode iniciar o servidor com:" -ForegroundColor Cyan
    Write-Host "   .\iniciar-servidor.ps1" -ForegroundColor White
    Write-Host "   OU" -ForegroundColor Gray
    Write-Host "   python start.py" -ForegroundColor White
    Write-Host ""
    exit 0
}
