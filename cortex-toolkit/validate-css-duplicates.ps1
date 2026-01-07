<#
.SYNOPSIS
    Validates CSS files for duplicate rules across stylesheets
.DESCRIPTION
    Detects exact, partial, and scattered CSS duplicates to eliminate redundancy.
    Calculates redundancy percentage and generates consolidation recommendations.
.PARAMETER Detailed
    Include all duplicate instances in report
.PARAMETER ThresholdPercentage
    Set redundancy alert threshold (default: 5%)
.PARAMETER ExcludeFiles
    Skip specific CSS files
.PARAMETER OutputFormat
    JSON or HTML report (default: JSON)
.EXAMPLE
    .\validate-css-duplicates.ps1 -Detailed -ThresholdPercentage 3
.NOTES
    Version: 1.0.0
    Author: Asif Hussain
    Created: January 3, 2026
#>

param(
    [switch]$Detailed,
    [int]$ThresholdPercentage = 5,
    [string[]]$ExcludeFiles = @(),
    [ValidateSet('JSON', 'HTML')]
    [string]$OutputFormat = 'JSON'
)

# Configuration
$CssDirectory = Join-Path $PSScriptRoot "..\docs\assets\css"
$ReportDirectory = Join-Path $PSScriptRoot "..\cortex-brain\documents\reports"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$ReportPath = Join-Path $ReportDirectory "css-duplicates-$Timestamp.json"

# Ensure report directory exists
if (-not (Test-Path $ReportDirectory)) {
    New-Item -ItemType Directory -Path $ReportDirectory -Force | Out-Null
}

# Helper function to parse CSS file
function Parse-CssFile {
    param(
        [string]$FilePath
    )
    
    $content = Get-Content $FilePath -Raw
    $selectors = @{}
    
    # Simple regex to extract CSS rules (selector { properties })
    $pattern = '([^\{\}]+)\s*\{([^\{\}]+)\}'
    $matches = [regex]::Matches($content, $pattern)
    
    $lineNumber = 1
    foreach ($match in $matches) {
        $selector = $match.Groups[1].Value.Trim()
        $properties = $match.Groups[2].Value.Trim()
        
        # Calculate line number
        $beforeMatch = $content.Substring(0, $match.Index)
        $lineNumber = ($beforeMatch -split "`n").Count
        
        # Parse properties into key-value pairs
        $propHash = @{}
        $propLines = $properties -split ';' | Where-Object { $_ -match '\S' }
        foreach ($propLine in $propLines) {
            if ($propLine -match '^\s*([^:]+)\s*:\s*(.+)\s*$') {
                $propName = $matches[1].Trim()
                $propValue = $matches[2].Trim()
                $propHash[$propName] = $propValue
            }
        }
        
        if ($propHash.Count -gt 0) {
            $selectors[$selector] = @{
                Properties = $propHash
                Line = $lineNumber
                File = Split-Path $FilePath -Leaf
            }
        }
    }
    
    return $selectors
}

# Helper function to compare CSS rules
function Compare-CssRules {
    param(
        [hashtable]$Selector1,
        [hashtable]$Selector2
    )
    
    $props1 = $Selector1.Properties
    $props2 = $Selector2.Properties
    
    # Exact duplicate check
    $props1Keys = $props1.Keys | Sort-Object
    $props2Keys = $props2.Keys | Sort-Object
    
    if (($props1Keys -join ',') -eq ($props2Keys -join ',')) {
        $allMatch = $true
        foreach ($key in $props1Keys) {
            if ($props1[$key] -ne $props2[$key]) {
                $allMatch = $false
                break
            }
        }
        if ($allMatch) {
            return @{ Type = 'Exact'; Overlap = 100 }
        }
    }
    
    # Partial duplicate check
    $commonKeys = $props1Keys | Where-Object { $props2Keys -contains $_ }
    if ($commonKeys.Count -gt 0) {
        $matchingProps = $commonKeys | Where-Object {
            $props1[$_] -eq $props2[$_]
        }
        
        $overlapPercentage = [math]::Round(($matchingProps.Count / [math]::Max($props1.Count, $props2.Count)) * 100, 2)
        
        if ($overlapPercentage -ge 50) {
            return @{
                Type = 'Partial'
                Overlap = $overlapPercentage
                CommonProperties = $matchingProps
                UniqueInSecond = $props2Keys | Where-Object { $props1Keys -notcontains $_ }
            }
        }
    }
    
    return $null
}

