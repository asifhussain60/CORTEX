@echo off
REM ============================================
REM CORTEX GitPages Local Server (Windows)
REM One-click: Kill existing → Start HTTP server → Open browser
REM 
REM Port: 8080 (HTTP)
REM Target: index.html in current directory
REM ============================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ========================================
echo   CORTEX Documentation Server
echo   Platform: Windows
echo   Port: 8080
echo ========================================
echo.

REM Kill any existing HTTP processes on port 8080
echo [1/4] Stopping existing server on port 8080...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8080" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    echo   Stopped process %%a
)
timeout /t 1 /nobreak >nul

REM Check for Python (needed for http.server)
echo [2/4] Checking Python...
where python >nul 2>&1
if errorlevel 1 (
    echo   ERROR: Python not found in PATH
    echo   Please install Python or add to PATH
    pause
    exit /b 1
)
echo   Python OK

REM Start HTTP server with explicit binding (FOREGROUND)
echo [3/4] Starting HTTP server...
echo   URL: http://localhost:8080
echo.
echo ========================================
echo   SERVER RUNNING
echo   
echo   URL: http://localhost:8080
echo   Press Ctrl+C to stop the server
echo ========================================
echo.

REM Open browser first (background, non-blocking)
start "" http://localhost:8080

timeout /t 2 /nobreak >nul

REM Run server in FOREGROUND (this will block)
python -m http.server 8080 --bind 127.0.0.1
