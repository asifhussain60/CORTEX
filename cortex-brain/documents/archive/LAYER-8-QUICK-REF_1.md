# Test Location Isolation - Quick Reference

**Rule:** TEST_LOCATION_SEPARATION (Tier 0 Instinct)  
**Layer:** 8 - Test Location Isolation  
**Status:** ✅ Active

---

## Quick Decision Tree

```
Are you testing CORTEX code?
│
├─ YES → Tests go in CORTEX/tests/
│         (brain, agents, workflows, tier systems)
│
└─ NO  → Tests go in user repo
          (application features, business logic)
```

---

## Examples

### ✅ CORRECT

| Source File | Test Location | Reason |
|------------|---------------|---------|
| `/CORTEX/src/tier0/brain_protector.py` | `/CORTEX/tests/test_brain_protector.py` | CORTEX infrastructure |
| `/Users/you/myapp/src/payment.py` | `/Users/you/myapp/tests/test_payment.py` | User application |
| `/CORTEX/src/workflows/tdd_orchestrator.py` | `/CORTEX/tests/workflows/test_tdd_orchestrator.py` | CORTEX workflow |
| `/home/dev/project/lib/auth.js` | `/home/dev/project/tests/lib/auth.test.js` | User library |

### ❌ WRONG

| Source File | Wrong Test Location | Why Wrong | Correct Location |
|------------|-------------------|-----------|------------------|
| `/Users/you/myapp/src/feature.py` | `/CORTEX/tests/test_feature.py` | App test in CORTEX | `/Users/you/myapp/tests/test_feature.py` |
| `/CORTEX/src/tier1/memory.py` | `/Users/you/tests/test_memory.py` | CORTEX test in user repo | `/CORTEX/tests/tier1/test_memory.py` |

---

## Auto-Detection Logic

```python
def is_cortex_test(source_file: str) -> bool:
    """
    Returns True if source file is within CORTEX folder.
    """
    source_path = Path(source_file).resolve()
    cortex_root = Path(__file__).parent.parent.parent.resolve()
    
    try:
        source_path.relative_to(cortex_root)
        return True  # Source is within CORTEX
    except ValueError:
        return False  # Source is outside CORTEX
```

---

## Brain Learning

**What gets stored in brain:**
```yaml
✅ patterns:
  - framework: "pytest"
  - naming: "test_*.py"
  - fixtures: "conftest.py with db_session"
  - mocks: "responses library for API"
  
❌ NOT stored:
  - Actual test code
  - Business logic
  - User's IP
```

**Storage location:** `cortex-brain/tier2/knowledge_graph.db`

---

## Configuration

```python
TDDWorkflowConfig(
    auto_detect_test_location=True,   # Auto-detect user repo
    enable_brain_learning=True,       # Capture patterns
    user_repo_root=None,              # Auto-detected
    is_cortex_test=False              # Set automatically
)
```

---

## Common Issues

### Issue: "Tests generated in wrong location"
**Solution:** CORTEX auto-detects. If wrong, check:
1. Is source file path correct?
2. Is working directory set correctly?
3. Try explicit `user_repo_root` in config

### Issue: "Brain not learning from my tests"
**Solution:** Enable brain learning:
```python
config.enable_brain_learning = True
```

### Issue: "CORTEX using wrong test framework"
**Solution:** CORTEX auto-detects from:
- `requirements.txt` (Python)
- `package.json` (JavaScript)
- `.csproj` (C#)
- Existing test files

---

## Enforcement

**Brain Protector Agent:**
- Monitors all test generation
- Validates paths before creation
- Blocks violations
- Suggests correct alternatives

**Challenge Example:**
```
⚠️  Layer 8 Violation: Test Location Isolation

Target: CORTEX/tests/test_user_feature.py
Reason: Application test in CORTEX folder

✅ Correct: /Users/you/myapp/tests/test_user_feature.py
```

---

**Version:** 1.0  
**Updated:** 2025-11-24  
**Author:** Asif Hussain
