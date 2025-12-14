# Script de teste para verificar se o encoding UTF-8 está funcionando corretamente
# Uso: .\testar-encoding.ps1

# Configura encoding UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null
$env:PYTHONIOENCODING = "utf-8"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TESTE DE ENCODING UTF-8" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Teste 1: Encoding do PowerShell
Write-Host "Teste 1: Encoding do PowerShell" -ForegroundColor Yellow
Write-Host "  OutputEncoding: $([Console]::OutputEncoding.EncodingName)" -ForegroundColor Gray
Write-Host "  InputEncoding: $([Console]::InputEncoding.EncodingName)" -ForegroundColor Gray
Write-Host "  Code Page: $([Console]::OutputEncoding.CodePage)" -ForegroundColor Gray
Write-Host ""

# Teste 2: Caracteres especiais
Write-Host "Teste 2: Caracteres especiais" -ForegroundColor Yellow
Write-Host "  Acentos: á é í ó ú ã õ ç" -ForegroundColor White
Write-Host "  Maiúsculas: Á É Í Ó Ú Ã Õ Ç" -ForegroundColor White
Write-Host ""

# Teste 3: Emojis
Write-Host "Teste 3: Emojis" -ForegroundColor Yellow
Write-Host "  ✅ ❌ ⚠️ 📋 🔧 🚀 💡 🎯 📊 🔍" -ForegroundColor White
Write-Host ""

# Teste 4: Python
Write-Host "Teste 4: Teste via Python" -ForegroundColor Yellow
$testScriptPath = "test_encoding_temp.py"
$testScriptContent = @'
# -*- coding: utf-8 -*-
import sys
import os

if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

print('Teste de encoding Python:')
print('  Acentos: á é í ó ú ã õ ç')
print('  Maiúsculas: Á É Í Ó Ú Ã Õ Ç')
print('  Emojis: ✅ ❌ ⚠️ 📋 🔧 🚀 💡 🎯 📊 🔍')
print('  Encoding stdout:', sys.stdout.encoding)
print('  PYTHONIOENCODING:', os.getenv('PYTHONIOENCODING', 'não definido'))
'@

try {
    $testScriptContent | Out-File -FilePath $testScriptPath -Encoding UTF8 -NoNewline
    python $testScriptPath
    Remove-Item $testScriptPath -ErrorAction SilentlyContinue
} catch {
    Write-Host "  Erro ao executar teste Python: $_" -ForegroundColor Red
}
Write-Host ""

# Teste 5: Arquivo verificar_config.py
Write-Host "Teste 5: Executando verificar_config.py" -ForegroundColor Yellow
if (Test-Path "verificar_config.py") {
    python verificar_config.py
} else {
    Write-Host "  Arquivo verificar_config.py não encontrado" -ForegroundColor Red
}
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TESTE CONCLUÍDO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Se todos os caracteres apareceram corretamente, o encoding está funcionando!" -ForegroundColor Green
Write-Host "Se aparecerem caracteres estranhos, há problemas de encoding." -ForegroundColor Yellow
