@echo off
REM Script batch para iniciar o servidor (mais simples que PowerShell)
REM Uso: iniciar.bat

cd /d "%~dp0"
call backend\venv\Scripts\activate.bat
python start.py
pause
