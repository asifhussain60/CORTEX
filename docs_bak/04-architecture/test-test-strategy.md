# Test Strategy for Execution Specifications

**Document:** AC-PERMANENT-FIX-010 Phase 1  
**Author:** CORTEX Orchestrator  
**Date:** 2026-01-26  
**Status:** Test Strategy Definition

---

## 1. Overview

This document defines comprehensive testing strategy for Phase 1-8 of AC-PERMANENT-FIX-010
execution specifications implementation.

**Test Philosophy:**
- CORE-008: Tests BEFORE implementation (TDD)
- Parallel test streams (old code + new code)
- Equivalence testing (prove old ≈ new)
- Progressive expansion through phases

---

## 2. Test Pyramid

```
            ▲
           /|\
          / | \
         /  |  \           Integration Tests (20%)
        /   |   \          - End-to-end workflows
       /    |    \         - Gateway + specs interaction
      /_____|_____\        - Governance + orchestrators
     /      |      \
    /       |       \       Unit Tests (60%)
   /        |        \      - Individual components
  /         |         \     - Mocking dependencies
 /__________|_________\     - Edge cases
 |          |          |
 |   E2E    | Strategy |    Strategy Tests (20%)
 |__________|__________|    - DoR gate
            |                - Intent classification
            ▼                - Decision making
```

---

## 3. Phase 1 Test Plan

### 3.1 Unit Tests (Foundation Layer)

**Location:** `tests/unit/cortex/execution/`

#### Test File: `test-spec-models.py`
- [ ] Test RoutingRule dataclass validation
- [ ] Test OrchestratorDispatch dataclass validation
- [ ] Test OperationRouting dataclass validation
- [ ] Test ViolationCode enum completeness
- **Target:** 8 tests, 100% pass

#### Test File: `test-spec-schema-val.py`
- [ ] Validate JSON schema format (well-formed JSON)
- [ ] Verify all required definitions present
- [ ] Verify schema validation rules are present
- [ ] Test schema with valid spec documents
- [ ] Test schema rejects invalid specs
- **Target:** 6 tests, 100% pass

#### Test File: `test-exec-gateway-impl.py`
- [ ] MasterGateway instantiation
- [ ] GatewayResult dataclass creation
- [ ] Spec validation rejection (invalid format)
- [ ] Spec validation acceptance (valid format)
- [ ] Basic gateway execute flow
- **Target:** 8 tests, 100% pass

#### Test File: `test-gateway-validator-spec.py`
- [ ] ValidationViolation creation
- [ ] ValidationResult creation
- [ ] Validate required fields present
- [ ] Validate unknown fields detected
- [ ] Validate operation field string check
- [ ] Validate intent field enumeration
- **Target:** 12 tests, 100% pass

#### Test File: `test-structured-decision.py`
- [ ] StructuredDecision creation (all types)
- [ ] StructuredDecision.to_dict() JSON-serializable
- [ ] StructuredDecision.to_json() valid JSON
- [ ] Format approval decision (no markdown)
- [ ] Format routing decision
- [ ] Format governance violation (structured codes)
- [ ] Format error result
- [ ] Format success result
- [ ] Ensure JSON serializable validation
- **Target:** 14 tests, 100% pass

**Unit Test Total:** 48 tests, 100% passing

---

### 3.2 Integration Tests (Specification Layer)

**Location:** `tests/integration/`

#### Test File: `test-spec-registry-integration.py`
- [ ] Load all YAML specs without error
- [ ] Cache parsed specs in memory
- [ ] Retrieve specs by operation
- [ ] Spec consistency validation
- [ ] Cross-spec reference validation
- [ ] SpecRegistry performance < 5ms lookup
- **Target:** 6 tests, 100% pass

#### Test File: `test-core-040-mandate.py`
- [ ] CORE-040 rule exists and valid YAML
- [ ] Rule enforcement methods documented
- [ ] Violation codes match schema
- [ ] Migration path defined
- [ ] CI/CD integration hooks defined
- **Target:** 5 tests, 100% pass

**Integration Test Total:** 11 tests, 100% passing

---

### 3.3 Governance Compliance Tests

**Location:** `tests/unit/cortex_brain/tier0/`

#### Test File: `test-core-040.py`
- [ ] CORE-040 rule exists in governance registry
- [ ] Rule version tracked
- [ ] Enforcement level documented
- [ ] Related rules cross-referenced
- [ ] Migration phases defined clearly
- **Target:** 5 tests, 100% pass

**Governance Test Total:** 5 tests, 100% passing

---

### 3.4 Documentation Tests

**Location:** `tests/integration/`

#### Test File: `test-gateway-design-doc.py`
- [ ] Design document exists at correct path
- [ ] Document contains all required sections
- [ ] Code examples are syntactically correct Python
- [ ] Architecture diagrams are properly formatted
- [ ] References to other docs are valid
- **Target:** 5 tests, 100% pass

