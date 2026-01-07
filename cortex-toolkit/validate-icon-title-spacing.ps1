<#
.SYNOPSIS
    Validates and fixes icon-title spacing patterns across HTML/CSS files

.DESCRIPTION
    Detects icon-title pairs that are incorrectly formatted:
    - Icons on separate lines from text (should be inline)
    - Incorrect gap spacing in CSS (should be var(--spacing-sm))
    - Missing flex display properties for icon containers
    
    Enforces glassmorphism design standard v4.2.5+ icon-title rules

.PARAMETER DetectOnly
    Only detect issues without fixing them

.PARAMETER AutoFix
    Automatically fix detected issues

.PARAMETER ReportPath
    Path to save the validation report (default: cortex-brain/documents/reports/)

.EXAMPLE
    .\validate-icon-title-spacing.ps1 -DetectOnly
    .\validate-icon-title-spacing.ps1 -AutoFix

.NOTES
    Author: Asif Hussain
    Version: 1.0.0
    Compliance: glassmorphism-design-standard.md v4.2.5+
#>

param(
    [switch]$DetectOnly,
    [switch]$AutoFix,
    [string]$ReportPath = "cortex-brain\documents\reports\icon-title-spacing-validation.json"
)

$ErrorActionPreference = "Stop"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

# Configuration
$docsPath = "docs"
$cssPath = "docs\assets\css"
$backupPath = "backups\icon-title-fix-$timestamp"

# Classes that should have icon-title patterns
$targetClasses = @(
    ".section-title",
    ".page-title",
    ".tier-header",
    ".capability-tile",
    ".principles-header",
    ".card-header",
    ".feature-header",
    ".subsection-title"
)

# Expected CSS gap value
$expectedGap = "var(--spacing-sm)"

Write-Host "`n🔍 CORTEX Icon-Title Spacing Validator v1.0.0" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Results tracking
$results = @{
    timestamp = $timestamp
    htmlIssues = @()
    cssIssues = @()
    summary = @{
        htmlFilesScanned = 0
        cssFilesScanned = 0
        totalIssues = 0
        fixedIssues = 0
    }
}

#region HTML Pattern Detection

Write-Host "`n📄 Scanning HTML files for icon-title pattern issues..." -ForegroundColor Yellow

$htmlFiles = Get-ChildItem -Path $docsPath -Filter "*.html" -Recurse
$results.summary.htmlFilesScanned = $htmlFiles.Count

