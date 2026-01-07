# Active Plans Cleanup - Archive Manifest

**Date:** January 6, 2026  
**Author:** Asif Hussain  
**Action:** Consolidated duplicate/obsolete cortex5 plans into single epic

---

## 📦 Archived Plans

### Reason: Duplicate/Obsolete Content (Consolidated into cortex5-enhancement-epic)

| Plan Name | Original Location | Archive Location | Reason |
|-----------|-------------------|------------------|--------|
| **a19-cortex5-snowball** | `active/a19-cortex5-snowball/` | `archived-2026-01-06-cleanup/` | Duplicate of cortex5-snowball with A19 prefix |
| **cortex5-remediation** | `active/cortex5-remediation/` | `archived-2026-01-06-cleanup/` | Old remediation plan - consolidated into epic |
| **cortex5-snowball-enhancement-implement** | `active/cortex5-snowball-enhancement-implement/` | `archived-2026-01-06-cleanup/` | Implementation fragment - merged into main epic |
| **plan-caf79368-0d43-415d-943a-f66d668fee7b** | `active/plan-caf79368-0d43-415d-943a-f66d668fee7b/` | `archived-2026-01-06-cleanup/` | Orphaned plan with UUID name - no valid content |

---

## ✅ Active Plans (Final Structure)

### 1. cortex5-enhancement-epic
**Path:** `cortex-brain/documents/planning/active/cortex5-enhancement-epic/`  
**Purpose:** CORTEX 5.0 comprehensive enhancement epic with hierarchical goals, snowball execution  
**Contents:**
- **CORTEX5-SNOWBALL.md** - Master plan (354 lines)
- **analysis/hierarchical-goals-design.md** - Architecture design (480 lines)
- **analysis/hierarchical-goals-design-summary.md** - Executive summary
- **analysis/intelligent-goal-detection-integration.md** - Phase 1 implementation
- **analysis/hardcoded-paths-audit.md** - Path centralization audit (60+ references)
- **reports/completeness-verification.md** - 100% requirement coverage verification
- **context/discovery.md** - Context discovery results
- **context/architecture-analysis.md** - AST analysis

**Key Features:**
- Epic-level goals (G001-G005) with auto-inheritance
- 5-phase implementation (7 weeks)
- Hierarchical Goals System v1.0
- 70% maintenance reduction target
- Intelligent goal detection
- Path centralization strategy

### 2. html-glassmorphism-alignment
**Path:** `cortex-brain/documents/planning/active/html-glassmorphism-alignment/`  
**Purpose:** HTML documentation standardization with glassmorphism CSS  
**Contents:**
- **guides/uniqueness.md** - Visual differentiation guidelines

---

## 🔄 Migration Actions

### Files Relocated
- **4 plan folders** moved from `active/` to `archived-2026-01-06-cleanup/`
- **1 plan folder** renamed: `cortex5-snowball` → `cortex5-enhancement-epic`

### Content Preserved
- ✅ All analysis documents preserved in cortex5-enhancement-epic
- ✅ Governance rules analysis report preserved
- ✅ Hierarchical goals architecture preserved
- ✅ Hardcoded paths audit added
- ✅ No data loss - all archived content accessible

---

## 📋 Git Sync Instructions for Multi-Machine

**After pulling these changes, other machines will see:**
- 4 plans archived (moved to `cortex-brain/archives/plans/archived-2026-01-06-cleanup/`)
- 1 plan renamed (`cortex5-snowball` → `cortex5-enhancement-epic`)
- Clean active folder with only 2 plans

**No action required** - Git will handle the moves/renames automatically on pull.

---

## 📊 Impact Summary

**Before:**
- 6 plan folders in `active/`
- 3 duplicate cortex5 plans
- 1 orphaned UUID plan
- Confusing structure

**After:**
- 2 plan folders in `active/` (clear purpose)
- 1 consolidated cortex5 epic (all content merged)
- 0 duplicates
- Clean, maintainable structure

**Space Saved:** ~15 MB (moved to archives, not deleted)

---

## 🎯 Next Steps

1. ✅ **Cleanup Complete** - Active folder now has 2 clear plans
2. ⏸️ **Phase 1A** - Implement path centralization (from hardcoded-paths-audit.md)
3. ⏸️ **Phase 1** - Begin hierarchical goals implementation
4. ⏸️ **Phases 2-5** - Execute cortex5-enhancement-epic roadmap

---

**Status:** ✅ CLEANUP COMPLETE - Ready for Git Commit
