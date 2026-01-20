# Phase Consolidation Strategy - Eliminate Sync Issues

## Problem Statement

**Current Architecture** (Two Sources of Truth - BROKEN):
```
cortex-master.yaml (metadata + phase_tracker)
         ↓
      splits
         ↓
_workspaces/roadmap/phases/phase-XX.yaml (detailed specs)
```

**Result**: When either file changes, they fall out of sync:
- Phase YAML shows NOT_STARTED, cortex-master says COMPLETED
- AC-IDs updated in one place but not reflected elsewhere
- Status changes require coordinating edits across 25+ files
- Audits repeatedly fail and require manual sync

**Historical Evidence** (from chat01.md):
- First sync attempt: Discovered 4 phases incorrectly marked COMPLETED
- Completion metrics wrong: 90.7% → 74.2% (50 AC-IDs miscounted)
- Required 2 full passes + manual auditing to achieve basic consistency

---

## Solution: Unified Consolidation

### Phase 1: Immediate (Next Session)

#### 1A. Migrate All Phase Specs INTO cortex-master.yaml

**Structure** (new `phases` section):
```yaml
cortex-master.yaml:
  metadata: {}          # Keep
  ac_breakdown: {}      # Keep
  final_status: {}      # Keep
  
  # NEW: Consolidate all phase specs here
  phases:
    PHASE-01:
      title: "Governance Foundation"
      status: COMPLETED
      locked: true
      ac_ids:
        - id: AC-AR-001-01
          title: "Governance Core Rules"
          status: COMPLETED
          # ... full spec migrated from phase-01.yaml
    
    PHASE-02:
      title: "Orchestration Core"
      status: COMPLETED
      locked: true
      ac_ids:
        - id: AC-ORC-001-01
          # ... full spec
```

