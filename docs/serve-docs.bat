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

REM Start HTTP server with explicit binding
echo [3/4] Starting HTTP server...
echo   URL: http://localhost:8080
echo   Binding: 127.0.0.1 (localhost only)

REM Start in a new window to prevent blocking
start "CORTEX HTTP Server" /MIN python -m http.server 8080 --bind 127.0.0.1

REM Wait for server to initialize (give it time to start)
timeout /t 4 /nobreak >nul

REM Verify server is running
netstat -aon | findstr ":8080" | findstr "LISTENING" >nul 2>&1
if errorlevel 1 (
    echo   ERROR: Server failed to start
    echo   Check if port 8080 is already in use
    pause
    exit /b 1
)
echo   Server started successfully

REM Open default browser
echo [4/4] Opening browser...
start http://localhost:8080

echo.
echo ========================================
echo   SUCCESS: Server running
echo   URL: http://localhost:8080
echo   
echo   To stop: Close the "CORTEX HTTP Server" window
echo   or run: taskkill /F /IM python.exe
echo ========================================
echo.
echo Press any key to close this window (server continues running)...
pause >nul
