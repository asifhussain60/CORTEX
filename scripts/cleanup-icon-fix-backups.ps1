# Cleanup Font Awesome Icon Fix Backups
# Removes .bak files created by fix-fontawesome-icons.ps1
# Version: 1.0.0
# Author: Asif Hussain

$ErrorActionPreference = "Stop"

Write-Host "🧹 Font Awesome Icon Fix Backup Cleanup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Get all .bak files
$bakFiles = Get-ChildItem -Path "docs" -Filter "*.bak" -Recurse -File

$totalFiles = $bakFiles.Count

if ($totalFiles -eq 0) {
    Write-Host "✨ No backup files found. Already cleaned!" -ForegroundColor Green
    exit 0
}

Write-Host "Found $totalFiles backup files" -ForegroundColor Yellow
Write-Host ""
Write-Host "⚠️  This will PERMANENTLY delete all .bak files." -ForegroundColor Red
Write-Host "Press ENTER to continue or Ctrl+C to cancel..." -ForegroundColor Yellow
Read-Host

$deletedCount = 0

foreach ($file in $bakFiles) {
    Remove-Item -Path $file.FullName -Force
    $deletedCount++
    Write-Host "🗑️  Deleted: $($file.FullName -replace [regex]::Escape($PWD), '.')" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✨ Cleanup Complete!" -ForegroundColor Green
Write-Host "   Backup files deleted: $deletedCount" -ForegroundColor White
Write-Host ""
