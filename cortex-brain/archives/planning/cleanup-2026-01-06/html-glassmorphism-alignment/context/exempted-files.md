# Context: Exempted Files Documentation

**Generated:** 2026-01-04  
**Source:** Phase 4-6 Compliance Assessment

---

## Summary

- **Total Exempted Files:** 5
- **Reason:** Utility/demo pages with intentional non-compliance
- **Effective Compliance:** 100% (315 compliant + 5 exempted)

---

## Exempted Files

### 1. docs/faq.html
**Reason:** False positive (not T1, intentional simple markup)  
**Non-Compliance:** Minimal CSS classes (FAQ-specific structure)  
**Justification:** FAQ pages use simple list structure, glassmorphism not required  
**Maintenance:** No updates needed

### 2. docs/sitemap.html
**Reason:** False positive (not T1, auto-generated)  
**Non-Compliance:** Auto-generated markup without design classes  
**Justification:** Sitemap is auto-generated, primarily for SEO/crawlers  
**Maintenance:** Regenerated automatically, exempt from design standards

### 3. docs/panel-viewer.html
**Reason:** Utility tool (dynamic styles required)  
**Non-Compliance:** Inline styles for dynamic panel rendering  
**Justification:** JavaScript-driven panel viewer requires dynamic inline styles  
**Maintenance:** Intentional inline styles for functionality

### 4. docs/design-system/panel-viewer.html
**Reason:** Dev tool (demonstration purposes)  
**Non-Compliance:** Mixed inline styles for demonstration  
**Justification:** Shows developers how to use panels, includes examples  
**Maintenance:** Educational tool, intentional non-compliance

### 5. docs/design-system/glassmorphism-guide.html
**Reason:** Educational examples (shows before/after)  
**Non-Compliance:** Contains non-compliant examples for teaching  
**Justification:** Educational page shows non-compliant patterns with corrections  
**Maintenance:** Intentionally includes non-compliant examples for comparison

---

## Compliance Report Reference

- **Report:** `reports/compliance-report-20260104_065344.json`
- **CSV:** `reports/non-compliant-files-20260104_065344.csv`
- **Tool:** `cortex-toolkit/check-glassmorphism-compliance.ps1`

---

## Verification

All 5 exempted files have been:
- ✅ Individually analyzed
- ✅ Exemption reason documented
- ✅ Approved for exemption
- ✅ Listed in compliance exemptions report

**Effective Compliance Rate:** 100%  
**True Non-Compliance:** 0 files
