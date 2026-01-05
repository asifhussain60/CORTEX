#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Validates that section content (heading + children) are wrapped in glassmorphism panels.

.DESCRIPTION
    Scans HTML files to detect naked sections where <h2 class="section-title"> and its 
    following content are not wrapped together in <section class="glass-card-display">. 
    Enforces glassmorphism design standard v4.3.0.

.PARAMETER Path
    Root directory to scan for HTML files.

.PARAMETER Recursive
    Recursively scan subdirectories.

.PARAMETER AutoFix
    Automatically wrap section content in glassmorphism panels (creates backups).

.EXAMPLE
    .\validate-panel-wrapping.ps1 -Path "docs/" -Recursive

.EXAMPLE
    .\validate-panel-wrapping.ps1 -Path "docs/orchestrators/index.html" -AutoFix

.NOTES
    Version: 1.1.0
    Author: Asif Hussain
    Date: January 5, 2026
    Standard: glassmorphism-design-standard.md v4.3.0
    
    FIXED: Now detects full section wrapping (heading + content together),
    not just heading-only wrapping.
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$Path,
    
    [switch]$Recursive,
    
    [switch]$AutoFix
)

$ErrorActionPreference = "Stop"

# ANSI colors
$RED = "`e[31m"
$GREEN = "`e[32m"
$YELLOW = "`e[33m"
$CYAN = "`e[36m"
$RESET = "`e[0m"

function Write-ColorOutput {
    param([string]$Message, [string]$Color)
    Write-Host "${Color}${Message}${RESET}"
}

function Test-NakedHeadings {
    param([string]$FilePath)
    
    $content = Get-Content -Path $FilePath -Raw
    $issues = @()
    
    # Split into lines for line number tracking
    $lines = $content -split "`n"
    
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        $lineNum = $i + 1
        
        # Detect <h2 class="section-title">
        if ($line -match '<h2[^>]*class="[^"]*section-title[^"]*"[^>]*>') {
            # Check previous lines for glass-card-display wrapper
            $hasWrapper = $false
            $lookback = [Math]::Min($i, 5) # Check up to 5 lines back
            
            for ($j = $i - $lookback; $j -lt $i; $j++) {
                if ($lines[$j] -match '<section[^>]*class="[^"]*glass-card-display[^"]*"[^>]*>') {
                    # Found wrapper, now check if content after heading is INSIDE the same section
                    # Look ahead to find the next significant content (masonry-grid, etc.)
                    $nextContentLine = -1
                    $sectionCloseLine = -1
                    
                    for ($k = $i + 1; $k -lt [Math]::Min($lines.Count, $i + 10); $k++) {
                        if ($lines[$k] -match '<div[^>]*class="[^"]*masonry-grid[^"]*"') {
                            $nextContentLine = $k
                            break
                        }
                    }
                    
                    # Find section close tag after heading
                    for ($k = $i + 1; $k -lt [Math]::Min($lines.Count, $i + 5); $k++) {
                        if ($lines[$k] -match '</section>') {
                            $sectionCloseLine = $k
                            break
                        }
                    }
                    
                    # If section closes BEFORE content starts, it's heading-only wrapping (WRONG)
                    if ($sectionCloseLine -gt 0 -and $nextContentLine -gt 0 -and $sectionCloseLine -lt $nextContentLine) {
                        $hasWrapper = $false
                        break
                    }
                    
                    $hasWrapper = $true
                    break
                }
            }
            
            if (-not $hasWrapper) {
                $issues += @{
                    Line = $lineNum
                    Content = $line.Trim()
                }
            }
        }
    }
    
    return $issues
}

