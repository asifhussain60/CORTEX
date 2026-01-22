@echo off
REM ============================================
REM CORTEX MkDocs Server Launcher (Windows)
REM One-click: Kill existing → Start server → Open browser
REM 
REM Usage: serve-docs.bat
REM For Mac/Linux: Use serve-docs.sh instead
REM ============================================

setlocal enabledelayedexpansion
cd /d "%~dp0.."

echo.
echo ========================================
echo   CORTEX Documentation Server
echo   Platform: Windows
echo ========================================
echo.

REM Detect Python executable
set "PYTHON_EXE=.venv\Scripts\python.exe"
if not exist "!PYTHON_EXE!" (
    set "PYTHON_EXE=python.exe"
)

REM Kill any existing mkdocs/python processes on port 8000
echo [1/4] Stopping existing server on port 8000...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    echo   Stopped process %%a
)
timeout /t 1 /nobreak >nul

REM Verify mkdocs is installed
echo [2/4] Checking dependencies...
"!PYTHON_EXE!" -m pip show mkdocs >nul 2>&1
if errorlevel 1 (
    echo   ERROR: mkdocs not found. Installing...
    "!PYTHON_EXE!" -m pip install mkdocs mkdocs-material >nul 2>&1
    if errorlevel 1 (
        echo   FAILED to install mkdocs. Please run: pip install mkdocs mkdocs-material
        pause
        exit /b 1
    )
)
echo   Dependencies OK

REM Start mkdocs serve in background
echo [3/4] Starting MkDocs server...
start "" /B "!PYTHON_EXE!" -m mkdocs serve --dev-addr 127.0.0.1:8000

REM Wait for server to initialize
timeout /t 3 /nobreak >nul

REM Open default browser
echo [4/4] Opening browser at http://127.0.0.1:8000/
start http://127.0.0.1:8000/INDEX/

echo.
echo ========================================
echo   Server running at http://127.0.0.1:8000
echo   Press Ctrl+C to stop
echo ========================================
echo.

REM Keep window open to show server logs
"!PYTHON_EXE!" -m mkdocs serve --dev-addr 127.0.0.1:8000
