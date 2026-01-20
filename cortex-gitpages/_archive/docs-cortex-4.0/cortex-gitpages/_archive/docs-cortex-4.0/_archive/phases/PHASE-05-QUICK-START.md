# PHASE-05 QUICK START GUIDE
## Brittleness Fixes & Stabilization - Implementation Guide

**Phase**: PHASE-05  
**Status**: IN_PROGRESS  
**Start Date**: 2026-01-18  
**Estimated Completion**: 2026-02-01 (12-14 days)

---

## 🎯 What is PHASE-05?

PHASE-05 is a **stabilization phase** that fixes brittleness and reliability issues in the CORTEX codebase:

```
Goal: Make CORTEX robust, portable, and test-reliable
├── Code Quality (3 ACs) - Clean, maintainable code
├── Platform Support (4 ACs) - Windows, macOS, Linux compatibility
└── Test Reliability (10 ACs) - Stable, isolated, fast tests
```

---

## 📊 Quick Stats

```
Total AC-IDs:              17
├── Code Quality:           3 ACs (AC-NFR-001-01 to 03)
├── Cross-Platform:         4 ACs (AC-BRITTLE-001 to 005)
└── Test Stabilization:    10 ACs (AC-BRITTLE-006 to 014)

Total Tests Required:     259
├── Unit Tests:           187
└── Integration Tests:     72

Estimated Effort:    12-14 days
Test Pass Rate:     100% (target)
```

---

## 🚀 Implementation Waves (5 Sequential Waves)

### Wave 1: Import Path Foundation (Days 1-2)
**Start**: Now  
**ACs**: AC-BRITTLE-001, AC-BRITTLE-002  
**Tests**: 52 total (20+18 unit, 8+6 integration)  
**Goal**: Build core import/path infrastructure

```bash
# What you'll create:
cortex_brain/tier0/import_resolver.py    # Import resolution
cortex_brain/tier0/path_abstraction.py   # Path portability

# What you'll test:
tests/unit/test_import_resolver.py       # 20 unit tests
tests/integration/test_import_*.py       # 8 integration tests
```

**Key Classes**:
- `ImportResolver` - Resolve module imports
- `PathAbstraction` - Cross-platform paths
- `ImportCache` - Cache resolved imports

---

### Wave 2: Platform Support (Days 3-4)
**Prerequisite**: Wave 1 complete  
**ACs**: AC-BRITTLE-003, AC-BRITTLE-004, AC-BRITTLE-005  
**Tests**: 42 total (12+10+10 unit, 4+3+3 integration)  
**Goal**: Windows, macOS, Linux compatibility

```bash
# What you'll create:
cortex_brain/tier0/platform_compat.py    # Platform-specific fixes

# Platforms Covered:
# - Windows: Drive letters, UNC paths, separators
# - macOS: .app bundles, symlinks, case-sensitivity
# - Linux: Relative paths, containers, permissions
```

**Platform Classes**:
- `WindowsPathHandler` - Windows-specific logic
- `MacOSPathHandler` - macOS-specific logic
- `LinuxPathHandler` - Linux-specific logic

---

### Wave 3: Code Quality (Days 5-6)
**Prerequisite**: Wave 2 complete  
**ACs**: AC-NFR-001-01, AC-NFR-001-02, AC-NFR-001-03  
**Tests**: 49 total (15+10+12 unit, 5+3+4 integration)  
**Goal**: Code quality standards

```bash
# What you'll do:
1. AC-NFR-001-01: Maintainability audit
   - Analyze all code tiers
   - Identify technical debt
   - Create refactoring plan

2. AC-NFR-001-02: Code style enforcement
   - Configure Black, isort, pylint
   - Update .pylintrc, .black.json, pyproject.toml
   - Run formatters on all code

3. AC-NFR-001-03: Type annotations
   - Add type hints to all functions
   - Run mypy validation
   - 100% coverage target
```

**Config Files to Update**:
- `.pylintrc` - Linting rules
- `.black.json` - Code formatter
- `pyproject.toml` - Tool configuration

---

### Wave 4: Test Stabilization (Days 7-10)
**Prerequisite**: Wave 3 complete  
**ACs**: AC-BRITTLE-006 through AC-BRITTLE-010  
**Tests**: 80 total (8+14+16+12+10 unit, 2+5+4+6+3 integration)  
**Goal**: Reliable, isolated tests

```bash
# What you'll do:
AC-BRITTLE-006: Audit flaky tests
├── Identify test failures patterns
├── Root cause analysis
└── Create remediation plan

AC-BRITTLE-007: Test isolation
├── Fix test interdependencies
├── Proper fixture setup/teardown
└── State cleanup between tests

AC-BRITTLE-008: Timing issues
├── Fix timing-dependent failures
├── Async/await handling
└── Proper sleep replacement (events)

AC-BRITTLE-009: Database state
├── Transaction handling
├── Rollback strategies
└── Clean state between tests

AC-BRITTLE-010: Mock management
├── Centralize mock creation
├── Mock factory pattern
└── Prevent mock drift
```

