@echo off
setlocal
echo ==============================================================
echo WJC GLOBAL GROUP — JARVIS COMMAND CENTER
echo ==============================================================

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at .venv.
    echo Please run: python -m venv .venv ^&^& .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

echo Starting JARVIS Command Center server...
.venv\Scripts\python.exe server.py

pause
