# CORTEX Testing Strategy

**Version:** 1.0  
**Author:** Asif Hussain  
**Copyright © 2025 Asif Hussain. All rights reserved.**

---

## Overview

CORTEX uses a three-tier testing strategy to balance comprehensive validation with rapid feedback.

---

## Testing Tiers

### Tier 1: Smoke Tests (< 30 seconds)

**Purpose:** Fast validation for development workflow

**Location:** `tests/smoke/`

**Coverage:**
- Orchestrator imports
- SKULL rule enforcement
- Critical method existence
- Basic initialization
- Configuration file presence

**When to Run:**
- Before commits
- During active development
- CI/CD pre-checks

**Command:**
```bash
pytest tests/smoke/ -v
```

**Expected Result:** All tests pass in under 30 seconds

---

### Tier 2: Integration Tests (2-5 minutes)

**Purpose:** Comprehensive workflow validation

**Location:** `tests/orchestrators/`

**Coverage:**
- Full orchestrator workflows
- File I/O operations
- Git checkpoints
- Phase transitions
- Error handling
- Metrics collection

**When to Run:**
- Before pull requests
- After major feature changes
- Weekly full validation

**Command:**
```bash
pytest tests/orchestrators/ -v
```

**Expected Result:** 525+ tests pass with full coverage

---

### Tier 3: End-to-End Tests (10-15 minutes)

**Purpose:** Complete system validation

**Location:** `tests/e2e/`

**Coverage:**
- Multi-orchestrator workflows
- Real project scenarios
- Dashboard generation
- Learning capture
- Brain tier integration

**When to Run:**
- Before releases
- Monthly comprehensive validation
- Production deployment prep

**Command:**
```bash
pytest tests/ -v --cov=src
```

**Expected Result:** 100% orchestrator coverage, all e2e scenarios pass

---

## Usage Guidelines

### Development Workflow

1. **Write Code** → Run smoke tests
2. **Fix Bugs** → Run integration tests for affected module
3. **Refactor** → Run full integration suite
4. **Release** → Run all tiers

### CI/CD Pipeline

```yaml
stages:
  - smoke      # < 30s  - Block on failure
  - integration # 2-5m  - Block on failure
  - e2e        # 10-15m - Report only
```

### Performance Targets

| Tier | Target | Max Acceptable |
|------|--------|----------------|
| Smoke | 10s | 30s |
| Integration | 2m | 5m |
| E2E | 10m | 15m |

---

## Test Selection

### Run Smoke Tests Only
```bash
pytest tests/smoke/
```

### Run Specific Orchestrator Tests
```bash
pytest tests/orchestrators/test_planning_orchestrator_v3_1.py -v
```

### Run All Tests with Coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

### Run Tests Matching Pattern
```bash
pytest -k "planning" -v
```

---

## Smoke Test Categories

### Import Validation
- All orchestrators import without errors
- Dependencies resolve correctly
- No circular imports

### SKULL Rule Enforcement
- TDD_ENFORCEMENT present
- RED_PHASE_VALIDATION present
- HOLISTIC_CODE_DISCOVERY_ENFORCEMENT present
- REFACTOR_CODE_CLEANUP_ENFORCEMENT present
- GIT_ISOLATION_ENFORCEMENT present
- TEST_LOCATION_SEPARATION present

### Critical Methods
- create_plan
- execute_plan_autonomously
- create_temporary_plan
- approve_temporary_plan
- start_session
- execute

### Configuration
- cortex.config.json exists
- brain-protection-rules.yaml exists
- response-templates.yaml exists
- cortex-operations.yaml exists

---

## Troubleshooting

### Smoke Tests Failing

**Import Errors:**
- Check Python path includes `src/`
- Verify all dependencies in `requirements.txt`
- Run `pip install -r requirements.txt`

**SKULL Rule Missing:**
- Verify `cortex-brain/brain-protection-rules.yaml` exists
- Check rule name spelling
- Ensure rules loader is working

### Integration Tests Slow

**File I/O Bottleneck:**
- Use `pytest-xdist` for parallel execution:
  ```bash
  pytest tests/orchestrators/ -n auto
  ```

**Git Operations Slow:**
- Use in-memory git for tests
- Mock git operations where appropriate

### E2E Tests Failing

**Environment Issues:**
- Check `.venv` is activated
- Verify all system dependencies installed
- Run environment diagnostics

---

## Best Practices

### Writing Smoke Tests

✅ **DO:**
- Use mocks/stubs for external dependencies
- Validate structure without execution
- Keep tests independent
- Assert critical interfaces only

❌ **DON'T:**
- Perform real file I/O
- Make network calls
- Execute full workflows
- Create temporary files (unless cleaned immediately)

### Writing Integration Tests

✅ **DO:**
- Use `pytest` fixtures for setup/teardown
- Test complete workflows
- Validate file outputs
- Check error handling

❌ **DON'T:**
- Depend on external services
- Leave artifacts behind
- Assume test execution order

---

## Metrics

### Current Coverage (2025-12-14)

- **Smoke Tests:** 50+ tests, ~15s execution
- **Integration Tests:** 525+ tests, ~3-5m execution
- **Orchestrator Coverage:** 100% (9/9 orchestrators)
- **SKULL Rule Coverage:** 100% (6/6 rules)

---

## Future Enhancements

1. **Mutation Testing** - Validate test effectiveness
2. **Property-Based Testing** - Generate edge cases automatically
3. **Visual Regression** - Screenshot comparison for dashboards
4. **Performance Benchmarks** - Track execution time trends

---

**Quick Start:**

```bash
# Fast validation (development)
pytest tests/smoke/ -v

# Comprehensive validation (pre-commit)
pytest tests/orchestrators/ -v

# Full system validation (release)
pytest tests/ -v --cov=src
```
