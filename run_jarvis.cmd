@echo off
setlocal
cd /d "C:\Javis Command Center\jarvis-command-center"

:: Ensure port 8730 is clean before starting
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8730" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

:: Run the server
".venv\Scripts\python.exe" server.py
