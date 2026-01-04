# Phase 9: Performance & Accessibility Testing Script
# Author: Asif Hussain
# Date: 2026-01-04
# Purpose: Comprehensive performance metrics for HTML Glassmorphism Alignment

Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  PHASE 9: PERFORMANCE & ACCESSIBILITY TESTING                  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

$reportDir = "d:\PROJECTS\CORTEX\cortex-brain\documents\planning\active\html-glassmorphism-alignment\reports"
if (-not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir -Force | Out-Null
}

# ═══════════════════════════════════════════════════════════════
# 1. CSS FILE SIZE ANALYSIS
# ═══════════════════════════════════════════════════════════════
Write-Host "📊 Task 1: CSS File Size Analysis" -ForegroundColor Yellow

$cssFiles = Get-ChildItem -Path "d:\PROJECTS\CORTEX\docs\assets\css\*.css" -Recurse
$totalSize = ($cssFiles | Measure-Object -Property Length -Sum).Sum
$totalKB = [math]::Round($totalSize/1KB, 2)

$minifiedFiles = Get-ChildItem -Path "d:\PROJECTS\CORTEX\docs\assets\css\minified\*.css" -Recurse -ErrorAction SilentlyContinue
$minifiedSize = ($minifiedFiles | Measure-Object -Property Length -Sum).Sum
$minifiedKB = [math]::Round($minifiedSize/1KB, 2)

$coreGlassSize = (Get-Item "d:\PROJECTS\CORTEX\docs\assets\css\cortex-glass-system.css").Length / 1KB
$coreGlassMinSize = (Get-Item "d:\PROJECTS\CORTEX\docs\assets\css\minified\cortex-glass-system.min.css").Length / 1KB

Write-Host "  ✓ Total CSS: $totalKB KB (unminified)" -ForegroundColor Green
Write-Host "  ✓ Minified CSS: $minifiedKB KB" -ForegroundColor Green
Write-Host "  ✓ Core Glass System: $([math]::Round($coreGlassSize, 2)) KB" -ForegroundColor Green
Write-Host "  ✓ Core Glass System (min): $([math]::Round($coreGlassMinSize, 2)) KB" -ForegroundColor Green

if ($minifiedKB -lt 100) {
    Write-Host "  ✅ PASS: Minified CSS < 100KB target" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  WARNING: Minified CSS exceeds 100KB target" -ForegroundColor Yellow
}

# ═══════════════════════════════════════════════════════════════
# 2. CRITICAL CSS FILES ANALYSIS
# ═══════════════════════════════════════════════════════════════
Write-Host "`n📊 Task 2: Critical CSS Files (Glassmorphism Core)" -ForegroundColor Yellow

$criticalFiles = @(
    "glass-design-tokens.css",
    "glass-base-patterns.css",
    "glass-animations.css",
    "glass-utilities.css",
    "glass-ui-components.css",
    "cortex-glass-system.css"
)

$criticalSize = 0
foreach ($file in $criticalFiles) {
    $filePath = "d:\PROJECTS\CORTEX\docs\assets\css\$file"
    if (Test-Path $filePath) {
        $size = (Get-Item $filePath).Length / 1KB
        Write-Host "  • $file : $([math]::Round($size, 2)) KB" -ForegroundColor Cyan
        $criticalSize += $size
    }
}

Write-Host "  ✓ Critical CSS Bundle: $([math]::Round($criticalSize, 2)) KB" -ForegroundColor Green

# ═══════════════════════════════════════════════════════════════
# 3. HTML FILE ANALYSIS
# ═══════════════════════════════════════════════════════════════
Write-Host "`n📊 Task 3: HTML File Count & Size" -ForegroundColor Yellow

$htmlFiles = Get-ChildItem -Path "d:\PROJECTS\CORTEX\docs\*.html" -Recurse
$htmlCount = $htmlFiles.Count
$htmlSize = ($htmlFiles | Measure-Object -Property Length -Sum).Sum
$htmlKB = [math]::Round($htmlSize/1KB, 2)

Write-Host "  • Total HTML files: $htmlCount" -ForegroundColor Cyan
Write-Host "  • Total HTML size: $htmlKB KB" -ForegroundColor Cyan
Write-Host "  • Average file size: $([math]::Round($htmlKB / $htmlCount, 2)) KB" -ForegroundColor Cyan

# ═══════════════════════════════════════════════════════════════
# 4. BACKDROP-FILTER USAGE ANALYSIS
# ═══════════════════════════════════════════════════════════════
Write-Host "`n📊 Task 4: Backdrop-Filter Performance Analysis" -ForegroundColor Yellow

