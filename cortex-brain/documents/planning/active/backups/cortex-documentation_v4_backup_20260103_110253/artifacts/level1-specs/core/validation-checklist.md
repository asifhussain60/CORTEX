# Validation Checklist - CORTEX Documentation Site

**Version:** 4.0.0 | **Last Updated:** January 2, 2026  
**Copyright © 2026 Asif Hussain. All rights reserved.**

---

## 🎯 Pre-Deployment Validation

### 1. Design Standards Validation

**Zero Inline Styles Check:**
```bash
# Check for inline styles (MUST return 0)
grep -r 'style="' docs/security/*.html | wc -l
grep -r 'style="' docs/orchestrators/*.html | wc -l
grep -r 'style="' docs/sts/*.html | wc -l

# Expected: 0 for all commands
```

**Hardcoded Colors Check:**
```bash
# Check for hardcoded hex colors in HTML (MUST return 0)
grep -rE '#[0-9a-fA-F]{6}' docs/security/*.html | grep -v 'href=' | grep -v 'content=' | wc -l
grep -rE '#[0-9a-fA-F]{6}' docs/orchestrators/*.html | grep -v 'href=' | grep -v 'content=' | wc -l
grep -rE '#[0-9a-fA-F]{6}' docs/sts/*.html | grep -v 'href=' | grep -v 'content=' | wc -l

# Expected: 0 for all commands
```

**CSS Variable Usage Check:**
```bash
# Validate CSS variable usage (SHOULD find multiple)
grep -r 'var(--' docs/security/*.html | wc -l
grep -r 'var(--' docs/orchestrators/*.html | wc -l
grep -r 'var(--' docs/sts/*.html | wc -l

# Expected: >50 across all pages
```

**Glassmorphism Classes Check:**
```bash
# Check for glassmorphism classes
grep -rE 'class="[^"]*glass-card' docs/security/*.html | wc -l
grep -rE 'class="[^"]*glass-card' docs/orchestrators/*.html | wc -l
grep -rE 'class="[^"]*glass-card' docs/sts/*.html | wc -l

# Expected: >13 for Security, >15 for Orchestrators, >6 for STS
```

**T1 Animation Classes Check:**
```bash
# Check for T1 animation classes
grep -rE 'class="[^"]*animation-t1' docs/security/*.html | wc -l
grep -rE 'class="[^"]*animation-t1' docs/orchestrators/*.html | wc -l
grep -rE 'class="[^"]*animation-t1' docs/sts/*.html | wc -l

# Expected: >13 for Security, >15 for Orchestrators, >6 for STS
```

---

### 2. Responsive Design Validation

**Breakpoint Testing:**
```bash
# Test at required breakpoints
# - 375px (iPhone SE)
# - 768px (iPad)
# - 1024px (Laptop)
# - 1440px (Desktop)
# - 1920px (4K)

# Use browser DevTools responsive mode
```

**Touch Target Validation:**
```bash
# Ensure all interactive elements are at least 44x44px
# Use browser DevTools to inspect button/link dimensions
```

---

### 3. Visualization Validation

**Mermaid Diagram Check:**
```bash
# Verify all Mermaid diagrams render correctly
# Look for <div class="mermaid"> elements

grep -r 'class="mermaid"' docs/**/*.html | wc -l

# Expected: >50 across all pages
```

**D3.js Visualization Check:**
```bash
# Verify D3.js visualization containers exist
# Look for id attributes matching viz patterns

grep -rE 'id="[^"]*-viz"' docs/**/*.html | wc -l

# Expected: >30 across Security/Orchestrators pages
```

---

### 4. Performance Validation

**Page Load Time:**
```bash
# All pages should load <3s on 3G connection
# Use Chrome DevTools Network tab (Slow 3G throttling)

# Expected: <3000ms for initial load
```

**Asset Size Check:**
```bash
# Check total page size
du -h docs/security/*.html
du -h docs/orchestrators/*.html
du -h docs/sts/*.html

# Expected: <50KB per page (HTML only)
```

---

### 5. Accessibility Validation

**ARIA Labels:**
```bash
# Check for ARIA labels on interactive elements
grep -r 'aria-label' docs/**/*.html | wc -l

# Expected: >100 across all pages
```

**Alt Text on Images:**
```bash
# Check for alt attributes on images
grep -r '<img' docs/**/*.html | grep -v 'alt=' | wc -l

# Expected: 0 (all images must have alt text)
```

**Keyboard Navigation:**
```bash
# Manual test: Tab through all interactive elements
# Ensure focus indicators are visible
# Ensure all actions accessible via keyboard
```

---

### 6. Content Validation

**Broken Links Check:**
```bash
# Check for broken internal links
# Use link checker tool or manual verification

find docs -name "*.html" -exec grep -H 'href="' {} \; | grep -v 'http' | cut -d':' -f2 | sort -u

# Verify each relative link resolves
```

**Missing Images:**
```bash
# Check for missing image files
find docs -name "*.html" -exec grep -oP 'src="\K[^"]+' {} \; | sort -u | while read img; do
    [ -f "docs/$img" ] || echo "Missing: $img"
done

# Expected: No output (all images exist)
```

---

### 7. Cross-Browser Validation

**Browser Compatibility Matrix:**

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | Latest | ⏳ Test |
| Firefox | Latest | ⏳ Test |
| Safari | Latest | ⏳ Test |
| Edge | Latest | ⏳ Test |

**Manual Testing Required:**
- [ ] Chrome: All visualizations render correctly
- [ ] Firefox: Glass effects display properly
- [ ] Safari: CSS Grid layout works
- [ ] Edge: No console errors

