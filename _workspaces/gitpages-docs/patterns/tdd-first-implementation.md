# TDD-First Implementation Pattern
**Pattern ID:** PAT-001  
**Category:** Development Workflow  
**Status:** ✅ Validated (chat01.md)  
**Reusability:** HIGH

---

## 🎯 Problem

Implementing new features without tests leads to:
- Rework when tests reveal design flaws
- Low confidence in correctness
- Difficult refactoring (no safety net)
- Technical debt accumulation

## ✅ Solution

**RED → GREEN → REFACTOR cycle with tests written FIRST:**

### Phase 1: 🔴 RED (Tests First)
Write comprehensive tests BEFORE any implementation exists.

**Example from chat01.md:**
```python
# tests/unit/models/test_phase_detail_schema.py
def test_phase_detail_model_initialization():
    """Test that PhaseDetailModel initializes correctly."""
    phase = PhaseDetailModel(
        phase_id="phase-01",
        phase_name="Orchestrator Event Bus",
        # ... all required fields
    )
    assert phase.phase_id == "phase-01"
```

**Expected Behavior:**
- Import errors are NORMAL (implementation doesn't exist yet)
- Test runner shows failures
- Clear specification of expected behavior

### Phase 2: 🟢 GREEN (Minimal Implementation)
Create the simplest implementation that makes tests pass.

**Example from chat01.md:**
```python
# cortex/models/phase_detail_schema.py
from pydantic import BaseModel, Field

class PhaseDetailModel(BaseModel):
    """Phase detail page data model."""
    phase_id: str = Field(..., description="Unique phase identifier")
    phase_name: str = Field(..., description="Human-readable phase name")
    # ... implementation matching test expectations
```

**Result:** All 19 tests passing on first run ✅

### Phase 3: 🔵 REFACTOR (Optimize)
Improve code quality while keeping tests green.

---

## 📊 Evidence from chat01.md

| Metric | Value |
|--------|-------|
| **Tests Written First** | 23 tests before implementation |
| **Implementation Rework** | 0 cycles (tests passed immediately) |
| **Test Pass Rate** | 19/19 (100%) on first run |
| **Time Efficiency** | No debugging needed |

---

## 🔧 Implementation Steps

### Step 1: Write Test Specification
```bash
# Create test file first
touch tests/unit/models/test_my_feature.py

# Write comprehensive tests covering:
# - Happy path
# - Edge cases
# - Error conditions
# - Validation rules
```

### Step 2: Run Tests (Expect Failures)
```bash
pytest tests/unit/models/test_my_feature.py -v

# Expected output:
# ❌ ImportError: No module named 'cortex.models.my_feature'
# This is CORRECT for TDD RED phase
```

### Step 3: Create Minimal Implementation
```bash
# Create implementation file
touch cortex/models/my_feature.py

# Write ONLY enough code to pass tests
```

### Step 4: Validate GREEN
```bash
pytest tests/unit/models/test_my_feature.py -v

# Expected output:
# ✅ All tests passing
```

### Step 5: Refactor (Optional)
```bash
# Improve code quality while keeping tests green
# - Extract functions
# - Add docstrings
# - Optimize logic
```

---

## ⚠️ Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| **Writing implementation first** | Delete code, write tests, start over |
| **Import errors panic** | Expected in RED phase - proceed with confidence |
| **Skipping edge cases** | Test failure scenarios explicitly |
| **Over-engineering in GREEN** | Minimal code only - refactor later |

---

## 🎓 VS Code Cache Management

**Issue:** Import errors during RED phase confuse Pylance cache.

**Solution:** Clear caches before GREEN phase:
```bash
rm -rf ~/Library/Caches/pylance*
rm -rf ~/.vscode/extensions/ms-python.vscode-pylance-*/dist/bundled/stubs
find . -type d -name "__pycache__" -exec rm -rf {} +
rm -rf .pytest_cache .mypy_cache

# Then: Cmd+Shift+P → "Python: Restart Language Server"
```

---

## 🔗 Related Patterns

- **Incremental Feature Delivery** - Break large features into testable increments
- **VS Code Cache Clearing** - Developer environment maintenance

---

## 📚 References

- **CORE-008:** Tests BEFORE code (TDD mandatory)
- **chat01.md:** Successful TDD execution example
- **EnhancementOrchestrator:** Automated CORE-008 enforcement

---

**Validated:** 2026-02-05 via chat01.md session  
**Success Rate:** 100% (19/19 tests passing first run)