**New Test Utilities**:
- `tests/conftest.py` - Enhanced fixtures
- `tests/utils/flakiness_reporter.py` - Track flaky tests
- `tests/utils/db_transaction_handler.py` - DB isolation
- `tests/utils/mock_factory.py` - Mock creation

---

### Wave 5: Final Validation (Days 11-12)
**Prerequisite**: Wave 4 complete  
**ACs**: AC-BRITTLE-011 through AC-BRITTLE-014  
**Tests**: 56 total (6+8+12+8 unit, 2+8+8+4 integration)  
**Goal**: Comprehensive validation

```bash
# What you'll do:
AC-BRITTLE-011: Coverage gaps
├── Measure branch coverage
├── Identify gaps
└── Create improvement plan

AC-BRITTLE-012: Smoke tests
├── Create fast tests
├── Focus on critical paths
└── <10 second total runtime

AC-BRITTLE-013: Production readiness
├── End-to-end validation
├── Production simulation
└── Performance checks

AC-BRITTLE-014: CI/CD stabilization
├── Fix pipeline failures
├── Add retry logic
└── Improve logging
```

**New Test Suites**:
- `tests/smoke/` - Fast smoke tests
- `tests/production_readiness/` - Readiness checks
- `.github/workflows/` - Updated CI/CD

---

## 🏁 Phase Completion Checklist

For each AC-ID:

- [ ] Write all unit tests (TDD)
- [ ] Write all integration tests
- [ ] Implement the feature
- [ ] All tests pass (green)
- [ ] 100% code coverage for the feature
- [ ] Type hints complete
- [ ] Docstrings complete
- [ ] Commit to git with audit log entry
- [ ] Mark AC as COMPLETED in cortex-master.yaml

For the entire phase:

- [ ] All 17 ACs = COMPLETED
- [ ] All 259 tests passing
- [ ] Phase status updated to COMPLETED
- [ ] Phase locked in cortex-master.yaml
- [ ] Final validation passed
- [ ] Git tag created (phase-05-complete)

---

## 🔧 TDD Workflow (For Each AC)

```
1. Load AC Specification
   ├── Open cortex-master.yaml
   ├── Find phases.phase_05.ac_ids.AC-XXXX
   └── Review success_criteria and testing requirements

2. Write Tests First (TDD)
   ├── Create tests/unit/test_ac_xxxx.py
   ├── Write all N unit tests (from testing.unit_tests_expected)
   ├── Create tests/integration/test_ac_xxxx.py
   ├── Write all M integration tests
   └── Verify tests are RED (fail initially)

3. Implement Code
   ├── Create implementation module
   ├── Add type hints
   ├── Add docstrings
   └── Follow governance rules

4. Run Tests
   ├── Run unit tests: pytest tests/unit/test_ac_xxxx.py
   ├── Run integration tests: pytest tests/integration/test_ac_xxxx.py
   ├── Verify all tests GREEN (pass)
   └── Check coverage >95%

5. Verify & Commit
   ├── Code review (self)
   ├── Coverage check
   ├── Type checking: mypy
   ├── Style check: black, isort, pylint
   ├── Commit: git commit -m "ac-xxxx: implementation complete"
   └── Update cortex-master.yaml status: COMPLETED

6. Move to Next AC
   └── Repeat for next AC-ID
```

---

## 📂 File Organization Reference

```
CORTEX/
├── cortex_brain/
│   └── tier0/
│       ├── import_resolver.py (NEW - Wave 1)
│       ├── path_abstraction.py (NEW - Wave 1)
│       ├── platform_compat.py (NEW - Wave 2)
│       └── governance/
│           └── (existing - no changes)
│
├── tests/
│   ├── conftest.py (ENHANCED - Wave 4)
│   ├── unit/
│   │   ├── test_import_resolver.py (NEW - Wave 1)
│   │   ├── test_path_abstraction.py (NEW - Wave 1)
│   │   ├── test_platform_compat_*.py (NEW - Wave 2)
│   │   ├── test_code_quality.py (NEW - Wave 3)
│   │   └── test_brittleness_*.py (NEW - Wave 4-5)
│   ├── integration/
│   │   ├── test_import_resolver_integration.py (NEW - Wave 1)
│   │   ├── test_path_abstraction_integration.py (NEW - Wave 1)
│   │   └── test_brittleness_*.py (NEW - Wave 2-5)
│   ├── smoke/
│   │   └── *.py (NEW - Wave 5)
│   ├── production_readiness/
│   │   └── *.py (NEW - Wave 5)
│   └── utils/
│       ├── flakiness_reporter.py (NEW - Wave 4)
│       ├── db_transaction_handler.py (NEW - Wave 4)
│       └── mock_factory.py (NEW - Wave 4)
│
├── .github/
│   └── workflows/
│       ├── test.yml (UPDATED - Wave 5)
│       └── quality.yml (UPDATED - Wave 5)
│
├── .pylintrc (CREATED/UPDATED - Wave 3)
├── .black.json (CREATED/UPDATED - Wave 3)
├── pyproject.toml (UPDATED - Wave 3)
└── pytest.ini (UPDATED - all waves)
```