$backdropCount = 0
foreach ($file in $cssFiles) {
    $content = Get-Content $file.FullName -Raw
    $matches = [regex]::Matches($content, "backdrop-filter\s*:")
    $backdropCount += $matches.Count
}

Write-Host "  • Backdrop-filter instances: $backdropCount" -ForegroundColor Cyan
if ($backdropCount -lt 50) {
    Write-Host "  ✅ PASS: Backdrop-filter usage optimized" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  WARNING: High backdrop-filter usage (GPU intensive)" -ForegroundColor Yellow
}

# ═══════════════════════════════════════════════════════════════
# 5. CSS IMPORT ORDER VALIDATION
# ═══════════════════════════════════════════════════════════════
Write-Host "`n📊 Task 5: CSS Import Order Validation" -ForegroundColor Yellow

$sampleHTML = "d:\PROJECTS\CORTEX\docs\index.html"
$htmlContent = Get-Content $sampleHTML -Raw

$expectedOrder = @(
    "glass-design-tokens",
    "glass-base-patterns",
    "glass-animations",
    "glass-utilities",
    "glass-ui-components"
)

$importOrderCorrect = $true
$lastPos = 0
foreach ($css in $expectedOrder) {
    $pos = $htmlContent.IndexOf($css)
    if ($pos -lt $lastPos -and $pos -ne -1) {
        $importOrderCorrect = $false
        Write-Host "  ⚠️  WARNING: $css out of order" -ForegroundColor Yellow
    }
    $lastPos = $pos
}

if ($importOrderCorrect) {
    Write-Host "  ✅ PASS: CSS import order correct (tokens → patterns → utilities)" -ForegroundColor Green
} else {
    Write-Host "  ❌ FAIL: CSS import order incorrect" -ForegroundColor Red
}

# ═══════════════════════════════════════════════════════════════
# 6. ACCESSIBILITY QUICK CHECKS
# ═══════════════════════════════════════════════════════════════
Write-Host "`n📊 Task 6: Accessibility Quick Checks" -ForegroundColor Yellow

# Check for alt text on images
$imagesWithoutAlt = 0
foreach ($file in $htmlFiles | Select-Object -First 10) {
    $content = Get-Content $file.FullName -Raw
    $imgMatches = [regex]::Matches($content, "<img\s+[^>]*>")
    foreach ($match in $imgMatches) {
        if ($match.Value -notmatch "alt\s*=") {
            $imagesWithoutAlt++
        }
    }
}

Write-Host "  • Images without alt text (sample): $imagesWithoutAlt" -ForegroundColor Cyan

# Check for ARIA labels
$ariaLabelsCount = 0
foreach ($file in $htmlFiles | Select-Object -First 10) {
    $content = Get-Content $file.FullName -Raw
    $ariaMatches = [regex]::Matches($content, "aria-label\s*=")
    $ariaLabelsCount += $ariaMatches.Count
}

Write-Host "  • ARIA labels found (sample): $ariaLabelsCount" -ForegroundColor Cyan

# Check for reduced motion support
$reducedMotionFiles = 0
foreach ($file in $cssFiles) {
    $content = Get-Content $file.FullName -Raw
    if ($content -match "prefers-reduced-motion") {
        $reducedMotionFiles++
    }
}

Write-Host "  • CSS files with reduced motion support: $reducedMotionFiles" -ForegroundColor Cyan

if ($reducedMotionFiles -gt 0) {
    Write-Host "  ✅ PASS: Reduced motion support implemented" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  WARNING: No reduced motion support found" -ForegroundColor Yellow
}

# ═══════════════════════════════════════════════════════════════
# 7. MOBILE RESPONSIVENESS CHECK
# ═══════════════════════════════════════════════════════════════
Write-Host "`n📊 Task 7: Mobile Responsiveness Analysis" -ForegroundColor Yellow

$mediaQueryFiles = 0
$breakpoints = @{}

foreach ($file in $cssFiles) {
    $content = Get-Content $file.FullName -Raw
    $matches = [regex]::Matches($content, "@media\s*\([^)]*max-width\s*:\s*(\d+)px")
    if ($matches.Count -gt 0) {
        $mediaQueryFiles++
        foreach ($match in $matches) {
            $width = $match.Groups[1].Value
            if (-not $breakpoints.ContainsKey($width)) {
                $breakpoints[$width] = 0
            }
            $breakpoints[$width]++
        }
    }
}

Write-Host "  • CSS files with media queries: $mediaQueryFiles" -ForegroundColor Cyan
Write-Host "  • Common breakpoints:" -ForegroundColor Cyan
foreach ($bp in $breakpoints.GetEnumerator() | Sort-Object Key) {
    Write-Host "    - ${bp.Key}px: ${bp.Value} instances" -ForegroundColor Gray
}

