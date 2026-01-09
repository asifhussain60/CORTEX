# CLEANUP TODO - CORTEX 6.0 Acceptance Criteria Consolidation

**Created:** 2026-01-09  
**Priority:** P1_HIGH  
**Status:** PENDING

---

## 🎯 Objective

Run a cleanup cycle on the `.asif/AI-Learning/` folder to:
1. Remove obsolete acceptance criteria files
2. Consolidate relevant content into canonical location
3. Update all references to point to new location
4. Archive historical files properly

---

## 📋 Cleanup Tasks

### Task 1: Review and Archive `.asif/AI-Learning/cortex6/`
**Status:** PENDING

**Files to Review:**
- [ ] `00-PROGRESS.md` - Archive or delete if superseded
- [ ] `AUTONOMOUS-EXECUTION-PLAN.md` - Archive or delete
- [ ] `EXECUTIVE-SUMMARY.md` - Archive or delete
- [ ] `analysis/` folder - Review for relevant content
- [ ] `architecture/` folder - Review for relevant content
- [ ] `epics/` folder - Review for relevant content
- [ ] `reports/` folder - Review for relevant content
- [ ] `requirements/` folder - Review for relevant content
- [ ] `source-of-truth/` folder - Review for relevant content
- [ ] `validation/` folder - Review for relevant content

**Action:** Archive to `cortex-brain/archives/planning/cortex6-legacy-20260109/` or delete if obsolete

---

### Task 2: Review and Archive `.asif/AI-Learning/cortex6-fixes/`
**Status:** PENDING

**Files to Review:**
- [ ] `00-CURRENT-STATUS.md` - Archive
- [ ] `00-INDEX.md` - Archive
- [ ] `00-PROGRESS-DASHBOARD.yaml` - Archive
- [ ] `00-REMEDIATION-MASTER-PLAN.yaml` - Compare with canonical, archive
- [ ] `00-VISUAL-SUMMARY.md` - Archive
- [ ] `P0-*.yaml` through `P6-*.md` - Archive as completed work
- [ ] `reports/` folder - Archive completed reports
- [ ] All `*SUMMARY*.md`, `*GUIDE*.md` - Archive

**Action:** Archive to `cortex-brain/archives/planning/cortex6-fixes-20260109/`

---

### Task 3: Verify Canonical References
**Status:** PENDING

**Files to Update (if needed):**
- [x] `.github/prompts/cortex-search.prompt.md` - ✅ UPDATED
- [x] `.github/prompts/cortex-align.prompt.md` - ✅ ALREADY CORRECT
- [ ] `.github/prompts/CORTEX.prompt.md` - Check if referencing old paths
- [ ] `.github/copilot-instructions.md` - Check if referencing old paths
- [ ] Any other prompts in `.github/prompts/`

**Canonical Location:**
```
cortex-brain/documents/planning/active/cortex6/acceptance-criteria/
├── 00-CORTEX6-ENTERPRISE-ACCEPTANCE-CRITERIA.yaml
├── remediation-plan.yaml
├── snowball-strategy.yaml
├── README.md
└── archive/
```

---

### Task 4: Update Source of Truth References
**Status:** PENDING

**Check these files for old references:**
- [ ] `cortex-brain/TRUTH-SOURCES.yaml`
- [ ] `cortex-brain/config/*.yaml`
- [ ] `src/orchestrators/*.py` - Check for hardcoded AC paths

---

### Task 5: Vacuum Orchestrator Run
**Status:** PENDING

**Execute:**
```
/CORTEX vacuum --target .asif/AI-Learning/cortex6
/CORTEX vacuum --target .asif/AI-Learning/cortex6-fixes
```

**Goals:**
- Identify orphaned files
- Detect duplicate content
- Suggest archive candidates
- Generate cleanup report

---

## 🔄 Execution Order (Snowball)

1. **Task 3** - Verify references (prevents broken links)
2. **Task 4** - Update source of truth references
3. **Task 1** - Archive cortex6 folder
4. **Task 2** - Archive cortex6-fixes folder
5. **Task 5** - Run vacuum to verify cleanup

---

## ✅ Completion Criteria

- [ ] All acceptance criteria consolidated in canonical location
- [ ] All prompts reference `cortex-brain/documents/planning/active/cortex6/acceptance-criteria/`
- [ ] `.asif/AI-Learning/cortex6*` folders archived or deleted
- [ ] No orphaned references to old paths
- [ ] Vacuum report shows clean state

---

## 📁 Archive Structure (Target)

```
cortex-brain/archives/planning/
├── cortex6-legacy-20260109/           # From .asif/AI-Learning/cortex6
│   ├── source-of-truth/
│   ├── analysis/
│   └── ...
└── cortex6-fixes-20260109/            # From .asif/AI-Learning/cortex6-fixes
    ├── P0-P6 phase files
    ├── reports/
    └── ...
```

---

## 🚀 Next Action

Run cleanup when ready:
```
/CORTEX cleanup --target .asif/AI-Learning --archive
```

Or use vacuum for analysis first:
```
/CORTEX vacuum --scope .asif/AI-Learning --dry-run
```

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
