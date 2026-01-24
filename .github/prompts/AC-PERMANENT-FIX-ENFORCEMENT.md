# AC-PERMANENT-FIX Enforcement Guide

**Version:** 1.0 | **Updated:** 2026-01-24 | **Authority:** cortex-total-recall.prompt.md v5.0

---

## 🎯 Purpose

Enforce permanent fixes to prevent regressions of critical issues tracked in AC-PERMANENT-FIX commits.

**Key Pattern:** Once a permanent fix is implemented and verified, the system **MUST NEVER revert it** without explicit acknowledgment and override.

---

## 📋 Active Permanent Fixes (4 Total)

### AC-PERMANENT-FIX-001: Orchestrator Registry Unwiring

**Problem:**
- Registry auto-regeneration causing all orchestrator wiring to be lost on every git pull
- Recurring issue preventing Phase 1 deployment

**Root Cause:**
- `setup_cortex_hub.py` auto-generating `registry_template: true`
- Creates empty template instead of preserving production wiring

**Solution (Permanent):**
- Set `registry_template: false` in `cortex_brain/tier0/repo-registry.yaml`
- Populate with all 23 orchestrators (6 core, 5+ domain, 6+ support)
- Add preservation logic to `setup_cortex_hub.py`

**Files Modified:**
- `cortex_brain/tier0/repo-registry.yaml` (registry_template: false)
- `cortex/scripts-root-archive/setup_cortex_hub.py` (preservation logic)

**Verification Command:**
```bash
# Check registry is locked
grep "registry_template:" cortex_brain/tier0/repo-registry.yaml
# Expected: registry_template: false

# Count wired orchestrators
grep -c "wiring_status: \"wired\"" cortex_brain/tier0/repo-registry.yaml
# Expected: 18+ (minimum threshold from AC-PERMANENT-FIX-002)
```

**Critical:** If this reverts to `registry_template: true`, system blocks all operations.

---

### AC-PERMANENT-FIX-002: Verification & Documentation

**Problem:**
- No verification mechanism to prevent regression of AC-PERMANENT-FIX-001

**Solution (Permanent):**
- Created `tests/unit/orchestrators/verify_registry.py` - Registry validation tool
- Created `tests/unit/orchestrators/test_fix_verification.py` - Automated regression tests
- Updated `docs/ORCHESTRATOR-UNWIRING-FIX-PERMANENT-SOLUTION.md` - Comprehensive documentation

**Files Created:**
- `tests/unit/orchestrators/verify_registry.py` (validation logic)
- `tests/unit/orchestrators/test_fix_verification.py` (automated tests)
- `docs/ORCHESTRATOR-UNWIRING-FIX-PERMANENT-SOLUTION.md` (documentation)

**Verification Command:**
```bash
# Run regression tests
pytest tests/unit/orchestrators/test_fix_verification.py -v

# Run registry validation
python tests/unit/orchestrators/verify_registry.py
```

**Critical:** If test files are deleted or disabled, system warns of potential regression.

---

### AC-PERMANENT-FIX-003: Executive Summary & Readiness

**Problem:**
- No clear statement of fix completion
- Unclear deployment readiness status

**Solution (Permanent):**
- Executive summary document `docs/ORCHESTRATOR-UNWIRING-FIX-PERMANENT-SOLUTION.md`
- Clear statement of:
  - 18/23 orchestrators registered
  - Registry locked (non-regenerating)
  - All safety measures in place

**Files Modified:**
- `docs/ORCHESTRATOR-UNWIRING-FIX-PERMANENT-SOLUTION.md` (comprehensive summary)

**Verification Command:**
```bash
# Check documentation exists and contains readiness statement
grep -i "ready for deployment\|phase 1" docs/ORCHESTRATOR-UNWIRING-FIX-PERMANENT-SOLUTION.md
```

**Non-Critical:** Documentation-only fix. Warnings if doc is removed.

---

### AC-PERMANENT-FIX-004: Complete Transformation Status

**Problem:**
- Need confirmation Phase 1 transformation is complete and verified
- No verification that registry persists across git operations

