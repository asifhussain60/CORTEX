# Test Migration Analysis Report

**Version:** 1.0 | **Date:** December 21, 2025  
**Author:** Asif Hussain | **Phase:** Phase 6 - Week 10 Day 3

---

## Executive Summary

Analysis of test organization across CORTEX 4.0 orchestrators reveals a **dual-pattern architecture**: co-located tests for newer orchestrators (ADO, Sanitization) and centralized tests for legacy/foundational components (Planning System, System Integrity, Base Orchestrator).

**Key Findings:**
- ✅ **18 co-located test files** in `src/orchestrators/*/tests/`
- ✅ **11 central test files** in `tests/orchestrators/`
- ✅ **80 ADO tests** (co-located, 91.44% coverage)
- ✅ **70 Sanitization tests** (co-located, 100% pass rate)
- ✅ **138 Planning System tests** (central location, 84.6% coverage)
- ⚠️ **5 orchestrators WITHOUT tests**: base, tdd, story_enhancement, system, planning (orchestrator files)

---

## Current Test Distribution

### Pattern 1: Co-Located Tests (Recommended for CORTEX 4.0)

**Orchestrators with Co-Located Tests:**

| Orchestrator | Location | Test Files | Test Cases | Coverage | Status |
|--------------|----------|------------|------------|----------|--------|
| ADO | `src/orchestrators/ado/tests/` | 8 | 80 | 91.44% | ✅ COMPLETE |
| Sanitization | `src/orchestrators/sanitization/tests/` | 10 | 70 | Unknown | ✅ COMPLETE |

**Benefits:**
- Tests live with implementation code
- Easy discovery (same directory structure)
- Clear ownership and maintenance responsibility
- Supports modular development
- Facilitates orchestrator-specific test utilities

### Pattern 2: Central Tests Directory (Legacy Pattern)

**Orchestrators with Central Tests:**

| Component | Location | Test Files | Test Cases | Notes |
|-----------|----------|------------|------------|-------|
| Planning System | `tests/orchestrators/planning/` | 4 | 138 | Integration tests (executor, phase_mgr, git, session) |
| System Integrity | `tests/orchestrators/system/` | 1 | Unknown | Single integration test |
| Base Orchestrator | `tests/orchestrators/base/` | 1 | Unknown | Adaptive features test |
| Autonomous Execution | `tests/orchestrators/` | 1 | Unknown | Engine test |
| Adaptive Execution | `tests/orchestrators/adaptive_execution/` | 1 | Unknown | Execution test |

**Characteristics:**
- Separation between implementation and tests
- Historically used for foundational/infrastructure components
- Requires manual navigation between code and tests
- May indicate "shared" or "cross-cutting" test utilities

---

## Orchestrators WITHOUT Tests

### Critical Gap Analysis

| Orchestrator | Location | Status | Risk Level |
|--------------|----------|--------|------------|
| Base Orchestrator | `src/orchestrators/base/` | Has 1 central test, no co-located | 🟡 MEDIUM |
| TDD v4.0 | `src/orchestrators/tdd/` | NO TESTS | 🔴 HIGH |
| Planning Orchestrator | `src/orchestrators/planning/` | Tests in central only | 🟡 MEDIUM |
| Story Enhancement | `src/orchestrators/story_enhancement/` | NO TESTS | 🟠 HIGH |
| System Integrity | `src/orchestrators/system/` | 1 central test only | 🟠 HIGH |

**Note:** TDD Orchestrator v4.0 marked as "COMPLETE" in CORTEX4-STATUS.md with "26 tests" - **tests location unknown or not discovered**. Requires investigation.

---

## Test Organization Standards (CORTEX 4.0)

### Recommended Pattern: Co-Located Tests

**Directory Structure:**
```
src/orchestrators/{orchestrator_name}/
├── {orchestrator_name}_orchestrator.py
├── tests/
│   ├── __init__.py
│   ├── test_orchestrator_foundation.py  # Base functionality
│   ├── test_{phase1}_phase.py           # Per-phase tests
│   ├── test_{phase2}_phase.py
│   ├── test_edge_cases.py               # Edge cases
│   ├── test_error_handling.py           # Error scenarios
│   └── test_{orchestrator}_e2e.py       # End-to-end tests
└── __init__.py
```

**Test File Naming Convention:**
- `test_orchestrator_foundation.py` - Core orchestrator behavior (engagement hints, phase transitions)
- `test_{phase}_phase.py` - Individual phase logic
- `test_edge_cases.py` - Boundary conditions
- `test_{feature}.py` - Specific features (rollback, approval, dry-run)
- `test_{orchestrator}_e2e.py` - Full workflow tests

