# MkDocs UTF-8 Encoding Fix
# 
# Set these environment variables before running mkdocs build
# to ensure proper UTF-8 encoding on Windows

$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "✓ UTF-8 environment variables set" -ForegroundColor Green
Write-Host "  PYTHONUTF8=$env:PYTHONUTF8" -ForegroundColor Gray
Write-Host "  PYTHONIOENCODING=$env:PYTHONIOENCODING" -ForegroundColor Gray
Write-Host ""
Write-Host "Now run: mkdocs build --clean" -ForegroundColor Yellow