---

## 📊 Success Metrics

### Expected Results Summary

| Validation Check | Expected | Critical? |
|------------------|----------|-----------|
| **Inline Styles** | 0 | ✅ YES |
| **Hardcoded Colors** | 0 | ✅ YES |
| **CSS Variables** | >50 | ⚠️ WARN |
| **Glass Cards** | >34 | ✅ YES |
| **T1 Animations** | >34 | ⚠️ WARN |
| **Mermaid Diagrams** | >50 | ⚠️ WARN |
| **D3.js Visualizations** | >30 | ⚠️ WARN |
| **Page Load Time** | <3s | ⚠️ WARN |
| **ARIA Labels** | >100 | ⚠️ WARN |
| **Broken Links** | 0 | ✅ YES |
| **Missing Images** | 0 | ✅ YES |

---

## 🚀 Automated Validation Script

**PowerShell Script:** `validate_docs.ps1`

```powershell
# CORTEX Documentation Validation Script
param(
    [string]$DocsPath = "D:\PROJECTS\CORTEX\docs"
)

Write-Host "🔍 CORTEX Documentation Validation" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

$results = @{
    Passed = 0
    Failed = 0
    Warnings = 0
}

# Test 1: Inline Styles
Write-Host "Test 1: Inline Styles..." -NoNewline
$inlineStyles = (Get-ChildItem "$DocsPath" -Recurse -Filter "*.html" | Select-String 'style="').Count
if ($inlineStyles -eq 0) {
    Write-Host " ✅ PASS" -ForegroundColor Green
    $results.Passed++
} else {
    Write-Host " ❌ FAIL ($inlineStyles found)" -ForegroundColor Red
    $results.Failed++
}

# Test 2: Hardcoded Colors
Write-Host "Test 2: Hardcoded Colors..." -NoNewline
$hardcodedColors = (Get-ChildItem "$DocsPath" -Recurse -Filter "*.html" | Select-String '#[0-9a-fA-F]{6}' | Where-Object { $_.Line -notmatch 'href=|content=' }).Count
if ($hardcodedColors -eq 0) {
    Write-Host " ✅ PASS" -ForegroundColor Green
    $results.Passed++
} else {
    Write-Host " ❌ FAIL ($hardcodedColors found)" -ForegroundColor Red
    $results.Failed++
}

# Test 3: CSS Variables
Write-Host "Test 3: CSS Variables..." -NoNewline
$cssVars = (Get-ChildItem "$DocsPath" -Recurse -Filter "*.html" | Select-String 'var\(--').Count
if ($cssVars -gt 50) {
    Write-Host " ✅ PASS ($cssVars found)" -ForegroundColor Green
    $results.Passed++
} else {
    Write-Host " ⚠️  WARN ($cssVars found, expected >50)" -ForegroundColor Yellow
    $results.Warnings++
}

# Test 4: Glass Card Classes
Write-Host "Test 4: Glass Card Classes..." -NoNewline
$glassCards = (Get-ChildItem "$DocsPath" -Recurse -Filter "*.html" | Select-String 'glass-card').Count
if ($glassCards -gt 34) {
    Write-Host " ✅ PASS ($glassCards found)" -ForegroundColor Green
    $results.Passed++
} else {
    Write-Host " ❌ FAIL ($glassCards found, expected >34)" -ForegroundColor Red
    $results.Failed++
}

# Test 5: Broken Links
Write-Host "Test 5: Broken Links..." -NoNewline
$brokenLinks = 0
Get-ChildItem "$DocsPath" -Recurse -Filter "*.html" | ForEach-Object {
    $content = Get-Content $_.FullName -Raw
    $links = [regex]::Matches($content, 'href="([^"]+\.html)"')
    foreach ($link in $links) {
        $target = $link.Groups[1].Value
        if (-not $target.StartsWith('http')) {
            $fullPath = Join-Path (Split-Path $_.FullName) $target
            if (-not (Test-Path $fullPath)) {
                $brokenLinks++
            }
        }
    }
}
if ($brokenLinks -eq 0) {
    Write-Host " ✅ PASS" -ForegroundColor Green
    $results.Passed++
} else {
    Write-Host " ❌ FAIL ($brokenLinks broken links)" -ForegroundColor Red
    $results.Failed++
}

# Summary
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "VALIDATION SUMMARY" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan
Write-Host "✅ Passed:  $($results.Passed)" -ForegroundColor Green
Write-Host "❌ Failed:  $($results.Failed)" -ForegroundColor Red
Write-Host "⚠️  Warnings: $($results.Warnings)" -ForegroundColor Yellow

if ($results.Failed -eq 0) {
    Write-Host "`n🎉 ALL CRITICAL TESTS PASSED!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n⛔ VALIDATION FAILED - Fix issues above" -ForegroundColor Red
    exit 1
}
```

---

## 📋 Manual Validation Checklist

### Pre-Deployment Final Checks

- [ ] **All automated tests pass** (run `validate_docs.ps1`)
- [ ] **Visual inspection** of each page
- [ ] **Cross-browser testing** (Chrome, Firefox, Safari, Edge)
- [ ] **Responsive design testing** (375px, 768px, 1024px, 1440px, 1920px)
- [ ] **Visualization testing** (all Mermaid diagrams render)
- [ ] **Interactive element testing** (all D3.js visualizations work)
- [ ] **Navigation testing** (all links work)
- [ ] **Accessibility testing** (keyboard navigation, screen reader)
- [ ] **Performance testing** (page load <3s)
- [ ] **Documentation review** (content accuracy)

---

**Validation Status:** Ready for use  
**Last Updated:** January 2, 2026
