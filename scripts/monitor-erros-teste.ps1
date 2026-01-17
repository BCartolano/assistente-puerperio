# Script de Monitoramento - Erros durante Testes Mobile (Tarefas 4 e 5)
# Monitora Broken Pipe, DOM Exceptions e outros erros críticos

Write-Host "🔍 Monitoramento de Erros - Tarefas 4 e 5" -ForegroundColor Cyan
Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Yellow
Write-Host ""

# Monitora múltiplos arquivos de log
$errorLog = "logs\error_debug.log"
$contextLog = "logs\context_metrics.log"
$feedbackLog = "logs\user_feedback.log"

# Cria logs se não existirem
if (-not (Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" -Force | Out-Null }
foreach ($log in @($errorLog, $contextLog, $feedbackLog)) {
    if (-not (Test-Path $log)) { New-Item -ItemType File -Path $log -Force | Out-Null }
}

Write-Host "📋 Monitorando:" -ForegroundColor Green
Write-Host "   - Broken Pipe Errors"
Write-Host "   - DOM Exceptions"
Write-Host "   - Context Tags (cansaço_extremo_critico)"
Write-Host "   - Feedback Log Updates"
Write-Host ""

# Função para verificar erros
function Monitor-Errors {
    $errorPatterns = @(
        "BrokenPipe",
        "Broken Pipe",
        "DOMException",
        "DOM.*Exception",
        "streaming.*error",
        "typewriter.*error",
        "requestAnimationFrame"
    )
    
    # Monitora error_debug.log
    Get-Content $errorLog -Wait -Tail 10 -ErrorAction SilentlyContinue | ForEach-Object {
        foreach ($pattern in $errorPatterns) {
            if ($_ -match $pattern) {
                Write-Host "[ERROR] $_" -ForegroundColor Red
            }
        }
    }
}

# Monitora context_metrics.log para cansaço_extremo_critico
function Monitor-ContextTags {
    Get-Content $contextLog -Wait -Tail 20 -ErrorAction SilentlyContinue | ForEach-Object {
        if ($_ -match "cansaço_extremo_critico") {
            Write-Host "[SUCCESS] ✅ Tag crítica detectada: $_" -ForegroundColor Green
        } elseif ($_ -match "cansaço_extremo") {
            Write-Host "[INFO] Tag detectada: $_" -ForegroundColor Yellow
        }
    }
}

# Monitora feedback log para confirmação de escrita
function Monitor-FeedbackLog {
    $lastSize = 0
    while ($true) {
        if (Test-Path $feedbackLog) {
            $currentSize = (Get-Item $feedbackLog).Length
            if ($currentSize -gt $lastSize) {
                Write-Host "[FEEDBACK] ✅ Log atualizado! Novo tamanho: $currentSize bytes" -ForegroundColor Green
                Write-Host "[FEEDBACK] Últimas linhas:" -ForegroundColor Cyan
                Get-Content $feedbackLog -Tail 5 | ForEach-Object {
                    Write-Host "   $_" -ForegroundColor White
                }
                $lastSize = $currentSize
            }
        }
        Start-Sleep -Seconds 2
    }
}

# Inicia monitoramento em paralelo (simulado via jobs)
Write-Host "🚀 Iniciando monitoramento..." -ForegroundColor Green
Write-Host ""

# Monitora context tags (prioridade alta)
Start-Job -ScriptBlock {
    param($log)
    Get-Content $log -Wait -Tail 20 | ForEach-Object {
        if ($_ -match "cansaço_extremo_critico") {
            Write-Output "[SUCCESS] ✅ $_"
        }
    }
} -ArgumentList $contextLog | Out-Null

# Monitora erros
Start-Job -ScriptBlock {
    param($log)
    Get-Content $log -Wait -Tail 10 | ForEach-Object {
        if ($_ -match "BrokenPipe|DOMException|streaming.*error") {
            Write-Output "[ERROR] ❌ $_"
        }
    }
} -ArgumentList $errorLog | Out-Null

# Monitora feedback log (check periódico)
Write-Host "📊 Verificando feedback log a cada 2 segundos..." -ForegroundColor Cyan
$feedbackWatcher = Start-Job -ScriptBlock {
    param($log)
    $lastSize = 0
    while ($true) {
        if (Test-Path $log) {
            $currentSize = (Get-Item $log).Length
            if ($currentSize -gt $lastSize) {
                Write-Output "[FEEDBACK] ✅ Log atualizado: $currentSize bytes"
                Get-Content $log -Tail 3 | ForEach-Object {
                    Write-Output "   $_"
                }
                $lastSize = $currentSize
            }
        }
        Start-Sleep -Seconds 2
    }
} -ArgumentList $feedbackLog

# Exibe output dos jobs
while ($true) {
    Get-Job | Receive-Job | ForEach-Object {
        Write-Host $_
    }
    Start-Sleep -Seconds 1
}

# Cleanup ao sair
$null = Register-EngineEvent PowerShell.Exiting -Action {
    Get-Job | Stop-Job
    Get-Job | Remove-Job
}
