# Cria .env a partir de env.example (sem sobrescrever) e oferece abrir no Notepad
Param(
    [string]$EnvExamplePath = "env.example",
    [string]$EnvPath = ".env"
)

if (-not (Test-Path $EnvExamplePath)) {
    Write-Error "Arquivo '$EnvExamplePath' não encontrado na raiz do projeto."
    exit 1
}

if (-not (Test-Path $EnvPath)) {
    Copy-Item -Path $EnvExamplePath -Destination $EnvPath
    Write-Host "[OK] .env criado a partir de $EnvExamplePath"
} else {
    Write-Host "[INFO] .env já existe; nada a fazer."
}

$answer = Read-Host "Quer abrir o .env no bloco de notas agora? (S/N)"
if ($answer -match '^[sS]') {
    notepad $EnvPath
}
exit 0
