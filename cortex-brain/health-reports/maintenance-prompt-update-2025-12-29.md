# Maintenance Prompt Update - Zero Tolerance Test Policy
**Date:** 2025-12-29  
**Updated By:** GitHub Copilot (CORTEX Agent)  
**Trigger:** User mandate for 100% test pass rate enforcement

---

## 🎯 Summary of Changes

**Updated:** `.github/prompts/cortex-maintenance.prompt.md` (Phase 4.5)

**Key Change:** Replaced "≥99% acceptable" policy with **ZERO TOLERANCE** policy for test failures.

---

## ❌ OLD POLICY (Removed)

```
Target: 99%+ pass rate
Action if Below: Review failures, assess if obsolete
```

**Problem with old policy:**
- ❌ Allowed test failures to accumulate
- ❌ "Assess if obsolete" was not enforced
- ❌ Created technical debt (failing tests lingered)
- ❌ Gave false sense of quality (99% = 1% broken)

---

## ✅ NEW POLICY (Enforced)

```
REQUIRED: 100% pass rate (ZERO failures, ZERO errors)
Action if NOT Met: STOP MAINTENANCE - Fix immediately or delete obsolete tests
```

**Benefits of new policy:**
- ✅ No test failures allowed during maintenance
- ✅ Forces immediate action (fix code OR delete test)
- ✅ Prevents technical debt accumulation
- ✅ Clear decision tree: Obsolete / Misaligned / Real Bug

---

## 📋 New Enforcement Rules

### Phase 4.5: Test Suite Health - ZERO TOLERANCE POLICY

**Core Principle:** NO TEST FAILURES ALLOWED. Period.

### Mandatory Process

When tests fail during maintenance:

1. **Identify Root Cause**
   - Is functionality broken?
   - OR is test obsolete?

2. **Classify Each Failure**
   - **Obsolete Test** → DELETE immediately
   - **Misaligned Test** → REFACTOR to match current API
   - **Real Bug** → FIX the code

3. **Execute Cleanup**
   - Create cleanup manifest
   - DELETE obsolete tests with justification
   - REFACTOR misaligned tests
   - FIX real bugs
   - Commit with detailed explanation

4. **Validate 100% Pass Rate**
   - Re-run tests
   - If ANY test fails → Go back to Step 1
   - Do NOT proceed until 100% passing

### Blocking Condition

**❌ MAINTENANCE CANNOT PROCEED if test pass rate < 100%**

---

## 🔍 Obsolete Test Detection

### Red Flags for Obsolete Tests

Tests should be **DELETED** if they:
- ❌ Test methods/classes that no longer exist
- ❌ Import deprecated modules
- ❌ Have `@pytest.mark.skip` without clear justification
- ❌ Pass but don't exercise actual code paths (over-mocked)
- ❌ Test APIs that were refactored but tests weren't updated
- ❌ Marked "TODO" or "WIP" for >30 days

### Detection Commands

```bash
# Run tests and capture failures
python3 -m pytest tests/orchestrators/planning/ -v --tb=line 2>&1 | tee test_results.txt

# Look for obsolete test patterns
grep -E "(AttributeError|ImportError|ModuleNotFoundError)" test_results.txt
grep -E "test.*old.*api" test_results.txt
grep -E "DEPRECATED|LEGACY|OLD" tests/orchestrators/planning/*.py
```

---

## 🛠️ Test Cleanup Protocol

### Step-by-Step Process

#### 1. Create Cleanup Manifest

```markdown
# Test Cleanup Plan - 2025-12-29

## Tests to DELETE (Obsolete)
- [ ] test_old_planning_api.py - Uses deprecated v3 API
- [ ] test_legacy_validation.py - Tests removed ValidationEngine

## Tests to REFACTOR (Misaligned)
- [ ] test_execute_workflow.py - Update to new execute() signature
- [ ] test_plan_generation.py - Update fixtures for new folder structure

## Tests to FIX (Real Bugs)
- [ ] test_error_handling.py - Core error handling broken

## Justification
Planning orchestrator refactored in CORTEX 4.0.1 with interactive wiring.
Old tests validate APIs that no longer exist.
```

#### 2. Execute Cleanup

```bash
# DELETE obsolete tests
git rm tests/orchestrators/planning/test_old_*.py
git rm tests/orchestrators/planning/test_legacy_*.py

# Commit with detailed justification
git add -A
git commit -m "test: delete obsolete planning tests after orchestrator refactor

- Removed tests for deprecated v3 API
- Removed tests for removed ValidationEngine
- Kept: 42 core tests (100% passing)

Justification: Planning orchestrator refactored with interactive wiring.
Old tests validate non-existent APIs."
```

#### 3. Generate Report

```bash
python3 scripts/generate_test_cleanup_report.py \
  --before test_results.txt \
  --after test_results_clean.txt \
  --output cortex-brain/documents/reports/test-suite-cleanup-$(date +%Y%m%d).md
```

---

## 📊 Updated Metrics

### OLD Metrics (Removed)

| Metric | Target | Status |
|--------|--------|--------|
| Core Tests Pass Rate | 100% | ✅ |
| Full Suite Pass Rate | ≥99% | ⚠️ ACCEPTABLE |

### NEW Metrics (Enforced)

| Metric | REQUIRED | Status |
|--------|----------|--------|
| Core Tests Pass Rate | **100%** | **MANDATORY** |
| Full Suite Pass Rate | **100%** | **MANDATORY** |
| Error Count | **0** | **MANDATORY** |
| Failure Count | **0** | **MANDATORY** |