**Example (Sanitization Orchestrator):**
```
src/orchestrators/sanitization/tests/
├── test_orchestrator_foundation.py  (8 tests)
├── test_analyze_phase.py            (3 tests)
├── test_mapping_phase.py            (7 tests)
├── test_transform_phase.py          (8 tests)
├── test_validate_phase.py           (11 tests)
├── test_report_phase.py             (3 tests)
├── test_interactive_approval.py     (5 tests)
├── test_dry_run_mode.py             (3 tests)
├── test_rollback_scenarios.py       (10 tests)
└── test_sanitization_e2e.py         (12 tests)
```

---

## Migration Recommendations

### Priority 1: HIGH RISK - Create Missing Tests

**1. TDD Orchestrator v4.0**
- **Current:** Marked complete with "26 tests" but no tests discovered
- **Action:** Locate existing tests OR create co-located test suite
- **Estimate:** 3-5 days (if creating from scratch)
- **Target Coverage:** 90%+
- **Test Files Needed:**
  - `test_orchestrator_foundation.py`
  - `test_red_phase.py`
  - `test_green_phase.py`
  - `test_refactor_phase.py`
  - `test_tech_discovery.py`
  - `test_adaptive_learning.py`
  - `test_tdd_e2e.py`

**2. Story Enhancement Orchestrator**
- **Current:** NO TESTS
- **Action:** Create co-located test suite
- **Estimate:** 2-3 days
- **Target Coverage:** 85%+

**3. System Integrity Orchestrator**
- **Current:** 1 central integration test only
- **Action:** Create comprehensive co-located test suite (8 phases)
- **Estimate:** 3-4 days
- **Target Coverage:** 85%+

### Priority 2: MEDIUM RISK - Migrate Central to Co-Located

**Planning System Orchestrator**
- **Current:** 138 tests in `tests/orchestrators/planning/`
- **Action:** Migrate to `src/orchestrators/planning/tests/`
- **Reasoning:** Co-location improves maintainability
- **Estimate:** 1-2 days (refactor imports, update paths)
- **Risk:** Low (tests already exist, just relocating)

**Base Orchestrator**
- **Current:** 1 test in `tests/orchestrators/base/`
- **Action:** Expand to comprehensive suite + co-locate
- **Estimate:** 2 days
- **Target Coverage:** 85%+

### Priority 3: LOW RISK - Documentation & Standardization

**1. Update Test Discovery Documentation**
- Document co-located pattern as CORTEX 4.0 standard
- Add examples to orchestrator development guide
- Update CI/CD to run both patterns

**2. Create Test Template**
- Provide `test_orchestrator_template.py` for new orchestrators
- Include foundation tests (engagement hints, phase transitions)
- Add pytest fixtures for common orchestrator setup

**3. Centralize Test Utilities**
- Keep shared test utilities in `tests/fixtures/orchestrator_fixtures.py`
- Create mock data in `tests/mocks/` for cross-orchestrator use
- Document when to use central vs co-located utilities

---

## Test Coverage Goals

### Current State (Measured Orchestrators)

| Orchestrator | Coverage | Target | Gap |
|--------------|----------|--------|-----|
| ADO | 91.44% | 85% | ✅ +6.44% |
| Planning System | 84.6% | 85% | ⚠️ -0.4% |
| Sanitization | Unknown | 85% | ❓ Measure |
| TDD v4.0 | Unknown | 90% | ❓ Locate tests |
| Others | 0% | 85% | 🔴 -85% |

### Phase 6 Completion Criteria (Tests)

For Phase 6 to be 100% complete, **all orchestrators must have:**
- ✅ Co-located test suites
- ✅ 85%+ coverage (90% for TDD orchestrator)
- ✅ Foundation tests (engagement, transitions, completion)
- ✅ Per-phase unit tests
- ✅ End-to-end integration tests
- ✅ Edge case and error handling tests

**Current Phase 6 Status:** 50% (test infrastructure partial)

---

## Implementation Plan

### Week 10 Remaining (Current)

**Task:** Complete Test Migration Analysis ✅
- [x] Analyze current test distribution
- [x] Identify gaps and risks
- [x] Document migration recommendations
- [x] Define CORTEX 4.0 test standards

### Week 11-13: Post-Phase 5 Enhancements

**Note:** These weeks focus on enhancing existing orchestrators AFTER Phase 5 (Agentic AI) is complete. Test migration should be integrated into this work.

**Week 11: TDD v4.0 Enhancement**
- Locate existing 26 tests (mentioned in CORTEX4-STATUS.md)
- Create missing tests if not found
- Enhance to 90%+ coverage
- Add adaptive learning test coverage

**Week 12: Documentation Orchestrator Enhancement**
- Create co-located test suite (if missing)
- Test auto-documentation features
- Verify D3.js visualization generation

**Week 13: Execution Orchestrator Enhancement**
- Create co-located test suite (if missing)
- Test autonomous execution modes
- Verify tiered routing

