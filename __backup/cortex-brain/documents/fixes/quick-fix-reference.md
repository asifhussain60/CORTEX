# QUICK FIX REFERENCE - CORTEX 6.0 Phase 1 Repair

**Status:** READY TO EXECUTE | **Effort:** 16-23 hours | **Blocking:** Phase 2

---

## THE 5-STEP FIX

### 🔴 STEP 1: Fix Test Infrastructure (2-3 hrs)
**Problem:** 11 test files break pytest collection  
**Fix:**
```bash
# Delete broken tests
rm tests/unit/test_invalid-_name-_with-_dashes.py
rm tests/unit/test_api_orchestrator.py
# ... (9 more deletions)

# Implement test discovery/execution
# AC-TEST-001: src/infrastructure/test_discovery.py
# AC-TEST-002: src/infrastructure/test_executor.py

# Verify
python3 -m pytest tests/ --collect-only -q  # Should have 0 errors
```
**Result:** All tests collect → Can run full suite

---

### 🔴 STEP 2: Fix Hardcoded Paths (3-4 hrs)
**Problem:** 222 hardcoded "cortex-brain/" paths violate CORE-005  
**Fix:**
```bash
# Create portable path utility
# src/utils/path_utils.py (project_root(), cortex_brain_path())

# Replace all hardcoded paths
# Before: log_path = "cortex-brain/audit-logs/..."
# After:  log_path = audit_logs_path() / "..."

# Add pre-commit hook
# .git/hooks/pre-commit (grep for 'cortex-brain/' and block)
```
**Verify:**
```bash
grep -r "cortex-brain/" src/ tests/ --include="*.py" | wc -l  # Should be 0
```
**Result:** CI/CD portable across machines

---

### 🟠 STEP 3: Implement Missing Audit ACs (4-6 hrs)
**Problem:** AC-AUDIT-004-007 missing (traceability, vacuum, isolation, hash chain)  
**Fix:**
```python
# AC-AUDIT-004: Add ac_id field to audit log entries
# AC-AUDIT-005: Create audit_vacuum.py (retention policy)
# AC-AUDIT-006: Initialize per-repo audit databases
# AC-AUDIT-007: Add event_hash + prev_event_hash chain verification

# Create tests for each: tests/infrastructure/test_*_audit_*.py
```
**Result:** Complete audit infrastructure

---

### 🟠 STEP 4: Implement Evidence Bundle System (6-8 hrs)
**Problem:** AC-EVIDENCE-001-003 missing (no evidence bundles generated)  
**Fix:**
```python
# AC-EVIDENCE-001: Create 3-file bundle structure
#   - manifest.yaml (spec, AC-ID, governance rules)
#   - test_results.json (pass/fail, coverage %)
#   - audit_trace.jsonl (audit events)

# AC-EVIDENCE-002: Implement 3 validation gates
#   - Gate 1: Test coverage >= 80% (BLOCKER)
#   - Gate 2: Audit completeness (BLOCKER)
#   - Gate 3: Governance compliance (BLOCKER)

# AC-EVIDENCE-003: Auto-generate bundles
#   - Run tests for AC → Collect results
#   - Query audit events → Create trace
#   - Generate manifest → Create bundle
```
**Result:** Evidence bundles generated per AC

---

### ✅ STEP 5: Evidence Collection & Verification (1-2 hrs)
**Problem:** Verification rate 0% (23 false positives in tracker)  
**Fix:**
```bash
# 1. Run full test suite
python3 -m pytest tests/ -v --tb=short

# 2. Generate evidence bundles
python3 scripts/generate_all_evidence_bundles.py

# 3. Update tracker with VERIFIED results
python3 scripts/update_tracker_verified.py

# 4. Sync plan viewer
python3 scripts/sync_plan_viewer_data.py

# 5. Validate
python3 scripts/audit_based_evidence_validator.py
# Expected: Verification rate ≥80%
```
**Result:** Verification rate ≥80%, Phase 2 ready

---

## KEY DELIVERABLES