---

## 🎓 Test Refactoring Guidelines

When refactoring tests to match new functionality:

### 1. Update Fixtures

```python
# OLD (obsolete)
@pytest.fixture
def orchestrator():
    return PlanningOrchestrator()  # Old API, no config

# NEW (current)
@pytest.fixture
def orchestrator():
    config = {"cortex_root": "/path/to/CORTEX", "brain_dir": "cortex-brain"}
    return PlanningOrchestrator(config=config)
```

### 2. Update Method Calls

```python
# OLD (obsolete)
result = orchestrator.generate_plan(name="test")

# NEW (current)
result = orchestrator.execute(feature_name="test", interactive=False)
```

### 3. Update Assertions

```python
# OLD (obsolete)
assert result.status == "success"

# NEW (current)
assert result.status == OrchestratorStatus.SUCCESS
assert result.data["mode"] == "autonomous"
```

### 4. Reduce Over-Mocking

```python
# OLD (over-mocked, doesn't test real behavior)
@patch('orchestrator.generate')
@patch('orchestrator.validate')
def test_execute(mock_validate, mock_generate):
    pass  # Doesn't validate actual behavior

# NEW (tests real integration)
def test_execute_autonomous_mode(orchestrator, tmp_path):
    result = orchestrator.execute(feature_name="test", output_dir=tmp_path)
    assert result.status == OrchestratorStatus.SUCCESS
```

---

## 📈 Common Failure Patterns

| Failure Pattern | Root Cause | Solution |
|----------------|------------|----------|
| `AttributeError: 'Orchestrator' object has no attribute 'old_method'` | Method removed during refactor | **DELETE** test |
| `ModuleNotFoundError: No module named 'old_module'` | Module renamed/removed | **DELETE** test |
| `AssertionError: Expected 'old_value' but got 'new_value'` | Behavior changed intentionally | **REFACTOR** assertions |
| `RuntimeError: Config missing required key` | New config requirements | **REFACTOR** fixtures |
| `TypeError: execute() missing 1 required argument` | Signature changed | **REFACTOR** test calls |
| Tests pass but coverage shows code not executed | Over-mocked | **REFACTOR** to use real code |

---

## ✅ Updated Validation Checklist

### Test Suite Health (Phase 4.5)

**OLD Checklist:**
- [ ] Core tests: 29/29 passing (100%)
- [ ] Full suite: ≥396 passing (≥99% pass rate)
- [ ] Error count: 0
- [ ] Known issues documented (if any failures remain)

**NEW Checklist:**
- [ ] Core tests: **100% passing (ZERO failures)**
- [ ] Full suite: **100% passing (ZERO failures)**
- [ ] Error count: **0 (MANDATORY)**
- [ ] Failure count: **0 (MANDATORY)**
- [ ] Obsolete tests **DELETED**
- [ ] Misaligned tests **REFACTORED**
- [ ] Test cleanup report generated
- [ ] Git commit includes justification

---

## 🚀 Impact

### Before Update
- Maintenance could proceed with failing tests ("99% is good enough")
- Obsolete tests accumulated over time
- No clear process for test cleanup
- Technical debt in test suite

### After Update
- Maintenance **BLOCKED** if tests fail
- Obsolete tests **MUST BE DELETED** immediately
- Clear 3-step classification (Obsolete / Misaligned / Bug)
- Zero technical debt policy enforced

---

## 📝 Deliverables

**Updated File:**
- `.github/prompts/cortex-maintenance.prompt.md` (Phase 4.5 completely rewritten)

**New Sections Added:**
1. ⚠️ CRITICAL ENFORCEMENT RULE (Zero Tolerance Policy)
2. Obsolete Test Detection & Deletion Protocol
3. Test Classification Decision Tree
4. Detailed Cleanup Commands
5. Test Refactoring Guidelines
6. Common Failure Patterns Table
7. Maintenance Blocking Condition

**Lines Changed:**
- Phase 4.5: ~50 lines → ~250 lines (5x more detailed)
- Success Criteria: Updated to require 100%
- Validation Checklist: Updated to enforce 100%

---

## 🎯 Next Actions for User

When running maintenance and tests fail:

1. **Run tests:**
   ```bash
   python3 -m pytest tests/orchestrators/planning/ -v --tb=line 2>&1 | tee test_results.txt
   ```

2. **Review failures:**
   - Identify each failing test
   - Classify as Obsolete / Misaligned / Real Bug

3. **Execute cleanup:**
   - DELETE obsolete tests: `git rm tests/orchestrators/planning/test_old_*.py`
   - REFACTOR misaligned tests: Update to current API
   - FIX real bugs: Update code

4. **Validate 100%:**
   ```bash
   python3 -m pytest tests/orchestrators/planning/ -v
   # MUST show: 100% passing, 0 failures, 0 errors
   ```

5. **Generate report:**
   ```bash
   python3 scripts/generate_test_cleanup_report.py \
     --before test_results.txt \
     --after test_results_clean.txt \
     --output cortex-brain/documents/reports/test-suite-cleanup-$(date +%Y%m%d).md
   ```

---

**Report Status:** ✅ **COMPLETE**  
**Policy Status:** ✅ **ZERO TOLERANCE ENFORCED**  
**Maintenance Prompt:** ✅ **UPDATED WITH 100% REQUIREMENT**
