# CORTEX Toolkit - Testing Utilities

Testing, validation, and quality assurance tools.

## Tools

### validate (`cortex-validate`)

**Purpose:** Validate deployment integrity and system state.

**File:** `validate_deployment.py`

**Usage:**
```bash
python cortex-toolkit/testing/validate_deployment.py
```

**Features:**
- Deployment integrity checks
- Configuration validation
- Dependency verification
- File structure validation

---

### test-performance (`cortex-test-perf`)

**Purpose:** Generate and run performance tests.

**File:** `generate_performance_tests.py`

**Usage:**
```bash
python cortex-toolkit/testing/generate_performance_tests.py
```

**Features:**
- Performance test generation
- Benchmark execution
- Performance regression detection
- Timing analysis

---

### verify-no-mocks (`cortex-verify-mocks`)

**Purpose:** Verify no mock objects in tests (SKULL enforcement).

**File:** `verify_no_mocks.py`

**Usage:**
```bash
python cortex-toolkit/testing/verify_no_mocks.py
```

**Features:**
- Mock detection in test files
- TDD validation
- SKULL rule enforcement
- Test quality assurance

---

## Integration

Testing utilities integrate with:
- **TDD Mastery:** RED→GREEN→REFACTOR cycle
- **SKULL Protection:** Brain protection rules
- **CI/CD:** Automated validation gates

## Best Practices

- Run validation before deployment
- Include performance tests in CI pipeline
- Enforce no-mock rule for integration tests
- Use pytest for test execution
