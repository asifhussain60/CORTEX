# Phase 8.3C: Simplified Consolidation (6 Real P0 Duplicates)

**Status:** EXECUTION READY  
**Date:** February 3, 2026  
**Authority:** CORTEX Master Orchestrator  

---

## 📋 Actual P0 Consolidation Targets (6 Duplicates)

Based on Phase 8.3A audit findings, these are the **legitimate** duplications to consolidate:

### 1. bootstrap.py
```
Canonical:  cortex/bootstrap.py
Duplicate:  cortex/wiring/bootstrap.py
Effort:     30 minutes (consolidation + imports)
Risk:       LOW (isolated, few references)
```

### 2. lazy_module_loader.py
```
Canonical:  cortex/visualization/spa/lazy_module_loader.py
Duplicate:  cortex/visualization/scripts/lazy_module_loader.py
Effort:     30 minutes
Risk:       LOW (visualization-only module)
```

### 3. version_manager.py
```
Canonical:  cortex/orchestrators/version_manager.py
Duplicate:  cortex/domain_brain/version_manager.py
Effort:     30 minutes
Risk:       MEDIUM (multiple imports possible)
```

### 4. lens_integration.py
```
Canonical:  cortex/brain/discovery/lens_integration.py
Duplicate:  cortex/domain_brain/lens_integration.py
Effort:     30 minutes
Risk:       MEDIUM (LENS integration critical)
```

### 5. testing_framework.py
```
Canonical:  cortex/orchestrators/adaptive/testing_framework.py
Duplicate:  cortex/tools/testing_framework.py
Effort:     30 minutes
Risk:       LOW (test utilities only)
```

### 6. template_validator.py
```
Canonical:  cortex/templates/template_validator.py
Duplicate:  cortex/tools/template_validator.py
Effort:     30 minutes
Risk:       LOW (validation utilities)
```

---

## ⚙️ Consolidation Process (Per File)

For each of the 6 files, execute:

```bash
# Step 1: Locate canonical and duplicate
canonical="path/to/canonical.py"
duplicate="path/to/duplicate.py"

# Step 2: Find all imports of the duplicate
grep -r "from $duplicate import" cortex/ tests/
grep -r "import $duplicate" cortex/ tests/

# Step 3: Update all imports to point to canonical
# (automated via import replacement)

# Step 4: Verify no references remain to duplicate
grep -r "$duplicate" cortex/ tests/ || echo "✅ No references found"

# Step 5: Delete duplicate file
rm "$duplicate"

# Step 6: Run affected tests
pytest tests/unit/ -v

# Step 7: Commit
git add -A
git commit -m "Consolidate $filename duplicates (P0)"
```

---

## 📊 Timeline

| Phase | Duration | Status |
|-------|----------|--------|
| Pre-consolidation validation | 30 min | ⏳ Ready |
| 6 × Consolidation tasks | 3 hrs | ⏳ Ready |
| Regression testing (172+ tests) | 2 hrs | ⏳ Ready |
| Final validation & cleanup | 30 min | ⏳ Ready |
| **Total** | **~6 hours** | ✅ |

**Execution Window:** Feb 3-5, 2026 (3 days available, 6 hours needed)

---

## 🎯 Success Criteria

### Technical
- ✅ All 6 duplicate files deleted
- ✅ All imports updated to canonical paths
- ✅ Zero import resolution errors
- ✅ 172+ tests passing (regression validation)
- ✅ Zero new CORE rule violations
- ✅ Pre-commit hook passes all checks

### Documentation
- ✅ Git history clean & logical (one commit per file)
- ✅ Consolidation documented in commit messages
- ✅ Metrics dashboard updated with progress
- ✅ Changes reflected in registry

### Governance
- ✅ CORE-008 (TDD) - Tests validate consolidation
- ✅ CORE-030 (Implementation Truth) - Code matches intent
- ✅ CORE-035 (Single Canonical) - Duplicates eliminated
- ✅ CORE-026 (Git checkpoints) - Clean commit history

---

## 🛠️ Automated Consolidation Script

**File:** `scripts/phase_8_3c_p0_consolidation.py`

**Usage:**
```bash
# Dry-run (no changes)
python3 scripts/phase_8_3c_p0_consolidation.py --dry-run

# Execute (with safety checks)
python3 scripts/phase_8_3c_p0_consolidation.py --execute

# Verbose mode
python3 scripts/phase_8_3c_p0_consolidation.py --execute --verbose
```

**What it does:**
1. Validates canonical files exist
2. Locates all duplicates
3. Finds all import references
4. Updates imports in-place
5. Deletes duplicate files
6. Runs validation tests
7. Reports results