# Main execution
Write-Host "🔍 CSS Duplicate Detection Started" -ForegroundColor Cyan
Write-Host "📁 Scanning: $CssDirectory" -ForegroundColor Gray

# Get all CSS files
$cssFiles = Get-ChildItem -Path $CssDirectory -Filter "*.css" -Recurse |
    Where-Object { $ExcludeFiles -notcontains $_.Name }

Write-Host "📄 Found $($cssFiles.Count) CSS files" -ForegroundColor Gray

# Parse all CSS files
$allSelectors = @{}
$totalLines = 0

foreach ($cssFile in $cssFiles) {
    Write-Host "   Parsing: $($cssFile.Name)..." -ForegroundColor DarkGray
    $selectors = Parse-CssFile -FilePath $cssFile.FullName
    
    foreach ($selector in $selectors.Keys) {
        $key = "$($cssFile.Name):$selector"
        $allSelectors[$key] = $selectors[$selector]
    }
    
    $totalLines += (Get-Content $cssFile.FullName).Count
}

Write-Host "✅ Parsed $($allSelectors.Count) CSS selectors" -ForegroundColor Green

# Detect duplicates
$exactDuplicates = @()
$partialDuplicates = @()
$scatteredPatterns = @{}

$selectorKeys = @($allSelectors.Keys)  # Convert to array
Write-Host "🔍 Comparing $($selectorKeys.Count) selectors..." -ForegroundColor Gray

for ($i = 0; $i -lt $selectorKeys.Count; $i++) {
    $key1 = $selectorKeys[$i]
    if (-not $allSelectors.ContainsKey($key1)) { continue }
    
    $selector1 = ($key1 -split ':')[1]
    
    for ($j = $i + 1; $j -lt $selectorKeys.Count; $j++) {
        $key2 = $selectorKeys[$j]
        if (-not $allSelectors.ContainsKey($key2)) { continue }
        
        $selector2 = ($key2 -split ':')[1]
        
        # Check if same selector name
        if ($selector1 -eq $selector2) {
            $comparison = Compare-CssRules -Selector1 $allSelectors[$key1] -Selector2 $allSelectors[$key2]
            
            if ($comparison) {
                if ($comparison.Type -eq 'Exact') {
                    $exactDuplicates += @{
                        Selector = $selector1
                        File1 = $allSelectors[$key1].File
                        Line1 = $allSelectors[$key1].Line
                        File2 = $allSelectors[$key2].File
                        Line2 = $allSelectors[$key2].Line
                        Properties = $allSelectors[$key1].Properties.Keys
                        Action = "DELETE $($allSelectors[$key2].File):$($allSelectors[$key2].Line) instance (duplicate)"
                    }
                } elseif ($comparison.Type -eq 'Partial') {
                    $partialDuplicates += @{
                        Selector = $selector1
                        File1 = $allSelectors[$key1].File
                        Line1 = $allSelectors[$key1].Line
                        File2 = $allSelectors[$key2].File
                        Line2 = $allSelectors[$key2].Line
                        Overlap = $comparison.CommonProperties
                        UniqueInSecond = $comparison.UniqueInSecond
                        OverlapPercentage = $comparison.Overlap
                        Action = "MERGE into $($allSelectors[$key1].File), delete $($allSelectors[$key2].File)"
                    }
                }
            }
        }
    }
    
    # Track scattered patterns (same property:value across different selectors)
    foreach ($prop in $allSelectors[$key1].Properties.Keys) {
        $propValue = $allSelectors[$key1].Properties[$prop]
        $pattern = "$prop : $propValue"
        
        if (-not $scatteredPatterns.ContainsKey($pattern)) {
            $scatteredPatterns[$pattern] = @()
        }
        $scatteredPatterns[$pattern] += @{
            Selector = $selector1
            File = $allSelectors[$key1].File
            Line = $allSelectors[$key1].Line
        }
    }
}

# Filter scattered patterns (only those with 3+ occurrences)
$significantScattered = $scatteredPatterns.GetEnumerator() |
    Where-Object { $_.Value.Count -ge 3 } |
    ForEach-Object {
        @{
            Property = $_.Key
            Occurrences = $_.Value.Count
            Files = ($_.Value | Select-Object -ExpandProperty File -Unique)
            Action = "EXTRACT to utility class"
        }
    }