### Phase 7: Infrastructure Activation

**Week 11 Days 1-2: Ready-But-Inactive Infrastructure Scan**
- This scan will identify Story Enhancement & System Integrity gaps
- Activation checklists should include test requirements

---

## Metrics & Success Criteria

### Quantitative Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Orchestrators with co-located tests | 2/8 (25%) | 8/8 (100%) | 🔴 |
| Average test coverage | ~88% (2 measured) | 85%+ (all) | 🟡 |
| Orchestrators with 0 tests | 3/8 (37.5%) | 0/8 (0%) | 🔴 |
| Total orchestrator test cases | 288+ (partial) | 500+ (estimate) | 🟡 |
| Test execution time | <2min (current) | <5min (all) | ✅ |

### Qualitative Success Criteria

- ✅ All orchestrators follow CORTEX 4.0 co-located pattern
- ✅ Test discovery is automatic (pytest finds all tests)
- ✅ Each orchestrator has foundation + phase + e2e tests
- ✅ CI/CD runs all orchestrator tests on every commit
- ✅ Test maintenance is owner's responsibility (co-location benefit)
- ✅ Shared utilities documented and discoverable

---

## Risk Assessment

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| TDD tests truly missing (not just undiscovered) | Medium | High | Create from scratch using sanitization/ADO as template |
| Test migration breaks existing CI/CD | Low | High | Run both patterns during transition, deprecate old gradually |
| Coverage drops during migration | Medium | Medium | Measure before/after, block merge if coverage decreases |
| Orphaned central tests remain | High | Low | Audit after migration, move or delete unused tests |

### Schedule Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Creating missing tests takes longer than estimated | Medium | Medium | Prioritize by orchestrator criticality (TDD first) |
| Weeks 11-13 enhancements delayed by test work | Low | Low | Test creation is PART of enhancement work |
| Phase 5 blocks Phase 6 completion | High | Medium | Parallelize - test migration can happen independently |

---

## Next Actions

**Immediate (Week 10 Day 3 - TODAY):**
1. ✅ Complete this analysis report
2. ⏳ Investigate TDD v4.0 test location (26 tests claimed in status)
3. ⏳ Update CORTEX4-STATUS.md with test migration task

**Short-term (Weeks 11-13):**
1. Create missing test suites (TDD, Story Enhancement, System Integrity)
2. Migrate Planning System tests to co-location
3. Expand Base Orchestrator tests
4. Measure and document coverage for all orchestrators

**Medium-term (Phase 7):**
1. Update orchestrator development guide with test standards
2. Create test template for future orchestrators
3. Integrate test requirements into activation checklists
4. Audit and remove orphaned central tests

---

## Appendix A: Test File Inventory

### Co-Located Tests (src/orchestrators/)

**ADO Orchestrator (8 files):**
- test_ado_orchestrator_foundation.py
- test_ado_discovery_phase.py
- test_ado_dor_workflow.py
- test_ado_approval_gate.py
- test_ado_work_item_generation.py
- test_ado_api_integration.py
- test_ado_git_checkpoint.py
- test_ado_edge_cases.py

**Sanitization Orchestrator (10 files):**
- test_orchestrator_foundation.py
- test_analyze_phase.py
- test_mapping_phase.py
- test_transform_phase.py
- test_validate_phase.py
- test_report_phase.py
- test_interactive_approval.py
- test_dry_run_mode.py
- test_rollback_scenarios.py
- test_sanitization_e2e.py

### Central Tests (tests/orchestrators/)

**Planning System (4 files):**
- test_plan_executor.py
- test_phase_manager_integration.py
- test_git_checkpoint_integration.py
- test_session_manager.py

**Other (4 files):**
- test_autonomous_execution_engine.py
- test_adaptive_execution.py
- test_base_orchestrator_adaptive.py
- test_system_integrity_orchestrator.py

---

## Appendix B: pytest Configuration

**Current pytest.ini:**
```ini
[pytest]
testpaths = tests src
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

**Recommendation:** This configuration already supports both patterns (tests/ and src/ discovery). No changes needed.

---

## Conclusion

Test migration analysis reveals a **healthy foundation with gaps**. The co-located pattern (ADO, Sanitization) demonstrates best practices with excellent coverage. Priority efforts should focus on:

1. **Finding/creating TDD v4.0 tests** (HIGH PRIORITY)
2. **Creating missing test suites** (Story Enhancement, System Integrity)
3. **Migrating Planning System tests to co-location** (MEDIUM PRIORITY)

Estimated total effort: **8-12 days** spread across Weeks 11-13, aligning perfectly with Post-Phase 5 enhancement schedule.

**Status:** Test migration analysis COMPLETE ✅  
**Next:** Investigate TDD v4.0 test location + update CORTEX4-STATUS.md