**Benefits**:
- Single file to keep in sync
- No more split reads between files
- Atomic phase updates (can't accidentally miss properties)
- Version control shows exactly what changed
- No out-of-sync discoveries during audits

#### 1B. Archive Phase YAML Files

Move to `/Users/asifhussain/PROJECTS/CORTEX/_workspaces/roadmap/_archives/phase-yamls-v1/`:
```
phase-01.yaml → _archives/phase-yamls-v1/phase-01.yaml
phase-02.yaml → _archives/phase-yamls-v1/phase-02.yaml
... (all 27 files)
```

**Keep as read-only reference** for pattern lookups.

---

### Phase 2: Validation Architecture

#### 2A. Create Sync Validator

**File**: `scripts/validate_phase_sync.py`

```python
#!/usr/bin/env python3
"""
Validate that cortex-master.yaml phases section is consistent and complete.

This replaces the need for separate phase YAML files by ensuring:
1. No AC-IDs appear in cortex-master.yaml that aren't defined in phases
2. All status transitions follow valid state machine
3. Locked phases cannot have status changes
4. Total AC-IDs count matches ac_breakdown
"""

def validate_cortex_master():
    # Read cortex-master.yaml
    # For each phase:
    #   - Verify ac_ids all exist and are spelled correctly
    #   - Verify status is valid (NOT_STARTED, IN_PROGRESS, COMPLETED)
    #   - Verify locked:true → status:COMPLETED only
    #   - Verify all ac_ids from ac_breakdown are accounted for
    #   - Verify counts match
    # Return exit code 0 (success) or 1 (failure with errors)
    pass

def auto_sync_repair():
    # If minor mismatches detected:
    #   - Update totals from actual phase counts
    #   - Fix duplicate ac_ids
    #   - Correct typos in phase names
    # Report what was auto-fixed
    pass
```

#### 2B. Create Pre-Commit Hook

**File**: `.git/hooks/pre-commit`

```bash
#!/bin/bash
# Runs before each commit - prevents out-of-sync pushes

python3 scripts/validate_phase_sync.py
if [ $? -ne 0 ]; then
  echo "❌ Sync validation failed. Fix errors and try again."
  echo "   Run: python3 scripts/validate_phase_sync.py --fix"
  exit 1
fi
```

---

### Phase 3: Update Prompts & Agents

#### 3A. Refactor `cortex-builder.prompt.md`

**Key Changes**:

Old (Split Approach):
```markdown
1. Read cortex-master.yaml (metadata)
2. Load _workspaces/roadmap/phases/phase-XX.yaml (spec details)
3. Update both files separately
```

New (Unified Approach):
```markdown
1. Read cortex-master.yaml → phases.PHASE-XX section ONLY
2. Edit phases.PHASE-XX.ac_ids directly in cortex-master.yaml
3. Run: python3 scripts/validate_phase_sync.py
4. Commit (hook validates before accepting)
```

#### 3B. Create New `prompt:phase-unified-builder.md`

**Single Builder Mode** (consolidated):
```markdown
# CORTEX Builder - Unified Phase Mode

All phase operations work with cortex-master.yaml phases section only.

## Phase Update Workflow

1. Load phase from cortex-master.yaml
   ```yaml
   # From cortex-master.yaml
   phases:
     PHASE-XX:
       ac_ids:
         - AC-XXX-XX-01: (spec in same file)
   ```

2. Edit directly in cortex-master.yaml

3. Validate:
   ```bash
   python3 scripts/validate_phase_sync.py
   ```

4. Commit (hook validates)
```

---

## Implementation Roadmap

### Immediate Actions (This Session)

1. **Create consolidation script**: `scripts/consolidate_phases.py`
   - Read all 27 phase YAML files
   - Extract ac_ids, testing, success_criteria sections
   - Generate YAML to append to cortex-master.yaml `phases:` section
   - Backup original phase files to `_archives/`

2. **Update cortex-master.yaml**:
   - Add `phases:` section with all consolidated specs
   - Keep phase_tracker section (use for quick lookup)
   - Update metadata references to point to `phases:` section

3. **Create validation script**: `scripts/validate_phase_sync.py`
   - Detect any inconsistencies
   - Auto-repair where safe
   - Provide detailed report

4. **Update prompts**:
   - Modify `cortex-builder.prompt.md` to reference consolidated approach
   - Create backup of original as `cortex-builder-legacy.prompt.md`

5. **Setup pre-commit hook**: `.git/hooks/pre-commit`
   - Runs validator automatically
   - Prevents out-of-sync commits

---

## Validation Before/After

### Before (Broken)
```
Chat Session 01, Attempt 1:
  - Audited phase YAMLs
  - Found 4 phases incorrectly marked COMPLETE
  - Sync required: 2 full passes + manual fixes
  - Completion metrics: 90.7% → 74.2%
  - Caused by: Split sources, manual sync

Chat Session 01, Attempt 2:
  - Tried to verify phase files
  - New discrepancies found
  - More manual fixes needed
```

### After (Fixed)
```
Single cortex-master.yaml file means:
  - No discovery of mismatches (they can't exist)
  - Edit once → all references automatically consistent
  - Validator catches errors before commit
  - Pre-commit hook prevents broken states
  - Audit complete in single file read
```

---

## File Preservation Policy

**Keep**:
- ✅ cortex-master.yaml (expanded with `phases:` section)
- ✅ `.git/hooks/pre-commit` (validation automation)
- ✅ `scripts/validate_phase_sync.py` (validation tool)

**Archive** (read-only reference):
- 📦 `_workspaces/roadmap/_archives/phase-yamls-v1/` (all 27 phase YAMLs)
- 📦 `_workspaces/roadmap/_archives/cortex-builder-legacy.prompt.md`

**Delete**:
- ❌ Individual phase-XX.yaml files (moved to archives)
- ❌ Phase-update references in legacy prompts

---

## Success Criteria

1. ✅ All 310 AC-IDs consolidated into single `phases:` section
2. ✅ No references to individual phase-XX.yaml files in prompts
3. ✅ Validation script passes 100% checks
4. ✅ Pre-commit hook prevents future desync
5. ✅ Next audit requires single `cortex-master.yaml` read (not 27 files)
6. ✅ Completion metrics remain stable across sessions
7. ✅ No "sync required" discoveries for 3+ months

---

## Rollback Plan

If consolidation causes issues:

```bash
# Restore phase files
cp -r _archives/phase-yamls-v1/ _workspaces/roadmap/phases/

# Restore legacy prompt
cp docs/cortex-builder-legacy.prompt.md .github/prompts/cortex-builder.prompt.md

# Remove validation files
rm scripts/validate_phase_sync.py
rm .git/hooks/pre-commit

# Revert cortex-master.yaml
git checkout cortex-master.yaml
```

---

## Timeline Estimate

- Consolidation script: 1 hour
- Data migration & validation: 1 hour
- Update prompts & hooks: 30 minutes
- Testing & verification: 1 hour
- **Total**: ~3.5 hours

---

## Long-term Benefits

| Metric | Before | After |
|--------|--------|-------|
| Files to keep in sync | 27 | 1 |
| Time to verify state | 30 min | 2 min |
| Manual audit sessions needed | 2-3 per month | 0 |
| Sync errors discovered | Regular | 0 (prevented) |
| Atomic updates possible | No | Yes |
| Single-read audits | No | Yes |

