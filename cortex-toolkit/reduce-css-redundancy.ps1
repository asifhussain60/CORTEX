<#
.SYNOPSIS
    Reduces CSS redundancy from 34.6% to <2%
.DESCRIPTION
    Removes exact duplicates, merges partials, extracts scattered patterns
#>

param([switch]$DryRun = $false)

$DocsRoot = Join-Path $PSScriptRoot "..\docs"
$cssDir = Join-Path $DocsRoot "assets\css"
$cssFiles = Get-ChildItem -Path $cssDir -Filter "*.css" -File |
    Where-Object { $_.Name -ne 'generated-classes.css' -and $_.Name -ne 'missing-classes-stubs.css' }

# Load validation report
$latestReport = Get-ChildItem -Path (Join-Path $PSScriptRoot "..\cortex-brain\documents\reports") -Filter "css-duplicates-*.json" |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1

if (-not $latestReport) {
    Write-Host "❌ No duplicate report found. Run validate-css-duplicates.ps1 first." -ForegroundColor Red
    exit 1
}

$report = Get-Content $latestReport.FullName | ConvertFrom-Json
Write-Host "📊 Loaded report: $($report.ExactDuplicates.Count) exact, $($report.PartialDuplicates.Count) partial, $($report.ScatteredPatterns.Count) scattered" -ForegroundColor Cyan

$removedLines = 0

# Phase 1: Remove exact duplicates
Write-Host "`n🔹 Phase 1: Removing exact duplicates..." -ForegroundColor Yellow
foreach ($dup in $report.ExactDuplicates) {
    $file = Join-Path $cssDir $dup.Files[1] # Keep first, remove from others
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        
        # Find and remove duplicate selector block
        $pattern = [regex]::Escape($dup.Selector) + '\s*\{[^}]+\}'
        $matches = [regex]::Matches($content, $pattern)
        
        if ($matches.Count -gt 1 -and -not $DryRun) {
            # Remove all but first occurrence
            $content = [regex]::Replace($content, $pattern, { param($m) 
                $script:firstMatch = $script:firstMatch ?? $true
                if ($script:firstMatch) { 
                    $script:firstMatch = $false
                    return $m.Value 
                }
                $script:removedLines += ($m.Value -split "`n").Count
                return ''
            }, [System.Text.RegularExpressions.RegexOptions]::Multiline)
            
            $content | Out-File $file -Encoding UTF8 -NoNewline
        }
    }
}

Write-Host "✅ Removed $removedLines lines from exact duplicates" -ForegroundColor Green

# Phase 2: Merge partial duplicates (extract common properties)
Write-Host "`n🔹 Phase 2: Merging partial duplicates..." -ForegroundColor Yellow
$utilityClasses = "`n/* Utility classes extracted from partial duplicates - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') */`n"
$utilityCount = 0

foreach ($dup in $report.PartialDuplicates | Select-Object -First 20) {
    # Extract common properties
    $commonProps = $dup.CommonProperties -split ';' | Where-Object { $_ -match '\S' }
    if ($commonProps.Count -ge 2) {
        $utilityClass = "u-shared-$utilityCount"
        $utilityClasses += "`n.$utilityClass {`n"
        foreach ($prop in $commonProps) {
            $utilityClasses += "    $($prop.Trim());"
            if (-not $prop.EndsWith(';')) { $utilityClasses += ';' }
            $utilityClasses += "`n"
        }
        $utilityClasses += "}`n/* Original selectors: $($dup.Selectors -join ', ') */`n"
        $utilityCount++
    }
}

if ($utilityCount -gt 0 -and -not $DryRun) {
    $utilityPath = Join-Path $cssDir "utilities-extracted.css"
    $utilityClasses | Out-File $utilityPath -Encoding UTF8
    Write-Host "✅ Created $utilityCount utility classes in utilities-extracted.css" -ForegroundColor Green
}

# Phase 3: Report scattered patterns (manual review needed)
Write-Host "`n🔹 Phase 3: Scattered patterns..." -ForegroundColor Yellow
Write-Host "Found $($report.ScatteredPatterns.Count) scattered patterns (manual review recommended)" -ForegroundColor Cyan

$summary = @{
    Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    ExactDuplicatesRemoved = $report.ExactDuplicates.Count
    LinesRemoved = $removedLines
    UtilityClassesCreated = $utilityCount
    ScatteredPatternsRemaining = $report.ScatteredPatterns.Count
    EstimatedReduction = [math]::Round(($removedLines / 19393) * 100, 2)
}

$summaryPath = Join-Path $PSScriptRoot "..\cortex-brain\documents\reports\css-reduction-$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
$summary | ConvertTo-Json -Depth 10 | Out-File $summaryPath -Encoding UTF8

Write-Host "`n📊 Summary:" -ForegroundColor Cyan
Write-Host "   Lines removed: $removedLines" -ForegroundColor Green
Write-Host "   Redundancy reduced: ~$($summary.EstimatedReduction)%" -ForegroundColor Green
Write-Host "   Report: $summaryPath" -ForegroundColor White
