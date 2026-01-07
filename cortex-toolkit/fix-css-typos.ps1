<#
.SYNOPSIS
    Fixes 401 CSS class typos
.DESCRIPTION
    Replaces typo classes with suggested correct classes
#>

param([switch]$DryRun = $false)

$DocsRoot = Join-Path $PSScriptRoot "..\docs"
$reportPath = Get-ChildItem -Path (Join-Path $PSScriptRoot "..\cortex-brain\documents\reports") -Filter "missing-css-classes-*.json" |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1

if (-not $reportPath) {
    Write-Host "❌ No report found" -ForegroundColor Red
    exit 1
}

$report = Get-Content $reportPath.FullName | ConvertFrom-Json
$typos = $report.Details.Typos

Write-Host "Found $($typos.PSObject.Properties.Count) typos to fix" -ForegroundColor Cyan

$filesUpdated = 0
$classesFixed = 0

foreach ($typoProperty in $typos.PSObject.Properties) {
    $typo = $typoProperty.Name
    $suggestion = $typoProperty.Value.Suggestion
    $files = $typoProperty.Value.Data.Files
    
    # Skip invalid suggestions
    if ([string]::IsNullOrEmpty($suggestion)) { continue }
    
    Write-Host "  $typo → $suggestion" -ForegroundColor Yellow
    
    foreach ($file in $files) {
        if (-not (Test-Path $file)) { continue }
        
        $content = Get-Content $file -Raw
        $originalContent = $content
        
        # Replace typo with suggestion (word boundary aware)
        $pattern = "\b$([regex]::Escape($typo))\b"
        $content = $content -replace $pattern, $suggestion
        
        if ($content -ne $originalContent -and -not $DryRun) {
            $content | Out-File $file -Encoding UTF8 -NoNewline
            $filesUpdated++
        }
    }
    $classesFixed++
}

if ($DryRun) {
    Write-Host "Would fix $classesFixed typos in multiple files" -ForegroundColor Yellow
} else {
    Write-Host "✅ Fixed $classesFixed typos in $filesUpdated file updates" -ForegroundColor Green
}