# Calculate statistics
$exactLines = $exactDuplicates.Count * 5  # Estimate 5 lines per rule
$partialLines = $partialDuplicates.Count * 3  # Estimate 3 lines overlap
$scatteredLines = ($significantScattered | Measure-Object -Property Occurrences -Sum).Sum

$totalRedundantLines = $exactLines + $partialLines + $scatteredLines
$redundancyPercentage = [math]::Round(($totalRedundantLines / $totalLines) * 100, 2)

# Build report
$report = @{
    scan_timestamp = (Get-Date -Format "o")
    files_scanned = $cssFiles.Count
    total_css_lines = $totalLines
    duplicate_analysis = @{
        exact_duplicates = @{
            count = $exactDuplicates.Count
            lines_wasted = $exactLines
            percentage = [math]::Round(($exactLines / $totalLines) * 100, 2)
            instances = if ($Detailed) { $exactDuplicates } else { $exactDuplicates | Select-Object -First 5 }
        }
        partial_duplicates = @{
            count = $partialDuplicates.Count
            overlapping_lines = $partialLines
            percentage = [math]::Round(($partialLines / $totalLines) * 100, 2)
            instances = if ($Detailed) { $partialDuplicates } else { $partialDuplicates | Select-Object -First 5 }
        }
        scattered_duplicates = @{
            count = $significantScattered.Count
            consolidation_potential = $scatteredLines
            percentage = [math]::Round(($scatteredLines / $totalLines) * 100, 2)
            patterns = if ($Detailed) { $significantScattered } else { $significantScattered | Select-Object -First 5 }
        }
    }
    total_redundancy = @{
        lines = $totalRedundantLines
        percentage = $redundancyPercentage
        savings_potential = "~$totalRedundantLines lines, $([math]::Round($totalRedundantLines * 0.03, 0))KB reduction"
    }
    recommendations = @(
        "Delete $($exactDuplicates.Count) exact duplicate rules ($exactLines lines)",
        "Merge $($partialDuplicates.Count) partial duplicates ($partialLines lines consolidated)",
        "Extract $($significantScattered.Count) scattered patterns to utility classes ($scatteredLines lines → $($significantScattered.Count) lines)"
    )
}

# Save report
$report | ConvertTo-Json -Depth 10 | Out-File -FilePath $ReportPath -Encoding UTF8

# Display summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📊 CSS DUPLICATE DETECTION REPORT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📁 Files Scanned: $($cssFiles.Count)" -ForegroundColor Gray
Write-Host "📄 Total CSS Lines: $totalLines" -ForegroundColor Gray
Write-Host ""
Write-Host "🔍 Duplicate Analysis:" -ForegroundColor Yellow
Write-Host "   Exact Duplicates: $($exactDuplicates.Count) ($exactLines lines, $($report.duplicate_analysis.exact_duplicates.percentage)%)" -ForegroundColor $(if ($exactDuplicates.Count -gt 0) { 'Red' } else { 'Green' })
Write-Host "   Partial Duplicates: $($partialDuplicates.Count) ($partialLines lines, $($report.duplicate_analysis.partial_duplicates.percentage)%)" -ForegroundColor $(if ($partialDuplicates.Count -gt 0) { 'Yellow' } else { 'Green' })
Write-Host "   Scattered Patterns: $($significantScattered.Count) ($scatteredLines lines, $($report.duplicate_analysis.scattered_duplicates.percentage)%)" -ForegroundColor $(if ($significantScattered.Count -gt 0) { 'Yellow' } else { 'Green' })
Write-Host ""
Write-Host "💾 Total Redundancy: $totalRedundantLines lines ($redundancyPercentage%)" -ForegroundColor $(if ($redundancyPercentage -gt $ThresholdPercentage) { 'Red' } else { 'Green' })
Write-Host "💰 Savings Potential: $($report.total_redundancy.savings_potential)" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Recommendations:" -ForegroundColor Yellow
foreach ($rec in $report.recommendations) {
    Write-Host "   - $rec" -ForegroundColor Gray
}
Write-Host ""
Write-Host "📄 Report saved: $ReportPath" -ForegroundColor Green
Write-Host ""

if ($redundancyPercentage -gt $ThresholdPercentage) {
    Write-Host "⚠️  WARNING: Redundancy ($redundancyPercentage%) exceeds threshold ($ThresholdPercentage%)" -ForegroundColor Red
    exit 1
} else {
    Write-Host "✅ CSS Duplicate Detection Passed" -ForegroundColor Green
    exit 0
}
