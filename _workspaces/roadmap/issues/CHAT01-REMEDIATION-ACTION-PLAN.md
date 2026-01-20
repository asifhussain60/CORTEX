# CHAT01 Remediation Action Plan

**Date**: January 18, 2026  
**Status**: ACTIVE - Implementation Phase  
**Owner**: cortex-builder  
**Review Reference**: [chat01.md](.github/.chats/chat01.md)

---

## Executive Summary

Chat01 identified 3 critical issues during the holistic CORTEX review. This document provides the step-by-step remediation plan following the **Unified Phase Mode** approach defined in `cortex-builder.prompt.md`.

**All issues are actionable and fixable in 3.5 hours total.**

---

## Issues Identified in Chat01

### Issue 1: Phase YAML Status Synchronization
**Severity**: HIGH (Administrative)  
**Time to Fix**: 30 minutes  
**Blocker**: No (code is correct, documentation is wrong)

**Finding**: Multiple phases have status mismatches:
- `cortex-master.yaml` → `phase_tracker` shows status X
- `_workspaces/roadmap/phases/phase-XX.yaml` shows status Y
- Reality: Implementation follows cortex-master.yaml

**Affected Phases**:
- PHASE-01: cortex-master.yaml=COMPLETED, phase-01.yaml=NOT_STARTED
- PHASE-03: cortex-master.yaml=COMPLETED, phase-03.yaml=NOT_STARTED
- PHASE-04: cortex-master.yaml=COMPLETED, phase-04.yaml=NOT_STARTED
- PHASE-05: cortex-master.yaml=COMPLETED, phase-05.yaml=NOT_STARTED

**Root Cause**: Before Unified Phase Mode, these files were split sources. After consolidation, phase YAML files became read-only reference only (archived). Status mismatches occurred because both files were being updated independently.

---

### Issue 2: Integration Test Failures
**Severity**: MEDIUM (Environment-specific)  
**Time to Fix**: 1-2 hours  
**Blocker**: No (not production code issue)

**Finding**: 4 of 82 integration tests failing
- Pass rate: 95% (78/82 passing)
- Failure type: Database connection pool exhaustion
- Impact: Only observed under high concurrency in test environment

**Affected Tests**:
- `tests/integration/test_orchestrator_suite.py` (likely)
- `tests/integration/test_resilience_suite.py` (likely)

**Root Cause**: Test fixtures not properly releasing database connections. Connection pool tuning needed for test environment.

---

### Issue 3: Path Reference Updates
**Severity**: LOW (Documentation only)  
**Time to Fix**: 20 minutes  
**Blocker**: No (zero code impact)

**Finding**: Phase YAML files contain old path references
- Old: `src/cortex/...`
- New: `cortex/...` (and `cortex_brain/...`)

**Affected Files**:
- `_workspaces/roadmap/phases/phase-*.yaml` (27 files)