**Documentation Test Total:** 5 tests, 100% passing

---

## 4. Phase 1 Test Execution

### 4.1 Test Run Order

```bash
# 1. Run unit tests (should pass immediately)
pytest tests/unit/cortex/execution/ -v

# 2. Run governance tests (validate CORE-040)
pytest tests/unit/cortex_brain/tier0/test-core-040.py -v

# 3. Run integration tests (validate specs)
pytest tests/integration/test-spec-registry-integration.py -v

# 4. Run documentation tests
pytest tests/integration/test-gateway-design-doc.py -v

# 5. Overall validation
pytest tests/unit/cortex/execution/ \
        tests/unit/cortex_brain/tier0/test-core-040.py \
        tests/integration/test-spec-*.py \
        -v --tb=short
```

### 4.2 Success Criteria (Phase 1)

| Criterion | Target | Status |
|-----------|--------|--------|
| Unit tests passing | 48/48 (100%) | ⏳ |
| Integration tests passing | 11/11 (100%) | ⏳ |
| Governance tests passing | 5/5 (100%) | ⏳ |
| Documentation tests passing | 5/5 (100%) | ⏳ |
| No regressions in existing tests | 6,847+ passing | ⏳ |
| Code coverage | >80% for new code | ⏳ |
| Spec schema valid | JSON-LD compliant | ⏳ |

---

## 5. Phase 2-5 Testing (Future Phases)

### 5.1 Refactoring Tests (Phase 4)

```
Parallel Test Streams:
  OLD PATH: Direct orchestrator calls (test-old-exec-path.py)
  NEW PATH: Via MasterGateway (test-new-exec-path.py)
  EQUIVALENCE: Prove old ≈ new (test-exec-equiv.py)
```

Tests to update:
- 12 IntentRouter tests
- 15 MasterOrchestrator tests
- 8 Governance tests
- 10 Integration tests
**Total:** 50-70 tests requiring updates

### 5.2 Production Validation Tests (Phase 6-8)

```
Gateway Enforcement Tests:
  - Direct orchestrator call detection
  - Gateway bypass attempt detection
  - Proper error handling and logging
  
Performance Benchmarks:
  - Spec lookup < 5ms (target)
  - Cache hit rate > 95%
  - Memory overhead < 10MB
```

---

## 6. Test Data & Fixtures

### 6.1 Sample Specifications

**Location:** `tests/fixtures/`

```yaml
# intent_samples.yaml
- intent: "implement"
  keywords: ["create", "add", "build"]
  
- intent: "fix"
  keywords: ["fix", "bug", "issue"]
```

### 6.2 Mock Objects

**Location:** `tests/conftest.py`

```python
@pytest.fixture
def mock_spec_registry():
    """Mock SpecRegistry for unit tests."""
    
@pytest.fixture
def mock_gateway_validator():
    """Mock GatewayValidator for unit tests."""
    
@pytest.fixture
def sample_operation_spec():
    """Sample operation specification for testing."""
```

---

## 7. Continuous Integration

### 7.1 GitHub Actions Workflow

**File:** `.github/workflows/test-phase-1.yaml`

```yaml
name: Phase 1 Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Phase 1 tests
        run: pytest tests/unit/cortex/execution/ ...
      - name: Report coverage
        run: coverage report
```

### 7.2 Test Reporting

```
Phase 1 Test Report
  ✅ Unit Tests: 48/48 passing
  ✅ Integration: 11/11 passing
  ✅ Governance: 5/5 passing
  ✅ Docs: 5/5 passing
  ✅ Regressions: 6,847/6,847 passing
  
Coverage:
  - exec_gateway_impl.py: 95%
  - gateway_validator_spec.py: 92%
  - structured_decision.py: 89%
  - Overall: 92% (target: >80%)
```

---

## 8. Test Maintenance

### 8.1 Test Updates Required

When updating specs:
- Re-run test-spec-schema-val.py
- Re-run test-spec-registry-integration.py
- Update fixtures if spec structure changes

When updating gateway:
- Run test-exec-gateway-impl.py
- Run integration tests to verify backwards compatibility

### 8.2 Test Documentation

Each test file should include:
- Purpose of test
- CORE rules being validated
- Expected behavior
- Edge cases covered

---

## 9. References

- **Unit Tests:** `tests/unit/cortex/execution/`
- **Integration Tests:** `tests/integration/`
- **Fixtures:** `tests/fixtures/`
- **Conftest:** `tests/conftest.py`
- **CI/CD:** `.github/workflows/`

---

**Document Status:** STRATEGY PHASE  
**Next Phase:** Phase 2 - Specification Implementation  
**Expected Test Completion:** 2026-02-02
