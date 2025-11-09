# SKULL Protection Quick Reference

**"The SKULL protects the brain. Test before you claim."**

---

## 🛡️ The 4 Rules

| Rule | Severity | Violation | Fix |
|------|----------|-----------|-----|
| **SKULL-001** | 🚫 BLOCKING | "Fixed ✅" without tests | Add test: `test_feature_works` |
| **SKULL-002** | 🚫 BLOCKING | Integration without E2E test | Add test: `test_integration_end_to_end` |
| **SKULL-003** | ⚠️ WARNING | CSS without visual validation | Add test: `test_css_computed_style` |
| **SKULL-004** | ⚠️ WARNING | Retry without diagnosis | Document root cause first |

---

## 📝 Usage Example

```python
from src.tier0.skull_protector import enforce_skull, FixValidationRequest

# Before claiming fix complete
request = FixValidationRequest(
    fix_type="bug_fix",  # or "integration", "css_change", "retry"
    tests_run=["test_button_color_is_dark"],
    verification={"test_passed": True},
    description="Fix button color"
)

# Validate
try:
    validation = enforce_skull(request)
    return "Fixed ✅ (Verified by: test_button_color_is_dark)"
except SkullProtectionError as e:
    return f"❌ BLOCKED: {e.message}"
```

---

## ✅ Fix Types

- `bug_fix` - Bug fixes (requires test)
- `feature` - New features (requires test)
- `integration` - Component integration (requires E2E test)
- `css_change` - CSS/UI updates (requires visual test)
- `refactor` - Code restructuring (requires test)
- `retry` - Retry after failure (requires diagnosis)

---

## 🎯 Test Naming Patterns

**SKULL detects these keywords in test names:**

- **Integration:** `integration`, `e2e`, `end_to_end`
- **Visual:** `visual`, `css`, `style`, `computed`, `browser`
- **General:** Any test name with `test_` prefix

---

## 📊 When SKULL Blocks

```
❌ BLOCKED: SKULL-001 VIOLATION
No tests run for bug_fix. Cannot claim fix is complete without test validation.

Required: At least one automated test
Found: []

Alternatives:
- Create automated test before claiming fix
- Run test and include results in response
- Show test output: 'Fixed ✅ (Verified by: test_name)'
```

---

## 🔧 Quick Fixes

### Violation: No test run
```python
# Add this before claiming success
tests_run = ["test_my_feature"]
```

### Violation: No E2E test for integration
```python
# Add integration test
tests_run = ["test_unit_component", "test_integration_end_to_end"]
```

### Violation: No visual test for CSS
```python
# Add visual validation
tests_run = ["test_css_computed_style_is_correct"]
```

### Violation: Retry without diagnosis
```python
# Add diagnosis to verification
verification = {
    "diagnosis": "Root cause: Browser cache not cleared",
    "fix_approach_changed": True
}
```

---

## 📁 Files

- **Implementation:** `src/tier0/skull_protector.py`
- **Tests:** `tests/tier0/test_skull_protector.py`
- **Rules:** `cortex-brain/brain-protection-rules.yaml`
- **Documentation:** `cortex-brain/SKULL-PROTECTION-LAYER.md`

---

## 🎉 Benefits

✅ No untested changes reach production  
✅ "Fixed ✅" actually means fixed  
✅ Catch issues immediately, not after 3 attempts  
✅ Forces root cause analysis  
✅ Test suite grows with every fix  

---

**Created:** 2025-11-09  
**Incident:** CSS + Vision API testing failures  
**Status:** PRODUCTION READY ✅
