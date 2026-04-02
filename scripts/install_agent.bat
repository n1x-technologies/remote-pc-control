@echo off
REM Install script for Remote PC Agent (Windows)

echo ========================================
echo Remote PC Control - Agent Installation
echo ========================================
echo.

REM Check Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python no esta instalado
    echo Instalalo desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

python --version
echo Python encontrado

REM Check Tailscale
where tailscale >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ADVERTENCIA: Tailscale no esta instalado
    echo Descargalo desde: https://tailscale.com/download
    echo.
    pause
)

echo.
echo Instalando dependencias Python...
pip install -r ..\requirements.txt

echo.
echo Configurando agente...
cd ..\agent
python setup_agent.py

echo.
echo ========================================
echo INSTALACION COMPLETADA
echo ========================================
echo.
echo Para iniciar el agente:
echo   python agent.py
echo.
echo O configura un Scheduled Task para inicio automatico.
echo.
pause
