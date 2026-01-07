<#
.SYNOPSIS
    Batch validates all HTML files in docs/ directory

.DESCRIPTION
    Runs validate-html-structure.ps1 on all HTML files and generates report.
    Use before committing HTML changes to catch issues early.

.PARAMETER Path
    Path to scan (default: docs/)

.PARAMETER Recursive
    Scan subdirectories

.EXAMPLE
    .\validate-all-html.ps1 -Path "docs/" -Recursive

.NOTES
    Author: Asif Hussain
    Version: 1.0.0
#>

param(
    [string]$Path = "docs/",
    [switch]$Recursive
)

$ErrorActionPreference = "Continue"

$BLUE = "`e[94m"
$GREEN = "`e[92m"
$RED = "`e[91m"
$YELLOW = "`e[93m"
$RESET = "`e[0m"

Write-Host "${BLUE}🔍 CORTEX Batch HTML Validator${RESET}" -ForegroundColor Blue
Write-Host "Scanning: $Path`n" -ForegroundColor Cyan

$searchOption = if ($Recursive) { "**/*.html" } else { "*.html" }
$htmlFiles = Get-ChildItem -Path $Path -Filter "*.html" -Recurse:$Recursive | 
    Where-Object { $_.Name -notmatch '\.backup-' } |
    Sort-Object FullName

if ($htmlFiles.Count -eq 0) {
    Write-Host "${YELLOW}No HTML files found${RESET}" -ForegroundColor Yellow
    exit 0
}

Write-Host "Found $($htmlFiles.Count) HTML files`n" -ForegroundColor Cyan

$results = @{
    Passed = @()
    Warnings = @()
    Critical = @()
}

foreach ($file in $htmlFiles) {
    $relativePath = $file.FullName.Replace((Get-Location).Path, "").TrimStart('\', '/')
    Write-Host "Validating: $relativePath" -NoNewline
    
    $output = & "$PSScriptRoot\validate-html-structure.ps1" -FilePath $file.FullName 2>&1
    $exitCode = $LASTEXITCODE
    
    switch ($exitCode) {
        0 { 
            Write-Host " ${GREEN}✅${RESET}" -ForegroundColor Green
            $results.Passed += $relativePath
        }
        1 { 
            Write-Host " ${YELLOW}⚠️${RESET}" -ForegroundColor Yellow
            $results.Warnings += $relativePath
        }
        2 { 
            Write-Host " ${RED}❌${RESET}" -ForegroundColor Red
            $results.Critical += $relativePath
        }
    }
}

# Summary Report
Write-Host "`n${BLUE}═══════════════════════════════════════════════════════${RESET}" -ForegroundColor Blue
Write-Host "${BLUE}                  SUMMARY REPORT${RESET}" -ForegroundColor Blue
Write-Host "${BLUE}═══════════════════════════════════════════════════════${RESET}`n" -ForegroundColor Blue

Write-Host "Total Files Scanned: $($htmlFiles.Count)" -ForegroundColor Cyan
Write-Host "${GREEN}Passed:   $($results.Passed.Count)${RESET}" -ForegroundColor Green
Write-Host "${YELLOW}Warnings: $($results.Warnings.Count)${RESET}" -ForegroundColor Yellow
Write-Host "${RED}Critical: $($results.Critical.Count)${RESET}`n" -ForegroundColor Red

if ($results.Critical.Count -gt 0) {
    Write-Host "${RED}FILES REQUIRING C52 RECONSTRUCTION:${RESET}" -ForegroundColor Red
    foreach ($file in $results.Critical) {
        Write-Host "  ❌ $file" -ForegroundColor Red
    }
    Write-Host ""
}

if ($results.Warnings.Count -gt 0) {
    Write-Host "${YELLOW}FILES WITH WARNINGS:${RESET}" -ForegroundColor Yellow
    foreach ($file in $results.Warnings) {
        Write-Host "  ⚠️  $file" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Exit code
if ($results.Critical.Count -gt 0) {
    Write-Host "${RED}⚠️  ACTION REQUIRED: $($results.Critical.Count) files need reconstruction${RESET}`n" -ForegroundColor Red
    exit 2
} elseif ($results.Warnings.Count -gt 0) {
    Write-Host "${YELLOW}Minor issues detected in $($results.Warnings.Count) files${RESET}`n" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "${GREEN}✅ All HTML files passed validation${RESET}`n" -ForegroundColor Green
    exit 0
}
