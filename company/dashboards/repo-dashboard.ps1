# ============================================================================
# CORTEX Repository Dashboard Launcher
# ============================================================================
# Serves company/dashboards via HTTP on localhost:8080 and opens browser
# 
# Usage: Right-click → Run with PowerShell
#        OR: .\repo-dashboard.ps1
# ============================================================================

$ErrorActionPreference = "Stop"
$Port = 8888
$DashboardDir = $PSScriptRoot

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   CORTEX Repository Dashboard Launcher" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Kill any existing process on port 8080
Write-Host "[1/3] Checking for existing process on port $Port..." -ForegroundColor Yellow

$existingProcess = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | 
    Select-Object -ExpandProperty OwningProcess -Unique

if ($existingProcess) {
    foreach ($pid in $existingProcess) {
        $processName = (Get-Process -Id $pid -ErrorAction SilentlyContinue).ProcessName
        Write-Host "      Killing process: $processName (PID: $pid)" -ForegroundColor Red
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Milliseconds 500
    Write-Host "      Port $Port cleared." -ForegroundColor Green
} else {
    Write-Host "      Port $Port is available." -ForegroundColor Green
}

# Step 2: Start Python HTTP server
Write-Host ""
Write-Host "[2/3] Starting HTTP server on http://localhost:$Port ..." -ForegroundColor Yellow

# Change to dashboard directory
Set-Location $DashboardDir

# Start Python server in background
$serverJob = Start-Job -ScriptBlock {
    param($dir, $port)
    Set-Location $dir
    python -m http.server $port 2>&1
} -ArgumentList $DashboardDir, $Port

Start-Sleep -Seconds 1

# Verify server started
$serverRunning = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue
if ($serverRunning.TcpTestSucceeded) {
    Write-Host "      Server started successfully!" -ForegroundColor Green
} else {
    Write-Host "      Warning: Server may still be starting..." -ForegroundColor Yellow
}

# Step 3: Open browser
Write-Host ""
Write-Host "[3/3] Opening browser..." -ForegroundColor Yellow

$url = "http://localhost:$Port/index.html"
Start-Process $url

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   Dashboard running at: $url" -ForegroundColor White
Write-Host "   Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Keep script running and show server output
Write-Host "Server logs:" -ForegroundColor DarkGray
Write-Host "------------" -ForegroundColor DarkGray

try {
    # Run server in foreground (allows Ctrl+C to stop)
    python -m http.server $Port
}
finally {
    # Cleanup: Stop any background jobs
    Get-Job | Stop-Job -PassThru | Remove-Job -Force -ErrorAction SilentlyContinue
    Write-Host ""
    Write-Host "Server stopped." -ForegroundColor Yellow
}