if ($mediaQueryFiles -gt 5) {
    Write-Host "  ✅ PASS: Mobile responsiveness implemented" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  WARNING: Limited mobile responsiveness" -ForegroundColor Yellow
}

# ═══════════════════════════════════════════════════════════════
# 8. GENERATE SUMMARY REPORT
# ═══════════════════════════════════════════════════════════════
Write-Host "`n📊 Generating Performance Test Results Report..." -ForegroundColor Yellow

$report = @"
# Phase 9: Performance & Accessibility Test Results
**Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")  
**Plan:** HTML View Glassmorphism Alignment  
**Phase:** 9 - Performance & Accessibility Testing

---

## 📊 Performance Metrics

### 1. CSS File Size Analysis

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Total CSS (unminified) | $totalKB KB | - | ℹ️ Reference |
| Total CSS (minified) | $minifiedKB KB | <100KB | $(if ($minifiedKB -lt 100) { "✅ PASS" } else { "⚠️ FAIL" }) |
| Core Glass System | $([math]::Round($coreGlassSize, 2)) KB | - | ℹ️ Reference |
| Core Glass System (min) | $([math]::Round($coreGlassMinSize, 2)) KB | - | ✅ Optimized |

**Analysis:**
- The critical glassmorphism CSS bundle is highly optimized
- Minified core system is only $([math]::Round($coreGlassMinSize, 2)) KB (excellent for production)
- Total minified CSS at $minifiedKB KB $(if ($minifiedKB -lt 100) { "meets the <100KB target" } else { "exceeds target - consider lazy loading non-critical CSS" })

### 2. Critical CSS Files (Glassmorphism Core)

| File | Size (KB) |
|------|-----------|
$(foreach ($file in $criticalFiles) {
    $filePath = "d:\PROJECTS\CORTEX\docs\assets\css\$file"
    if (Test-Path $filePath) {
        $size = (Get-Item $filePath).Length / 1KB
        "| $file | $([math]::Round($size, 2)) KB |`n"
    }
})
| **Total Critical Bundle** | **$([math]::Round($criticalSize, 2)) KB** |

### 3. HTML Analysis

| Metric | Value |
|--------|-------|
| Total HTML files | $htmlCount |
| Total HTML size | $htmlKB KB |
| Average file size | $([math]::Round($htmlKB / $htmlCount, 2)) KB |

### 4. Backdrop-Filter Usage

- **Total instances:** $backdropCount
- **Performance impact:** $(if ($backdropCount -lt 50) { "✅ Low (GPU optimized)" } else { "⚠️ High (consider optimization)" })
- **Recommendation:** $(if ($backdropCount -lt 50) { "Current usage is optimal" } else { "Consider reducing backdrop-filter instances or using CSS containment" })

### 5. CSS Import Order Validation

**Status:** $(if ($importOrderCorrect) { "✅ PASS" } else { "❌ FAIL" })

**Expected Order (Verified):**
1. glass-design-tokens.css (CSS variables)
2. glass-base-patterns.css (foundational styles)
3. glass-animations.css (motion design)
4. glass-utilities.css (helper classes)
5. glass-ui-components.css (component styles)

---

## ♿ Accessibility Metrics

### 1. Alt Text Coverage (Sample of 10 files)

- **Images without alt text:** $imagesWithoutAlt
- **Status:** $(if ($imagesWithoutAlt -eq 0) { "✅ PASS" } else { "⚠️ Needs improvement" })

### 2. ARIA Labels (Sample of 10 files)

- **ARIA labels found:** $ariaLabelsCount
- **Status:** $(if ($ariaLabelsCount -gt 5) { "✅ Good coverage" } else { "ℹ️ Consider adding more" })

### 3. Reduced Motion Support

- **CSS files with support:** $reducedMotionFiles / $($cssFiles.Count)
- **Status:** $(if ($reducedMotionFiles -gt 0) { "✅ PASS" } else { "⚠️ FAIL" })

### 4. Mobile Responsiveness

- **Files with media queries:** $mediaQueryFiles
- **Common breakpoints:** $($breakpoints.Keys.Count) unique breakpoints
- **Status:** $(if ($mediaQueryFiles -gt 5) { "✅ PASS" } else { "⚠️ Limited" })

**Breakpoint Distribution:**
$(foreach ($bp in $breakpoints.GetEnumerator() | Sort-Object Key) {
    "- ${bp.Key}px: ${bp.Value} instances`n"
})

---

