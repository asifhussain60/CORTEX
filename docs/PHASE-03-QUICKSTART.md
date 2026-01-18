# ⚡ PHASE-03 Quick Start Guide

**Status**: 🟢 Ready to Begin  
**First AC-ID**: AC-NFR-002-01 (Graceful Degradation Framework)  
**Time to Complete**: ~3-4 hours (TDD)  

---

## Start Here (30 seconds)

```bash
# 1. Read the kickoff summary
cat docs/PHASE-03-KICKOFF-SUMMARY.md

# 2. Read detailed spec for first AC-ID
cat docs/AC-NFR-002-01-SPECIFICATION.md

# 3. You're ready to code!
```

---

## The TDD Workflow (AC-NFR-002-01)

### Step 1: Create Test File (5 minutes)
```bash
touch tests/tier2/test_graceful_degradation.py
```

### Step 2: Write All Tests First (30 minutes)
Based on spec in `docs/AC-NFR-002-01-SPECIFICATION.md`:

- 12 unit tests (see "Unit Tests (12 total)" section)
- 5 integration tests (see "Integration Tests (5 total)" section)

```python
# tests/tier2/test_graceful_degradation.py
import pytest
from cortex_brain.tier2.resilience import (
    GracefulDegradationFramework,
    FallbackStrategy,
    PartialFunctionalityMode,
    ComponentFailure,
    DegradedResponse,
)

class TestGracefulDegradationFramework:
    def test_init_framework(self):
        """Framework initializes with empty registry"""
        framework = GracefulDegradationFramework()
        # assertions...
    
    # ... 11 more unit tests
    
    # ... 5 integration tests
```

### Step 3: Watch Tests Fail (Normal!)
```bash
pytest tests/tier2/test_graceful_degradation.py -v
# All tests fail - this is expected (TDD)
```

### Step 4: Implement Classes (2 hours)
Create in: `cortex_brain/tier2/resilience/__init__.py` (or separate module)

Key classes from spec:
- `GracefulDegradationFramework` - main orchestrator
- `FallbackStrategy` - encapsulates strategies
- `PartialFunctionalityMode` - degraded operation
- `ComponentFailure` - exception class
- `DegradedResponse` - response wrapper

**Requirements**:
- 100% type hints on all public methods
- 100% docstrings on all public methods
- Thread-safe if concurrent access

### Step 5: Run Tests Until All Pass (1 hour)
```bash
pytest tests/tier2/test_graceful_degradation.py -v
# Keep implementing until all 17 pass with 100% pass rate
```

### Step 6: Update Master File (2 minutes)
```bash
# Edit: _workspaces/roadmap/cortex-master.yaml
# Find: phases: → phase_03: → ac_ids: → AC-NFR-002-01:
# Change:
#   status: COMPLETED
#   completed_at: '2026-01-18T...' (current timestamp)
```

### Step 7: Validate (1 minute)
```bash
python3 scripts/validation/validate_phase_sync.py
# Should pass with all checks OK
```

### Step 8: Commit (1 minute)
```bash
git add _workspaces/roadmap/cortex-master.yaml \
       tests/tier2/test_graceful_degradation.py \
       cortex_brain/tier2/resilience.py

git commit -m "phase-03: AC-NFR-002-01 COMPLETED - Graceful Degradation Framework

- Implemented 5 classes (GracefulDegradationFramework, FallbackStrategy, PartialFunctionalityMode, ComponentFailure, DegradedResponse)
- All 17 tests passing (12 unit + 5 integration)
- 100% type hints and docstrings
- Thread-safe implementation with RLock
- <100ms overhead for degradation decision
- Governance compliance: CORE-008, CORE-011, CORE-012, CORE-024, CORE-028"
```

---

## Master File Reference

All specs are in: `_workspaces/roadmap/cortex-master.yaml`

### Location
```bash
# See current PHASE-03 status
grep -A 50 "phase_03:" _workspaces/roadmap/cortex-master.yaml

# See AC-NFR-002-01 details
grep -A 30 "AC-NFR-002-01:" _workspaces/roadmap/cortex-master.yaml
```

### Update After Completing AC-ID
```yaml
# File: _workspaces/roadmap/cortex-master.yaml
# Find this section:
phase_03:
  ac_ids:
    AC-NFR-002-01:
      status: COMPLETED           # ← Change this from IN_PROGRESS/NOT_STARTED
      completed_at: '2026-01-18T14:45:00Z'  # ← Add this timestamp

# That's it! No other files to update.
```

---

## The 5 Classes You Need to Implement

### 1. GracefulDegradationFramework
Main orchestrator for degradation strategies

**Key Methods**:
- `__init__()` - Initialize
- `register_component(name, primary_strategy, fallback_strategies)` - Register
- `execute_with_degradation(component_name, *args, **kwargs)` - Execute with fallback
- `is_degraded(component_name)` - Check degradation status
- `get_degradation_status()` - Get all components status

