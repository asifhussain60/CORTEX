#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Clean up documentation build artifacts and stale files.

.DESCRIPTION
    Removes mkdocs build output and temporary files from docs directory.
    Useful before rebuilding documentation.

.EXAMPLE
    .\cleanup-docs.ps1
#>

param(
    [switch]$Full,
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"

Write-Host "🧹 Documentation Cleanup" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan

# Paths (relative to project root, one level up from docs)
$projectRoot = Split-Path -Parent (Get-Location)
$buildDir = Join-Path $projectRoot "_build"
$docsDir = Get-Location

# Clean build artifacts
if (Test-Path $buildDir) {
    Write-Host "Removing build directory: $buildDir"
    Remove-Item $buildDir -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "✓ Build directory removed" -ForegroundColor Green
}

# Clean pytest cache
$pytestCache = Join-Path $docsDir "_tests" ".pytest_cache"
if (Test-Path $pytestCache) {
    Write-Host "Removing pytest cache"
    Remove-Item $pytestCache -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "✓ Pytest cache removed" -ForegroundColor Green
}

# Clean pycache
Get-ChildItem -Path $docsDir -Filter "__pycache__" -Recurse -Directory | ForEach-Object {
    Write-Host "Removing pycache: $($_.FullName)"
    Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
}

if ($Full) {
    Write-Host "`nFull cleanup enabled" -ForegroundColor Yellow
    
    # Remove pytest log
    $pytestLog = Join-Path $projectRoot "pytest-docs.log"
    if (Test-Path $pytestLog) {
        Remove-Item $pytestLog -Force -ErrorAction SilentlyContinue
        Write-Host "✓ Pytest log removed" -ForegroundColor Green
    }
}

Write-Host "`n✓ Cleanup complete" -ForegroundColor Green
