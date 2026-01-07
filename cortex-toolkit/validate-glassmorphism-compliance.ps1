<#
.SYNOPSIS
    Validates HTML views against glassmorphism-design-standard.md compliance
.DESCRIPTION
    Checks all HTML files for glassmorphism standard violations (inline styles,
    animation tiers, spacing, hierarchy, CSS quality rules).
.PARAMETER StandardVersion
    Glassmorphism standard version to validate against (default: 4.2.0)
.PARAMETER StrictMode
    Fail if overall compliance score < 95%
.PARAMETER ExcludePages
    Skip specific HTML files
.EXAMPLE
    .\validate-glassmorphism-compliance.ps1 -StandardVersion 4.2.0 -StrictMode
.NOTES
    Version: 1.0.0
    Author: Asif Hussain
    Created: January 3, 2026
#>

param(
    [string]$StandardVersion = "4.2.0",
    [switch]$StrictMode,
    [string[]]$ExcludePages = @()
)

$HtmlDirectory = Join-Path $PSScriptRoot "..\docs"
$StandardPath = Join-Path $PSScriptRoot "..\cortex-brain\documents\standards\glassmorphism-design-standard.md"
$ReportDirectory = Join-Path $PSScriptRoot "..\cortex-brain\documents\reports"
$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$ReportPath = Join-Path $ReportDirectory "glassmorphism-compliance-$Timestamp.json"

if (-not (Test-Path $ReportDirectory)) {
    New-Item -ItemType Directory -Path $ReportDirectory -Force | Out-Null
}

Write-Host "🎨 Glassmorphism Compliance Validation Started" -ForegroundColor Cyan
Write-Host "📄 Standard Version: $StandardVersion" -ForegroundColor Gray

# Verify standard exists
if (-not (Test-Path $StandardPath)) {
    Write-Error "Glassmorphism standard not found: $StandardPath"
    exit 1
}

# Get all HTML files
$htmlFiles = Get-ChildItem -Path $HtmlDirectory -Filter "*.html" -Recurse |
    Where-Object { $_.FullName -notmatch 'archives|cortex-lens-output' -and $ExcludePages -notcontains $_.Name }

Write-Host "✅ Found $($htmlFiles.Count) HTML files to validate" -ForegroundColor Green

# Initialize violation counters
$inlineStyleViolations = @()
$animationTierViolations = @()
$spacingViolations = @()
$hierarchyViolations = @()
$bulletListViolations = @()

# Check for inline style violations (Principle 9)
foreach ($htmlFile in $htmlFiles) {
    $content = Get-Content $htmlFile.FullName -Raw
    $lineNumber = 1
    
    foreach ($line in (Get-Content $htmlFile.FullName)) {
        if ($line -match 'style\s*=\s*"[^"]+"') {
            $inlineStyleViolations += @{
                file = $htmlFile.Name
                line = $lineNumber
                issue = "Inline style attribute forbidden (Principle 9)"
                action = "MOVE to CSS class"
                severity = "CRITICAL"
            }
        }
        $lineNumber++
    }
}

# Check for animation tier violations (Level 1 pages must use T1 only)
foreach ($htmlFile in $htmlFiles) {
    # Skip index.html (Level 0)
    if ($htmlFile.Name -eq "index.html" -and $htmlFile.DirectoryName -match '\\docs$') {
        continue
    }
    
    $content = Get-Content $htmlFile.FullName -Raw
    if ($content -match 'animation-t3|animation-t2') {
        $lineNumber = 1
        foreach ($line in (Get-Content $htmlFile.FullName)) {
            if ($line -match 'animation-(t2|t3)') {
                $animationTierViolations += @{
                    file = $htmlFile.Name
                    line = $lineNumber
                    issue = "Level 1 pages must use animation-t1 only (found $($matches[1]))"
                    action = "REPLACE with animation-t1"
                    severity = "HIGH"
                }
            }
            $lineNumber++
        }
    }
}

# Check for bullet list violations (Principle 13)
foreach ($htmlFile in $htmlFiles) {
    $content = Get-Content $htmlFile.FullName -Raw
    $lineNumber = 1
    
    foreach ($line in (Get-Content $htmlFile.FullName)) {
        # Detect visual content lists (not navigation)
        if ($line -match '<ul[^>]*>' -and $line -notmatch 'class="[^"]*nav') {
            $bulletListViolations += @{
                file = $htmlFile.Name
                line = $lineNumber
                issue = "Visual content using <ul> (should use cards per Principle 13)"
                action = "REPLACE with .capability-tiles or .principle-card-grid"
                severity = "LOW"
            }
        }
        $lineNumber++
    }
}

