# CORTEX Intelligent UX Dashboard
# PowerShell Setup Script for Windows

Write-Host "🧠 CORTEX Intelligent UX Dashboard - Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check Node.js installation
try {
    $nodeVersion = node -v
    Write-Host "✅ Node.js $nodeVersion detected" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is not installed" -ForegroundColor Red
    Write-Host "   Please install Node.js 18+ from https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Check Node version
$versionNumber = [int]($nodeVersion -replace 'v(\d+).*', '$1')
if ($versionNumber -lt 18) {
    Write-Host "⚠️  Node.js version 18+ required (found: $nodeVersion)" -ForegroundColor Yellow
    Write-Host "   Please upgrade Node.js from https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Install npm dependencies
Write-Host "📦 Installing npm dependencies..." -ForegroundColor Cyan
npm install

# Install Playwright browsers
Write-Host "🌐 Installing Playwright browsers..." -ForegroundColor Cyan
npx playwright install

Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📚 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Start local server:  npm run serve"
Write-Host "   2. Run tests:           npm test"
Write-Host "   3. Test UI mode:        npm run test:ui"
Write-Host ""
Write-Host "🎯 Dashboard: http://localhost:8080/dashboard.html" -ForegroundColor Green
Write-Host ""
