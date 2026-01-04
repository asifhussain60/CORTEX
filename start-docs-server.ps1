# Start Documentation Server on Port 8000
# Kills any existing process on port 8000 and starts fresh HTTP server

Write-Host "🔍 Checking for processes on port 8000..." -ForegroundColor Cyan

# Find process using port 8000
$processId = (Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue).OwningProcess

if ($processId) {
    Write-Host "⚠️  Found process $processId on port 8000. Killing..." -ForegroundColor Yellow
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    Start-Sleep -Milliseconds 500
    Write-Host "✅ Process killed" -ForegroundColor Green
} else {
    Write-Host "✅ Port 8000 is free" -ForegroundColor Green
}

# Start HTTP server
Write-Host "🚀 Starting HTTP server at http://localhost:8000" -ForegroundColor Cyan
Write-Host "📁 Serving from: D:\PROJECTS\CORTEX\docs" -ForegroundColor Cyan
Write-Host "" -ForegroundColor White
Write-Host "🌐 Open in browser:" -ForegroundColor Green
Write-Host "   http://localhost:8000/architecture/index.html" -ForegroundColor White
Write-Host "" -ForegroundColor White
Write-Host "Press Ctrl+C to stop server" -ForegroundColor Yellow
Write-Host "" -ForegroundColor White

Set-Location "D:\PROJECTS\CORTEX\docs"
python -m http.server 8000
