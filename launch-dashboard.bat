@echo off
REM CORTEX Dashboard Launcher
REM Starts HTTP server and opens browser
REM Author: Asif Hussain

echo ================================
echo   CORTEX Dashboard Launcher
echo ================================
echo.

REM Change to dashboard directory (parent of ui/)
cd /d "%~dp0cortex-brain\dashboards"

echo Starting HTTP server on port 8080...
echo Dashboard URL: http://localhost:8080/ui/index.html?source=mock
echo.
echo Press Ctrl+C to stop server
echo.

REM Start server in background
start /B python -m http.server 8080

REM Wait 2 seconds for server to start
timeout /t 2 /nobreak >nul

REM Open browser
start http://localhost:8080/ui/index.html?source=mock

REM Keep window open and show server logs
python -m http.server 8080