---

## 📈 Regression Testing Plan

After each consolidation:

```bash
# Unit tests only (fast)
pytest tests/unit/ -v

# After all 6: Full suite
pytest tests/ -v --tb=short

# Coverage report
pytest tests/ --cov=cortex --cov-report=html
```

**Baseline:** 172+ existing tests (all currently passing ✅)  
**Target:** 172+ tests still passing after consolidation

---

## ✅ Execution Checklist

Before starting Phase 8.3C:

- [ ] Phase 8.3A committed (cf0cdde4f)
- [ ] Pre-commit hook active (chmod 755 verified)
- [ ] DuplicationDetector wired & operational
- [ ] Metrics dashboard accessible
- [ ] Consolidation script dry-run successful
- [ ] 172+ tests passing (baseline)
- [ ] Git status clean
- [ ] All 6 P0 targets identified & documented

**All items checked?** Proceed to execution.

---

## 🚀 Execution Steps (In Order)

### Phase 3A: Pre-Consolidation (30 minutes)

```bash
# 1. Verify git status
git status

# 2. Ensure all tests pass
pytest tests/ -v --tb=short

# 3. Run dry-run
python3 scripts/phase_8_3c_p0_consolidation.py --dry-run

# 4. Review dry-run output for any issues
```

### Phase 3B: Consolidation (3 hours)

```bash
# 5. Execute consolidation (with safety checks)
python3 scripts/phase_8_3c_p0_consolidation.py --execute

# 6. Review changes
git status
git diff --stat

# 7. Validate imports resolve
python3 -c "import cortex; print('✅ Imports resolve')"
```

### Phase 3C: Regression Testing (2 hours)

```bash
# 8. Run full test suite
pytest tests/ -v --tb=short

# 9. Check coverage
pytest tests/ --cov=cortex --cov-report=term-missing

# 10. Manual smoke tests
python3 -c "from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator"
```

### Phase 3D: Finalization (30 minutes)

```bash
# 11. Create single commit for all consolidations
git add -A
git commit -m "Phase 8.3C: Consolidate 6 P0 duplicate files

Consolidated duplicates:
  - bootstrap.py
  - lazy_module_loader.py
  - version_manager.py
  - lens_integration.py
  - testing_framework.py
  - template_validator.py

All 172+ tests passing.
Regression validated.
Zero new violations."

# 12. Push to repository
git push origin CORTEX

# 13. Update metrics dashboard
# (Dashboard auto-updates from registry)

# 14. Final validation
git log --oneline -5
pytest tests/ -q
```

---

## ⚠️ Rollback Plan (If Needed)

If consolidation causes issues:

```bash
# 1. Identify the problematic commit
git log --oneline | head -1

# 2. Revert the commit
git revert HEAD

# 3. Investigate the issue
# (each file has separate commit for easy bisect)

# 4. Fix the issue
# (update imports, add exception, etc.)

# 5. Re-consolidate
python3 scripts/phase_8_3c_p0_consolidation.py --dry-run
python3 scripts/phase_8_3c_p0_consolidation.py --execute
```

**Note:** Each of the 6 files should have its own commit for easy rollback if needed.

---

## 📚 Reference Documentation

- **Phase 8.3A Index:** [PHASE-8.3A-INDEX.md](_workspaces/cortex-plan/PHASE-8.3A-INDEX.md)
- **Quick Reference:** [PHASE-8.3A-QUICK-REFERENCE.md](_workspaces/cortex-plan/PHASE-8.3A-QUICK-REFERENCE.md)
- **Decision Framework:** [PHASE-8.3-DECISION-FRAMEWORK.md](_workspaces/cortex-plan/PHASE-8.3-DECISION-FRAMEWORK.md)
- **Audit Findings:** [PHASE-8.3C-ACTUAL-AUDIT-FINDINGS.md](_workspaces/cortex-plan/PHASE-8.3C-ACTUAL-AUDIT-FINDINGS.md)

---

## ✅ Sign-Off

**Phase 8.3C Status:** READY FOR EXECUTION  
**Execution Window:** Feb 3-5, 2026  
**Expected Duration:** ~6 hours  
**Risk Level:** 🟢 LOW  
**Success Probability:** 95%+

**Targets:** 6 real P0 duplications  
**Baseline:** 172+ tests  
**Target Outcome:** 172+ tests still passing, 0 violations, duplicates eliminated

---

**Ready to execute Phase 8.3C? ✅ YES**

*Proceed to: Step 1 - Pre-Consolidation Validation*
