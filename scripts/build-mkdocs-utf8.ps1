# MkDocs UTF-8 Build Script
# 
# This script ensures MkDocs builds with proper UTF-8 encoding

# Set UTF-8 environment
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "🚀 Building MkDocs with UTF-8 encoding..." -ForegroundColor Cyan
Write-Host ""

# Clean previous build
if (Test-Path "site") {
    Write-Host "🧹 Cleaning old build..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "site"
}

# Build MkDocs
Write-Host "🔨 Running mkdocs build..." -ForegroundColor Yellow
mkdocs build --clean --strict

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Build successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔍 Running encoding tests..." -ForegroundColor Yellow
    python tests/test_mkdocs_encoding.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ All encoding tests passed!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next: mkdocs serve" -ForegroundColor Cyan
    } else {
        Write-Host ""
        Write-Host "⚠ Some encoding tests failed. Check output above." -ForegroundColor Red
    }
} else {
    Write-Host ""
    Write-Host "❌ Build failed. Check errors above." -ForegroundColor Red
}
