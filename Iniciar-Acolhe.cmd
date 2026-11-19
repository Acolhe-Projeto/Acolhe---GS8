@echo off
setlocal
cd /d "%~dp0"
if exist .venv\Scripts\python.exe (
    .venv\Scripts\python.exe -m app.launcher
) else (
    python -m app.launcher
)
pause
