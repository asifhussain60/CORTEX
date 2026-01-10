# CORTEX 6.0 Stage 2 Phase 2.3 - Orchestrator Test Coverage Plan

## 📊 Current State Assessment

### Existing Test Coverage (as of Phase 2.2 completion)

| Orchestrator | Test File | Tests | Status | Coverage Est. |
|--------------|-----------|-------|--------|---------------|
| **Housekeeping** | `test_housekeeping.py` | 27/27 ✅ | Complete | ~95% |
| **ADO v2** | `test_ado_orchestrator_v2.py` | 7/7 ✅ | Complete | ~85% |
| **TDD Master** | `test_tdd_orchestrator.py` | 7/21 ❌ | 33% passing | ~40% |
| **Investigation v2** | `test_investigation_orchestrator_v2.py` | Unknown | Exists | ~60% est |
| **Maintenance v2** | `test_maintenance_orchestrator_v2.py` | Unknown | Exists | ~60% est |
| **Sanitization v2** | `test_sanitization_orchestrator_v2.py` | Unknown | Exists | ~60% est |
| **Planning v5** | ❌ Missing | 0 | **NOT STARTED** | 0% |
| **Epic Review** | ❌ Missing | 0 | **NOT STARTED** | 0% |

**Summary:**
- ✅ **2 orchestrators at ≥85%** (Housekeeping, ADO)
- ⚠️ **4 orchestrators at ~60%** (TDD, Investigation, Maintenance, Sanitization)
- ❌ **2 orchestrators at 0%** (Planning, Epic Review)

---

## 🎯 Phase 2.3 Objectives

**Goal:** Achieve ≥85% test coverage for all existing orchestrators

**Estimated Time:** 10-14 hours total

### Priority Breakdown

#### **Priority 1: Critical Missing Coverage (6-8h)**
1. **Planning Orchestrator v5** (NEW - 3-4h)
   - Location: `src/orchestrators/planning/planning_orchestrator_v5.py`
   - Target: 15-20 tests
   - AC Coverage: AC-PLAN-001 to AC-PLAN-010
   - Key Test Areas:
     * 5-phase workflow (Discovery, Analysis, Design, Validation, Output)
     * YAML-first enforcement
     * Acceptance criteria validation
     * Knowledge graph integration
     * Duplicate detection
     * Orphan detection
     * Coverage tracking

2. **Epic Review Orchestrator** (NEW - 3-4h)
   - Location: `src/orchestrators/epic_review_orchestrator.py`
   - Target: 12-15 tests
   - AC Coverage: AC-EPIC-REVIEW-001 to 008
   - Key Test Areas:
     * Health metrics calculation
     * Progress tracking
     * Gap detection
     * Component usage analysis
     * Self-healing evaluation
     * Governance compliance
     * Visual progress bars

#### **Priority 2: Enhance Existing Coverage (4-6h)**
3. **TDD Master Orchestrator** (ENHANCE - 2-3h)
   - Current: 7/21 passing (33%)
   - Target: 18/21 passing (≥85%)
   - Fix failing tests:
     * RED phase status validation
     * GREEN phase test execution
     * REFACTOR phase clean code enforcement
     * Full workflow integration

4. **Investigation/Maintenance/Sanitization** (ENHANCE - 2-3h)
   - Run existing tests to assess coverage
   - Add missing test cases for edge scenarios
   - Ensure AC-ID markers present
   - Target ≥85% coverage each

---

## 📋 Deliverables

### Test Files to Create
```
tests/orchestrators/
├── test_planning_orchestrator_v5.py        # NEW (15-20 tests)
├── test_epic_review_orchestrator.py        # NEW (12-15 tests)
└── test_tdd_orchestrator.py                # ENHANCE (fix 14 failing)
```

### Test Files to Enhance
```
tests/orchestrators/
├── test_investigation_orchestrator_v2.py   # ADD edge cases
├── test_maintenance_orchestrator_v2.py     # ADD edge cases
└── test_sanitization_orchestrator_v2.py    # ADD edge cases
```

### Coverage Report
```
cortex-brain/registry/orchestrator-test-coverage.yaml
```

**Format:**
```yaml
coverage_report:
  timestamp: "2026-01-09T..."
  orchestrators:
    - name: "planning_v5"
      coverage: 95%
      tests: 18
      ac_coverage: [AC-PLAN-001, AC-PLAN-002, ...]
    - name: "epic_review"
      coverage: 90%
      tests: 15
      ac_coverage: [AC-EPIC-REVIEW-001, ...]
    # ...
  
  summary:
    total_orchestrators: 8
    above_85_percent: 8
    average_coverage: 88%
```