---

## 🔄 Daily Workflow

**Morning**:
1. Check which AC you're on in Wave X
2. Open `cortex-master.yaml` → find AC-ID section
3. Review the success_criteria and testing requirements
4. Plan the day's work (unit tests, implementation, integration tests)

**Development**:
1. Start with tests (TDD)
2. Write unit tests first
3. Run: `pytest tests/unit/test_ac_xxxx.py -v` (expect failures)
4. Implement code
5. Run tests again (expect successes)
6. Write integration tests
7. Run: `pytest tests/integration/test_ac_xxxx.py -v`
8. Verify coverage: `pytest --cov`

**Evening**:
1. Commit completed AC: `git commit -m "ac-xxxx: implementation complete"`
2. Update cortex-master.yaml: AC status → COMPLETED
3. Run validation: `python3 scripts/validate_phase_sync.py`
4. Commit master changes: `git commit -m "cortex-master: AC-xxxx marked COMPLETED"`
5. Update this guide with progress

---

## ✅ Definition of Done (Per AC)

Each AC is **DONE** when:

- ✅ All unit tests pass (green)
- ✅ All integration tests pass (green)
- ✅ Code coverage >95%
- ✅ 100% type hints
- ✅ 100% docstrings
- ✅ Code review passed (self or peer)
- ✅ Passes pylint, black, isort checks
- ✅ No warnings in mypy
- ✅ Committed to git
- ✅ Status updated to COMPLETED in cortex-master.yaml
- ✅ Audit log entry created

---

## 🆘 When Stuck

If a test keeps failing:

1. **Read the error carefully** - It tells you what's wrong
2. **Add print statements** - Debug what's happening
3. **Simplify** - Remove features until test passes
4. **Check dependencies** - Make sure mocks are set up
5. **Ask in comments** - Document the issue

If an implementation is hard:

1. **Break it down** - Smaller functions are easier
2. **Start simple** - Add complexity step-by-step
3. **Copy patterns** - Look at similar code
4. **Write tests first** - Let tests guide design
5. **Review code** - Get feedback early

---

## 📞 Phase Navigation

**Previous Phase**: PHASE-04 (Production Hardening & Security) ✅ COMPLETED

**Next Phase**: PHASE-PARALLEL (Folder Migration & Organization)

**After PHASE-05**: 
- PHASE-PARALLEL can run in parallel
- PHASE-06-ECOSYSTEM starts after PHASE-05
- Follow the blocks/requires fields in cortex-master.yaml

---

## 🎓 Learning Resources

- `cortex-builder.prompt.md` - Phase methodology
- `cortex-master.yaml` - Source of truth for all phases
- `tests/` - Look at existing tests for patterns
- `cortex_brain/` - Look at existing code for style

---

## 📈 Progress Tracking

| Wave | ACs | Tests | Est. Days | Status |
|------|-----|-------|-----------|--------|
| 1 | 2 | 52 | 1-2 | ⏭️ READY |
| 2 | 3 | 42 | 2-3 | ⏸️ Blocked by Wave 1 |
| 3 | 3 | 49 | 2-3 | ⏸️ Blocked by Wave 2 |
| 4 | 5 | 80 | 3-4 | ⏸️ Blocked by Wave 3 |
| 5 | 4 | 56 | 2-3 | ⏸️ Blocked by Wave 4 |
| **Total** | **17** | **259** | **12-14** | **IN_PROGRESS** |

---

## 🚀 Next Immediate Step

**Start Wave 1 Now**:

1. Open AC-BRITTLE-001 in cortex-master.yaml
2. Create `tests/unit/test_import_resolver.py`
3. Write 20 unit tests (TDD style)
4. Run: `pytest tests/unit/test_import_resolver.py -v` (expect RED)
5. Create `cortex_brain/tier0/import_resolver.py`
6. Implement ImportResolver class
7. Run tests again (expect GREEN)
8. Repeat for integration tests
9. Move to AC-BRITTLE-002

---

**Good luck! PHASE-05 implementation is now LIVE. 🚀**

---

Generated: 2026-01-18  
Phase: 05 of 24+  
Status: IN_PROGRESS ✅
