<#
.SYNOPSIS
    Automatically extracts inline styles and converts them to CSS classes
.DESCRIPTION
    Scans HTML files for inline style attributes, extracts common patterns,
    generates CSS classes, and replaces inline styles with class references.
.EXAMPLE
    .\fix-inline-styles.ps1 -DryRun
.NOTES
    Version: 1.0.0
    Author: Asif Hussain
    Created: January 3, 2026
#>

param(
    [switch]$DryRun = $false,
    [int]$BatchSize = 50
)

$DocsRoot = Join-Path $PSScriptRoot "..\docs"
$CssFile = Join-Path $DocsRoot "assets\css\generated-classes.css"
$ReportPath = Join-Path $PSScriptRoot "..\cortex-brain\documents\reports\inline-style-fixes-$(Get-Date -Format 'yyyyMMdd_HHmmss').json"

Write-Host "🔧 Inline Style Fixer" -ForegroundColor Cyan
Write-Host "Mode: $(if ($DryRun) { 'DRY RUN' } else { 'EXECUTE' })" -ForegroundColor $(if ($DryRun) { 'Yellow' } else { 'Green' })

# Get all HTML files
$htmlFiles = Get-ChildItem -Path $DocsRoot -Filter "*.html" -Recurse -File |
    Where-Object { $_.FullName -notmatch 'archives|cortex-lens-output' }

Write-Host "📄 Found $($htmlFiles.Count) HTML files" -ForegroundColor Gray

# Track inline styles
$inlineStyles = @{}
$fileChanges = @{}
$totalInlineStylesFound = 0

foreach ($file in $htmlFiles) {
    $content = Get-Content $file.FullName -Raw
    $matches = [regex]::Matches($content, 'style="([^"]+)"')
    
    if ($matches.Count -gt 0) {
        $totalInlineStylesFound += $matches.Count
        $fileChanges[$file.FullName] = @{
            OriginalCount = $matches.Count
            Styles = @()
        }
        
        foreach ($match in $matches) {
            $styleValue = $match.Groups[1].Value
            $fileChanges[$file.FullName].Styles += $styleValue
            
            # Track style patterns
            if (-not $inlineStyles.ContainsKey($styleValue)) {
                $inlineStyles[$styleValue] = @{
                    Count = 0
                    Files = @()
                }
            }
            $inlineStyles[$styleValue].Count++
            if ($inlineStyles[$styleValue].Files -notcontains $file.Name) {
                $inlineStyles[$styleValue].Files += $file.Name
            }
        }
    }
}

Write-Host "🔍 Found $totalInlineStylesFound inline styles in $($fileChanges.Count) files" -ForegroundColor Yellow

# Generate CSS classes for common patterns
$generatedClasses = @()
$classCounter = 1

foreach ($style in $inlineStyles.Keys | Sort-Object { $inlineStyles[$_].Count } -Descending) {
    $count = $inlineStyles[$style].Count
    
    # Only create classes for styles used 2+ times
    if ($count -ge 2) {
        $className = "inline-fix-$classCounter"
        $generatedClasses += @{
            ClassName = $className
            Style = $style
            UsageCount = $count
            Files = $inlineStyles[$style].Files
        }
        $classCounter++
    }
}

Write-Host "✅ Generated $($generatedClasses.Count) CSS classes for common patterns" -ForegroundColor Green

# Generate CSS file content
$cssContent = @"
/* Auto-generated CSS classes from inline styles */
/* Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') */
/* DO NOT EDIT - Use fix-inline-styles.ps1 to regenerate */

"@

foreach ($class in $generatedClasses) {
    $cssContent += "`n.$($class.ClassName) {`n"
    # Parse inline style into individual properties
    $properties = $class.Style -split ';' | Where-Object { $_ -match '\S' }
    foreach ($prop in $properties) {
        $cssContent += "    $prop;`n"
    }
    $cssContent += "}`n"
}

if (-not $DryRun) {
    # Save CSS file
    $cssContent | Out-File $CssFile -Encoding UTF8
    Write-Host "💾 Saved CSS classes to: $CssFile" -ForegroundColor Green
    
    # Update HTML files
    $filesUpdated = 0
    foreach ($filePath in $fileChanges.Keys) {
        $content = Get-Content $filePath -Raw
        $updated = $false
        
        # Replace inline styles with class references
        foreach ($class in $generatedClasses) {
            $pattern = [regex]::Escape("style=`"$($class.Style)`"")
            if ($content -match $pattern) {
                $content = $content -replace $pattern, "class=`"$($class.ClassName)`""
                $updated = $true
            }
        }
        
        if ($updated) {
            $content | Out-File $filePath -Encoding UTF8 -NoNewline
            $filesUpdated++
        }
    }
    
    Write-Host "✅ Updated $filesUpdated files" -ForegroundColor Green
}

# Generate report
$report = @{
    Timestamp = Get-Date -Format 'o'
    DryRun = $DryRun
    TotalInlineStylesFound = $totalInlineStylesFound
    FilesWithInlineStyles = $fileChanges.Count
    GeneratedClasses = $generatedClasses.Count
    FilesUpdated = if ($DryRun) { 0 } else { $filesUpdated }
    TopPatterns = $generatedClasses | Select-Object -First 20
}

$report | ConvertTo-Json -Depth 10 | Out-File $ReportPath -Encoding UTF8
Write-Host "📄 Report saved: $ReportPath" -ForegroundColor Gray

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "   Total inline styles: $totalInlineStylesFound" -ForegroundColor White
Write-Host "   Files affected: $($fileChanges.Count)" -ForegroundColor White
Write-Host "   CSS classes generated: $($generatedClasses.Count)" -ForegroundColor White
if (-not $DryRun) {
    Write-Host "   Files updated: $filesUpdated" -ForegroundColor Green
}
Write-Host "========================================`n" -ForegroundColor Cyan

if ($DryRun) {
    Write-Host "⚠️  DRY RUN - No changes made. Run without -DryRun to apply fixes." -ForegroundColor Yellow
}
