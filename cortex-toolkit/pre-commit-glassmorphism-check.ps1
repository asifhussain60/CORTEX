# 🛡️ CORTEX Glassmorphism Pre-Commit Hook
# =========================================
#
# Validates HTML/CSS changes against glassmorphism design standard before commit.
#
# Author: Asif Hussain
# Version: 1.0.0
# Date: January 4, 2026
# Copyright: © 2026 Asif Hussain. All rights reserved.
#
# Installation:
#   1. Copy to .git/hooks/pre-commit
#   2. Make executable: chmod +x .git/hooks/pre-commit
#
# This hook will:
# - Validate HTML files for inline styles
# - Check CSS compliance with design standard
# - Verify icon-title spacing
# - Detect non-compliant class usage

$ErrorActionPreference = "Stop"

Write-Host "🛡️ CORTEX Glassmorphism Compliance Check" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Get staged files
$stagedFiles = git diff --cached --name-only --diff-filter=ACM

# Filter HTML and CSS files
$htmlFiles = $stagedFiles | Where-Object { $_ -match '\.html$' }
$cssFiles = $stagedFiles | Where-Object { $_ -match '\.css$' }

$violations = @()
$warnings = @()

# Check 1: Inline styles in HTML (CRITICAL)
if ($htmlFiles) {
    Write-Host "📄 Checking HTML files for inline styles..." -ForegroundColor Yellow
    
    foreach ($file in $htmlFiles) {
        if (Test-Path $file) {
            $content = Get-Content $file -Raw
            
            # Check for style attributes
            $styleMatches = [regex]::Matches($content, 'style\s*=\s*["\'][^"\']+["\']')
            
            if ($styleMatches.Count -gt 0) {
                $violations += @{
                    File = $file
                    Rule = "NO_INLINE_STYLES"
                    Message = "Found $($styleMatches.Count) inline style(s)"
                    Severity = "CRITICAL"
                }
            }
        }
    }
}

# Check 2: Missing glassmorphism classes (WARNING)
if ($htmlFiles) {
    Write-Host "🎨 Checking HTML files for glassmorphism compliance..." -ForegroundColor Yellow
    
    $requiredPatterns = @(
        'glass-card-(clickable|display)',
        'animation-t[1-3]',
        'pulse-glow-glass'
    )
    
    foreach ($file in $htmlFiles) {
        if (Test-Path $file) {
            $content = Get-Content $file -Raw
            
            # Check if file has card elements but missing glass classes
            if ($content -match '<div[^>]*class="[^"]*card[^"]*"') {
                $hasGlassCard = $content -match 'glass-card-(clickable|display)'
                
                if (-not $hasGlassCard) {
                    $warnings += @{
                        File = $file
                        Rule = "GLASSMORPHISM_CLASSES_MISSING"
                        Message = "Card elements found but no glassmorphism classes"
                        Severity = "WARNING"
                    }
                }
            }
        }
    }
}

# Check 3: Font Awesome icon format (CRITICAL)
if ($htmlFiles) {
    Write-Host "🎯 Checking Font Awesome icon format..." -ForegroundColor Yellow
    
    foreach ($file in $htmlFiles) {
        if (Test-Path $file) {
            $content = Get-Content $file -Raw
            
            # Find icons without style prefix
            $badIcons = [regex]::Matches($content, '<i[^>]*class="[^"]*\bfa-[a-z\-]+[^"]*"[^>]*>')
            
            foreach ($match in $badIcons) {
                if ($match.Value -notmatch '\b(fas|far|fab|fal|fad)\b') {
                    $violations += @{
                        File = $file
                        Rule = "FONT_AWESOME_PREFIX_MISSING"
                        Message = "Icon missing style prefix (fas/far/fab/fal/fad)"
                        Severity = "CRITICAL"
                        Context = $match.Value
                    }
                }
            }
        }
    }
}

# Check 4: CSS duplicate rules (WARNING)
if ($cssFiles) {
    Write-Host "🔍 Checking CSS files for duplicates..." -ForegroundColor Yellow
    
    foreach ($file in $cssFiles) {
        if (Test-Path $file) {
            $content = Get-Content $file -Raw
            
            # Extract class selectors
            $classes = [regex]::Matches($content, '^\.([\w\-_]+)\s*\{', 'Multiline')
            $classCounts = @{}
            
            foreach ($match in $classes) {
                $className = $match.Groups[1].Value
                if ($classCounts.ContainsKey($className)) {
                    $classCounts[$className]++
                } else {
                    $classCounts[$className] = 1
                }
            }
            
            $duplicates = $classCounts.GetEnumerator() | Where-Object { $_.Value -gt 1 }
            
            if ($duplicates) {
                foreach ($dup in $duplicates) {
                    $warnings += @{
                        File = $file
                        Rule = "CSS_DUPLICATE_CLASS"
                        Message = "Class '.$ ($dup.Key)' defined $($dup.Value) times"
                        Severity = "WARNING"
                    }
                }
            }
        }
    }
}

# Check 5: Icon-title spacing (MEDIUM)
if ($htmlFiles) {
    Write-Host "📏 Checking icon-title spacing..." -ForegroundColor Yellow
    
    foreach ($file in $htmlFiles) {
        if (Test-Path $file) {
            $content = Get-Content $file -Raw
            
            # Check for icons followed by text without proper spacing
            $badSpacing = [regex]::Matches($content, '<i class="fa[srlab]+ fa-[^"]+"></i>[^\s<]')
            
            if ($badSpacing.Count -gt 0) {
                $warnings += @{
                    File = $file
                    Rule = "ICON_TITLE_SPACING"
                    Message = "Found $($badSpacing.Count) icon(s) with insufficient spacing"
                    Severity = "MEDIUM"
                }
            }
        }
    }
}

# Display results
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "📊 Compliance Check Results" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

if ($violations.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "✅ All checks passed! Commit allowed." -ForegroundColor Green
    Write-Host ""
    exit 0
}

# Display violations
if ($violations.Count -gt 0) {
    Write-Host "❌ CRITICAL VIOLATIONS ($($violations.Count)):" -ForegroundColor Red
    Write-Host ""
    
    foreach ($v in $violations) {
        Write-Host "  File: $($v.File)" -ForegroundColor Red
        Write-Host "  Rule: $($v.Rule)" -ForegroundColor Yellow
        Write-Host "  Message: $($v.Message)" -ForegroundColor White
        if ($v.Context) {
            Write-Host "  Context: $($v.Context)" -ForegroundColor Gray
        }
        Write-Host ""
    }
    
    Write-Host "⛔ COMMIT BLOCKED - Fix violations before committing" -ForegroundColor Red
    Write-Host ""
    Write-Host "📖 See glassmorphism-design-standard.md for compliance rules" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Display warnings
if ($warnings.Count -gt 0) {
    Write-Host "⚠️  WARNINGS ($($warnings.Count)):" -ForegroundColor Yellow
    Write-Host ""
    
    foreach ($w in $warnings) {
        Write-Host "  File: $($w.File)" -ForegroundColor Yellow
        Write-Host "  Rule: $($w.Rule)" -ForegroundColor Cyan
        Write-Host "  Message: $($w.Message)" -ForegroundColor White
        Write-Host ""
    }
    
    Write-Host "⚠️  Warnings detected but commit allowed" -ForegroundColor Yellow
    Write-Host "💡 Consider fixing warnings to improve code quality" -ForegroundColor Cyan
    Write-Host ""
}

exit 0