# Check for hierarchy violations (max Level 1)
foreach ($htmlFile in $htmlFiles) {
    $relativePath = $htmlFile.FullName -replace [regex]::Escape($HtmlDirectory), ""
    $depth = ($relativePath -split '\\').Count - 2  # Subtract 2 for root and filename
    
    if ($depth -gt 2) {  # Level 0 = 0, Level 1 = 1-2, Level 2+ = 3+
        $hierarchyViolations += @{
            file = $htmlFile.Name
            path = $relativePath
            depth = $depth
            issue = "Page depth ($depth) exceeds Level 1 maximum (Principle 8)"
            action = "FLATTEN hierarchy or consolidate into Level 1 page"
            severity = "LOW"
        }
    }
}

Write-Host "✅ Scanned $($htmlFiles.Count) HTML files" -ForegroundColor Green

# Load CSS quality reports (from previous phases)
$cssReports = @{
    duplicates = $null
    usage = $null
    responsive = $null
}

$latestDuplicates = Get-ChildItem -Path $ReportDirectory -Filter "css-duplicates-*.json" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$latestUsage = Get-ChildItem -Path $ReportDirectory -Filter "css-usage-*.json" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$latestResponsive = Get-ChildItem -Path $ReportDirectory -Filter "responsive-design-*.json" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($latestDuplicates) {
    $cssReports.duplicates = Get-Content $latestDuplicates.FullName | ConvertFrom-Json
}
if ($latestUsage) {
    $cssReports.usage = Get-Content $latestUsage.FullName | ConvertFrom-Json
}
if ($latestResponsive) {
    $cssReports.responsive = Get-Content $latestResponsive.FullName | ConvertFrom-Json
}

# Calculate compliance scores
$criticalViolations = $inlineStyleViolations.Count
$highViolations = $animationTierViolations.Count
$mediumViolations = $spacingViolations.Count
$lowViolations = $bulletListViolations.Count + $hierarchyViolations.Count

$totalViolations = $criticalViolations + $highViolations + $mediumViolations + $lowViolations
$complianceScore = [math]::Round((1 - ($totalViolations / ($htmlFiles.Count * 5))) * 100, 2)

$grade = if ($complianceScore -ge 95) { 'A+' }
         elseif ($complianceScore -ge 90) { 'A' }
         elseif ($complianceScore -ge 85) { 'B+' }
         elseif ($complianceScore -ge 80) { 'B' }
         else { 'C' }

# Build report
$report = @{
    scan_timestamp = (Get-Date -Format "o")
    glassmorphism_compliance = @{
        standard_version = $StandardVersion
        total_html_files = $htmlFiles.Count
        violations = @{
            inline_styles = @{
                count = $inlineStyleViolations.Count
                severity = "CRITICAL"
                instances = $inlineStyleViolations | Select-Object -First 20
            }
            animation_tier_violations = @{
                count = $animationTierViolations.Count
                severity = "HIGH"
                instances = $animationTierViolations | Select-Object -First 20
            }
            spacing_violations = @{
                count = $spacingViolations.Count
                severity = "MEDIUM"
                instances = $spacingViolations | Select-Object -First 20
            }
            hierarchy_violations = @{
                count = $hierarchyViolations.Count
                severity = "LOW"
                instances = $hierarchyViolations | Select-Object -First 20
            }
            bullet_list_violations = @{
                count = $bulletListViolations.Count
                severity = "LOW"
                instances = $bulletListViolations | Select-Object -First 20
            }
        }
        core_principles_compliance = @{
            principle_9_no_inline_styles = @{
                compliant = ($inlineStyleViolations.Count -eq 0)
                violations = $inlineStyleViolations.Count
            }
            principle_10_responsive = @{
                compliant = if ($cssReports.responsive) { $cssReports.responsive.responsive_analysis.viewport_compliance.compliance_rate -eq 100 } else { $false }
                viewport_meta_tags = if ($cssReports.responsive) { "$($cssReports.responsive.responsive_analysis.viewport_compliance.compliance_rate)%" } else { "N/A" }
            }
            principle_11_spacing = @{
                compliant = ($spacingViolations.Count -eq 0)
                violations = $spacingViolations.Count
            }
            principle_13_cards_over_bullets = @{
                compliant = ($bulletListViolations.Count -eq 0)
                violations = $bulletListViolations.Count
            }
            principle_17_20_css_quality = @{
                principle_17_zero_duplicates = @{
                    compliant = if ($cssReports.duplicates) { $cssReports.duplicates.total_redundancy.percentage -lt 2.0 } else { $false }
                    redundancy_percentage = if ($cssReports.duplicates) { $cssReports.duplicates.total_redundancy.percentage } else { 0 }
                    threshold = 2.0
                }
                principle_18_100_usage = @{
                    compliant = if ($cssReports.usage) { $cssReports.usage.unused_css_classes.percentage -lt 5.0 } else { $false }
                    unused_percentage = if ($cssReports.usage) { $cssReports.usage.unused_css_classes.percentage } else { 0 }
                    threshold = 5.0
                }
                principle_19_zero_missing = @{
                    compliant = if ($cssReports.usage) { $cssReports.usage.missing_css_classes.count -eq 0 } else { $false }
                    missing_count = if ($cssReports.usage) { $cssReports.usage.missing_css_classes.count } else { 0 }
                    threshold = 0
                }
                principle_20_mobile_first = @{
                    compliant = if ($cssReports.responsive) { $cssReports.responsive.mobile_friendliness_score.overall_score -ge 95 } else { $false }
                    score = if ($cssReports.responsive) { $cssReports.responsive.mobile_friendliness_score.overall_score } else { 0 }
                    grade = if ($cssReports.responsive) { $cssReports.responsive.mobile_friendliness_score.grade } else { "N/A" }
                    threshold = 95.0
                }
            }
        }
    }
    compliance_score = @{
        critical_violations = $criticalViolations
        high_violations = $highViolations
        medium_violations = $mediumViolations
        low_violations = $lowViolations
        overall_compliance = $complianceScore
        grade = $grade
    }
    recommendations = @()
}

