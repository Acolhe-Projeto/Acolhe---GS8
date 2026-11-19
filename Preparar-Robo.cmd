@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe python -m venv .venv
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m pip install -r robot\requirements.txt
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m robot.setup_local %*
if errorlevel 1 goto failed
echo.
echo Preparacao concluida. Execute Iniciar-Acolhe.cmd para abrir o Acolhe e a IA local.
pause
exit /b 0
:failed
echo Falha na preparacao. Confira a mensagem acima.
pause
exit /b 1
