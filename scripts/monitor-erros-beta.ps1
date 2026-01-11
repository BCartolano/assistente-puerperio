# scripts/monitor-erros-beta.ps1
# Monitora logs de erro durante o Beta Fechado
# Filtra apenas erros críticos (500, exceptions, broken pipe)

$logFile = "logs/error_debug.log"

# Garante que a pasta logs existe
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# Garante que o arquivo de log existe
if (-not (Test-Path $logFile)) {
    Write-Host "[INFO] Arquivo $logFile ainda nao foi criado."
    Write-Host "[INFO] Ele sera criado automaticamente quando o backend iniciar ou quando ocorrer um erro 500."
    Write-Host "[INFO] Monitorando pasta logs/ para criacao do arquivo..."
    Write-Host ""
}

Write-Host "============================================================"
Write-Host "MONITOR DE ERROS - BETA FECHADO"
Write-Host "============================================================"
Write-Host "Monitorando: $logFile"
Write-Host "Filtros: ERRO 500, BrokenPipeError, Exceptions criticas"
Write-Host "Pressione Ctrl+C para parar."
Write-Host "============================================================"
Write-Host ""

# Monitora o arquivo em tempo real, filtrando apenas erros críticos
Get-Content $logFile -Wait -Tail 0 -ErrorAction SilentlyContinue | ForEach-Object {
    $line = $_
    
    # Filtra apenas linhas críticas
    if ($line -match "ERRO 500" -or 
        $line -match "BrokenPipeError" -or 
        $line -match "Exception" -or 
        $line -match "Traceback" -or
        $line -match "CRITICAL" -or
        $line -match "ERROR") {
        
        # Destaca erros críticos
        if ($line -match "ERRO 500") {
            Write-Host "[ERRO 500] $line" -ForegroundColor Red
        } elseif ($line -match "BrokenPipeError") {
            Write-Host "[BROKEN PIPE] $line" -ForegroundColor Yellow
        } elseif ($line -match "Exception|Traceback") {
            Write-Host "[EXCEPTION] $line" -ForegroundColor Magenta
        } else {
            Write-Host $line
        }
    }
}