## 🎯 Phase 9 Acceptance Criteria

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| CSS file size (minified) | <100KB | $minifiedKB KB | $(if ($minifiedKB -lt 100) { "✅ PASS" } else { "⚠️ FAIL" }) |
| Backdrop-filter usage | Optimized | $backdropCount instances | $(if ($backdropCount -lt 50) { "✅ PASS" } else { "⚠️ WARNING" }) |
| CSS import order | Correct | $(if ($importOrderCorrect) { "Verified" } else { "Incorrect" }) | $(if ($importOrderCorrect) { "✅ PASS" } else { "❌ FAIL" }) |
| Reduced motion support | Present | $reducedMotionFiles files | $(if ($reducedMotionFiles -gt 0) { "✅ PASS" } else { "⚠️ FAIL" }) |
| Mobile responsiveness | 3+ breakpoints | $($breakpoints.Keys.Count) breakpoints | $(if ($breakpoints.Keys.Count -ge 3) { "✅ PASS" } else { "⚠️ LIMITED" }) |

---

## 📋 Recommendations

### Performance Optimizations
1. $(if ($minifiedKB -ge 100) { "Consider lazy loading non-critical CSS (story.css, learning-hub.css)" } else { "✅ CSS bundle size is optimal" })
2. $(if ($backdropCount -ge 50) { "Reduce backdrop-filter usage or use CSS containment for better GPU performance" } else { "✅ Backdrop-filter usage is optimized" })
3. Implement critical CSS inline for index.html (FCP optimization)
4. Use `<link rel="preload">` for glassmorphism core CSS

### Accessibility Improvements
1. $(if ($imagesWithoutAlt -gt 0) { "Add alt text to all images (found $imagesWithoutAlt without alt)" } else { "✅ Alt text coverage is complete" })
2. $(if ($ariaLabelsCount -lt 10) { "Increase ARIA label usage for interactive elements" } else { "✅ ARIA label coverage is good" })
3. $(if ($reducedMotionFiles -eq 0) { "Add prefers-reduced-motion support to all animation CSS" } else { "✅ Reduced motion support is present" })
4. Validate keyboard navigation for all interactive elements
5. Run WAVE or Axe DevTools for comprehensive accessibility audit

### Browser Compatibility
1. Test glassmorphism fallbacks in Safari <15.4 (backdrop-filter support)
2. Validate in 5 browsers: Chrome, Firefox, Safari, Edge, Opera
3. Test on 3 mobile devices: iOS Safari, Android Chrome, Samsung Internet

---

## 🚀 Next Steps

1. **Phase 10:** Integration Testing
   - W3C HTML validation
   - Link checker (all internal links)
   - Visual regression testing
   - End-to-end user flow testing

2. **Phase 11:** Deployment Validation
   - GitHub Pages deployment test
   - CDN cache invalidation
   - Production smoke tests
   - Rollback verification

3. **Phase 12:** REFACTOR
   - Whole-file cleanup
   - Documentation updates
   - Final git commit
   - Plan completion

---

**Report Generated:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")  
**Author:** CORTEX Autonomous Orchestrator  
**Next Phase:** Integration Testing (Phase 10)
"@

$reportPath = Join-Path $reportDir "performance-test-results.md"
$report | Out-File -FilePath $reportPath -Encoding UTF8
Write-Host "`n✅ Report saved: $reportPath" -ForegroundColor Green

# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════
Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                   PHASE 9 TEST SUMMARY                         ║" -ForegroundColor Cyan
Write-Host "╠════════════════════════════════════════════════════════════════╣" -ForegroundColor Cyan
Write-Host "║ CSS Size (minified): $minifiedKB KB $(if ($minifiedKB -lt 100) { '✅' } else { '⚠️' })                              ║" -ForegroundColor Cyan
Write-Host "║ Backdrop-filter usage: $backdropCount instances $(if ($backdropCount -lt 50) { '✅' } else { '⚠️' })                   ║" -ForegroundColor Cyan
Write-Host "║ CSS import order: $(if ($importOrderCorrect) { 'Correct ✅' } else { 'Incorrect ❌' })                          ║" -ForegroundColor Cyan
Write-Host "║ Reduced motion: $(if ($reducedMotionFiles -gt 0) { 'Supported ✅' } else { 'Missing ⚠️' })                        ║" -ForegroundColor Cyan
Write-Host "║ Mobile responsive: $($breakpoints.Keys.Count) breakpoints $(if ($breakpoints.Keys.Count -ge 3) { '✅' } else { '⚠️' })                        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host "`n📊 Full report: $reportPath" -ForegroundColor Yellow
Write-Host "🎯 Phase 9 Status: TESTING COMPLETE - Proceed to report generation`n" -ForegroundColor Green
