# HTML Regeneration Context

## 🎯 Objective

Delete and recreate 32 invalid HTML files following `docgen.prompt.md` guidelines to achieve 100% glassmorphism compliance and proper HTML5 structure.

## 📋 Requirements

### Critical Principles from docgen.prompt.md

1. **File Regeneration (Section 1.5):**
   - ✅ CORRECT: Delete first, then create fresh
   - ❌ WRONG: Partial update or replace_string_in_file on HTML

2. **Glassmorphism Enforcement (Section 2):**
   - ALL pages link to: `<link rel="stylesheet" href="../assets/css/main.css">`
   - ❌ FORBIDDEN: Inline `style=""` attributes (except story button image)
   - ❌ FORBIDDEN: Page-specific `<style>` tags
   - ❌ FORBIDDEN: Alternate CSS files in subdirectories

3. **Feature Benefit Panels (Section 3):**
   Every feature/orchestrator page MUST start with feature-benefit-panel div

4. **HTML Quality Tools (Section 2.5):**
   - Remove inline styles: `python3 cortex-toolkit/documentation/html-tools/html_style_centralizer.py`
   - Validate syntax: `python3 cortex-toolkit/documentation/html-tools/html_validator.py`

## 📊 Current State

**Total Files:** 58 HTML files  
**✅ Valid:** 26 (45%)  
**❌ Invalid:** 32 (55%)

### Error Breakdown
- **Self-closing </br> tags:** 17 files (~60 instances)
- **Invalid </img> closing tags:** 10 files
- **Mismatched tag structure:** 4 files
- **Missing closing angle brackets:** 8 files

## 🎯 Success Criteria

1. ✅ All 58 HTML files pass html5lib validation
2. ✅ Zero inline styles (centralized CSS)
3. ✅ Feature-benefit panels on all orchestrator pages
4. ✅ WCAG 2.1 Level AA accessibility compliance
5. ✅ Proper HTML5 semantic structure

---

**Last Updated:** December 27, 2025  
**Status:** Phase 4 Complete (All files validated)
