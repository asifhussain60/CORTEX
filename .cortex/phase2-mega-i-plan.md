# PHASE 2 (MEGA-I): Test Isolation & Standardization

**Priority:** P0  
**Estimated Sessions:** 2-3  
**Start Date:** 2026-02-15

## Objective
Eliminate test interdependencies, establish fixtures, ensure parallel execution safety.

## Stages

### S1: Fixture Consolidation (1-2h)
- Audit conftest.py files across test hierarchy
- Create shared fixtures in tests/conftest.py
- Eliminate duplicate fixture definitions
- **AC:** Single source of truth for fixtures

### S2: Test Isolation Audit (2-3h)
- Run tests with pytest-xdist (parallel mode)
- Identify state leakage between tests
- Fix shared resource conflicts (files, DBs, ports)
- **AC:** All tests pass with `-n auto` flag

### S3: Mock Standardization (1-2h)
- Replace ad-hoc mocking with pytest-mock
- Create reusable mock factories
- Document mocking patterns
- **AC:** Consistent mocking across codebase

### S4: Temporary File Cleanup (30min-1h)
- Audit temp file usage in tests
- Use pytest tmp_path fixtures
- Ensure cleanup in teardown
- **AC:** No test artifacts left after run

### S5: Database Isolation (1-2h)
- Ensure each test gets fresh DB
- Use transactions + rollback pattern
- Mock external DB calls in unit tests
- **AC:** No DB state leakage

## Success Criteria
- ✅ All tests pass in parallel mode (`pytest -n auto`)
- ✅ No flaky tests (3 consecutive runs pass)
- ✅ Fixture reuse >80% (no duplication)
- ✅ Zero temp file leaks
- ✅ DB tests isolated with rollback

## Estimated Effort
- **Optimistic:** 5-6 hours
- **Realistic:** 8-10 hours
- **Pessimistic:** 12-15 hours (if major refactoring needed)
