# TDD Mastery - Quick Start Guide

**Get started with TDD Mastery in 5 minutes**

---

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
pytest tests/test_generator/ -v
pytest tests/workflows/ -v
```

---

## Your First TDD Session

### Step 1: Create Source File

**File:** `my_app/calculator.py`

```python
def add(a: int, b: int) -> int:
    """Add two numbers."""
    pass  # Not implemented yet
```

### Step 2: Initialize Orchestrator

```python
from workflows.tdd_workflow_orchestrator import (
    TDDWorkflowOrchestrator,
    TDDWorkflowConfig
)

# Configure
config = TDDWorkflowConfig(
    project_root=".",
    test_output_dir="tests"
)

# Create orchestrator
orchestrator = TDDWorkflowOrchestrator(config)

# Start session
session_id = orchestrator.start_session("calculator_tdd")
print(f"Session started: {session_id}")
```

### Step 3: Generate Tests (RED Phase)

```python
# Generate comprehensive tests
result = orchestrator.generate_tests(
    source_file="my_app/calculator.py",
    function_name="add",
    scenarios=["edge_cases", "parametrized"]
)

print(f"✅ Generated {result['test_count']} tests")
print(f"📄 Test file: {result['test_file']}")
```

**Generated Tests:** `tests/my_app/test_calculator.py`

```python
def test_add_basic():
    assert add(2, 3) == 5

def test_add_negative_numbers():
    assert add(-1, -2) == -3

def test_add_zero():
    assert add(0, 5) == 5

@pytest.mark.parametrize("a,b,expected", [
    (1, 1, 2),
    (10, 20, 30),
    (-5, 5, 0),
])
def test_add_parametrized(a, b, expected):
    assert add(a, b) == expected
```

### Step 4: Run Tests (Should Fail)

```bash
$ pytest tests/my_app/test_calculator.py -v

# Expected: 4 failed (because add() not implemented)
```

### Step 5: Implement (GREEN Phase)

```python
# my_app/calculator.py
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
```

```bash
$ pytest tests/my_app/test_calculator.py -v

# Expected: 4 passed ✅
```

```python
# Verify tests pass
orchestrator.verify_tests_pass({
    "passed": 4,
    "failed": 0,
    "code_lines": 2
})
```

### Step 6: Get Refactoring Suggestions (REFACTOR Phase)

```python
suggestions = orchestrator.suggest_refactorings("my_app/calculator.py")

for suggestion in suggestions:
    print(f"{suggestion['type']}: {suggestion['description']}")
```

### Step 7: Complete Cycle

```python
orchestrator.complete_refactor_phase(lines_refactored=0)  # No refactoring needed
metrics = orchestrator.complete_cycle()

print(f"✅ Cycle complete!")
print(f"Tests: {metrics['tests_passing']}/{metrics['tests_written']}")
```

### Step 8: Save Progress

```python
from workflows.page_tracking import PageLocation

location = PageLocation(
    filepath="my_app/calculator.py",
    line_number=1,
    function_name="add"
)

orchestrator.save_progress(location, "Completed add function")
```

---

## Common Commands

### Resume Existing Session

```python
sessions = orchestrator.list_active_sessions()
print(f"Active sessions: {len(sessions)}")

# Resume specific session
resumed = orchestrator.resume_session(session_id)
print(f"Resumed: {resumed['feature_name']}")
```

### Get Session Summary

```python
summary = orchestrator.get_session_summary()

print(f"Feature: {summary['feature_name']}")
print(f"Cycles: {summary['total_cycles']}")
print(f"Tests: {summary['total_tests_written']}")
print(f"Pass rate: {summary['test_pass_rate']:.1f}%")
```

---

## Test Generation Scenarios

### Edge Cases
```python
result = orchestrator.generate_tests(
    source_file="my_file.py",
    scenarios=["edge_cases"]
)
# Generates: empty strings, None, zero, negative, boundary values
```

### Domain Knowledge
```python
result = orchestrator.generate_tests(
    source_file="auth/login.py",
    scenarios=["domain_knowledge"]
)
# Generates: password hashing, JWT tokens, session management
```

### Error Conditions
```python
result = orchestrator.generate_tests(
    source_file="api/endpoint.py",
    scenarios=["error_conditions"]
)
# Generates: ValueError, TypeError, network errors, timeouts
```

### Parametrized Tests
```python
result = orchestrator.generate_tests(
    source_file="utils/validator.py",
    scenarios=["parametrized"]
)
# Generates: multiple input combinations with pytest.mark.parametrize
```

### All Scenarios Combined
```python
result = orchestrator.generate_tests(
    source_file="payment/processor.py",
    scenarios=["edge_cases", "domain_knowledge", "error_conditions", "parametrized"]
)
# Generates: comprehensive test suite with all scenario types
```

---

## Configuration Options

```python
config = TDDWorkflowConfig(
    project_root=".",                          # Project root directory
    test_output_dir="tests",                   # Where to write test files
    session_storage="cortex-brain/sessions.db",# Session database path
    
    # Refactoring thresholds
    enable_refactoring=True,                   # Enable refactoring suggestions
    refactoring_confidence_threshold=0.75,     # Minimum confidence for suggestions
    
    # Session tracking
    enable_session_tracking=True,              # Enable save/resume
    auto_save_progress=True,                   # Auto-save after each phase
)
```

---

## Real-World Examples

See complete examples:
- `EXAMPLE-1-USER-AUTHENTICATION.md` - Authentication system with JWT
- `EXAMPLE-2-PAYMENT-PROCESSING.md` - Stripe payment integration
- `EXAMPLE-3-REST-API.md` - FastAPI REST endpoints (coming soon)

---

## Troubleshooting

### Import Error: "No module named 'workflows'"

```python
# Add project root to Python path
import sys
sys.path.insert(0, "/path/to/CORTEX")

from workflows.tdd_workflow_orchestrator import TDDWorkflowOrchestrator
```

### SQLite "database is locked"

Windows only - SQLite-WAL files may remain locked. This is a cleanup issue, not functional:

```python
# Use absolute paths for session storage
config = TDDWorkflowConfig(
    session_storage="D:/Projects/CORTEX/sessions.db"  # Absolute path
)
```

### No Tests Generated

Check that function exists in source file:

```python
# Ensure function is defined
def my_function():
    pass  # Even empty function works
```

---

## Next Steps

1. **Try authentication example:** `EXAMPLE-1-USER-AUTHENTICATION.md`
2. **Try payment example:** `EXAMPLE-2-PAYMENT-PROCESSING.md`
3. **Read Phase 1 report:** `cortex-brain/documents/implementation-guides/TDD-MASTERY-PHASE-1-FINAL-VALIDATION.md`
4. **Read Phase 2 report:** `cortex-brain/documents/implementation-guides/TDD-MASTERY-PHASE-2-FINAL-VALIDATION.md`
5. **Explore test generators:** `src/test_generator/` directory

---

**Questions?** See documentation in `cortex-brain/documents/implementation-guides/`
