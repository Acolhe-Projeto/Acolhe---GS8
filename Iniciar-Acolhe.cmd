@echo off
setlocal
cd /d "%~dp0"
rem Demo completa (IA local + visao): requer .venv preparado por scripts\preparar-demo.ps1
if exist .venv\Scripts\python.exe if exist scripts\iniciar-demo.ps1 (
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\iniciar-demo.ps1"
    goto :fim
)
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe -m app.server
) else (
    python -m app.server
)
:fim
pause
