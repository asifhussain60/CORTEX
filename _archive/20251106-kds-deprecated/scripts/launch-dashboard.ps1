# KDS Dashboard - All-in-One Launcher
# Purpose: Start API server and open dashboard with proper cleanup and testing
# Usage: .\launch-dashboard.ps1 [-Port 8765] [-SkipTests]

param(
    [int]$Port = 8765,
    [switch]$SkipTests,
    [switch]$KeepServerRunning
)

$ErrorActionPreference = 'Stop'

Write-Host "🧠 KDS Dashboard - All-in-One Launcher" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host ""

# Paths
$scriptDir = $PSScriptRoot
$kdsRoot = Split-Path $scriptDir -Parent
$dashboardPath = Join-Path $kdsRoot "kds-dashboard.html"
$apiServerScript = Join-Path $scriptDir "dashboard-api-server.ps1"
$testScript = Join-Path $kdsRoot "tests\test-dashboard-api.ps1"

# Verify files exist
if (-not (Test-Path $dashboardPath)) {
    Write-Host "❌ Error: Dashboard not found at $dashboardPath" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $apiServerScript)) {
    Write-Host "❌ Error: API server script not found at $apiServerScript" -ForegroundColor Red
    exit 1
}

# Step 0: Kill any existing API server processes
Write-Host "Step 0/4: Cleaning up existing processes..." -ForegroundColor Cyan

$existingServers = Get-Process -Name pwsh -ErrorAction SilentlyContinue | 
    Where-Object { $_.CommandLine -like "*dashboard-api-server.ps1*" }

if ($existingServers) {
    Write-Host "  Found $($existingServers.Count) existing server process(es)" -ForegroundColor Yellow
    foreach ($proc in $existingServers) {
        Write-Host "  Stopping PID: $($proc.Id)..." -ForegroundColor Gray
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
    Write-Host "  ✅ Cleaned up existing processes" -ForegroundColor Green
} else {
    Write-Host "  ✅ No existing processes found" -ForegroundColor Green
}

# Also check for any process listening on the port
try {
    $listener = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($listener) {
        Write-Host "  Found process listening on port $Port (PID: $($listener.OwningProcess))" -ForegroundColor Yellow
        Stop-Process -Id $listener.OwningProcess -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        Write-Host "  ✅ Freed port $Port" -ForegroundColor Green
    }
} catch {
    # Port is free
}

Write-Host ""

# Step 1: Start API Server in separate visible window
Write-Host "Step 1/4: Starting API Server..." -ForegroundColor Cyan
Write-Host "  Port: $Port" -ForegroundColor Gray
Write-Host "  Mode: Separate PowerShell window (visible)" -ForegroundColor Gray

# Start API server in a new visible PowerShell window
$process = Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd '$kdsRoot'; .\scripts\dashboard-api-server.ps1 -Port $Port" -PassThru

# Wait for server to start
Write-Host "  Waiting for server to initialize..." -ForegroundColor Gray
Start-Sleep -Seconds 3

# Check if process is running
if ($process -and !$process.HasExited) {
    Write-Host "  ✅ API Server started (PID: $($process.Id))" -ForegroundColor Green
} else {
    Write-Host "  ❌ API Server failed to start" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Step 2: Test API Server connectivity
Write-Host "Step 2/4: Testing API Server..." -ForegroundColor Cyan

$apiUrl = "http://localhost:$Port"
$maxRetries = 5
$retryCount = 0
$serverReady = $false

while ($retryCount -lt $maxRetries -and -not $serverReady) {
    try {
        $response = Invoke-WebRequest -Uri "$apiUrl/api/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            $serverReady = $true
            Write-Host "  ✅ API Server is responding (HTTP 200)" -ForegroundColor Green
            
            # Parse response to verify data
            $data = $response.Content | ConvertFrom-Json
            $totalChecks = ($data.categories | ForEach-Object { $_.checks.Count } | Measure-Object -Sum).Sum
            Write-Host "  ✅ Health data loaded: $totalChecks checks across $($data.categories.Count) categories" -ForegroundColor Green
        }
    } catch {
        $retryCount++
        if ($retryCount -lt $maxRetries) {
            Write-Host "  ⏳ Retry $retryCount/$maxRetries..." -ForegroundColor Yellow
            Start-Sleep -Seconds 2
        }
    }
}

if (-not $serverReady) {
    Write-Host "  ❌ API Server not responding after $maxRetries attempts" -ForegroundColor Red
    Write-Host "  Stopping server process..." -ForegroundColor Yellow
    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
    exit 1
}

Write-Host ""

# Step 3: Run comprehensive tests (unless skipped)
if (-not $SkipTests) {
    Write-Host "Step 3/4: Running Dashboard Tests..." -ForegroundColor Cyan
    
    if (Test-Path $testScript) {
        try {
            $testResult = & $testScript -Port $Port
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  ✅ All dashboard tests passed" -ForegroundColor Green
            } else {
                Write-Host "  ⚠️  Some tests failed (continuing anyway)" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "  ⚠️  Test execution error: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  ⚠️  Test script not found at $testScript" -ForegroundColor Yellow
        Write-Host "  Skipping tests..." -ForegroundColor Gray
    }
} else {
    Write-Host "Step 3/4: Skipping Tests (--SkipTests flag)" -ForegroundColor Yellow
}

Write-Host ""

# Step 4: Open Dashboard
Write-Host "Step 4/4: Opening Dashboard..." -ForegroundColor Cyan

$url = "file:///$($dashboardPath.Replace('\', '/'))"
Write-Host "  URL: $url" -ForegroundColor Gray

Start-Process $url

Write-Host "  ✅ Dashboard opened in browser" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host "✅ KDS Dashboard is ready!" -ForegroundColor Green
Write-Host ""
Write-Host "Dashboard:" -ForegroundColor Cyan
Write-Host "  • Opened in your default browser" -ForegroundColor Gray
Write-Host "  • Should show 'Connected' status with green checkmark" -ForegroundColor Gray
Write-Host "  • Click Refresh to reload health checks" -ForegroundColor Gray
Write-Host ""
Write-Host "API Server:" -ForegroundColor Cyan
Write-Host "  • Running on http://localhost:$Port" -ForegroundColor Gray
Write-Host "  • PID: $($process.Id)" -ForegroundColor Gray
Write-Host "  • Running in separate PowerShell window" -ForegroundColor Gray
Write-Host "  • Keep that window open while using dashboard" -ForegroundColor Gray
Write-Host ""
Write-Host "⚠️  IMPORTANT:" -ForegroundColor Yellow
Write-Host "  • NEVER open dashboard without API server running" -ForegroundColor Yellow
Write-Host "  • Always use this script to launch dashboard" -ForegroundColor Yellow
Write-Host "  • Dashboard is NOT functional in disconnected mode" -ForegroundColor Yellow
Write-Host ""
Write-Host "To Stop:" -ForegroundColor Yellow
Write-Host "  • Close the API server PowerShell window, or" -ForegroundColor Gray
Write-Host "  • Press Ctrl+C in the API server window" -ForegroundColor Gray
Write-Host ""
Write-Host "=" * 60 -ForegroundColor Gray