function Invoke-AutoFix {
    param([string]$FilePath, [array]$Issues)
    
    # Create backup
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupPath = "${FilePath}.backup-${timestamp}"
    Copy-Item -Path $FilePath -Destination $backupPath
    Write-ColorOutput "✅ Backup created: $backupPath" $GREEN
    
    $content = Get-Content -Path $FilePath -Raw
    
    # Regex to find naked section-title headings and wrap them
    $pattern = '([ \t]*)<h2([^>]*class="[^"]*section-title[^"]*"[^>]*)>([\s\S]*?)</h2>'
    
    $content = [regex]::Replace($content, $pattern, {
        param($match)
        $indent = $match.Groups[1].Value
        $h2Attrs = $match.Groups[2].Value
        $h2Content = $match.Groups[3].Value
        
        # Check if already wrapped (look for glass-card-display in previous 200 chars)
        $startPos = $match.Index
        $lookbackStart = [Math]::Max(0, $startPos - 200)
        $lookback = $content.Substring($lookbackStart, $startPos - $lookbackStart)
        
        if ($lookback -match '<section[^>]*class="[^"]*glass-card-display[^"]*"[^>]*>') {
            # Already wrapped, return as-is
            return $match.Value
        }
        
        # Wrap in glassmorphism panel
        return "${indent}<section class=`"glass-card-display`">`n${indent}    <h2${h2Attrs}>${h2Content}</h2>`n${indent}</section>"
    })
    
    Set-Content -Path $FilePath -Value $content -NoNewline
    Write-ColorOutput "✅ Applied fixes to: $FilePath" $GREEN
}

# Main execution
Write-ColorOutput "🔍 Glassmorphism Section Panel Validator v1.1.0" $CYAN
Write-ColorOutput "Standard: glassmorphism-design-standard.md v4.3.0" $CYAN
Write-ColorOutput "Checks: Full section wrapping (heading + content together)`n" $CYAN

$searchParams = @{
    Path = $Path
    Filter = "*.html"
}

if ($Recursive) {
    $searchParams.Recurse = $true
}

$htmlFiles = Get-ChildItem @searchParams

$totalIssues = 0
$filesWithIssues = 0

foreach ($file in $htmlFiles) {
    $issues = Test-NakedHeadings -FilePath $file.FullName
    
    if ($issues.Count -gt 0) {
        $filesWithIssues++
        $totalIssues += $issues.Count
        
        Write-ColorOutput "`n❌ $($file.Name)" $RED
        Write-ColorOutput "   Issues: $($issues.Count)" $YELLOW
        
        foreach ($issue in $issues) {
            Write-ColorOutput "   Line $($issue.Line): $($issue.Content)" $YELLOW
        }
        
        if ($AutoFix) {
            Invoke-AutoFix -FilePath $file.FullName -Issues $issues
        }
    }
}

# Summary
Write-ColorOutput "`n========================================" $CYAN
if ($totalIssues -eq 0) {
    Write-ColorOutput "✅ All sections properly wrapped!" $GREEN
    Write-ColorOutput "Scanned: $($htmlFiles.Count) files" $GREEN
    exit 0
} else {
    Write-ColorOutput "❌ Found $totalIssues sections with incorrect wrapping in $filesWithIssues files" $RED
    Write-ColorOutput "Scanned: $($htmlFiles.Count) files" $YELLOW
    Write-ColorOutput "`n⚠️  Common issues:" $YELLOW
    Write-ColorOutput "   - Heading-only panel (section closes before content)" $YELLOW
    Write-ColorOutput "   - No panel at all (naked section)" $YELLOW
    Write-ColorOutput "`n✅ Correct pattern:" $GREEN
    Write-ColorOutput "   <section class=`"glass-card-display`">" $GREEN
    Write-ColorOutput "       <h2 class=`"section-title`">Title</h2>" $GREEN
    Write-ColorOutput "       <div class=`"masonry-grid`">...</div>" $GREEN
    Write-ColorOutput "   </section>" $GREEN
    
    if (-not $AutoFix) {
        Write-ColorOutput "`n💡 Run with -AutoFix to automatically fix wrapping" $CYAN
    }
    
    exit 2
}
