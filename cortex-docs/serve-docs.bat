@echo off
REM ============================================
REM CORTEX GitPages Local Server (Windows)
REM Simple HTTP server for static files
REM 
REM Port: 8000 (HTTP) - Changed from 8080 to avoid conflicts
REM Target: index.html in current directory
REM ============================================

setlocal enabledelayedexpansion
cd /d "%~dp0"

echo.
echo ========================================
echo   CORTEX Documentation Server
echo   Platform: Windows
echo   Port: 8000
echo ========================================
echo.

REM Kill any existing HTTP processes on port 8000
echo [1/3] Stopping existing server on port 8000...
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    echo   Stopped process %%a
)
timeout /t 2 /nobreak >nul

REM Check for Python (needed for http.server)
echo [2/3] Checking Python...
where python >nul 2>&1
if errorlevel 1 (
    echo   ERROR: Python not found in PATH
    echo   Please install Python or add to PATH
    pause
    exit /b 1
)
echo   Python OK

REM Start HTTP server (FOREGROUND - no binding restrictions)
echo [3/3] Starting HTTP server...
echo.
echo ========================================
echo   SERVER RUNNING
echo   
echo   URL: http://localhost:8000
echo   Press Ctrl+C to stop the server
echo ========================================
echo.

REM Open browser (background)
start "" http://localhost:8000

timeout /t 2 /nobreak >nul

REM Run server WITHOUT --bind flag (fixes 400 errors)
python -m http.server 8000
