# 📋 CORTEX Documentation Cleanup Strategic Plan

**Generated:** 2026-01-03  
**Orchestrator:** cortex-doc-cleanup  
**Status:** 🟡 READY FOR EXECUTION

---

## 📊 Executive Summary

| Metric | Count | Severity |
|--------|-------|----------|
| **Total HTML Files** | 360 | ℹ️ INFO |
| **Orphaned Files** | 86 | 🔴 HIGH |
| **Broken Links** | 638 | 🔴 CRITICAL |
| **Unused Assets** | 71 | 🟡 MEDIUM |

---

## 🎯 Strategic Actions (Priority Order)

### **PRIORITY 1: Archive Consolidation** 🔥

**Problem:** Nested archive directories creating exponential broken links  
**Example:** `archives/cleanup-20260103-090641/archives/cleanup-20260103-071436/archives/cleanup-20260103-070859/`

**Action:**
```powershell
# Remove nested archives older than latest snapshot
Remove-Item "docs/archives/cleanup-*/archives" -Recurse -Force
```

**Impact:** Eliminates ~400 broken links from nested archive references

---

### **PRIORITY 2: Prototype Relocation** 🔧

**Problem:** 32 prototype files orphaned in `docs/prototypes/` not linked from main site

**Prototypes to Archive:**
- `prototypes/orchestrators/*.html` (11 files)
- `prototypes/security/*.html` (13 files)
- `prototypes/lens/index.html`
- `prototypes/sts/index.html`
- `prototypes/token-optimization/index.html`
- `prototypes/toolkit-manager/index.html`
- `prototypes/knowledge/index.html`

**Action:**
```powershell
# Move to archives with timestamp
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
Move-Item "docs/prototypes" "docs/archives/prototypes-$timestamp"
```

**Impact:** Reduces orphaned files by 32

---

### **PRIORITY 3: Validation Stub Cleanup** 📝

**Problem:** Orphaned validation stubs not linked from sitemap

**Files:**
- `validation/capabilities.html`
- `validation/metrics.html`

**Options:**
1. **Link from sitemap** (if content is valuable)
2. **Archive** (if outdated)
3. **Delete** (if placeholder)

**Recommended:** Archive (likely superseded by actual implementation)

---

### **PRIORITY 4: CSS Path Corrections** 🎨

**Problem:** Incorrect relative paths in subdirectories

**Pattern Found:**
```html
<!-- WRONG (in knowledge/security/*.html) -->
<link rel="stylesheet" href="../assets/css/variables.css">

<!-- CORRECT -->
<link rel="stylesheet" href="../../assets/css/variables.css">
```

**Files Affected:**
- `sharpen-the-saw/*.html` (7 files)
- `knowledge/**/*.html` (multiple subdirectories)

**Action:** Run automated path fixer script

---

### **PRIORITY 5: Unused Asset Cleanup** 🗑️

**Categories:**
- **Images:** 34 unused PNGs/JPGs
- **CSS:** 12 unused stylesheets
- **JS:** 8 unused scripts
- **Fonts:** 17 unused font files

**Action:** 
1. Generate detailed unused asset report
2. Manual review (some may be dynamically loaded)
3. Archive before deletion (safety net)

---

## 🚀 Execution Phases

### **Phase 1: Safety Preparation** ✈️
- [x] Run dry-run scan
- [x] Generate strategic plan
- [ ] Create full backup
- [ ] Git checkpoint

### **Phase 2: Archive Consolidation** 🗂️
- [ ] Identify nested archive depths
- [ ] Remove nested archives (keep only top-level)
- [ ] Verify no critical content lost
- [ ] Re-scan broken links

### **Phase 3: Prototype Relocation** 📦
- [ ] Catalog all prototypes
- [ ] Move to timestamped archive
- [ ] Update any internal references
- [ ] Re-scan orphaned files

### **Phase 4: CSS Path Fixes** 🔧
- [ ] Generate path correction script
- [ ] Test on 3 sample files
- [ ] Batch apply corrections
- [ ] Re-scan broken links

### **Phase 5: Validation Cleanup** ✅
- [ ] Review validation stub content
- [ ] Archive if outdated
- [ ] Update sitemap if keeping

### **Phase 6: Asset Optimization** 🖼️
- [ ] Generate detailed asset usage report
- [ ] Manual review flagged assets
- [ ] Archive unused assets
- [ ] Optionally delete after 30 days

### **Phase 7: Verification** 🔍
- [ ] Re-run full documentation scan
- [ ] Validate 0 broken links
- [ ] Validate <10 orphaned files
- [ ] Generate final report

### **Phase 8: Git Integration** 🌳
- [ ] Commit with detailed message
- [ ] Tag as `docs-cleanup-2026-01-03`
- [ ] Update CHANGELOG

---

## 📈 Expected Outcomes

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Broken Links** | 638 | <50 | 92% reduction |
| **Orphaned Files** | 86 | <10 | 88% reduction |
| **Unused Assets** | 71 | <20 | 72% reduction |
| **Archive Size** | — | ~150 files | Organized |

---

## 🛡️ Safety Measures

1. **Full Git Backup:** Create branch `docs-cleanup-backup-2026-01-03`
2. **Archive Before Delete:** Never delete without archiving
3. **Incremental Validation:** Re-scan after each phase
4. **Rollback Plan:** Keep archives for 60 days minimum

---

## 🔍 Root Cause Analysis

### Why Did This Happen?

1. **Nested Cleanup Runs:** Previous cleanup runs archived entire `docs/` folder recursively
2. **Prototype Drift:** Prototypes created but never promoted or archived
3. **Relative Path Errors:** Developers unaware of correct path depth
4. **No Link Validation:** Missing pre-commit hook for link checking

### Prevention Strategies

1. **Pre-Commit Hook:** Add link validation to `.git/hooks/pre-commit`
2. **CI/CD Integration:** GitHub Actions to validate docs on PR
3. **Prototype Lifecycle:** Formal promotion/archive process
4. **Archive Policy:** Flat structure, no nested archives

---

## 📝 Next Steps

**RECOMMENDED:** Execute Phase 2 (Archive Consolidation) first as it has highest impact (400+ broken links resolved).

**Command to Start:**
```powershell
# Create backup branch
git checkout -b docs-cleanup-backup-2026-01-03
git push origin docs-cleanup-backup-2026-01-03

# Return to main branch
git checkout CORTEX4-refactor

# Begin execution
python scripts/doc_cleanup_executor.py --phase 2 --dry-run
```

---

**Report Generated By:** CORTEX Documentation Cleanup Orchestrator v1.0.0  
**Author:** Asif Hussain  
**Copyright © 2026 Asif Hussain. All rights reserved.**
