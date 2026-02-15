# Recria o ambiente virtual (.venv) usando um Python que tenha a biblioteca padrão completa
# (resolve "No module named 'tempfile'" com Python 3.14 incompleto)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location $projectRoot

Write-Host "Projeto: $projectRoot" -ForegroundColor Cyan
Write-Host ""

# Candidatos de Python para testar (em ordem de preferência)
$candidates = @()
if (Get-Command py -ErrorAction SilentlyContinue) {
    try {
        $list = py --list 2>&1
        foreach ($line in $list) {
            if ($line -match "^\s*-V\s+(\d+\.\d+)") { $candidates += $matches[1] }
            if ($line -match "^\s*(\d+\.\d+)\s+")   { $candidates += $matches[1] }
        }
    } catch {}
}
# Garante que 3.12 e 3.11 estão na lista
@("3.12", "3.11", "3.10") | ForEach-Object { if ($_ -notin $candidates) { $candidates += $_ } }

$found = $null
foreach ($ver in $candidates) {
    try {
        $out = py -$ver -c "import tempfile; import sys; print(sys.executable)" 2>&1
        if ($LASTEXITCODE -eq 0 -and $out) {
            $found = $out.Trim()
            Write-Host "Python com tempfile OK: $ver -> $found" -ForegroundColor Green
            break
        }
    } catch {}
}

if (-not $found) {
    # Tenta python/python3 direto
    foreach ($cmd in @("python3", "python")) {
        if (Get-Command $cmd -ErrorAction SilentlyContinue) {
            try {
                $out = & $cmd -c "import tempfile; import sys; print(sys.executable)" 2>&1
                if ($LASTEXITCODE -eq 0 -and $out) {
                    $found = $out.Trim()
                    Write-Host "Python com tempfile OK: $cmd -> $found" -ForegroundColor Green
                    break
                }
            } catch {}
        }
        if ($found) { break }
    }
}

if (-not $found) {
    Write-Host "Nenhum Python com modulo 'tempfile' encontrado." -ForegroundColor Red
    Write-Host "Instale Python 3.12 ou 3.11 em https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Depois execute este script novamente." -ForegroundColor Yellow
    exit 1
}

$venvPath = Join-Path $projectRoot ".venv"
if (Test-Path $venvPath) {
    Write-Host "Removendo .venv antigo..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $venvPath
}

Write-Host "Criando novo .venv com: $found" -ForegroundColor Cyan
& $found -m venv $venvPath
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao criar venv." -ForegroundColor Red
    exit 1
}

$pip = Join-Path $venvPath "Scripts\pip.exe"
if (-not (Test-Path $pip)) { $pip = Join-Path $venvPath "bin\pip" }

Write-Host "Instalando dependencias (requirements.txt)..." -ForegroundColor Cyan
& $pip install -r (Join-Path $projectRoot "requirements.txt") --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "Aviso: pip install retornou erro. Rode manualmente: pip install -r requirements.txt" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Concluido. Ative o ambiente e inicie o app:" -ForegroundColor Green
Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  python start.py" -ForegroundColor White
Write-Host ""