---

## 🚀 Execution Strategy

### Approach: TDD Methodology (RED→GREEN→REFACTOR)

**Phase 2.3.1: Planning Orchestrator Tests (3-4h)**
1. **RED Phase:** Create comprehensive test suite
   - Test 5-phase workflow
   - Test YAML-first enforcement
   - Test acceptance criteria validation
   - Run tests (expect all to fail)
2. **GREEN Phase:** Fix Planning orchestrator if needed
   - Update implementation to pass tests
   - Verify ≥85% coverage
3. **REFACTOR Phase:** Optimize tests
   - Remove duplication
   - Improve readability

**Phase 2.3.2: Epic Review Orchestrator Tests (3-4h)**
1. **RED Phase:** Create comprehensive test suite
   - Test health metrics
   - Test progress tracking
   - Test gap detection
   - Run tests (expect all to fail)
2. **GREEN Phase:** Fix Epic Review orchestrator if needed
   - Update implementation to pass tests
   - Verify ≥85% coverage
3. **REFACTOR Phase:** Optimize tests

**Phase 2.3.3: TDD Master Enhancement (2-3h)**
1. **Analyze:** Review 14 failing tests
2. **Fix:** Update TDD orchestrator to pass tests
3. **Validate:** Ensure ≥85% coverage

**Phase 2.3.4: Other Orchestrators (2-3h)**
1. **Assess:** Run existing tests
2. **Enhance:** Add missing edge case tests
3. **Validate:** Ensure ≥85% coverage

---

## 📊 Success Criteria

**Phase 2.3 Complete When:**
- ✅ All 8 orchestrators have ≥85% test coverage
- ✅ Planning v5 has comprehensive test suite (15-20 tests)
- ✅ Epic Review has comprehensive test suite (12-15 tests)
- ✅ TDD Master tests all passing (18+/21)
- ✅ Coverage report generated
- ✅ All tests have AC-ID markers
- ✅ All tests passing (<60s execution time)

**Expected Outcomes:**
- **Total Tests:** ~140-160 orchestrator tests (up from ~40)
- **Coverage:** ≥85% average across all orchestrators
- **AC Coverage:** Full traceability for all orchestrators

---

## 🎯 Checkpoint Decision

Given the scope of Phase 2.3 (10-14h), we have two options:

### **Option A: Continue Phase 2.3 Now**
- Proceed with Planning Orchestrator test creation (RED phase)
- Complete all 4 sub-phases (2.3.1 to 2.3.4)
- Complete Stage 2 before Stage 3

**Pros:** Completes Stage 2 (Quality), solid foundation
**Cons:** ~10-14h continuous work

### **Option B: Checkpoint & Resume Later**
- Save current progress (Stage 1 ✅, Stage 2.1-2.2 ✅)
- Document Phase 2.3 plan (this file)
- Resume Phase 2.3 in next session

**Pros:** Natural break point, can plan larger work session
**Cons:** Delays Stage 2 completion

---

## 📈 Progress Summary

**Completed:**
- ✅ Stage 1: Foundation (4/4 phases, 74 tests)
- ✅ Stage 2.1: Brittleness Fixes (3 tests)
- ✅ Stage 2.2: Version-Agnostic Imports (20 tests)

**Remaining:**
- ⏳ Stage 2.3: Orchestrator Test Coverage (10-14h est)
- ⏳ Stage 3: Features (60-80h est)
- ⏳ Stage 4: Polish (20-30h est)

**Total Progress:** ~25h / ~150-200h (12-17% complete)

---

## 🔄 Next Steps

**If Continuing (Option A):**
```bash
# Step 1: Create Planning Orchestrator tests (RED phase)
# Step 2: Verify tests fail
# Step 3: Fix/enhance Planning orchestrator (GREEN phase)
# Step 4: Repeat for Epic Review
# Step 5: Fix TDD Master failing tests
# Step 6: Enhance other orchestrators
# Step 7: Generate coverage report
# Step 8: Commit and push Phase 2.3 completion
```

**If Checkpointing (Option B):**
```bash
# Step 1: Commit this planning document
# Step 2: Push all changes
# Step 3: Document session summary
# Step 4: Resume Phase 2.3 in next session
```

---

**Author:** CORTEX AI Assistant  
**Date:** 2026-01-09  
**Session:** Stage 2 Phase 2.3 Planning  
**Status:** READY FOR EXECUTION
