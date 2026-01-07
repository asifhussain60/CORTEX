# Environment Setup Verification Script
# Run this script to verify all prerequisites are installed

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Cortex-SDD Environment Verification" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# Check Node.js
Write-Host "Checking Node.js..." -NoNewline
try {
    $nodeVersion = node --version
    Write-Host " ✅ $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host " ❌ Not installed" -ForegroundColor Red
    Write-Host "   Install from: https://nodejs.org/" -ForegroundColor Yellow
    $allGood = $false
}

# Check npm
Write-Host "Checking npm..." -NoNewline
try {
    $npmVersion = npm --version
    Write-Host " ✅ v$npmVersion" -ForegroundColor Green
} catch {
    Write-Host " ❌ Not installed" -ForegroundColor Red
    $allGood = $false
}

# Check Angular CLI
Write-Host "Checking Angular CLI..." -NoNewline
try {
    $ngVersion = ng version 2>&1 | Select-String "Angular CLI" | Select-Object -First 1
    if ($ngVersion) {
        Write-Host " ✅ Installed" -ForegroundColor Green
    } else {
        throw "Not found"
    }
} catch {
    Write-Host " ❌ Not installed" -ForegroundColor Red
    Write-Host "   Install: npm install -g @angular/cli@19" -ForegroundColor Yellow
    $allGood = $false
}

# Check .NET SDK
Write-Host "Checking .NET SDK..." -NoNewline
try {
    $dotnetVersion = dotnet --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $majorVersion = [int]($dotnetVersion.Split('.')[0])
        if ($majorVersion -ge 9) {
            Write-Host " ✅ v$dotnetVersion" -ForegroundColor Green
        } else {
            Write-Host " ⚠️  v$dotnetVersion (Need 9.0+)" -ForegroundColor Yellow
            Write-Host "   Download from: https://dotnet.microsoft.com/download/dotnet/9.0" -ForegroundColor Yellow
            $allGood = $false
        }
    } else {
        throw "Not found"
    }
} catch {
    Write-Host " ❌ Not installed" -ForegroundColor Red
    Write-Host "   Download from: https://dotnet.microsoft.com/download/dotnet/9.0" -ForegroundColor Yellow
    $allGood = $false
}

# Check Docker (optional)
Write-Host "Checking Docker (optional)..." -NoNewline
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✅ Installed" -ForegroundColor Green
    } else {
        throw "Not found"
    }
} catch {
    Write-Host " ⚠️  Not installed (optional for SQL Server)" -ForegroundColor Yellow
}

# Check SQL Server connectivity (if possible)
Write-Host "Checking SQL Server..." -NoNewline
try {
    $sqlTest = Test-NetConnection -ComputerName localhost -Port 1433 -WarningAction SilentlyContinue
    if ($sqlTest.TcpTestSucceeded) {
        Write-Host " ✅ Running on localhost:1433" -ForegroundColor Green
    } else {
        Write-Host " ⚠️  Not running on localhost:1433" -ForegroundColor Yellow
        Write-Host "   Start SQL Server or run: docker-compose up -d" -ForegroundColor Yellow
    }
} catch {
    Write-Host " ⚠️  Could not check connectivity" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==================================" -ForegroundColor Cyan

if ($allGood) {
    Write-Host "✅ All prerequisites satisfied!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. cd backend && see SETUP.md" -ForegroundColor White
    Write-Host "2. cd frontend && see SETUP.md" -ForegroundColor White
} else {
    Write-Host "❌ Some prerequisites missing" -ForegroundColor Red
    Write-Host ""
    Write-Host "Install missing components and run this script again." -ForegroundColor Yellow
}

Write-Host "==================================" -ForegroundColor Cyan
