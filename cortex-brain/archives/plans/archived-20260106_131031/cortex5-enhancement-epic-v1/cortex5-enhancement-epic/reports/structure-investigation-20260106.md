# Investigation Report: Planning Active Directory Issues

**Date:** 2026-01-06  
**Investigator:** CORTEX Investigation v2  
**Target:** `cortex-brain/documents/planning/active`

---

## 🔍 Symptom Analysis

### Issues Identified

1. **Duplicate UUID-based Folders**
   - Multiple `plan-{UUID}` folders (12+ instances)
   - Violates meaningful naming convention (max 22 chars, kebab-case)
   - Examples: `plan-6aea5ec9-e4dc-4bf5-8a12-f69b6387451a`, `plan-355839c2-fe08-4223-98b1-b5f3e20088a4`

2. **Orphaned Child Plans**
   - Child plans nested incorrectly (e.g., `a19-continue-cortex5/`, `a19-script-consol-govern/`)
   - Should be at top level `planning/active/`, not inside parent epic
   - Violates parent-child hierarchy rules

3. **Naming Convention Violations**
   - Some folders exceed 22 character limit
   - Examples: `continue-cortex5-enhancement-epic-phase-1`, `test-epic-child-placement-feature-inside-cortex5`
   - Mix of `a19-` prefix (meaningful) vs `plan-{UUID}` (non-meaningful)

4. **Folder Structure Issues**
   - Inconsistent subfolder structure
   - Some have `integration/` and `features/` (non-standard)
   - Missing proper 5-subfolder standard: `analysis/`, `artifacts/`, `context/`, `reports/`, `tracking/`

5. **Nested Plan Explosion**
   - Epic has 30+ child folders, many are duplicates or continuations
   - Suggests continuation prompt issues

---

## 🎯 Root Cause Analysis

### Primary Causes

1. **Planning System v5 Implementation Gaps**
   - UUID generation fallback when meaningful name extraction fails
   - Child plan placement logic doesn't respect parent directory
   - Continuation logic creates new plans instead of resuming

2. **Folder Manager Issues**
   - `plan_folder_manager.py` has syntax errors (line 206)
   - Prevents proper folder validation and cleanup

3. **Migration from v4 to v5**
   - Legacy plans with old structure not migrated
   - Continuation prompts reference old paths

---

## 🛠️ Fix Strategy

### Phase 1: Safe Cleanup (Manual Review Required)

#### Safe to Delete (Duplicates/Empty)
```bash
# UUID-based plans (appear to be duplicates)
plan-2514c1f2-41f1-4750-8432-97cbebec669e/
plan-355839c2-fe08-4223-98b1-b5f3e20088a4/
plan-35c44312-780a-4a1f-9eee-86d8aac425d4/
plan-4992d565-d1fc-4699-b548-09deb4816ba3/
plan-53d9a58a-5f63-496f-a492-8a6f5ae033db/
plan-5ef62288-0f08-459a-8192-43aae89f31bf/
plan-6aea5ec9-e4dc-4bf5-8a12-f69b6387451a/
plan-a0b87693-6ca5-41f8-b8cc-7b1d4b18f69a/
plan-b5987583-d2e3-4da6-9fd6-f7a974db2bb8/
plan-bf90cb61-1746-44bb-9ec7-1aecf6c7e596/
plan-e0210d37-92fe-4a70-a17d-85d520455939/
plan-f85bd2af-ba45-4057-a9d6-4306f8c58681/
```

#### Consolidate (Move to Top Level)
```bash
# Child plans that should be at planning/active/ level
a19-continue-cortex5/          → move to ../
a19-continue-plan-cortex5/     → move to ../
a19-continue-plan-plan/        → move to ../
a19-fix-for-incorr-plan/       → move to ../
a19-invest-plan-folder/        → move to ../
a19-script-consol-govern/      → move to ../
a19-tdd-planning-orch/         → move to ../
a19-test-epic-child/           → move to ../
```

#### Rename (Naming Convention Violations)
```bash
# Exceeds 22 chars - needs truncation
continue-cortex5-enhancement-epic-phase-1/              → c5-epic-phase-1/
continue-cortex5-enhancement-epic-with-phase-1/         → c5-epic-w-phase-1/
continue-cortex5-enhancement-epic-from-phase-1--/       → c5-epic-from-p1/
continue-plan-cortex5-enhancement-epic-from/            → c5-plan-epic-from/
fix-for-incorrect-plan-folder-placement---child/        → fix-plan-folder-place/
investigate-plan-folder-path-bug---child-plans/         → inv-plan-folder-bug/
test-epic-child-placement-feature-inside-cortex5/       → test-epic-child-place/
script-consolidation-governance-for/                    → script-consol-gov/
tdd-planning-orchestrator-folder-structure/             → tdd-plan-orch-struct/
```

### Phase 2: Standardize Structure

All plans MUST have this structure:
```
{plan-name}/
├── A19-{plan-name}.md          # Master plan (max 22 chars)
├── README.md                    # Quick start
├── analysis/                    # Deep analysis
├── artifacts/                   # Generated artifacts
├── context/                     # Discovery + architecture
│   ├── discovery.md
│   └── architecture-analysis.md
├── reports/                     # Progress reports
└── tracking/                    # State tracking
    ├── progress-tracker.json
    └── CONTINUATION-PROMPT.md
```

**Remove non-standard folders:**
- `integration/` (should be in `artifacts/` or `context/`)
- `features/` (should be in `analysis/` or `reports/`)

### Phase 3: Prevention Mechanisms

1. **Fix Syntax Errors**
   - `src/utils/plan_folder_manager.py:206`
   - Blocks proper validation

2. **Update Planning System v5**
   - Enforce 22-char limit during name extraction
   - Add validation before folder creation
   - Improve continuation prompt logic (resume vs new plan)

3. **Add Pre-Commit Hook**
   - Validate folder names (kebab-case, ≤22 chars)
   - Check 5-subfolder structure
   - Prevent nested plans in wrong locations

---

## 📋 Cleanup Script

See: `cleanup-planning-active.sh` (created next)

---

## ✅ Success Criteria

- [ ] All UUID-based plans removed
- [ ] Child plans moved to proper locations
- [ ] All folder names ≤22 chars, kebab-case
- [ ] Standard 5-subfolder structure enforced
- [ ] Syntax errors fixed in plan_folder_manager.py
- [ ] Pre-commit validation added

---

**Next Steps:**
1. Review this report
2. Execute cleanup script (dry-run first)
3. Fix syntax errors
4. Implement prevention mechanisms