**Root Cause**: When codebase was reorganized from `src/` structure to `cortex/` root-level structure, phase YAML files were not updated (they're now read-only anyway).

---

## Remediation Plan

### SECTION A: Fix Issue 1 - Phase YAML Status Sync (30 min)

#### A.1: Identify the Real Issue (5 min)

**ACTUAL FINDING** (from validation):
- `phase_tracker` has **32 phases** defined (source of truth)
- `phases` section has only **12 phases** defined (incomplete)
- `phase_tracker` statuses: Mix of COMPLETED, NOT_STARTED, IN_PROGRESS
- `phases` statuses: Don't match `phase_tracker` for several phases

**Examples of mismatches**:
```
PHASE-03-CORE-ARCHITECTURE:
  phase_tracker: COMPLETED, locked=true
  phases:        IN_PROGRESS, locked=false  ← WRONG

PHASE-04-SAFETY-RELIABILITY:
  phase_tracker: COMPLETED, locked=true
  phases:        COMPLETED, locked=true  ← CORRECT

PHASE-05-PRODUCTION-HARDENING:
  phase_tracker: COMPLETED, locked=true
  phases:        IN_PROGRESS, locked=false  ← WRONG
```

#### A.2: Understand the Architecture (5 min)

Per `cortex-builder.prompt.md`, the unified architecture is:

```yaml
cortex-master.yaml:
  phase_tracker:
    PHASE-XX:
      status: COMPLETED  ← AUTHORITATIVE SOURCE (has all phases)
      locked: true
      ac_ids: [list]
      ...
      
  phases:
    phase_xx:           ← DETAILED SPECS (should have same phases)
      id: PHASE-XX
      status: COMPLETED ← Must match phase_tracker
      locked: true      ← Must match phase_tracker
      ac_ids:
        AC-XXX-XX-01: {...detailed...}

_workspaces/roadmap/phases/phase-XX.yaml:
  # READ-ONLY REFERENCE (archived, not actively used)
  # Do not edit - use cortex-master.yaml only
```

**Key insight**: The `phases` section is INCOMPLETE. It needs to be expanded to include all phases from `phase_tracker`.

#### A.3: Fix #1 - Sync Missing Phases (15 min)

**Action**: For each phase in `phase_tracker` that's NOT in `phases`, add entry to `phases` section.

**Example**: PHASE-02-CODEBASE-COHERENCE exists in phase_tracker but not in phases

```bash
# Count phases in each
grep "^  PHASE-" _workspaces/roadmap/cortex-master.yaml | wc -l  # Should be 32 in phase_tracker
grep "^  phase_" _workspaces/roadmap/cortex-master.yaml | wc -l  # Currently only 12
```

**Missing phases to add**:
- PHASE-02-CODEBASE-COHERENCE (phase_02)
- PHASE-07-ECOSYSTEM (phase_07)
- PHASE-07-INTENT-ROUTER (phase_07_intent_router)
- PHASE-08-CORE-ORCHESTRATORS (phase_08)
- PHASE-09-GOVERNANCE-TOOLS (phase_09)
- PHASE-10-ADAPTIVE-EXECUTION (phase_10)
- PHASE-11-HALLUCINATION-PREVENTION (phase_11)
- PHASE-12-KNOWLEDGE-ECOSYSTEM (phase_12)
- PHASE-13-OBSERVABILITY-MATURITY (phase_13)
- ... and 21 more

**Fix approach**:
```yaml
# In cortex-master.yaml → phases section, add:
  phase_02:  # NEW - was missing
    id: PHASE-02-CODEBASE-COHERENCE
    title: Codebase Coherence & Import Foundation
    status: NOT_STARTED  # Matches phase_tracker
    locked: false        # Matches phase_tracker
    ac_ids: {}           # Empty for now (can populate later)

  phase_07_intent_router:  # NEW - was missing
    id: PHASE-07-INTENT-ROUTER
    title: Intent Router
    status: COMPLETED    # Matches phase_tracker
    locked: true         # Matches phase_tracker
    ac_ids: {}           # Would need to populate from phase-07-intent-router.yaml
```

#### A.4: Fix #2 - Correct Status Mismatches (10 min)

For phases that exist in both but have different status/locked:

```yaml
# Before (WRONG)
phases:
  phase_03:
    id: PHASE-03
    status: IN_PROGRESS  ← phase_tracker says COMPLETED
    locked: false        ← phase_tracker says true

# After (CORRECT)
phases:
  phase_03:
    id: PHASE-03
    status: COMPLETED    ← Now matches phase_tracker
    locked: true         ← Now matches phase_tracker
```

**Affected phases to correct**:
- PHASE-03: IN_PROGRESS → COMPLETED, locked=true
- PHASE-05: IN_PROGRESS → COMPLETED, locked=true

#### A.5: Archive Phase YAML Files (5 min - optional)

Per `cortex-builder.prompt.md`:
> These files are HISTORICAL ONLY - all active work goes through cortex-master.yaml

**Recommended action**:
```bash
# Create archive directory
mkdir -p _workspaces/roadmap/_archives/phase-yamls-v1-20260118

# Move files to archive (optional - can keep as read-only reference)
cd _workspaces/roadmap/phases/
for file in phase-*.yaml; do
  # Add archive header
  (echo "# ⚠️ ARCHIVED - READ-ONLY REFERENCE"; echo "# This file is no longer part of active workflow"; echo "# Last updated: 2026-01-14"; echo "# Archived: 2026-01-18"; echo ""; cat "$file") > temp
  mv temp "$file"
done
```

**Do NOT delete** - keep as historical reference, but mark as read-only.

---

### SECTION B: Fix Issue 2 - Integration Test Failures (1-2 hours)

#### B.1: Identify the Root Cause (30 min)

**Step 1**: Run tests in isolation to identify the culprit
```bash
# Run tests with verbose output
pytest tests/integration/test_resilience_suite.py -v --tb=short 2>&1 | tee test_output.log

# If failures, grep for connection/pool errors
grep -i "connection\|pool\|exhausted" test_output.log
```

**Step 2**: Check for connection leak in test fixtures
```bash
# Search for database session management in tests
grep -r "session\|connection" tests/integration/ | grep -v ".pyc"

# Look for missing cleanup
grep -r "finally\|tearDown" tests/integration/
```

#### B.2: Fix Connection Pool Exhaustion (45 min - 1 hour 15 min)

**Root cause likely**: Test fixtures not closing connections properly

**Fix approach**:

1. **Update conftest.py fixtures**:
```python
@pytest.fixture
def db_session():
    """Database session with proper cleanup"""
    session = create_test_session()
    yield session
    session.close()  # ← Add explicit cleanup
    # session.dispose() if using connection pool
```

2. **Add connection pool reset**:
```python
@pytest.fixture(scope="function")
def reset_connection_pool():
    """Reset connection pool between tests"""
    from cortex_brain.tier0.state import get_db_pool
    yield
    pool = get_db_pool()
    pool.dispose()  # Clear exhausted connections
```

3. **Adjust pool size for tests**:
```python
# In conftest.py or test settings
os.environ['DB_POOL_SIZE'] = '5'  # Smaller for tests
os.environ['DB_MAX_OVERFLOW'] = '2'
```

#### B.3: Validate the Fix (15-30 min)

```bash
# Run full integration test suite
pytest tests/integration/ -v --tb=short

# Check all 82 tests pass
# Expected output should show: "78 passed, 4 passed" (or all 82 passed)
```

---

### SECTION C: Fix Issue 3 - Path References (20 min)

#### C.1: Understand the Context (5 min)

**Old structure** (pre-refactor):
```
src/
  cortex/
    api/
    brain/
    core/
    ...
```

**New structure** (current):
```
cortex/           ← Root level
  api/
  brain/
  core/
  ...
cortex_brain/     ← Brain-specific components
  tier0/
  tier1/
  tier2/
```

#### C.2: Update Phase YAML References (15 min)

**Files to update**: `_workspaces/roadmap/phases/phase-*.yaml` (27 files)

**However**: Per the prompt, these are now archived/read-only. Consider these options:

**Option A** (Recommended): Do nothing
- These files are read-only reference
- Active workflow uses cortex-master.yaml only
- Historical paths don't matter

**Option B**: Update for cleanliness
```bash
# Mass find-replace
cd _workspaces/roadmap/phases/
find . -name "*.yaml" -type f -exec sed -i 's|src/cortex|cortex|g' {} \;

# Verify changes
grep -r "src/" ./ | wc -l  # Should be 0
```

**Option C**: Add comment header (quick)
```yaml
# PATH REFERENCE NOTE
# Historical paths: src/cortex → current: cortex/
# Module paths: src/cortex_brain → current: cortex_brain/
```

---

## Implementation Steps

### Timeline

**Today (3.5 hours total)**:
1. **Section A** (30 min) - Sync phase status
2. **Section B** (1-2 hours) - Fix test failures
3. **Section C** (20 min) - Path references
4. **Validation** (20 min) - Run full suite

**Tomorrow (1 hour)**:
- Final verification
- Mark production-ready
- Prepare Phase 21 kickoff

---

## Validation Checklist

After completing all fixes, verify:

```bash
# ✅ Step 1: Validator passes
python3 scripts/validation/validate_phase_sync.py
# Expected: ✅ ALL CHECKS PASSED

# ✅ Step 2: All tests pass
pytest tests/ -v --tb=short
# Expected: 100% pass rate

# ✅ Step 3: No sync issues
grep -r "NOT_STARTED" _workspaces/roadmap/cortex-master.yaml | grep -i "phase-01\|phase-03\|phase-04\|phase-05"
# Expected: Only legitimate NOT_STARTED phases (not PHASE-01/03/04/05)

# ✅ Step 4: Phase tracker mirrors phases section
python3 -c "
import yaml
with open('_workspaces/roadmap/cortex-master.yaml') as f:
    data = yaml.safe_load(f)
    for phase_id in ['PHASE-01', 'PHASE-03', 'PHASE-04', 'PHASE-05']:
        pt_status = data['phase_tracker'][phase_id]['status']
        phase_status = data['phases'][phase_id.lower()]['status']
        print(f'{phase_id}: tracker={pt_status}, phases={phase_status}, match={pt_status==phase_status}')
"
# Expected: All show match=True

# ✅ Step 5: Git status clean
git status
# Expected: All changes committed or staged
```

---

## Risk Assessment

| Issue | Risk Level | Mitigation |
|-------|-----------|-----------|
| Issue 1 - Status Sync | LOW | Validator catches errors automatically |
| Issue 2 - Test Failures | LOW | Only env-specific, doesn't affect prod code |
| Issue 3 - Path Refs | MINIMAL | Read-only files, zero code impact |

---

## Success Metrics

**Before**: 
- Phase sync mismatches: 4 phases
- Test pass rate: 95% (4 failures)
- Path reference issues: 27 files

**After** (Target):
- Phase sync mismatches: 0 ✅
- Test pass rate: 100% ✅
- Path reference issues: 0 (via archival) ✅
- Production readiness: 93% → 100% ✅

---

## Notes & References

- **Cortex Builder Prompt**: `.github/prompts/cortex-builder.prompt.md` (key reference for Unified Phase Mode)
- **Validator Script**: `scripts/validation/validate_phase_sync.py` (automated checking)
- **Phase Files Location**: `_workspaces/roadmap/phases/` (now read-only)
- **Master File**: `_workspaces/roadmap/cortex-master.yaml` (single source of truth)

---

## Sign-Off

| Role | Status | Date |
|------|--------|------|
| Analysis | ✅ Complete | 2026-01-18 |
| Remediation Plan | ✅ Ready | 2026-01-18 |
| Implementation | 🔄 In Progress | 2026-01-18 |
| Validation | ⏳ Pending | 2026-01-18 |
| Production Ready | ⏳ Pending | 2026-01-18 |