### 2. FallbackStrategy
Encapsulates a single fallback strategy

**Key Methods**:
- `__init__(callable, priority, max_retries)` - Initialize
- `execute(*args, **kwargs)` - Execute with retries

### 3. PartialFunctionalityMode
Manages operation in degraded state

**Key Methods**:
- `disable_feature(feature_name, reason)` - Disable feature
- `enable_feature(feature_name)` - Re-enable feature
- `is_feature_available(feature_name)` - Check availability
- `get_available_features()` - List available features
- `get_status()` - Get all features status

### 4. ComponentFailure (Exception)
Represents component failure with context

**Key Attributes**:
- `component_name` - Failed component
- `reason` - Failure reason
- `strategies_tried` - Number of fallbacks attempted
- `last_exception` - Last exception encountered

### 5. DegradedResponse (Generic)
Wraps response with degradation metadata

**Key Methods**:
- `__init__(data, degradation_reason, mode, original_request_id)` - Initialize
- `get_data()` - Get wrapped data
- `is_degraded()` - Check if degraded
- `get_metadata()` - Get metadata dict

---

## Testing Strategy

### Unit Tests (12 total)
```
✓ Framework initialization
✓ Component registration (success & duplicate error)
✓ Primary strategy success
✓ Primary strategy failure with fallback
✓ Fallback strategy success
✓ All strategies fail (exception)
✓ Degradation status check
✓ Feature disable/enable
✓ Feature availability check
✓ Available features list
✓ DegradedResponse wrapper
✓ ComponentFailure exception
```

### Integration Tests (5 total)
```
✓ Multiple components with different states
✓ Degradation recovery (primary becomes available)
✓ Concurrent access (thread safety)
✓ Status reporting (all components)
✓ End-to-end workflow
```

---

## Governance Compliance

✅ **CORE-008**: Use TDD (tests first, then code)  
✅ **CORE-011**: 100% type hints on all public methods  
✅ **CORE-012**: 100% docstrings on all public methods  
✅ **CORE-024**: Log all state changes  
✅ **CORE-028**: Use portable paths: `from pathlib import Path; Path(__file__).parent`  

---

## Quick Commands

```bash
# Load phase info
grep -A 100 "phase_03:" _workspaces/roadmap/cortex-master.yaml | head -50

# Read AC-NFR-002-01 spec
cat docs/AC-NFR-002-01-SPECIFICATION.md

# Run tests
pytest tests/tier2/test_graceful_degradation.py -v

# Check type hints
mypy cortex_brain/tier2/resilience.py --strict

# Validate before commit
python3 scripts/validation/validate_phase_sync.py

# See what changed
git diff _workspaces/roadmap/cortex-master.yaml

# Commit
git commit -m "phase-03: AC-NFR-002-01 COMPLETED"
```

---

## Expected Timeline

| Task | Time |
|------|------|
| Create test file | 5 min |
| Write all tests | 30 min |
| Implement 5 classes | 2 hours |
| Make tests pass | 30 min |
| Type hints & docstrings | 15 min |
| Update master file | 5 min |
| Validate & commit | 10 min |
| **TOTAL** | **~3.5 hours** |

---

## Common Issues & Solutions

### Issue: Tests can't find module
**Solution**: Check `cortex_brain` folder exists and has `__init__.py`

### Issue: Type hints not recognized
**Solution**: Add `from __future__ import annotations` at top of file

### Issue: Validation fails
**Solution**: Run with `--verbose` flag:
```bash
python3 scripts/validation/validate_phase_sync.py --verbose
```

### Issue: Pre-commit hook fails
**Solution**: Make sure master file change is staged:
```bash
git add _workspaces/roadmap/cortex-master.yaml
```

---

## Next AC-IDs (After 002-01)

Once AC-NFR-002-01 is complete:

1. **AC-NFR-002-02**: Automatic Retry (builds on 002-01)
2. **AC-NFR-002-03**: Circuit Breaker (builds on 002-01)
3. **AC-NFR-004-01**: OpenTelemetry Metrics
4. **AC-NFR-004-02**: Dashboard Service
5. **AC-NFR-004-03**: Alert Management

All follow the same TDD workflow.

---

## References

📄 **Complete Spec**: `docs/AC-NFR-002-01-SPECIFICATION.md`  
📄 **Implementation Guide**: `docs/PHASE-03-IMPLEMENTATION-KICKOFF.md`  
📄 **All Resources**: `docs/PHASE-03-RESOURCES.md`  
📄 **Master Plan**: `_workspaces/roadmap/cortex-master.yaml` (phases: → phase_03:)  

---

## Ready?

✅ All 6 AC-IDs documented  
✅ First AC-ID has detailed spec  
✅ Pre-commit hook working  
✅ Master file ready  
✅ You have the TDD workflow  

**Start with AC-NFR-002-01 - Create test file and write tests first!**

---

**Status**: 🟢 Ready to Code  
**Commit**: 1b4099f81  
**Date**: 2026-01-18  
