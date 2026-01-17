# Script para Verificar Atualização do Feedback Log
# Usado após teste de feedback no celular

param(
    [switch]$Watch,
    [int]$IntervalSeconds = 2
)

$feedbackLog = "logs\user_feedback.log"

if (-not (Test-Path $feedbackLog)) {
    Write-Host "⚠️ Arquivo $feedbackLog não encontrado!" -ForegroundColor Yellow
    Write-Host "Criando arquivo..." -ForegroundColor Cyan
    New-Item -ItemType File -Path $feedbackLog -Force | Out-Null
}

if ($Watch) {
    Write-Host "👀 Monitorando $feedbackLog..." -ForegroundColor Cyan
    Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Yellow
    Write-Host ""
    
    $lastSize = (Get-Item $feedbackLog).Length
    $lastWriteTime = (Get-Item $feedbackLog).LastWriteTime
    
    while ($true) {
        $currentSize = (Get-Item $feedbackLog).Length
        $currentWriteTime = (Get-Item $feedbackLog).LastWriteTime
        
        if ($currentSize -ne $lastSize -or $currentWriteTime -ne $lastWriteTime) {
            Write-Host "✅ LOG ATUALIZADO!" -ForegroundColor Green
            Write-Host "   Tamanho: $lastSize → $currentSize bytes" -ForegroundColor White
            Write-Host "   Última atualização: $currentWriteTime" -ForegroundColor White
            Write-Host ""
            Write-Host "📄 Conteúdo completo:" -ForegroundColor Cyan
            Write-Host ("=" * 80) -ForegroundColor Gray
            Get-Content $feedbackLog -Raw
            Write-Host ("=" * 80) -ForegroundColor Gray
            
            # Verifica se User-Agent está presente
            $content = Get-Content $feedbackLog -Raw
            if ($content -match "User-Agent:") {
                Write-Host "✅ User-Agent encontrado!" -ForegroundColor Green
            } else {
                Write-Host "⚠️ User-Agent NÃO encontrado!" -ForegroundColor Yellow
            }
            
            $lastSize = $currentSize
            $lastWriteTime = $currentWriteTime
        }
        
        Start-Sleep -Seconds $IntervalSeconds
    }
} else {
    # Verificação única
    Write-Host "📋 Verificando $feedbackLog..." -ForegroundColor Cyan
    Write-Host ""
    
    if ((Get-Item $feedbackLog).Length -eq 0) {
        Write-Host "⚠️ Arquivo está vazio!" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Arquivo tem conteúdo: $((Get-Item $feedbackLog).Length) bytes" -ForegroundColor Green
        Write-Host "   Última atualização: $((Get-Item $feedbackLog).LastWriteTime)" -ForegroundColor White
        Write-Host ""
        Write-Host "📄 Conteúdo:" -ForegroundColor Cyan
        Write-Host ("=" * 80) -ForegroundColor Gray
        Get-Content $feedbackLog -Raw
        Write-Host ("=" * 80) -ForegroundColor Gray
        
        # Verifica User-Agent
        $content = Get-Content $feedbackLog -Raw
        if ($content -match "User-Agent:") {
            Write-Host "✅ User-Agent encontrado!" -ForegroundColor Green
            $content -match "User-Agent: (.+)" | Out-Null
            Write-Host "   Dispositivo: $($matches[1])" -ForegroundColor White
        } else {
            Write-Host "⚠️ User-Agent NÃO encontrado!" -ForegroundColor Yellow
        }
    }
}
