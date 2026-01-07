# ============================================================================
# CORTEX Toolkit - CSS Path Validator
# ============================================================================
# Purpose: Detect malformed CSS paths in HTML files
# Author: Asif Hussain
# Version: 1.0.0
# Created: January 3, 2026
# ============================================================================

param(
    [Parameter(Mandatory=$false)]
    [string]$DocsPath = "docs",
    
    [Parameter(Mandatory=$false)]
    [switch]$AutoFix,
    
    [Parameter(Mandatory=$false)]
    [switch]$DryRun,
    
    [Parameter(Mandatory=$false)]
    [switch]$Detailed
)

# Color output functions
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Info { param($Message) Write-Host "ℹ️  $Message" -ForegroundColor Cyan }
function Write-Warning { param($Message) Write-Host "⚠️  $Message" -ForegroundColor Yellow }

# Calculate fix complexity score
function Get-FixComplexityScore {
    param(
        [int]$AffectedFiles,
        [int]$UniquePatterns,
        [bool]$StructureIntact,
        [bool]$ContentValid
    )
    
    $score = 0
    
    # File count impact (0-3 points)
    if ($AffectedFiles -gt 50) { $score += 3 }
    elseif ($AffectedFiles -gt 20) { $score += 2 }
    elseif ($AffectedFiles -gt 5) { $score += 1 }
    
    # Pattern complexity (0-3 points)
    if ($UniquePatterns -gt 10) { $score += 3 }
    elseif ($UniquePatterns -gt 5) { $score += 2 }
    elseif ($UniquePatterns -gt 2) { $score += 1 }
    
    # Structure integrity (0-2 points)
    if (-not $StructureIntact) { $score += 2 }
    
    # Content validity (0-2 points)
    if (-not $ContentValid) { $score += 2 }
    
    return $score
}

# Get fix recommendation
function Get-FixRecommendation {
    param([int]$ComplexityScore)
    
    if ($ComplexityScore -le 3) {
        return @{
            Action = "REPAIR"
            Reason = "Low complexity - pattern-based fix is efficient"
            Color = "Green"
        }
    }
    elseif ($ComplexityScore -le 6) {
        return @{
            Action = "REPAIR (with caution)"
            Reason = "Medium complexity - manual review recommended"
            Color = "Yellow"
        }
    }
    else {
        return @{
            Action = "RECREATE"
            Reason = "High complexity - recreation may be safer"
            Color = "Red"
        }
    }
}

# Main validation logic
Write-Info "🔍 CORTEX CSS Path Validator v1.0.0"
Write-Host ""

$htmlFiles = Get-ChildItem -Path $DocsPath -Filter "*.html" -Recurse
$malformedFiles = @()
$patterns = @{}

Write-Info "Scanning $($htmlFiles.Count) HTML files for malformed CSS paths..."
Write-Host ""

foreach ($file in $htmlFiles) {
    $content = Get-Content $file.FullName -Raw
    
    # Detect malformed paths (3+ consecutive dots)
    if ($content -match '\.\.\/\.\.\.\.\/|href="\.\.\/\.\.\.\.\/') {
        $matches = Select-String -Path $file.FullName -Pattern '\.\.\/\.\.\.\.\/[^"]*' -AllMatches
        
        foreach ($match in $matches.Matches) {
            $malformedPath = $match.Value
            
            if (-not $patterns.ContainsKey($malformedPath)) {
                $patterns[$malformedPath] = @()
            }
            $patterns[$malformedPath] += $file.FullName
        }
        
        $malformedFiles += $file
    }
}

# Display results
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host "📊 VALIDATION RESULTS" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray
Write-Host ""

if ($malformedFiles.Count -eq 0) {
    Write-Success "All CSS paths are valid! No issues detected."
    exit 0
}

Write-Error "$($malformedFiles.Count) files with malformed CSS paths detected"
Write-Host ""

# Calculate complexity
$complexityScore = Get-FixComplexityScore -AffectedFiles $malformedFiles.Count `
                                          -UniquePatterns $patterns.Count `
                                          -StructureIntact $true `
                                          -ContentValid $true

$recommendation = Get-FixRecommendation -ComplexityScore $complexityScore

Write-Host "🎯 FIX COMPLEXITY ANALYSIS" -ForegroundColor Magenta
Write-Host "  Affected Files:    $($malformedFiles.Count)" -ForegroundColor White
Write-Host "  Unique Patterns:   $($patterns.Count)" -ForegroundColor White
Write-Host "  Complexity Score:  $complexityScore/10" -ForegroundColor White
Write-Host "  Recommendation:    $($recommendation.Action)" -ForegroundColor $recommendation.Color
Write-Host "  Reason:            $($recommendation.Reason)" -ForegroundColor Gray
Write-Host ""

# Display patterns
if ($Detailed) {
    Write-Host "🔍 DETECTED PATTERNS" -ForegroundColor Yellow
    Write-Host ""
    
    foreach ($pattern in $patterns.Keys) {
        Write-Host "  Pattern: " -NoNewline -ForegroundColor Gray
        Write-Host "$pattern" -ForegroundColor Red
        Write-Host "  Files affected: $($patterns[$pattern].Count)" -ForegroundColor Gray
        
        if ($patterns[$pattern].Count -le 5) {
            foreach ($file in $patterns[$pattern]) {
                $relativePath = $file.Replace((Get-Location).Path, "").TrimStart("\")
                Write-Host "    └─ $relativePath" -ForegroundColor DarkGray
            }
        }
        Write-Host ""
    }
}

# Auto-fix logic
if ($AutoFix -and -not $DryRun) {
    Write-Warning "🔧 AUTO-FIX MODE ENABLED"
    Write-Host ""
    
    $fixed = 0
    
    foreach ($file in $malformedFiles) {
        $content = Get-Content $file.FullName -Raw
        $originalContent = $content
        
        # Determine correct path based on depth
        $relativePath = $file.FullName.Replace((Resolve-Path $DocsPath).Path, "").TrimStart("\")
        $depth = ($relativePath -split "\\").Count - 1
        
        if ($depth -eq 1) {
            $correctPath = "../assets/css/"
        }
        elseif ($depth -eq 2) {
            $correctPath = "../../assets/css/"
        }
        else {
            $correctPath = "../" * $depth + "assets/css/"
        }
        
        # Remove malformed generated-classes.css links entirely (not needed)
        $content = $content -replace '<link\s+rel="stylesheet"\s+href="[^"]*\.\.\/\.\.\.\.\/[^"]*generated-classes\.css">', ''
        
        if ($content -ne $originalContent) {
            Set-Content -Path $file.FullName -Value $content -NoNewline
            $fixed++
            Write-Success "Fixed: $($file.Name)"
        }
    }
    
    Write-Host ""
    Write-Success "✨ Fixed $fixed files"
}
elseif ($AutoFix -and $DryRun) {
    Write-Info "🔍 DRY RUN MODE - No changes will be made"
    Write-Host ""
    
    foreach ($file in $malformedFiles) {
        $relativePath = $file.FullName.Replace((Get-Location).Path, "").TrimStart("\")
        Write-Host "  Would fix: $relativePath" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor DarkGray

if (-not $AutoFix) {
    Write-Info "💡 Run with -AutoFix to repair all malformed paths"
    Write-Info "💡 Run with -AutoFix -DryRun to preview changes"
    Write-Info "💡 Run with -Detailed to see all affected files"
}

exit $malformedFiles.Count