| Deliverable | Location | Status |
|-------------|----------|--------|
| Path utility | `src/utils/path_utils.py` | CREATE |
| Test discovery | `src/infrastructure/test_discovery.py` | CREATE |
| Test executor | `src/infrastructure/test_executor.py` | CREATE |
| Audit vacuum | `src/infrastructure/audit_vacuum.py` | CREATE |
| Evidence bundler | `src/infrastructure/evidence_bundler.py` | CREATE |
| Evidence gates | `src/infrastructure/evidence_gates.py` | CREATE |
| Auto-generator | `src/infrastructure/evidence_auto_generator.py` | CREATE |
| Pre-commit hook | `.git/hooks/pre-commit` | CREATE |
| Tests | `tests/infrastructure/test_*.py` | CREATE |

---

## SUCCESS METRICS

After repair, Phase 1 should be:

```
✅ Test Execution:   100% (all 46 tests collect, run cleanly)
✅ AC Completeness:  100% (34/34 implemented)
✅ Evidence:         100% (bundles for all ACs)
✅ Portability:      100% (0 hardcoded paths)
✅ Verification:     ≥80% (evidence-backed)
✅ Governance:       100% (CORE-005 enforced)
```

---

## BLOCKING DEPENDENCIES

```
Step 1 MUST complete before Step 2 can start
  └─ Need tests running to validate path refactoring

Step 2 MUST complete before Step 4 can start
  └─ Need portable code to bundle and deploy

Step 3 PARALLEL with Step 2-4
  └─ Audit ACs independent of paths/evidence

All Steps 1-4 MUST complete before Step 5
  └─ Need code stable + tests passing before verification
```

---

## EXECUTION COMMAND SEQUENCE

```bash
# Execute steps in order (do not parallelize)

# STEP 1: Test Infrastructure
rm tests/unit/test_*.py  # Remove broken tests (carefully)
# Implement AC-TEST-001, AC-TEST-002, link tests
python3 -m pytest tests/ --collect-only -q  # Verify: 0 errors

# STEP 2: Hardcoded Paths
# Create src/utils/path_utils.py
# Refactor all 222 paths (use find+replace)
# Add .git/hooks/pre-commit
grep -r "cortex-brain/" src/ tests/ --include="*.py" | wc -l  # Verify: 0

# STEP 3: Audit ACs
# Implement AC-AUDIT-004-007
# Create test files
python3 -m pytest tests/infrastructure/test_*audit*.py -v  # Verify: pass

# STEP 4: Evidence System
# Implement AC-EVIDENCE-001-003
# Create test files
python3 -m pytest tests/infrastructure/test_evidence*.py -v  # Verify: pass

# STEP 5: Verification
python3 -m pytest tests/ -v
python3 scripts/generate_all_evidence_bundles.py
python3 scripts/update_tracker_verified.py
python3 scripts/sync_plan_viewer_data.py
python3 scripts/audit_based_evidence_validator.py  # Verify: ≥80%
```

---

## IF BLOCKED

| Issue | Solution |
|-------|----------|
| Test collection still broken | Ensure all 11 stub files deleted, no syntax errors in remaining tests |
| Hardcoded paths still exist | Automate: `sed -i '' 's|cortex-brain/|project_root()/cortex_brain|g' src/*.py` |
| Evidence gates failing | Verify test coverage ≥80%, all audit events logged, governance rules applied |
| Verification <80% | Run tests with coverage, generate bundles, check for evidence gaps |
| Phase 2 still blocked | Ensure ALL 5 steps complete + verification ≥80% before proceeding |

---

## ESTIMATED TIMELINE

```
Day 1 (8 hrs):
  Morning:   Step 1 (Test Infrastructure)
  Afternoon: Step 2 (Hardcoded Paths)

Day 2 (8 hrs):
  Morning:   Step 3 (Audit ACs)
  Afternoon: Step 4 (Evidence System)

Day 3 (1-2 hrs):
  Morning:   Step 5 (Verification)
             Phase 2 Ready ✅
```

---

## AUTHORITY & PRECEDENCE

**Classification:** Phase 1 Foundation Repair  
**Authority:** CORTEX 6.0 Governance (Tier 0)  
**Precedence:** BLOCKING PHASE 2  
**Status:** READY TO EXECUTE

Once complete → Phase 2 Orchestration Core can proceed

