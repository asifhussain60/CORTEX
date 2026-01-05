# Validate Header Consistency Across Level 1 Views
# Version: 1.0.0
# Author: CORTEX
# Purpose: Ensure all Level 1 views have CORTEX logo (no Home nav, no Skip to Content)

param(
    [string]$Path = "docs"
)

$ErrorActionPreference = "Stop"

Write-Host "🔍 Validating header consistency across Level 1 views..." -ForegroundColor Cyan
Write-Host "Path: $Path" -ForegroundColor Gray
Write-Host ""

# Find all HTML files
$htmlFiles = Get-ChildItem -Path $Path -Filter "*.html" -Recurse

$issues = @()
$validFiles = @()

foreach ($file in $htmlFiles) {
    $content = Get-Content -Path $file.FullName -Raw
    $fileIssues = @()
    
    # Check for skip-to-content
    if ($content -match '<a\s+[^>]*class="skip-link"[^>]*>Skip to (main )?content</a>') {
        $fileIssues += "❌ Contains 'Skip to Content' link"
    }
    
    # Check for Home nav (should not exist)
    if ($content -match '<i class="fas fa-home"></i>\s*<span>Home</span>') {
        $fileIssues += "❌ Contains Home navigation (should be logo)"
    }
    
    # Check for CORTEX logo (should exist)
    $hasLogo = $content -match '<img[^>]*class="cortex-logo"[^>]*alt="CORTEX"[^>]*\/>'
    if (-not $hasLogo) {
        $fileIssues += "⚠️  Missing CORTEX logo in header"
    }
    
    if ($fileIssues.Count -gt 0) {
        $issues += [PSCustomObject]@{
            File = $file.FullName.Replace($PWD, '.')
            Issues = $fileIssues
        }
    } else {
        $validFiles += $file
    }
}

Write-Host "📊 Validation Results:" -ForegroundColor Cyan
Write-Host ""

if ($issues.Count -eq 0) {
    Write-Host "✅ All files pass validation!" -ForegroundColor Green
    Write-Host "  Total files checked: $($htmlFiles.Count)" -ForegroundColor White
    Write-Host "  Valid files: $($validFiles.Count)" -ForegroundColor Green
} else {
    Write-Host "⚠️  Found issues in $($issues.Count) files:" -ForegroundColor Yellow
    Write-Host ""
    
    foreach ($issue in $issues) {
        Write-Host "  📄 $($issue.File)" -ForegroundColor White
        foreach ($msg in $issue.Issues) {
            Write-Host "     $msg" -ForegroundColor $(if ($msg -match '^❌') { 'Red' } else { 'Yellow' })
        }
        Write-Host ""
    }
    
    Write-Host "  Total files checked: $($htmlFiles.Count)" -ForegroundColor White
    Write-Host "  Valid files: $($validFiles.Count)" -ForegroundColor Green
    Write-Host "  Files with issues: $($issues.Count)" -ForegroundColor Red
}

Write-Host ""
Write-Host "✅ Validation complete!" -ForegroundColor Cyan

# Exit with error code if issues found
if ($issues.Count -gt 0) {
    exit 1
}