foreach ($file in $htmlFiles) {
    $content = Get-Content $file.FullName -Raw
    $lines = Get-Content $file.FullName
    
    # Pattern 1: Icon on separate line from title text
    # Bad:  <h2 class="section-title">
    #           <i class="fas fa-icon"></i>
    #           Title Text
    #       </h2>
    
    $pattern1 = '(<h[1-6][^>]*(?:section-title|page-title|principles-header)[^>]*>)\s*\n\s*(<i class="[^"]*"><\/i>)\s*\n\s*([^<\n]+)\s*\n\s*(<\/h[1-6]>)'
    
    if ($content -match $pattern1) {
        $matches = [regex]::Matches($content, $pattern1)
        
        foreach ($match in $matches) {
            $lineNumber = ($content.Substring(0, $match.Index) -split "`n").Count
            
            $issue = @{
                file = $file.FullName.Replace("$PWD\", "")
                line = $lineNumber
                type = "ICON_SEPARATE_LINE"
                severity = "HIGH"
                current = $match.Value -replace '\n', ' '
                expected = "$($match.Groups[1].Value)$($match.Groups[2].Value) $($match.Groups[3].Value.Trim())$($match.Groups[4].Value)"
                description = "Icon and title text on separate lines (should be inline)"
            }
            
            $results.htmlIssues += $issue
            $results.summary.totalIssues++
            
            Write-Host "  ❌ $($issue.file):$($issue.line) - Icon on separate line" -ForegroundColor Red
        }
    }
    
    # Pattern 2: tier-header with nested div instead of tier-title-group
    # Bad:  <div class="tier-header">
    #           <span class="tier-icon">emoji</span> OR <div class="card-icon">...</div>
    #           <div>
    #               <div class="tier-title">...</div> OR <h3 class="card-title">...</h3>
    #               <div class="tier-subtitle">...</div> OR <p class="card-subtitle">...</p>
    #           </div>
    #       </div>
    # Good: Same but with <div class="tier-title-group"> instead of plain <div>
    
    # Find all tier-header blocks
    $tierHeaderPattern = '(?s)<div class="tier-header">(.*?)</div>\s*(?=</div>|<p>|<div class="capability)'
    $tierHeaders = [regex]::Matches($content, $tierHeaderPattern)
    
    foreach ($tierHeader in $tierHeaders) {
        # Check if it has an icon (span or div) followed by plain <div> (not tier-title-group)
        # Must have either tier-title/card-title inside
        if ($tierHeader.Value -match '<(?:span class="tier-icon"|div class="card-icon)' -and 
            $tierHeader.Value -match '<div>\s*<(?:div class="tier-title"|h3 class="card-title")' -and
            $tierHeader.Value -notmatch 'tier-title-group') {
            
            $lineNumber = ($content.Substring(0, $tierHeader.Index) -split "`n").Count
            
            $issue = @{
                file = $file.FullName.Replace("$PWD\", "")
                line = $lineNumber
                type = "TIER_HEADER_MISSING_WRAPPER"
                severity = "HIGH"
                current = $tierHeader.Value.Substring(0, [Math]::Min(200, $tierHeader.Value.Length))
                expected = "Add tier-title-group class to the div after icon element"
                description = "tier-header missing tier-title-group wrapper class"
            }
            
            $results.htmlIssues += $issue
            $results.summary.totalIssues++
            
            Write-Host "  ❌ $($issue.file):$($issue.line) - tier-header missing wrapper" -ForegroundColor Red
        }
    }
}

#endregion

#region CSS Gap Detection

Write-Host "`n🎨 Scanning CSS files for incorrect gap values..." -ForegroundColor Yellow

$cssFiles = Get-ChildItem -Path $cssPath -Filter "*.css" -Recurse
$results.summary.cssFilesScanned = $cssFiles.Count

foreach ($file in $cssFiles) {
    $content = Get-Content $file.FullName -Raw
    
    foreach ($className in $targetClasses) {
        # Find the class definition
        $classPattern = "($className\s*\{[^}]+\})"
        
        if ($content -match $classPattern) {
            $classBlock = $Matches[1]
            
            # Check if gap property exists and has wrong value
            if ($classBlock -match 'gap:\s*([^;]+);') {
                $currentGap = $Matches[1].Trim()
                
                if ($currentGap -ne $expectedGap) {
                    $lineNumber = ($content.Substring(0, $content.IndexOf($classBlock)) -split "`n").Count
                    
                    $issue = @{
                        file = $file.FullName.Replace("$PWD\", "")
                        line = $lineNumber
                        class = $className
                        type = "INCORRECT_GAP"
                        severity = "MEDIUM"
                        current = $currentGap
                        expected = $expectedGap
                        description = "Gap should be $expectedGap for icon-title coupling"
                    }
                    
                    $results.cssIssues += $issue
                    $results.summary.totalIssues++
                    
                    Write-Host "  ❌ $($issue.file):$($issue.line) - $className gap: $currentGap → $expectedGap" -ForegroundColor Red
                }
            }
            # Check if gap is missing entirely
            elseif ($classBlock -match 'display:\s*flex' -and $classBlock -notmatch 'gap:') {
                $lineNumber = ($content.Substring(0, $content.IndexOf($classBlock)) -split "`n").Count
                
                $issue = @{
                    file = $file.FullName.Replace("$PWD\", "")
                    line = $lineNumber
                    class = $className
                    type = "MISSING_GAP"
                    severity = "HIGH"
                    current = "none"
                    expected = $expectedGap
                    description = "Missing gap property for flex layout"
                }
                
                $results.cssIssues += $issue
                $results.summary.totalIssues++
                
                Write-Host "  ❌ $($issue.file):$($issue.line) - $className missing gap property" -ForegroundColor Red
            }
        }
    }
}

#endregion

#region Auto-Fix

if ($AutoFix -and $results.summary.totalIssues -gt 0) {
    Write-Host "`n🔧 Applying automatic fixes..." -ForegroundColor Yellow
    
    # Create backup
    if (-not (Test-Path $backupPath)) {
        New-Item -ItemType Directory -Path $backupPath -Force | Out-Null
    }
    
    # Fix HTML issues
    foreach ($issue in $results.htmlIssues) {
        $file = Join-Path $PWD $issue.file
        
        # Backup
        $backupFile = Join-Path $backupPath ($issue.file -replace '[\\\/]', '_')
        if (-not (Test-Path $backupFile)) {
            Copy-Item $file $backupFile -Force
        }
        
        $content = Get-Content $file -Raw
        
        if ($issue.type -eq "ICON_SEPARATE_LINE") {
            # Fix inline title pattern
            # Use the regex pattern directly instead of escaping the "current" value
            $pattern = '(<h[1-6][^>]*(?:section-title|page-title|principles-header)[^>]*>)\s*\n\s*(<i class="[^"]*"><\/i>)\s*\n\s*([^<\n]+)\s*\n\s*(<\/h[1-6]>)'
            
            $content = [regex]::Replace($content, $pattern, {
                param($match)
                return "$($match.Groups[1].Value)$($match.Groups[2].Value) $($match.Groups[3].Value.Trim())$($match.Groups[4].Value)"
            })
            
            Set-Content $file $content -NoNewline
            
            $results.summary.fixedIssues++
            Write-Host "  ✅ Fixed: $($issue.file)" -ForegroundColor Green
        }
        elseif ($issue.type -eq "TIER_HEADER_MISSING_WRAPPER") {
            # Fix tier-header wrapper pattern
            # Find tier-header blocks and replace plain <div> after icon with <div class="tier-title-group">
            
            # Pattern: icon element followed by <div> (not tier-title-group) containing title/subtitle
            $tierHeaderPattern = '(?s)(<div class="tier-header">.*?<(?:span class="tier-icon"|div class="card-icon[^"]*")[^>]*>.*?</(?:span|div)>)\s*(<div>)\s*(<(?:div class="tier-title"|h3 class="card-title"))'
            
            $content = [regex]::Replace($content, $tierHeaderPattern, {
                param($match)
                # Replace plain <div> with <div class="tier-title-group">
                return "$($match.Groups[1].Value) <div class=""tier-title-group""> $($match.Groups[3].Value)"
            })
            
            Set-Content $file $content -NoNewline
            
            $results.summary.fixedIssues++
            Write-Host "  ✅ Fixed: $($issue.file) - Added tier-title-group wrapper" -ForegroundColor Green
        }
    }
    
    # Fix CSS issues
    foreach ($issue in $results.cssIssues) {
        $file = Join-Path $PWD $issue.file
        
        # Backup
        $backupFile = Join-Path $backupPath ($issue.file -replace '[\\\/]', '_')
        if (-not (Test-Path $backupFile)) {
            Copy-Item $file $backupFile -Force
        }
        
        $content = Get-Content $file -Raw
        
        if ($issue.type -eq "INCORRECT_GAP") {
            # Replace gap value
            $pattern = "($($issue.class)\s*\{[^}]*gap:\s*)$($issue.current)(\s*;)"
            $replacement = "`${1}$expectedGap`${2}"
            $content = $content -replace $pattern, $replacement
        }
        elseif ($issue.type -eq "MISSING_GAP") {
            # Add gap property after display: flex
            $pattern = "($($issue.class)\s*\{[^}]*display:\s*flex\s*;)"
            $replacement = "`${1}`n    gap: $expectedGap;"
            $content = $content -replace $pattern, $replacement
        }
        
        Set-Content $file $content -NoNewline
        $results.summary.fixedIssues++
        Write-Host "  ✅ Fixed: $($issue.file) - $($issue.class)" -ForegroundColor Green
    }
    
    Write-Host "`n💾 Backup created: $backupPath" -ForegroundColor Cyan
}

#endregion

#region Summary Report

Write-Host "`n📊 Validation Summary" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "HTML Files Scanned: $($results.summary.htmlFilesScanned)" -ForegroundColor White
Write-Host "CSS Files Scanned: $($results.summary.cssFilesScanned)" -ForegroundColor White
Write-Host "Total Issues Found: $($results.summary.totalIssues)" -ForegroundColor $(if ($results.summary.totalIssues -gt 0) { "Red" } else { "Green" })

if ($AutoFix) {
    Write-Host "Issues Fixed: $($results.summary.fixedIssues)" -ForegroundColor Green
}

Write-Host "`n📋 Issue Breakdown:" -ForegroundColor Cyan
Write-Host "  HTML Pattern Issues: $($results.htmlIssues.Count)" -ForegroundColor White
Write-Host "  CSS Gap Issues: $($results.cssIssues.Count)" -ForegroundColor White

# Save report
$reportDir = Split-Path $ReportPath -Parent
if (-not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
}

$results | ConvertTo-Json -Depth 10 | Out-File $ReportPath -Encoding UTF8
Write-Host "`n💾 Report saved: $ReportPath" -ForegroundColor Cyan

#endregion

#region Recommendations

if ($results.summary.totalIssues -gt 0 -and -not $AutoFix) {
    Write-Host "`n💡 Recommendations:" -ForegroundColor Yellow
    Write-Host "  Run with -AutoFix to automatically correct these issues" -ForegroundColor White
    Write-Host "  Review glassmorphism-design-standard.md v4.2.5+ for compliance rules" -ForegroundColor White
}

if ($results.summary.totalIssues -eq 0) {
    Write-Host "`n✅ All icon-title patterns are correctly formatted!" -ForegroundColor Green
}

#endregion

Write-Host "`n" -NoNewline
