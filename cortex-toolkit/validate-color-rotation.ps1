#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Validates color rotation pattern (C50) on card grids to prevent visual monotony.

.DESCRIPTION
    Scans HTML files to detect card grids with 4+ items that lack 4-color rotation.
    Enforces glassmorphism design standard v4.3.0 Pattern C50.

.PARAMETER Path
    Root directory to scan for HTML files.

.PARAMETER Recursive
    Recursively scan subdirectories.

.PARAMETER MinCards
    Minimum number of cards before color rotation is required (default: 4).

.PARAMETER DetectOnly
    Only report issues, don't suggest fixes.

.EXAMPLE
    .\validate-color-rotation.ps1 -Path "docs/" -Recursive

.EXAMPLE
    .\validate-color-rotation.ps1 -Path "docs/orchestrators/index.html" -MinCards 4

.NOTES
    Version: 1.0.0
    Author: Asif Hussain
    Date: January 5, 2026
    Standard: glassmorphism-design-standard.md v4.3.0 (Pattern C50)
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$Path,
    
    [switch]$Recursive,
    
    [int]$MinCards = 4,
    
    [switch]$DetectOnly
)

$ErrorActionPreference = "Stop"

# ANSI colors
$RED = "`e[31m"
$GREEN = "`e[32m"
$YELLOW = "`e[33m"
$CYAN = "`e[36m"
$MAGENTA = "`e[35m"
$RESET = "`e[0m"

function Write-ColorOutput {
    param([string]$Message, [string]$Color)
    Write-Host "${Color}${Message}${RESET}"
}

function Test-ColorRotation {
    param([string]$FilePath)
    
    $content = Get-Content -Path $FilePath -Raw
    $issues = @()
    
    # Find all card grids
    if ($content -match '<div[^>]*class="[^"]*masonry-grid[^"]*"[^>]*>') {
        # Extract cards within grid
        $gridPattern = '<div[^>]*class="[^"]*masonry-grid[^"]*"[^>]*>([\s\S]*?)(?=<\/div>(?![^<]*<div[^>]*class="[^"]*masonry-grid))'
        
        if ($content -match $gridPattern) {
            $gridContent = $matches[1]
            
            # Count cards
            $cards = [regex]::Matches($gridContent, '<(?:a|div)[^>]*class="[^"]*glass-card-clickable[^"]*"')
            $cardCount = $cards.Count
            
            if ($cardCount -ge $MinCards) {
                # Check for color variant distribution
                $primaryCount = ([regex]::Matches($gridContent, 'card-variant-primary')).Count
                $infoCount = ([regex]::Matches($gridContent, 'card-variant-info')).Count
                $warningCount = ([regex]::Matches($gridContent, 'card-variant-warning')).Count
                $successCount = ([regex]::Matches($gridContent, 'card-variant-success')).Count
                
                $totalVariants = $primaryCount + $infoCount + $warningCount + $successCount
                
                # Check icon color classes
                $iconPrimaryCount = ([regex]::Matches($gridContent, 'card-icon-primary')).Count
                $iconInfoCount = ([regex]::Matches($gridContent, 'card-icon-info')).Count
                $iconWarningCount = ([regex]::Matches($gridContent, 'card-icon-warning')).Count
                $iconSuccessCount = ([regex]::Matches($gridContent, 'card-icon-success')).Count
                
                $hasMonotoneIcons = ($iconPrimaryCount -eq $cardCount) -or 
                                   ($iconInfoCount -eq $cardCount) -or 
                                   ($iconWarningCount -eq $cardCount) -or 
                                   ($iconSuccessCount -eq $cardCount)
                
                $hasNoVariants = $totalVariants -eq 0
                
                if ($hasNoVariants -or $hasMonotoneIcons) {
                    $issues += @{
                        CardCount = $cardCount
                        HasVariants = -not $hasNoVariants
                        MonotoneIcons = $hasMonotoneIcons
                        Distribution = @{
                            Primary = $primaryCount
                            Info = $infoCount
                            Warning = $warningCount
                            Success = $successCount
                        }
                        IconDistribution = @{
                            Primary = $iconPrimaryCount
                            Info = $iconInfoCount
                            Warning = $iconWarningCount
                            Success = $iconSuccessCount
                        }
                    }
                }
            }
        }
    }
    
    return $issues
}

function Show-ColorRotationSuggestion {
    param([int]$CardCount)
    
    Write-ColorOutput "`n📋 Suggested Color Rotation Pattern:" $CYAN
    
    $colors = @("primary", "info", "warning", "success")
    
    for ($i = 1; $i -le $CardCount; $i++) {
        $colorIndex = ($i - 1) % 4
        $color = $colors[$colorIndex]
        
        $colorDisplay = switch($color) {
            "primary" { "${MAGENTA}primary${RESET}" }
            "info" { "${CYAN}info${RESET}" }
            "warning" { "${YELLOW}warning${RESET}" }
            "success" { "${GREEN}success${RESET}" }
        }
        
        Write-Host "   Card $i → $colorDisplay"
    }
    
    Write-ColorOutput "`nPattern: primary → info → warning → success → repeat" $CYAN
}

# Main execution
Write-ColorOutput "🎨 Glassmorphism Color Rotation Validator v1.0.0" $CYAN
Write-ColorOutput "Standard: glassmorphism-design-standard.md v4.3.0 (Pattern C50)`n" $CYAN

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
    $issues = Test-ColorRotation -FilePath $file.FullName
    
    if ($issues.Count -gt 0) {
        $filesWithIssues++
        $totalIssues += $issues.Count
        
        Write-ColorOutput "`n❌ $($file.Name)" $RED
        
        foreach ($issue in $issues) {
            Write-ColorOutput "   Card Count: $($issue.CardCount)" $YELLOW
            
            if ($issue.MonotoneIcons) {
                Write-ColorOutput "   ⚠️  MONOTONE ICONS DETECTED" $RED
                Write-ColorOutput "   All icons use the same color class" $YELLOW
            }
            
            if (-not $issue.HasVariants) {
                Write-ColorOutput "   ⚠️  NO COLOR VARIANTS APPLIED" $RED
                Write-ColorOutput "   Missing card-variant-* classes" $YELLOW
            }
            
            Write-ColorOutput "`n   Current Distribution:" $CYAN
            Write-ColorOutput "   Card Variants - Primary: $($issue.Distribution.Primary), Info: $($issue.Distribution.Info), Warning: $($issue.Distribution.Warning), Success: $($issue.Distribution.Success)" $YELLOW
            Write-ColorOutput "   Icon Classes - Primary: $($issue.IconDistribution.Primary), Info: $($issue.IconDistribution.Info), Warning: $($issue.IconDistribution.Warning), Success: $($issue.IconDistribution.Success)" $YELLOW
            
            if (-not $DetectOnly) {
                Show-ColorRotationSuggestion -CardCount $issue.CardCount
            }
        }
    }
}

# Summary
Write-ColorOutput "`n========================================" $CYAN
if ($totalIssues -eq 0) {
    Write-ColorOutput "✅ All card grids use proper color rotation!" $GREEN
    Write-ColorOutput "Scanned: $($htmlFiles.Count) files" $GREEN
    exit 0
} else {
    Write-ColorOutput "❌ Found $totalIssues monotone grids in $filesWithIssues files" $RED
    Write-ColorOutput "Scanned: $($htmlFiles.Count) files" $YELLOW
    
    Write-ColorOutput "`n💡 Apply Pattern C50 (4-color rotation) to fix visual monotony" $CYAN
    Write-ColorOutput "   Reference: glass-morph-master.md Line 45-85" $CYAN
    
    exit 1
}
