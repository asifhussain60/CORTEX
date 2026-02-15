# Golden Test Framework - Orchestrator Tests

**Authority:** AC-GOLDEN-FRAMEWORK-001  
**Purpose:** Comprehensive orchestrator testing with zero mocks

## Directory Structure

```
tests/orchestrators/
├── core/                    # 8 core orchestrators (28 tests each)
│   ├── positive/           # Happy path scenarios
│   ├── negative/           # Forbidden action detection
│   ├── edge-cases/         # Boundary conditions
│   └── recovery/           # Crash and rollback
├── domain/                  # 6 domain orchestrators (16 tests each)
│   ├── positive/
│   ├── negative/
│   ├── edge-cases/
│   └── recovery/
├── support/                 # 14 support orchestrators (12 tests each)
│   ├── positive/
│   ├── negative/
│   ├── edge-cases/
│   └── recovery/
└── e2e/                    # Cross-orchestrator scenarios
```

## Test Categories

### Positive Tests
Happy path scenarios verifying correct orchestrator behavior.

### Negative Tests
Forbidden action detection - verify orchestrators properly BLOCK violations:
- TDD bypass attempts (`--ignore` flags)
- File naming violations (SCREAMING_CASE)
- Mock ratio >30%
- Missing audit trails

### Edge Case Tests
Boundary conditions:
- 0 orchestrators registered
- 1000+ concurrent requests
- 10MB context size
- Circular dependencies
- Empty requests

### Recovery Tests
Crash and rollback scenarios:
- Mid-execution crashes
- Database corruption
- EventBus disconnection
- Registry sync failures

## Base Test Classes

### `BaseOrchestratorTest`
Foundation class with real component fixtures:
- `real_event_bus()` - Live EventBus instance
- `audit_db()` - Real SQLite database
- `real_registry()` - GitBackedRegistry from cortex-registry/
- `assert_audit_trail()` - Verify AC markers
- `assert_no_mocks_used()` - Zero mock enforcement

### `BaseNegativeTest`
Forbidden action testing:
- `assert_blocked()` - Verify action blocked with correct error
- `assert_violation_logged()` - Verify governance violation logged

### `BaseEdgeCaseTest`
Boundary condition testing:
- `assert_graceful_degradation()` - Verify graceful failure
- `create_extreme_context()` - Generate boundary scenarios

### `BaseRecoveryTest`
Crash and rollback testing:
- `simulate_crash()` - Inject crash at execution point
- `assert_state_recovered()` - Verify recovery
- `assert_rollback_complete()` - Verify full rollback

## Running Tests

```bash
# Run all orchestrator tests
pytest tests/orchestrators/ -v

# Run specific category
pytest tests/orchestrators/core/positive/ -v

# Run specific orchestrator
pytest tests/orchestrators/core/positive/test-master-orchestrator.py -v

# Run with coverage
pytest tests/orchestrators/ --cov=cortex --cov-report=term
```

## Governance Compliance

- **CORE-008:** All tests follow TDD (written BEFORE implementation)
- **CORE-028:** All test files use kebab-case naming
- **CORE-002:** No markdown report generation (inline results only)
- **CORE-035:** Single canonical test implementation per orchestrator

## Zero Mock Policy

Golden tests use REAL components:
- ✅ Real EventBus (cortex.common.event_bus)
- ✅ Real GitBackedRegistry (cortex-registry/)
- ✅ Real SQLite databases (tmp_path fixtures)
- ❌ NO unittest.mock.Mock()
- ❌ NO unittest.mock.MagicMock()

Rationale: Catch integration issues that mocks hide.
