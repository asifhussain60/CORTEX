# CORTEX 4.0 Documentation Server (PowerShell)
# Launches HTTP server and opens browser automatically

$PORT = 8000
$URL = "http://localhost:$PORT"

Write-Host "🚀 CORTEX 4.0 Documentation Server" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Kill any process on port 8000
Write-Host "🔪 Checking port $PORT..." -ForegroundColor Yellow
$processOnPort = Get-NetTCPConnection -LocalPort $PORT -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique

if ($processOnPort) {
    Write-Host "   ✗ Killing process on port $PORT..." -ForegroundColor Red
    $processOnPort | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 2
    Write-Host "   ✅ Port cleared" -ForegroundColor Green
} else {
    Write-Host "   ✓ Port is free" -ForegroundColor Green
}

Write-Host ""
Write-Host "🚀 Starting server on port $PORT..." -ForegroundColor Cyan

# Change to docs directory
$rootDir = Split-Path $PSScriptRoot -Parent
Push-Location "$rootDir\docs"

# Start server in background job
$job = Start-Job -ScriptBlock {
    param($port)
    python -m http.server $port
} -ArgumentList $PORT

# Wait for server to start
Write-Host "⏳ Waiting for server to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

# Check if server is running
$isRunning = $false
for ($i = 0; $i -lt 10; $i++) {
    try {
        $response = Invoke-WebRequest -Uri $URL -Method Head -TimeoutSec 1 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $isRunning = $true
            break
        }
    } catch {
        Start-Sleep -Milliseconds 500
    }
}

if ($isRunning) {
    Write-Host "✅ Server started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📖 Documentation: $URL" -ForegroundColor Cyan
    Write-Host ""
    
    # Open browser
    Write-Host "🌐 Opening browser..." -ForegroundColor Magenta
    Start-Process $URL
    
    Write-Host ""
    Write-Host "⏹️  Press Ctrl+C to stop the server" -ForegroundColor Yellow
    Write-Host ""
    
    # Keep the script running
    try {
        while ($true) {
            Start-Sleep -Seconds 1
        }
    } finally {
        Write-Host ""
        Write-Host "🛑 Stopping server..." -ForegroundColor Red
        Stop-Job -Job $job
        Remove-Job -Job $job
        Pop-Location
        Write-Host "✅ Server stopped" -ForegroundColor Green
    }
} else {
    Write-Host "❌ Failed to start server" -ForegroundColor Red
    Stop-Job -Job $job -ErrorAction SilentlyContinue
    Remove-Job -Job $job -ErrorAction SilentlyContinue
    Pop-Location
    exit 1
}
