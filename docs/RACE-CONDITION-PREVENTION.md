# Race Condition and Infinite Loop Prevention Guide

## AC-FIX-007: Test Race Condition Prevention

**Date**: 2026-01-17  
**Reviewer**: cortex-review-brittleness  
**Status**: IMPLEMENTED

---

## Problem Summary

Multiple test files contained `while True:` loops without safety guards, causing indefinite hangs when:
- Mock orchestrators failed to signal completion properly
- Database connection errors caused retry loops
- Test fixtures returned malformed data

---

## Fixes Implemented

### 1. Global Pytest Timeout Configuration

**File**: `pytest.ini`

```ini
# Timeout settings (prevent hanging tests)
timeout = 30
timeout_method = thread
```

**Benefit**: All tests automatically timeout after 30 seconds, preventing CI/CD pipeline hangs.

### 2. Per-Module Timeout Markers

**Files**: 
- `tests/unit/core/orchestrator/test_master_orchestrator.py`
- `tests/unit/core/orchestrator/test_wrapped_orchestrators.py`

```python
# Apply timeout to all tests in this module to prevent hangs
pytestmark = pytest.mark.timeout(10)
```

**Benefit**: Orchestrator tests get stricter 10-second timeout due to higher risk.

### 3. Maximum Iteration Guards in Test Mocks

**Pattern Applied To**:
- `MasterOrchestrator.execute_workflow()` - MAX_WORKFLOW_ITERATIONS = 100
- `MasterOrchestrator._execute_domain()` - MAX_DOMAIN_ITERATIONS = 50
- `WrappedOrchestrator.execute_with_continuation()` - MAX_TURN_ITERATIONS = 50

**Example**:

```python
class MasterOrchestrator:
    # Safety guard: Maximum iterations to prevent infinite loops
    MAX_WORKFLOW_ITERATIONS = 100
    MAX_DOMAIN_ITERATIONS = 50
    
    def execute_workflow(self, ...):
        workflow_iterations = 0
        
        while self.current_domain is not None:
            workflow_iterations += 1
            if workflow_iterations > self.MAX_WORKFLOW_ITERATIONS:
                return Err(
                    f"Workflow exceeded maximum iterations ({self.MAX_WORKFLOW_ITERATIONS}). "
                    f"Possible infinite loop in domain transitions."
                )
            # ... rest of logic
```

**Benefit**: Explicit error messages instead of silent hangs.

---

## Prevention Rules for Future Code

### RULE 1: Never Use Bare `while True` in Tests

❌ **BAD**:
```python
def test_orchestrator():
    while True:
        result = orchestrator.execute()
        if result.is_complete():
            break
```

✅ **GOOD**:
```python
def test_orchestrator():
    MAX_ITERATIONS = 100
    iterations = 0
    
    while True:
        iterations += 1
        if iterations > MAX_ITERATIONS:
            pytest.fail(f"Test exceeded {MAX_ITERATIONS} iterations")
        
        result = orchestrator.execute()
        if result.is_complete():
            break
```

### RULE 2: All Orchestrator Tests Must Have Timeout Markers

❌ **BAD**:
```python
class TestMyOrchestrator:
    def test_execute(self):
        # No timeout marker
        pass
```

✅ **GOOD**:
```python
pytestmark = pytest.mark.timeout(10)

class TestMyOrchestrator:
    def test_execute(self):
        # Automatically times out after 10 seconds
        pass
```

### RULE 3: Mock Orchestrators Must Signal Completion

❌ **BAD**:
```python
class MockOrchestrator:
    def execute(self, input, context):
        return {"status": "pending"}  # Never completes!
```

✅ **GOOD**:
```python
class MockOrchestrator:
    def __init__(self):
        self.call_count = 0
    
    def execute(self, input, context):
        self.call_count += 1
        if self.call_count >= 3:
            return {"status": "completed"}  # Signals completion
        return {"status": "pending"}
```

### RULE 4: Integration Tests with External Resources Need Higher Timeouts

```python
@pytest.mark.integration
@pytest.mark.timeout(60)  # Higher timeout for DB/network operations
def test_database_orchestration():
    pass
```

### RULE 5: Conversation Protocol Loops Need MAX_TURNS Verification

```python
protocol = ConversationProtocol(
    orchestrator,
    max_turns=5,  # ALWAYS set explicit limit
    token_limit=30000,
)
```

---

## Testing the Fixes

### Run Orchestrator Tests with Timeout Protection

```bash
# Run all orchestrator tests (will timeout after 10s per test)
python -m pytest tests/unit/core/orchestrator/ -v

# Run specific hanging test with verbose timeout info
python -m pytest tests/unit/core/orchestrator/test_master_orchestrator.py::TestMasterOrchestratorSingleDomain::test_single_domain_workflow_completes -v --timeout=10

# Run all tests with timeout report
python -m pytest tests/ -v --timeout=30 --timeout-method=thread
```

### Verify Timeout Configuration

```bash
# Check pytest.ini has timeout settings
grep -A2 "Timeout settings" pytest.ini

# Verify test files have pytestmark
grep "pytestmark = pytest.mark.timeout" tests/unit/core/orchestrator/*.py
```

---

## Checklist for Code Reviews

When reviewing PRs with orchestrator or conversation protocol code:

- [ ] Does the code use `while True` loops?
- [ ] If yes, is there a MAX_ITERATIONS guard?
- [ ] Does the test file have `pytestmark = pytest.mark.timeout(N)`?
- [ ] Do mock orchestrators properly signal completion?
- [ ] Are ConversationProtocol instances created with explicit max_turns?
- [ ] Do integration tests have appropriate timeout increases?
- [ ] Is there error messaging that explains what happened on timeout?

---

## Related Issues

- **ISSUE-003**: Race condition findings in orchestrator tests
- **FINDING-001**: Infinite while True loops without safety limits
- **FINDING-002**: ConversationProtocol lacks iteration guards
- **FINDING-003**: Missing pytest-timeout configuration

---

## Audit Trail

```sql
-- Verify no hanging test patterns remain
SELECT COUNT(*) as test_files_with_while_true
FROM (
    SELECT DISTINCT file_path 
    FROM code_analysis 
    WHERE file_path LIKE 'tests/%'
      AND content LIKE '%while True:%'
      AND content NOT LIKE '%MAX_ITERATIONS%'
);
```

Expected: 0 files with unguarded while True loops.

---

## Copyright

Copyright © 2025-2026 Asif Hussain. All rights reserved.