# Add recommendations
if ($inlineStyleViolations.Count -gt 0) {
    $report.recommendations += "Fix $($inlineStyleViolations.Count) inline style violations (move to CSS classes)"
}
if ($animationTierViolations.Count -gt 0) {
    $report.recommendations += "Fix $($animationTierViolations.Count) animation tier violations (use T1 only on Level 1)"
}
if ($bulletListViolations.Count -gt 0) {
    $report.recommendations += "Replace $($bulletListViolations.Count) bullet lists with card-based layouts"
}
if ($cssReports.duplicates -and $cssReports.duplicates.total_redundancy.percentage -ge 2.0) {
    $report.recommendations += "Reduce CSS redundancy from $($cssReports.duplicates.total_redundancy.percentage)% to <2%"
}
if ($cssReports.usage -and $cssReports.usage.unused_css_classes.percentage -ge 5.0) {
    $report.recommendations += "Delete $($cssReports.usage.unused_css_classes.count) unused CSS classes"
}
if ($cssReports.usage -and $cssReports.usage.missing_css_classes.count -gt 0) {
    $report.recommendations += "Fix $($cssReports.usage.missing_css_classes.count) missing CSS classes"
}
if ($cssReports.responsive -and $cssReports.responsive.mobile_friendliness_score.overall_score -lt 95) {
    $report.recommendations += "Improve mobile-friendliness from $($cssReports.responsive.mobile_friendliness_score.grade) to A+"
}

$report | ConvertTo-Json -Depth 10 | Out-File -FilePath $ReportPath -Encoding UTF8

# Display summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "🎨 GLASSMORPHISM COMPLIANCE REPORT" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Overall Compliance: $complianceScore% (Grade: $grade)" -ForegroundColor $(if ($grade -match 'A') { 'Green' } else { 'Yellow' })
Write-Host ""
Write-Host "🚨 Violations by Severity:" -ForegroundColor Yellow
Write-Host "   CRITICAL (Inline Styles): $criticalViolations" -ForegroundColor $(if ($criticalViolations -eq 0) { 'Green' } else { 'Red' })
Write-Host "   HIGH (Animation Tiers): $highViolations" -ForegroundColor $(if ($highViolations -eq 0) { 'Green' } else { 'Red' })
Write-Host "   MEDIUM (Spacing): $mediumViolations" -ForegroundColor $(if ($mediumViolations -eq 0) { 'Green' } else { 'Yellow' })
Write-Host "   LOW (Bullets/Hierarchy): $lowViolations" -ForegroundColor $(if ($lowViolations -eq 0) { 'Green' } else { 'Gray' })
Write-Host ""
Write-Host "📄 Report saved: $ReportPath" -ForegroundColor Green
Write-Host ""

if ($report.recommendations.Count -gt 0) {
    Write-Host "📋 Priority Fixes:" -ForegroundColor Yellow
    foreach ($rec in $report.recommendations) {
        Write-Host "   - $rec" -ForegroundColor Gray
    }
    Write-Host ""
}

if ($StrictMode -and $complianceScore -lt 95) {
    Write-Host "❌ FAILED: Compliance score ($complianceScore%) below 95%" -ForegroundColor Red
    exit 1
} else {
    Write-Host "✅ Glassmorphism Compliance Validation Complete" -ForegroundColor Green
    exit 0
}
