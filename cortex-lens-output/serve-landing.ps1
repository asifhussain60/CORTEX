# CORTEX Lens - Live Development Server
# Purpose: Serve dashboard with live reload for interactive development
# Author: Asif Hussain
# Date: December 14, 2025

param(
    [string]$Port = "8000",
    [string]$Path = "cortex-lens-output\mock-landing"
)

Write-Host "🧠 CORTEX Lens - Live Development Server" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check if path exists
if (-not (Test-Path $Path)) {
    Write-Host "❌ Error: Path not found: $Path" -ForegroundColor Red
    Write-Host "   Creating directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $Path -Force | Out-Null
}

# Get absolute path
$AbsolutePath = Resolve-Path $Path
Write-Host "📁 Serving from: $AbsolutePath" -ForegroundColor Green
Write-Host "🌐 Server URL: http://localhost:$Port" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Instructions:" -ForegroundColor Yellow
Write-Host "   1. Dashboard will open in your default browser" -ForegroundColor White
Write-Host "   2. Edit HTML/CSS/JS files in the directory" -ForegroundColor White
Write-Host "   3. Refresh browser (F5) to see changes" -ForegroundColor White
Write-Host "   4. Press Ctrl+C to stop server" -ForegroundColor White
Write-Host ""
Write-Host "🔄 Live reload: Browser refresh required (F5)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Start Python HTTP server in new window
try {
    # Check if Python is available
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCmd) {
        Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
        exit 1
    }

    Write-Host "▶️  Starting server in new window on port $Port..." -ForegroundColor Green
    Write-Host ""

    # Open browser after 2 seconds
    Start-Job -ScriptBlock {
        Start-Sleep -Seconds 2
        Start-Process "http://localhost:$using:Port"
    } | Out-Null

    # Start server in new PowerShell window (stays open)
    $serverCommand = "cd '$AbsolutePath'; python -m http.server $Port; Read-Host 'Press Enter to close server'"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $serverCommand

    Write-Host "✅ Server started in new window" -ForegroundColor Green
    Write-Host "🌐 URL: http://localhost:$Port" -ForegroundColor Cyan
    Write-Host "📝 Close the server window to stop" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Press any key to exit this script (server will keep running)..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

} catch {
    Write-Host "❌ Server error: $_" -ForegroundColor Red
}
