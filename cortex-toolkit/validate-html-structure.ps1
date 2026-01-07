<#
.SYNOPSIS
    Validates HTML structure and CSS class usage against CORTEX standards

.DESCRIPTION
    Detects common broken HTML patterns that require Pattern C52 (Full Reconstruction):
    - Duplicate <style> blocks
    - Duplicate <head> sections  
    - Missing class="container" on <main>
    - Non-existent CSS classes
    - Broken header structure
    - Excessive inline styles
    - Deep nested sections

.PARAMETER FilePath
    Path to HTML file to validate

.EXAMPLE
    .\validate-html-structure.ps1 -FilePath "docs/orchestrators/index.html"

.NOTES
    Author: Asif Hussain
    Version: 1.0.0
    Reference: glass-morph-master.md Pattern C52
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$FilePath
)

$ErrorActionPreference = "Stop"

# Color codes for output
$RED = "`e[91m"
$YELLOW = "`e[93m"
$GREEN = "`e[92m"
$BLUE = "`e[94m"
$RESET = "`e[0m"

Write-Host "${BLUE}🔍 CORTEX HTML Structure Validator${RESET}" -ForegroundColor Blue
Write-Host "File: $FilePath`n" -ForegroundColor Cyan

if (-not (Test-Path $FilePath)) {
    Write-Host "${RED}❌ ERROR: File not found${RESET}" -ForegroundColor Red
    exit 1
}

$content = Get-Content $FilePath -Raw
$issues = @()
$warnings = @()
$reconstructionRequired = $false

# 1. Check for duplicate <style> blocks
$styleBlockCount = ([regex]::Matches($content, '<style[^>]*>')).Count
if ($styleBlockCount -gt 2) {
    $issues += "❌ CRITICAL: Duplicate <style> blocks detected ($styleBlockCount found, max 2 allowed)"
    $reconstructionRequired = $true
}

# 2. Check for duplicate <head> sections
$headCount = ([regex]::Matches($content, '<head>')).Count
if ($headCount -gt 1) {
    $issues += "❌ CRITICAL: Duplicate <head> sections detected ($headCount found)"
    $reconstructionRequired = $true
}

# 3. Check for class="container" on <main>
if ($content -notmatch '<main[^>]*class="[^"]*container[^"]*"') {
    $issues += "❌ CRITICAL: Missing class=`"container`" on <main> element"
    $reconstructionRequired = $true
}

# 4. Check for non-existent CSS classes
$forbiddenClasses = @(
    'tetris-grid',
    'stats-grid', 
    'category-grid',
    'capability-item',
    'section-heading',
    'stat-card',
    'category-card'
)

foreach ($class in $forbiddenClasses) {
    if ($content -match "class=`"[^`"]*$class[^`"]*`"") {
        $replacement = switch ($class) {
            'tetris-grid' { 'masonry-grid' }
            'stats-grid' { 'metadata-grid' }
            'category-grid' { 'masonry-grid' }
            'capability-item' { 'metric-card in metrics-grid' }
            'section-heading' { 'section-title' }
            'stat-card' { 'metadata-item' }
            'category-card' { 'glass-card-display' }
        }
        $issues += "❌ CRITICAL: Non-existent class '$class' (use '$replacement')"
        $reconstructionRequired = $true
    }
}

# 5. Check for broken header structure
if ($content -notmatch '<header[^>]*class="[^"]*glass-header[^"]*"') {
    $issues += "❌ CRITICAL: Missing class=`"glass-header`" on <header>"
    $reconstructionRequired = $true
}

# 6. Check for excessive inline styles
$inlineStyleCount = ([regex]::Matches($content, 'style="[^"]*"')).Count
if ($inlineStyleCount -gt 5) {
    $warnings += "⚠️  WARNING: Excessive inline styles detected ($inlineStyleCount found)"
}

# 7. Check for deep nested sections
$maxNestingDepth = 0
$currentDepth = 0
foreach ($char in $content.ToCharArray()) {
    if ($content.Substring([Math]::Max(0, $content.IndexOf($char) - 8), 8) -eq '<section') {
        $currentDepth++
        if ($currentDepth -gt $maxNestingDepth) { $maxNestingDepth = $currentDepth }
    }
    if ($content.Substring([Math]::Max(0, $content.IndexOf($char) - 9), 9) -eq '</section') {
        $currentDepth--
    }
}
if ($maxNestingDepth -gt 3) {
    $warnings += "⚠️  WARNING: Deep section nesting detected (depth: $maxNestingDepth, max: 3)"
}

# 8. Check for required CSS files
$requiredCSS = @(
    'main.css',
    'variables.css'
)
foreach ($css in $requiredCSS) {
    if ($content -notmatch $css) {
        $issues += "❌ CRITICAL: Missing required CSS file: $css"
        $reconstructionRequired = $true
    }
}

# 9. Check for Font Awesome 6.x
if ($content -match 'font-awesome/5\.' -or $content -notmatch 'font-awesome/6\.') {
    $warnings += "⚠️  WARNING: Font Awesome 6.x not detected (required for proper icon rendering)"
}

# 10. Check for skip-link accessibility
if ($content -notmatch 'class="skip-link"') {
    $warnings += "⚠️  WARNING: Missing accessibility skip-link"
}

# Output Results
Write-Host "`n${BLUE}═══════════════════════════════════════════════════════${RESET}" -ForegroundColor Blue
Write-Host "${BLUE}                  VALIDATION RESULTS${RESET}" -ForegroundColor Blue
Write-Host "${BLUE}═══════════════════════════════════════════════════════${RESET}`n" -ForegroundColor Blue

if ($issues.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "${GREEN}✅ PASSED: No issues detected${RESET}" -ForegroundColor Green
    Write-Host "${GREEN}HTML structure follows approved standards${RESET}`n" -ForegroundColor Green
    exit 0
}

if ($issues.Count -gt 0) {
    Write-Host "${RED}CRITICAL ISSUES (${issues.Count}):${RESET}" -ForegroundColor Red
    foreach ($issue in $issues) {
        Write-Host "  $issue" -ForegroundColor Red
    }
    Write-Host ""
}

if ($warnings.Count -gt 0) {
    Write-Host "${YELLOW}WARNINGS (${warnings.Count}):${RESET}" -ForegroundColor Yellow
    foreach ($warning in $warnings) {
        Write-Host "  $warning" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Recommendation
if ($reconstructionRequired) {
    Write-Host "${RED}═══════════════════════════════════════════════════════${RESET}" -ForegroundColor Red
    Write-Host "${RED}     ⚠️  PATTERN C52 RECONSTRUCTION REQUIRED ⚠️${RESET}" -ForegroundColor Red
    Write-Host "${RED}═══════════════════════════════════════════════════════${RESET}`n" -ForegroundColor Red
    
    Write-Host "Recommended Actions:" -ForegroundColor Cyan
    Write-Host "1. Backup file: Copy-Item `"$FilePath`" `"$FilePath.backup-`$(Get-Date -Format 'yyyyMMdd_HHmmss')`"" -ForegroundColor Gray
    Write-Host "2. Consult: cortex-brain/documents/planning/active/html-glassmorphism-alignment/glass-morph-master.md" -ForegroundColor Gray
    Write-Host "3. Use approved template from Pattern C52" -ForegroundColor Gray
    Write-Host "4. Delete broken file and recreate from scratch`n" -ForegroundColor Gray
    
    exit 2
} else {
    Write-Host "${YELLOW}Minor issues detected - manual fixes recommended${RESET}`n" -ForegroundColor Yellow
    exit 1
}
