# CORTEX5 Enhancement Epic - Structure Review

**Date:** 2026-01-06  
**Status:** 🔴 NEEDS CLEANUP  
**Location:** `cortex-brain/documents/planning/active/cortex5-enhancement-epic`

---

## 🎯 Current State

### ✅ Correct Structure (Keep)
```
cortex5-enhancement-epic/
├── README.md                           # ✅ Master readme
├── A19-cortex-50-remedi-with.md       # ✅ Plan document
├── CORTEX5-SNOWBALL.md                # ✅ Tracking doc
├── PHASE-0.5-COMPLETE.md              # ✅ Milestone marker
├── analysis/                           # ✅ Standard folder
├── context/                            # ✅ Standard folder
└── reports/                            # ✅ Standard folder
```

### 🔴 Incorrect Structure (Fix Required)

**Problem 1: Child Plans Nested Inside Epic**
These should NOT be subfolders - they violate the epic/child hierarchy:
```
❌ c5-epic-from-p1/              → Should be separate plan at active/ level
❌ c5-epic-phase-1/              → Should be separate plan at active/ level
❌ c5-epic-w-phase-1/            → Should be separate plan at active/ level
❌ c5-plan-epic-from/            → Should be separate plan at active/ level
❌ fix-plan-folder-place/        → Should be separate plan at active/ level
❌ inv-plan-folder-bug/          → Should be separate plan at active/ level
❌ script-consol-gov/            → Should be separate plan at active/ level
❌ tdd-plan-orch-struct/         → Should be separate plan at active/ level
❌ test-epic-child-place/        → Should be separate plan at active/ level
```

**Problem 2: Duplicate Documents**
```
❌ FIX-PLAN-FOLDER-PLACEMENT.md          → Redundant (covered by fix-plan-folder-place/)
❌ GOVERNANCE-RULE-SCRIPT-ORGANIZATION.md → Redundant (covered by script-consol-gov/)
❌ INVESTIGATION-REPORT.md               → Move to reports/ subfolder
```

---

## 🛠️ Fix Strategy

### Phase 1: Move Child Plans Out
All child plans should be at `planning/active/` level, not nested inside the epic:

```bash
# These are independent plans, not epic subfolders
mv c5-epic-from-p1/ ../../archives/nested-children/
mv c5-epic-phase-1/ ../../archives/nested-children/
mv c5-epic-w-phase-1/ ../../archives/nested-children/
mv c5-plan-epic-from/ ../../archives/nested-children/
mv fix-plan-folder-place/ ../../archives/nested-children/
mv inv-plan-folder-bug/ ../../archives/nested-children/
mv script-consol-gov/ ../../archives/nested-children/
mv tdd-plan-orch-struct/ ../../archives/nested-children/
mv test-epic-child-place/ ../../archives/nested-children/
```

### Phase 2: Consolidate Documents
```bash
# Move investigation report to proper location
mv INVESTIGATION-REPORT.md reports/structure-investigation-20260106.md

# Remove redundant markdown files (info already in subfolders)
rm FIX-PLAN-FOLDER-PLACEMENT.md
rm GOVERNANCE-RULE-SCRIPT-ORGANIZATION.md
```

### Phase 3: Add Missing Standard Folders
```bash
# Epic should have all 5 standard folders
mkdir -p artifacts/
mkdir -p tracking/
```

---

## ✅ Target Structure

After cleanup, the epic should look like this:

```
cortex5-enhancement-epic/
├── README.md                           # Quick start guide
├── A19-cortex-50-remedi-with.md       # Master plan document
├── CORTEX5-SNOWBALL.md                # Epic tracking
├── PHASE-0.5-COMPLETE.md              # Milestone marker
├── analysis/                           # Deep analysis docs
├── artifacts/                          # Generated files
├── context/                            # Discovery + architecture
│   ├── discovery.md
│   └── architecture-analysis.md
├── reports/                            # Progress reports
│   └── structure-investigation-20260106.md
└── tracking/                           # State tracking
    ├── progress-tracker.json
    └── CONTINUATION-PROMPT.md
```

**Rules:**
- ✅ Epic folder = Parent container only
- ✅ 5 standard subfolders: analysis/, artifacts/, context/, reports/, tracking/
- ✅ Master plan document (A19-*.md)
- ✅ README.md for quick start
- ❌ NO nested child plans (those go in active/ at same level as epic)
- ❌ NO duplicate documentation

---

## 📋 Cleanup Script

See: `cleanup-epic-structure.sh` (next step)

---

## 🎯 Success Criteria

- [ ] All child plans moved to archives (they were continuation attempts)
- [ ] Only 5 standard folders remain (+ root docs)
- [ ] INVESTIGATION-REPORT.md moved to reports/
- [ ] Duplicate .md files removed
- [ ] artifacts/ and tracking/ folders created
- [ ] Epic structure follows Planning System v5 standard

---

**Next Action:** Execute `cleanup-epic-structure.sh` to fix the structure
