#!/usr/bin/env pwsh
# CORTEX Fast Bootstrap Installer for Windows
# Optimized installation: Core packages first, optional later

Write-Host "🧠 CORTEX Fast Bootstrap Installer for Windows" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "🔍 Checking Python installation..." -ForegroundColor Yellow
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python not found. Installing Python 3.12..." -ForegroundColor Red
    winget install Python.Python.3.12
    Write-Host "✅ Python installed" -ForegroundColor Green
} else {
    $pyVersion = python --version
    Write-Host "✅ Python found: $pyVersion" -ForegroundColor Green
}

# Check Git
Write-Host "🔍 Checking Git installation..." -ForegroundColor Yellow
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Git not found. Installing Git..." -ForegroundColor Red
    winget install Git.Git
    Write-Host "✅ Git installed" -ForegroundColor Green
} else {
    $gitVersion = git --version
    Write-Host "✅ Git found: $gitVersion" -ForegroundColor Green
}

Write-Host ""
Write-Host "🗑️  Cleaning up legacy packages from CORTEX 3.9.0..." -ForegroundColor Yellow
Write-Host "   (Removing 67 unused packages, ~780 MB)" -ForegroundColor Gray
Write-Host ""

# Unused packages to remove
$unusedPackages = @(
    'matplotlib', 'Flask', 'networkx',
    'playwright', 'selenium', 'pytest-selenium',
    'PyGithub', 'esprima', 'tree-sitter-languages',
    'python-docx', 'pypdf', 'tomli',
    'pytest-cov', 'pytest-asyncio',
    'scikit-learn', 'numpy', 'send2trash'
)

$removed = 0
foreach ($pkg in $unusedPackages) {
    $checkInstalled = python -m pip show $pkg 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  🗑️  Removing $pkg..." -ForegroundColor Gray -NoNewline
        python -m pip uninstall -y $pkg --quiet 2>$null
        if ($LASTEXITCODE -eq 0) {
            $removed++
            Write-Host " ✅" -ForegroundColor Green
        } else {
            Write-Host " ⚠️  (skipped)" -ForegroundColor Yellow
        }
    }
}

if ($removed -gt 0) {
    Write-Host ""
    Write-Host "✅ Removed $removed unused packages" -ForegroundColor Green
}

Write-Host ""
Write-Host "📦 Installing CORTEX Core Dependencies..." -ForegroundColor Green
Write-Host "   (9 packages, ~20 MB, takes 30-45 seconds)" -ForegroundColor Gray
Write-Host ""

if (Test-Path "cortex-files") {
    cd cortex-files
    
    # Install core dependencies first (fast)
    $coreStart = Get-Date
    python -m pip install --upgrade pip --quiet
    python -m pip install -r requirements.txt
    $coreTime = (Get-Date) - $coreStart
    
    Write-Host ""
    Write-Host "✅ Core dependencies installed in $([math]::Round($coreTime.TotalSeconds, 1)) seconds" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 CORTEX is ready for basic usage!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📋 Next steps:" -ForegroundColor Yellow
    Write-Host "1. Use '/CORTEX setup' in GitHub Copilot Chat"
    Write-Host "2. Start with: '/CORTEX help'"
    Write-Host ""
    Write-Host "⚡ Optional: Install enhanced features (ML token optimization)" -ForegroundColor Yellow
    Write-Host "   Run: pip install -r requirements-optional.txt" -ForegroundColor Gray
    Write-Host "   (Takes ~3 minutes, enables ML-powered context compression)" -ForegroundColor Gray
    Write-Host ""
    
    # Ask if user wants optional features
    $installOptional = Read-Host "Install optional features now? (y/N)"
    if ($installOptional -eq "y" -or $installOptional -eq "Y") {
        Write-Host ""
        Write-Host "📦 Installing optional features..." -ForegroundColor Yellow
        Write-Host "   (3 packages: scikit-learn, numpy, send2trash - ~3 minutes, 205 MB)" -ForegroundColor Gray
        $optionalStart = Get-Date
        python -m pip install -r requirements-optional.txt
        $optionalTime = (Get-Date) - $optionalStart
        Write-Host ""
        Write-Host "✅ Optional features installed in $([math]::Round($optionalTime.TotalMinutes, 1)) minutes" -ForegroundColor Green
        Write-Host "🎉 Full CORTEX installation complete!" -ForegroundColor Cyan
    } else {
        Write-Host ""
        Write-Host "⏩ Skipping optional features (you can install later)" -ForegroundColor Gray
        Write-Host "   To install later: pip install -r requirements-optional.txt" -ForegroundColor Gray
    }
    
    Write-Host ""
    Write-Host "===============================================" -ForegroundColor Cyan
    Write-Host "✅ CORTEX Installation Complete!" -ForegroundColor Green
    Write-Host "===============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Use '/CORTEX' in GitHub Copilot Chat to get started" -ForegroundColor Yellow
    Write-Host ""
    
} else {
    Write-Host "❌ cortex-files directory not found!" -ForegroundColor Red
    Write-Host "   Please extract the CORTEX package first." -ForegroundColor Yellow
}
