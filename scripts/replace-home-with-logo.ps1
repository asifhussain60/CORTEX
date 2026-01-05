# Replace Home Nav with CORTEX Logo in Header
# Version: 1.0.0
# Author: CORTEX
# Purpose: Replace Home navigation link with CORTEX logo (200x200px) in all Level 1 views

param(
    [string]$Path = "docs",
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

Write-Host "🔍 Scanning for Home navigation links in headers..." -ForegroundColor Cyan
Write-Host "Path: $Path" -ForegroundColor Gray
Write-Host ""

# Find all HTML files with Home nav
$htmlFiles = Get-ChildItem -Path $Path -Filter "*.html" -Recurse

$filesWithHomeNav = @()

foreach ($file in $htmlFiles) {
    $content = Get-Content -Path $file.FullName -Raw
    
    # Match Home navigation pattern in header
    if ($content -match '<nav class="header-nav">[\s\S]*?<a href="[^"]*" class="nav-link">[\s\S]*?<i class="fas fa-home"></i>[\s\S]*?<span>Home</span>[\s\S]*?</a>[\s\S]*?</nav>') {
        $filesWithHomeNav += $file
        Write-Host "  ✓ Found in: $($file.FullName.Replace($PWD, '.'))" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "  Files found: $($filesWithHomeNav.Count)" -ForegroundColor White
Write-Host ""

if ($filesWithHomeNav.Count -eq 0) {
    Write-Host "✅ No Home navigation links found!" -ForegroundColor Green
    exit 0
}

if ($WhatIf) {
    Write-Host "⚠️  WhatIf mode - No changes made" -ForegroundColor Yellow
    exit 0
}

Write-Host "🔄 Replacing Home nav with CORTEX logo..." -ForegroundColor Cyan

$replacedCount = 0
foreach ($file in $filesWithHomeNav) {
    $content = Get-Content -Path $file.FullName -Raw
    
    # Determine relative path to logo based on file location
    $relativePath = $file.DirectoryName.Replace($PWD, '').Replace('\', '/').TrimStart('/')
    $depth = ($relativePath -split '/').Count - 1
    $logoPath = if ($depth -eq 0) { "assets/images/CORTEX-logo-200.png" } 
                elseif ($depth -eq 1) { "../assets/images/CORTEX-logo-200.png" }
                else { "../../assets/images/CORTEX-logo-200.png" }
    
    # Replace Home nav with logo
    $newContent = $content -replace '<nav class="header-nav">\s*<a href="[^"]*" class="nav-link">\s*<i class="fas fa-home"></i>\s*<span>Home</span>\s*</a>\s*</nav>', @"
<nav class="header-nav">
                <a href="../index.html" class="nav-logo">
                    <img src="$logoPath" alt="CORTEX" class="cortex-logo" />
                </a>
            </nav>
"@
    
    Set-Content -Path $file.FullName -Value $newContent -NoNewline
    $replacedCount++
    
    Write-Host "  ✓ Updated: $($file.FullName.Replace($PWD, '.'))" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Complete! Replaced Home nav in $replacedCount files" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  Note: You need to create the 200x200px logo at docs/assets/images/CORTEX-logo-200.png" -ForegroundColor Yellow
