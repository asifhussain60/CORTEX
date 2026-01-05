# Remove Skip to Content Links from All HTML Files
# Version: 1.0.0
# Author: CORTEX
# Purpose: Remove accessibility "Skip to main content" links from all HTML files

param(
    [string]$Path = "docs",
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

Write-Host "🔍 Scanning for 'Skip to Content' links..." -ForegroundColor Cyan
Write-Host "Path: $Path" -ForegroundColor Gray
Write-Host ""

# Find all HTML files with skip-to-content links
$htmlFiles = Get-ChildItem -Path $Path -Filter "*.html" -Recurse

$filesWithSkipLinks = @()
$totalMatches = 0

foreach ($file in $htmlFiles) {
    $content = Get-Content -Path $file.FullName -Raw
    
    # Match skip-to-content patterns
    if ($content -match '<a\s+[^>]*class="skip-link"[^>]*>Skip to (main )?content</a>') {
        $filesWithSkipLinks += $file
        $matches = [regex]::Matches($content, '<a\s+[^>]*class="skip-link"[^>]*>Skip to (main )?content</a>')
        $totalMatches += $matches.Count
        
        Write-Host "  ✓ Found in: $($file.FullName.Replace($PWD, '.'))" -ForegroundColor Yellow
        Write-Host "    Matches: $($matches.Count)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "  Files found: $($filesWithSkipLinks.Count)" -ForegroundColor White
Write-Host "  Total matches: $totalMatches" -ForegroundColor White
Write-Host ""

if ($filesWithSkipLinks.Count -eq 0) {
    Write-Host "✅ No skip-to-content links found!" -ForegroundColor Green
    exit 0
}

if ($WhatIf) {
    Write-Host "⚠️  WhatIf mode - No changes made" -ForegroundColor Yellow
    exit 0
}

Write-Host "🔄 Removing skip-to-content links..." -ForegroundColor Cyan

$removedCount = 0
foreach ($file in $filesWithSkipLinks) {
    $content = Get-Content -Path $file.FullName -Raw
    
    # Remove skip-to-content link (with surrounding whitespace)
    $newContent = $content -replace '\s*<a\s+[^>]*class="skip-link"[^>]*>Skip to (main )?content</a>\s*\r?\n', "`n"
    
    # Remove extra blank lines
    $newContent = $newContent -replace '\r?\n\r?\n\r?\n', "`n`n"
    
    Set-Content -Path $file.FullName -Value $newContent -NoNewline
    $removedCount++
    
    Write-Host "  ✓ Removed from: $($file.FullName.Replace($PWD, '.'))" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Complete! Removed skip-to-content links from $removedCount files" -ForegroundColor Green
