<#
.SYNOPSIS
    Removes unused CSS classes from stylesheets
.DESCRIPTION
    Scans HTML files for class usage, identifies unused CSS classes, and removes them
.EXAMPLE
    .\remove-unused-css.ps1 -DryRun
.NOTES
    Version: 1.0.0
    Author: Asif Hussain
    Created: January 3, 2026
#>

param(
    [switch]$DryRun = $false,
    [int]$MinUsageThreshold = 0
)

$DocsRoot = Join-Path $PSScriptRoot "..\docs"
$CssDirectory = Join-Path $DocsRoot "assets\css"
$ReportPath = Join-Path $PSScriptRoot "..\cortex-brain\documents\reports\unused-css-removal-$(Get-Date -Format 'yyyyMMdd_HHmmss').json"

Write-Host "🗑️  Unused CSS Remover" -ForegroundColor Cyan
Write-Host "Mode: $(if ($DryRun) { 'DRY RUN' } else { 'EXECUTE' })" -ForegroundColor $(if ($DryRun) { 'Yellow' } else { 'Green' })

# Get all HTML files and extract used classes
Write-Host "📄 Scanning HTML files for class usage..." -ForegroundColor Gray
$htmlFiles = Get-ChildItem -Path $DocsRoot -Filter "*.html" -Recurse -File |
    Where-Object { $_.FullName -notmatch 'archives|cortex-lens-output' }

$usedClasses = @{}
foreach ($file in $htmlFiles) {
    $content = Get-Content $file.FullName -Raw
    $matches = [regex]::Matches($content, 'class="([^"]+)"')
    
    foreach ($match in $matches) {
        $classes = $match.Groups[1].Value -split '\s+' | Where-Object { $_ -match '\S' }
        foreach ($class in $classes) {
            if (-not $usedClasses.ContainsKey($class)) {
                $usedClasses[$class] = 0
            }
            $usedClasses[$class]++
        }
    }
}

Write-Host "✅ Found $($usedClasses.Count) unique classes used in HTML" -ForegroundColor Green

# Get all CSS files and extract defined classes
Write-Host "📄 Scanning CSS files for class definitions..." -ForegroundColor Gray
$cssFiles = Get-ChildItem -Path $CssDirectory -Filter "*.css" -Recurse

$definedClasses = @{}
foreach ($file in $cssFiles) {
    $content = Get-Content $file.FullName -Raw
    # Match class selectors (simplified - handles .classname and .classname.other)
    $matches = [regex]::Matches($content, '\.([a-zA-Z0-9_-]+)')
    
    foreach ($match in $matches) {
        $className = $match.Groups[1].Value
        if (-not $definedClasses.ContainsKey($className)) {
            $definedClasses[$className] = @{
                File = $file.Name
                Count = 0
            }
        }
        $definedClasses[$className].Count++
    }
}

Write-Host "✅ Found $($definedClasses.Count) unique classes defined in CSS" -ForegroundColor Green

# Find unused classes
$unusedClasses = @()
foreach ($className in $definedClasses.Keys) {
    if (-not $usedClasses.ContainsKey($className)) {
        $unusedClasses += @{
            Class = $className
            File = $definedClasses[$className].File
            DefinitionCount = $definedClasses[$className].Count
        }
    }
}

$unusedClasses = $unusedClasses | Sort-Object File, Class

Write-Host "🔍 Found $($unusedClasses.Count) unused CSS classes" -ForegroundColor Yellow

if (-not $DryRun -and $unusedClasses.Count -gt 0) {
    Write-Host "⚠️  WARNING: Automatic removal of unused CSS is risky!" -ForegroundColor Red
    Write-Host "   Some classes may be used dynamically (JavaScript, pseudo-classes, etc.)" -ForegroundColor Yellow
    Write-Host "   Review the report before proceeding with manual cleanup." -ForegroundColor Yellow
    Write-Host "`n   To proceed anyway, this feature needs additional safety checks." -ForegroundColor Yellow
    Write-Host "   Recommended: Manual review of generated report." -ForegroundColor Yellow
}

# Generate report
$report = @{
    Timestamp = Get-Date -Format 'o'
    DryRun = $DryRun
    UsedClasses = $usedClasses.Count
    DefinedClasses = $definedClasses.Count
    UnusedClasses = $unusedClasses.Count
    UnusedPercentage = [math]::Round(($unusedClasses.Count / $definedClasses.Count) * 100, 2)
    TopUnused = $unusedClasses | Select-Object -First 50
}

$report | ConvertTo-Json -Depth 10 | Out-File $ReportPath -Encoding UTF8
Write-Host "📄 Report saved: $ReportPath" -ForegroundColor Gray

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "   Classes used in HTML: $($usedClasses.Count)" -ForegroundColor White
Write-Host "   Classes defined in CSS: $($definedClasses.Count)" -ForegroundColor White
Write-Host "   Unused classes: $($unusedClasses.Count) ($($report.UnusedPercentage)%)" -ForegroundColor Yellow
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "💡 Recommendation: Review the report before manual cleanup" -ForegroundColor Cyan
Write-Host "   Some 'unused' classes may be used by JavaScript or pseudo-selectors" -ForegroundColor Gray
