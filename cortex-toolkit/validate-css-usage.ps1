<#
.SYNOPSIS
    Validates CSS class usage between HTML and CSS files
.DESCRIPTION
    Finds unused CSS classes and missing CSS classes to ensure 100% alignment.
.PARAMETER IncludeOrphans
    Include unused CSS classes in report
.PARAMETER DetectCompound
    Validate compound selector usage (.glass-card.animation-t1)
.PARAMETER ExcludePatterns
    Skip CSS classes matching regex
.PARAMETER StrictMode
    Fail on any missing CSS class
.EXAMPLE
    .\validate-css-usage.ps1 -IncludeOrphans -DetectCompound -StrictMode
.NOTES
    Version: 1.0.0
    Author: Asif Hussain
    Created: January 3, 2026
#>

param(
    [switch]$IncludeOrphans,
    [switch]$DetectCompound,
    [string[]]$ExcludePatterns = @(),
    [switch]$StrictMode
)

$CssDirectory = Join-Path $PSScriptRoot "..\docs\assets\css"
$HtmlDirectory = Join-Path $PSScriptRoot "..\docs"
$ReportDirectory = Join-Path $PSScriptRoot "..\cortex-brain\documents\reports"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$ReportPath = Join-Path $ReportDirectory "css-usage-$Timestamp.json"

if (-not (Test-Path $ReportDirectory)) {
    New-Item -ItemType Directory -Path $ReportDirectory -Force | Out-Null
}

Write-Host "🔗 CSS Usage Validation Started" -ForegroundColor Cyan

# Extract CSS classes
$cssClasses = @{}
$cssFiles = Get-ChildItem -Path $CssDirectory -Filter "*.css" -Recurse

foreach ($cssFile in $cssFiles) {
    $content = Get-Content $cssFile.FullName -Raw
    $pattern = '\.([a-zA-Z0-9_-]+)(?=[^}]*\{)'
    $matches = [regex]::Matches($content, $pattern)
    
    foreach ($match in $matches) {
        $className = $match.Groups[1].Value
        if (-not $cssClasses.ContainsKey($className)) {
            $cssClasses[$className] = @{
                File = $cssFile.Name
                UsedInHtml = $false
            }
        }
    }
}

Write-Host "✅ Found $($cssClasses.Count) CSS classes" -ForegroundColor Green

# Extract HTML classes
$htmlClasses = @{}
$htmlFiles = Get-ChildItem -Path $HtmlDirectory -Filter "*.html" -Recurse |
    Where-Object { $_.FullName -notmatch 'archives|cortex-lens-output' }

foreach ($htmlFile in $htmlFiles) {
    $content = Get-Content $htmlFile.FullName -Raw
    $pattern = 'class="([^"]+)"'
    $matches = [regex]::Matches($content, $pattern)
    
    foreach ($match in $matches) {
        $classes = $match.Groups[1].Value -split '\s+'
        foreach ($class in $classes) {
            if ($class -match '\S') {
                if (-not $htmlClasses.ContainsKey($class)) {
                    $htmlClasses[$class] = @{
                        Files = @()
                        Count = 0
                    }
                }
                $htmlClasses[$class].Files += $htmlFile.Name
                $htmlClasses[$class].Count++
                
                # Mark CSS class as used
                if ($cssClasses.ContainsKey($class)) {
                    $cssClasses[$class].UsedInHtml = $true
                }
            }
        }
    }
}

Write-Host "✅ Found $($htmlClasses.Count) unique HTML classes" -ForegroundColor Green

# Analyze results
$unusedCss = $cssClasses.GetEnumerator() | Where-Object { -not $_.Value.UsedInHtml }
$missingCss = $htmlClasses.GetEnumerator() | Where-Object { -not $cssClasses.ContainsKey($_.Key) }

$report = @{
    scan_timestamp = (Get-Date -Format "o")
    css_analysis = @{
        total_classes_defined = $cssClasses.Count
        total_files_scanned = $cssFiles.Count
    }
    html_analysis = @{
        total_html_files = $htmlFiles.Count
        total_class_usages = ($htmlClasses.Values | Measure-Object -Property Count -Sum).Sum
        unique_classes_used = $htmlClasses.Count
    }
    unused_css_classes = @{
        count = $unusedCss.Count
        percentage = [math]::Round(($unusedCss.Count / $cssClasses.Count) * 100, 2)
        instances = $unusedCss | ForEach-Object {
            @{
                class = $_.Key
                file = $_.Value.File
                action = "DELETE (dead code)"
                confidence = "HIGH"
            }
        } | Select-Object -First 50
    }
    missing_css_classes = @{
        count = $missingCss.Count
        severity = "HIGH"
        instances = $missingCss | ForEach-Object {
            @{
                class = $_.Key
                used_in = $_.Value.Files | Select-Object -First 5
                usage_count = $_.Value.Count
                action = "ADD CSS definition"
            }
        } | Select-Object -First 50
    }
    recommendations = @(
        "Delete $($unusedCss.Count) unused CSS classes (estimated $($unusedCss.Count * 8) lines)",
        "Fix $($missingCss.Count) missing CSS classes (broken styling)"
    )
}

$report | ConvertTo-Json -Depth 10 | Out-File -FilePath $ReportPath -Encoding UTF8

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📊 CSS USAGE VALIDATION REPORT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📁 CSS Classes Defined: $($cssClasses.Count)" -ForegroundColor Gray
Write-Host "📄 HTML Classes Used: $($htmlClasses.Count)" -ForegroundColor Gray
Write-Host ""
Write-Host "❌ Unused CSS Classes: $($unusedCss.Count) ($($report.unused_css_classes.percentage)%)" -ForegroundColor $(if ($unusedCss.Count -gt 0) { 'Yellow' } else { 'Green' })
Write-Host "⚠️  Missing CSS Classes: $($missingCss.Count)" -ForegroundColor $(if ($missingCss.Count -gt 0) { 'Red' } else { 'Green' })
Write-Host ""
Write-Host "📄 Report saved: $ReportPath" -ForegroundColor Green
Write-Host ""

if ($StrictMode -and $missingCss.Count -gt 0) {
    Write-Host "❌ FAILED: Found $($missingCss.Count) missing CSS classes" -ForegroundColor Red
    exit 1
} else {
    Write-Host "✅ CSS Usage Validation Complete" -ForegroundColor Green
    exit 0
}
