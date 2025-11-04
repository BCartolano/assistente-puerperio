@echo off
chcp 65001 >nul
echo ========================================
echo Iniciando Assistente Puerperio com ngrok
echo ========================================
echo.

REM Verifica se o ngrok está disponível
where ngrok >nul 2>&1
if %errorlevel% equ 0 (
    set NGROK_CMD=ngrok
    echo ✓ ngrok encontrado no PATH
    goto :start_flask
)

REM Tenta encontrar ngrok.exe na pasta do projeto
if exist "%~dp0ngrok.exe" (
    set NGROK_CMD=%~dp0ngrok.exe
    echo ✓ ngrok encontrado na pasta do projeto
    goto :start_flask
)

REM Tenta encontrar na pasta Downloads
if exist "%USERPROFILE%\Downloads\ngrok.exe" (
    set NGROK_CMD=%USERPROFILE%\Downloads\ngrok.exe
    echo ✓ ngrok encontrado na pasta Downloads
    goto :start_flask
)

REM Se não encontrou, mostra mensagem de erro
echo.
echo ❌ ERRO: ngrok não encontrado!
echo.
echo Por favor, instale o ngrok:
echo 1. Baixe de: https://ngrok.com/download
echo 2. Extraia o ngrok.exe
echo 3. Coloque o ngrok.exe nesta pasta OU adicione ao PATH
echo.
echo Veja o guia completo em: COMO_INSTALAR_NGROK.md
echo.
pause
exit /b 1

:start_flask
echo.
echo Iniciando o servidor Flask...
start "Flask Server" cmd /k "cd /d %~dp0 && python start.py"

echo Aguardando o Flask iniciar (5 segundos)...
timeout /t 5 /nobreak >nul

echo.
echo ========================================
echo Iniciando ngrok...
echo O link público será exibido abaixo:
echo ========================================
echo.
echo 📋 COPIAR O LINK: Procure por "Forwarding" abaixo
echo    O link será algo como: https://xxxxx.ngrok.io
echo.
echo ⚠️  Para parar: Pressione Ctrl+C aqui
echo    Depois feche a janela do "Flask Server"
echo.
echo ========================================
echo.

%NGROK_CMD% http 5000