**Solution (Permanent):**
- Registry stability verification complete
- Setup script preservation logic verified
- All orchestrator wiring confirmed stable

**Files Modified:**
- `cortex_brain/tier0/repo-registry.yaml` (verified and locked)
- `cortex/scripts-root-archive/setup_cortex_hub.py` (preservation verified)

**Verification Command:**
```bash
# Check registry persistence across operations
# (simulated in unit tests)
pytest tests/unit/orchestrators/test_fix_verification.py::test_registry_persistence -v
```

**Critical:** If registry state doesn't persist across git operations, fix is reverted.

---

## 🔧 Efficient Identify-and-Fix Pattern

### Implementation in TotalRecallAgent

The agent automatically checks AC-PERMANENT-FIX status on initialization and during recall operations.

```python
from cortex.tools.total_recall_agent import TotalRecallAgent, ACPermanentFixEnforcer

# Pattern 1: Check all fixes
agent = TotalRecallAgent()
ac_status = agent.check_ac_permanent_fixes()

# Pattern 2: Automatic verification on recall (default)
result = agent.recall("orchestrator", verify_ac_permanent_fixes=True)

# Pattern 3: Manual verification
fixes = ACPermanentFixEnforcer.verify_all_fixes()
for fix_id, result in fixes.items():
    print(f"{fix_id}: {'✅ PASS' if result['valid'] else '❌ FAIL'}")
    print(f"  {result['message']}")
```

### Verification Algorithm

**Step 1: Identify** (Git History)
```bash
git log --all --oneline --grep="AC-PERMANENT-FIX"
```

**Step 2: Verify** (File State)
- AC-PERMANENT-FIX-001: `registry_template: false` + 18+ orchestrators wired
- AC-PERMANENT-FIX-002: Test and verification files exist
- AC-PERMANENT-FIX-003: Documentation exists with readiness statement
- AC-PERMANENT-FIX-004: Registry state persists (tested in unit tests)

**Step 3: Detect Regression** (Early Warning)
- If registry_template reverts to true: **BLOCK EXECUTION** (CRITICAL)
- If test files deleted: **WARN** (CRITICAL)
- If documentation removed: **WARN** (Non-critical)
- If registry state doesn't persist: **WARN** (CRITICAL)

**Step 4: Report** (Status Display)
```
**AC-PERMANENT-FIX Status:** ✅ ALL FIXES ACTIVE
- AC-PERMANENT-FIX-001 (Registry Wiring): ✅ LOCKED (18/23 wired)
- AC-PERMANENT-FIX-002 (Verification): ✅ TESTS PASSING
- AC-PERMANENT-FIX-003 (Readiness): ✅ DOCUMENTED
- AC-PERMANENT-FIX-004 (Complete): ✅ VERIFIED
```

---

## 🚨 Regression Detection & Response

### Critical Fixes (Block Execution)

If **ANY** of these fixes revert:
- AC-PERMANENT-FIX-001 (registry_template reverted to true)
- AC-PERMANENT-FIX-002 (test files deleted)
- AC-PERMANENT-FIX-004 (registry state not persisting)

**Action:** System raises `RuntimeError` and blocks all operations until fix is restored.

### Non-Critical Fixes (Warnings Only)

If **ANY** of these fixes revert:
- AC-PERMANENT-FIX-003 (documentation removed)

**Action:** System logs warning but continues execution (allows documentation updates).

### Manual Override (If Needed)

For exceptional cases requiring permanent fix reversion:

```python
# NOT RECOMMENDED - requires explicit override
result = agent.recall(
    "query",
    verify_ac_permanent_fixes=False  # Skip verification (ONLY FOR DEBUGGING)
)

# Always document the reason and create new AC-PERMANENT-FIX to track change
# git commit -m "AC-PERMANENT-FIX-005: [reason for reverting AC-PERMANENT-FIX-001]"
```

---

## 📊 Status Report Format

All operations include AC-PERMANENT-FIX status:

