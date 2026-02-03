@echo off
REM ============================================================================
REM CORTEX Repository Dashboard Launcher
REM ============================================================================
REM Serves company/dashboards via HTTP on localhost:8080 and opens browser
REM Double-click to run, or execute from command prompt
REM ============================================================================

setlocal enabledelayedexpansion

set PORT=8888
set DASHBOARD_DIR=%~dp0

echo.
echo ============================================================
echo    CORTEX Repository Dashboard Launcher
echo ============================================================
echo.

REM Step 1: Kill any existing process on port 8080
echo [1/3] Checking for existing process on port %PORT%...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%PORT%" ^| findstr "LISTENING"') do (
    echo       Killing process with PID: %%a
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 1 /nobreak >nul
echo       Port %PORT% cleared.

REM Step 2: Change to dashboard directory
cd /d "%DASHBOARD_DIR%"

REM Step 3: Open browser (do this before starting server so it doesn't block)
echo.
echo [2/3] Opening browser...
set URL=http://localhost:%PORT%/index.html
start "" "%URL%"

REM Step 4: Start Python HTTP server (this will block)
echo.
echo [3/3] Starting HTTP server on http://localhost:%PORT% ...
echo.
echo ============================================================
echo    Dashboard running at: %URL%
echo    Press Ctrl+C to stop the server
echo ============================================================
echo.
echo Server logs:
echo ------------

python -m http.server %PORT%

echo.
echo Server stopped.
pause
