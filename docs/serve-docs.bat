@echo off
REM ============================================
REM CORTEX MkDocs Server Launcher
REM One-click: Kill existing → Start server → Open browser
REM ============================================

cd /d "%~dp0.."
echo.
echo ========================================
echo   CORTEX Documentation Server
echo ========================================
echo.

REM Kill any existing mkdocs/python processes on port 8000
echo [1/3] Stopping existing server...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

REM Start mkdocs serve in background
echo [2/3] Starting MkDocs server...
start "" /B .venv\Scripts\python.exe -m mkdocs serve --dev-addr 127.0.0.1:8000

REM Wait for server to initialize
timeout /t 3 /nobreak >nul

REM Open default browser
echo [3/3] Opening browser...
start http://127.0.0.1:8000/INDEX/

echo.
echo ========================================
echo   Server running at http://127.0.0.1:8000
echo   Press Ctrl+C in this window to stop
echo ========================================
echo.

REM Keep window open to show server logs
.venv\Scripts\python.exe -m mkdocs serve --dev-addr 127.0.0.1:8000
