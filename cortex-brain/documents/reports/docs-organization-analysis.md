# Documentation Organization Analysis

**Generated:** 2026-01-03  
**Tool:** CORTEX Documentation Organizer v1.0.0  
**Status:** ✅ Analysis Complete

---

## 📊 Executive Summary

The docs/ folder has been analyzed for organizational compliance. Here's what was found:

### Root-Level Files
- ✅ **8 files** properly at root (infrastructure/essential pages)
- 📦 **4 files** need to be moved to subfolders
- ⚠️ **0 files** need manual review

### Link Graph
- 📄 **199 HTML files** scanned
- 🔗 **160 files** properly linked in navigation
- 🚫 **39 files** orphaned (not linked anywhere)

---

## 🎯 Recommended Actions

### 1. Move Root-Level Files (AUTOMATED)

These files will be automatically moved when you run the script:

| File | Current Location | Target Location |
|------|------------------|-----------------|
| `dashboard-diagnostic.html` | `docs/` | `docs/lens/diagnostics/` |
| `test-tabs.html` | `docs/` | `docs/prototypes/` |
| `testing-planning-orchestrator.md` | `docs/` | `docs/development/testing/` |
| `visual-differentiation-demo.html` | `docs/` | `docs/prototypes/` |

**Action:** Run `.\cortex-toolkit\docs-organizer.ps1 -DryRun $false`

### 2. Orphaned Files (REQUIRES REVIEW)

**39 orphaned files** were detected in 5 categories:

#### Story Chapters (13 files) - NEEDS NAVIGATION
These story chapters aren't accessible from the main story viewer:
- Chapter-01 through Chapter-13
- Prologue

**Recommendation:** Either:
- Add navigation links in `story/viewer.html` 
- Archive if deprecated content

#### Old/Backup Files (6 files) - SAFE TO DELETE
- `architecture/index-old.html`
- `lens/index-old.html`
- `toolkit-manager/index-old.html`
- `token-optimization/index-old.html`
- `getting-started/index-old.html`
- `knowledge/index-old.html`

**Recommendation:** Delete with `-DeleteOrphans` flag

#### Duplicates (2 files) - SAFE TO DELETE
Content duplicated in `technical/` folder:
- `technical/orchestrators/architectural-review.html`
- `technical/orchestrators/ado-planning.html`

**Recommendation:** Keep main versions, delete duplicates

#### Prototypes (2 files) - ARCHIVE OR LINK
- `prototypes/home-redesign-v2.html`
- `prototypes/mega-menu-prototype.html`

**Recommendation:** Archive if not needed for reference

#### Other (16 files) - MANUAL REVIEW
Various unlinked content files that need individual assessment:
- DDD fundamentals pages
- Testing pages (TDD, BDD)
- Best practices index
- Future roadmap
- ROI calculator
- Validation pages
- Technical security dashboard

**Recommendation:** Review each and either add to navigation or archive

---

## 🚀 Quick Start Guide

### Step 1: Preview (Safe - No Changes)
```powershell
.\cortex-toolkit\docs-organizer.ps1
```

### Step 2: Execute File Moves
```powershell
.\cortex-toolkit\docs-organizer.ps1 -DryRun $false
```

### Step 3: Review Orphans
Check the JSON report:
```
cortex-brain/documents/reports/docs-cleanup-20260103.json
```

### Step 4: Delete Old Files (Optional)
```powershell
.\cortex-toolkit\docs-organizer.ps1 -DryRun $false -DeleteOrphans
```

---

## 📋 What Gets Preserved

These files will **always stay at root**:
- `index.html` - Main landing page
- `faq.html` - FAQ page
- `sitemap.html` - Site map
- `search-index.json` - Search index
- `404.md` - GitHub Pages 404
- `README.md` - Repository README
- `DEPLOYMENT.md` - Deployment guide
- `QUICK-LAUNCH.md` - Quick launch guide

---

## 🔗 What Gets Updated

When files are moved, the script automatically updates:
- All `href=""` references in HTML files
- All `src=""` references (images, scripts)
- Relative path resolution (`../`, `./`)
- Parent → Child navigation
- Child → Parent navigation

**Example:**
```html
<!-- Before -->
<a href="dashboard-diagnostic.html">Diagnostic</a>

<!-- After -->
<a href="lens/diagnostics/dashboard-diagnostic.html">Diagnostic</a>
```

---

## 📁 Archive Strategy

Orphaned files are moved (not deleted) to:
```
docs/archives/cleanup-YYYYMMDD-HHMMSS/
```

This allows recovery if needed. Files can be manually deleted later.

---

## 🎯 Next Steps

1. **Run the organizer** to move misplaced root files
2. **Review story chapters** - add navigation or archive
3. **Delete old/backup files** using `-DeleteOrphans`
4. **Assess "Other" category** - add links or archive
5. **Test the site** locally to verify all changes
6. **Commit changes** to Git

---

## 📊 Detailed Report

Full analysis saved to:
```
cortex-brain/documents/reports/docs-cleanup-20260103.json
```

This JSON report contains:
- Complete link graph
- All orphaned files with paths
- Planned file moves
- Link update list
- Categorized orphan breakdown

---

## 🔄 Repeatability

This script can be run repeatedly:
- **Safe:** Dry-run mode by default
- **Idempotent:** Won't break already-organized structure
- **Additive:** Add new rules to `$MoveMap` anytime
- **Tracked:** JSON reports create audit trail

Add to your maintenance workflow:
```powershell
# Weekly docs health check
.\cortex-toolkit\docs-organizer.ps1 | Out-File "logs/docs-health-$(Get-Date -Format 'yyyyMMdd').txt"
```

---

## 📚 Documentation

Full documentation: `cortex-toolkit/docs/docs-organizer.md`

---

**Status:** Ready for execution  
**Risk:** Low (dry-run default, archiving enabled, full audit trail)  
**Impact:** High (clean structure, working navigation, maintainable docs)