```markdown
## 🧠 CORTEX Total Recall
**Author:** Asif Hussain | **Phase:** Production | **Orchestrator:** TotalRecallAgent ✅

---

**AC-PERMANENT-FIX Status:** ✅ ALL 4 FIXES ACTIVE

| Fix ID | Title | Status | Details |
|--------|-------|--------|---------|
| AC-PERMANENT-FIX-001 | Registry Wiring | ✅ LOCKED | registry_template: false, 18/23 orchestrators wired |
| AC-PERMANENT-FIX-002 | Verification | ✅ TESTS PASSING | verify_registry.py, test_fix_verification.py present |
| AC-PERMANENT-FIX-003 | Readiness | ✅ DOCUMENTED | ORCHESTRATOR-UNWIRING-FIX-PERMANENT-SOLUTION.md present |
| AC-PERMANENT-FIX-004 | Complete | ✅ VERIFIED | Registry persistence tested and confirmed |

**Timestamp:** 2026-01-24T15:30:00Z
**Verification Confidence:** 100% (all critical fixes active)

---

[Remaining output...]
```

---

## 🔄 Git Integration

### Commit Message Pattern

All commits related to AC-PERMANENT-FIX tracking must follow:
```
AC-PERMANENT-FIX-{id}: {description}

Ensures {fix_id} remains active and enforceable.
Verification: [command to verify]
```

### Viewing All AC-PERMANENT-FIX Commits

```bash
# All AC-PERMANENT-FIX commits
git log --all --oneline --grep="AC-PERMANENT-FIX"

# Specific fix
git log --all --grep="AC-PERMANENT-FIX-001" --format=fuller

# Changes in specific fix
git show ac-permanent-fix-001-commit-sha
```

---

## 📚 Integration Points

### TotalRecallAgent (Main Integration)

**File:** `cortex/tools/total_recall_agent.py`

**Classes:**
- `ACPermanentFixEnforcer` - Core verification and enforcement
- `TotalRecallAgent.check_ac_permanent_fixes()` - Public API to check status
- `TotalRecallAgent.recall(..., verify_ac_permanent_fixes=True)` - Automatic verification

**Usage:**
```python
agent = TotalRecallAgent()

# Check status
status = agent.check_ac_permanent_fixes()

# Verify on every recall (default)
result = agent.recall("feature_name")  # Verifies automatically

# Get status report
report = ACPermanentFixEnforcer.get_ac_permanent_fix_report()
print(report)
```

### Governance Integration (CORE-029)

All AC-PERMANENT-FIX reports include mandatory CORTEX headers:
```markdown
## 🧠 CORTEX Total Recall
**Author:** Asif Hussain | **Phase:** Production | **Orchestrator:** TotalRecallAgent ✅

---

**AC-PERMANENT-FIX Status:** [report...]
```

---

## ✅ Checklist for Developers

### Creating a New Permanent Fix

- [ ] Root cause analysis completed
- [ ] Solution implemented and tested
- [ ] Verification mechanism created (test + validation script)
- [ ] Documentation added
- [ ] Commit message format: `AC-PERMANENT-FIX-{id}: {title}`
- [ ] Update `ACPermanentFixEnforcer.PERMANENT_FIXES` in `total_recall_agent.py`
- [ ] Add verification method to `ACPermanentFixEnforcer`
- [ ] Update this document

### Maintaining Permanent Fixes

- [ ] Run `pytest tests/unit/orchestrators/test_fix_verification.py` regularly
- [ ] Monitor AC-PERMANENT-FIX status in CI/CD
- [ ] Never manually revert without updating AC-PERMANENT-FIX enforcement
- [ ] Document any intentional changes to permanent fixes

---

## 🎓 Quick Reference

| Command | Purpose |
|---------|---------|
| `git log --grep="AC-PERMANENT-FIX"` | List all permanent fixes |
| `agent.check_ac_permanent_fixes()` | Check status programmatically |
| `ACPermanentFixEnforcer.verify_all_fixes()` | Verify all fixes active |
| `ACPermanentFixEnforcer.get_ac_permanent_fix_report()` | Get status report |
| `pytest test_fix_verification.py` | Run regression tests |

---

**Last Updated:** 2026-01-24  
**Status:** ✅ PRODUCTION ACTIVE  
**Authority:** cortex-total-recall.prompt.md v5.0
