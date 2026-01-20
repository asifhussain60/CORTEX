---
# ⚠️ CRITICAL: PHASE E STUB PREVENTION RULES
# Read this before implementing ANY module in PHASE E

metadata:
  title: "STUB PREVENTION: DO NOT CREATE EMPTY CLASSES"
  authority: "cortex-builder.prompt.md § CORE-008"
  enforcement: "Mandatory - blocks production release"
  version: "1.0"
  date: "2026-01-20"

---

## ⚠️ THE BIGGEST MISTAKE YOU CAN MAKE

**Do NOT do this:**

```python
# ❌ WRONG - This is a stub, not an implementation
class OrchestratorDecorator:
    pass  # ← This is a stub! Will pass import but fail tests!

# ❌ WRONG - Function that does nothing
def execute(self, func):
    pass  # ← Tests will fail with "TypeError: None is not expected_type"

# ❌ WRONG - Return None when test expects a value
def get_name(self):
    return None  # ← Test will fail with "AssertionError: None != 'expected_name'"
```

**Result of stub creation:**
- ✗ Tests import successfully (false confidence)
- ✗ Tests fail immediately on first assertion
- ✗ You didn't actually implement anything
- ✗ Wastes time on test fixes instead of implementation

**This is WHY Phase D should NOT have created stubs in the first place.**

---

## ✅ CORRECT APPROACH: TEST-DRIVEN IMPLEMENTATION

**Do this instead:**

```python
# ✅ CORRECT - Implementation that test expects
class OrchestratorDecorator:
    """Decorator for orchestrator execution context.
    
    Manages decorator chain, execution context, and
    callback management for orchestrator methods.
    """
    
    def __init__(self, func: Optional[Callable] = None) -> None:
        """Initialize decorator.
        
        Args:
            func: Optional function to decorate immediately.
        """
        self.func = func
        self.decorators: List[Callable] = []
    
    def execute(self, func: Callable) -> Callable:
        """Execute decorator chain on function.
        
        Args:
            func: Function to decorate.
        
        Returns:
            Decorated function with execution context.
        
        Raises:
            TypeError: If func is not callable.
        """
        if not callable(func):
            raise TypeError(f"Expected callable, got {type(func)}")
        
        # Implementation based on test requirements
        for decorator in self.decorators:
            func = decorator(func)
        
        return func

# ✅ CORRECT - Proper return value
def get_name(self) -> str:
    """Get decorator name.
    
    Returns:
        Decorator name from function or "unknown".
    """
    if self.func and hasattr(self.func, '__name__'):
        return self.func.__name__
    return "unknown"
```

**Result of proper implementation:**
- ✓ Tests import successfully
- ✓ Tests run and pass
- ✓ Implementation is complete
- ✓ No rework needed

---

## 🚫 STUB DETECTION: How to catch yourself creating a stub

**Red flag 1: Empty function body**
```python
def method(self):
    pass  # ← This is a stub!
```
Fix: Implement based on test, not just pass

**Red flag 2: Placeholder return**
```python
def method(self) -> str:
    return "placeholder"  # ← Stub behavior
```
Fix: Return what test actually expects

**Red flag 3: Comment instead of code**
```python
def method(self):
    # TODO: implement this
    return None  # ← Stub! Has no implementation
```
Fix: Implement NOW, not TODO

**Red flag 4: Bare except clause (also governance violation)**
```python
try:
    something()
except:  # ← Stub error handling!
    pass
```
Fix: Catch specific exception, handle properly

**Red flag 5: Hardcoded mock data**
```python
def fetch_data(self) -> List[str]:
    return ["mock", "data"]  # ← Stub behavior, not real implementation
```
Fix: Implement to fetch real data or raise NotImplementedError if not testable

---

## 🧪 THE TEST-FIRST DISCIPLINE

### For EACH module, follow this exactly:

```
1. READ TEST
   └─ Open test file completely
   └─ Understand what it tests
   └─ Note all test methods

2. RUN TEST (RED phase)
   └─ pytest tests/.../test_module.py -v
   └─ Watch it FAIL
   └─ See the error message
   └─ This error tells you what to implement

3. IMPLEMENT (GREEN phase)
   └─ Add minimum code to make error go away
   └─ Not beautiful, not complete
   └─ Just enough to pass test

4. RUN TEST AGAIN
   └─ pytest tests/.../test_module.py -v
   └─ If pass → go to next test
   └─ If fail → go back to IMPLEMENT

5. REFACTOR (after all tests pass)
   └─ Add type hints
   └─ Add docstrings
   └─ Clean up code
   └─ Run tests again (still pass)

6. COMMIT
   └─ git add ...
   └─ git commit -m "Module: X - Implement Y, Z; 50 tests passing"
```

### The Critical Rule: See RED before GREEN

**ALWAYS do this:**
```bash
# 1. Run test BEFORE implementing (RED)
$ pytest tests/unit/core/test_my_module.py -v
ImportError: cannot import name 'MyClass'

# 2. Create class
# 3. Run test AGAIN (still RED, different error)
$ pytest tests/unit/core/test_my_module.py -v
TypeError: __init__() missing required argument 'name'

# 4. Fix __init__
# 5. Run test AGAIN
$ pytest tests/unit/core/test_my_module.py -v
AssertionError: 'actual' != 'expected'

# 6. Fix implementation
# 7. Run test AGAIN (GREEN!)
$ pytest tests/unit/core/test_my_module.py -v
45 passed in 0.45s ✓
```

**Never do this:**
```bash
# ✗ WRONG: Create class and hope it works
# ✗ WRONG: Don't run test until implementation done
# ✗ WRONG: See test fail and create stub to "fix" it
```

---

## 🚨 WHAT HAPPENS IF YOU CREATE STUBS

**Scenario: You create an empty class to "move forward"**

```python
# Your "stub" implementation
class ConversationProtocol:
    pass
```

**The test runs:**
```python
def test_init():
    convo = ConversationProtocol(session_id="123")
    assert convo.session_id == "123"  # ← Test fails immediately!
```

**What you see:**
```
FAILED test_init - TypeError: __init__() takes 1 positional argument but 2 were given
```

**What you have to do:**
- Fix __init__ signature
- Add session_id parameter
- Store it
- Re-run test (different error)
- Implement that requirement
- Repeat...

**You wasted time on test chasing instead of implementing!**

---

## ✅ WHAT HAPPENS IF YOU IMPLEMENT PROPERLY

**You read the test:**
```python
def test_init():
    convo = ConversationProtocol(session_id="123")
    assert convo.session_id == "123"
```

**You implement directly:**
```python
class ConversationProtocol:
    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
```

**Test passes immediately.**

**You move to next module.**

---

## 🔍 STUB DETECTION CHECKLIST

Before committing any module, run this checklist:

```
☐ Did I see the test FAIL before implementing?
  → If no: Go back and run test first!

☐ Does module have any "pass" statements?
  → If yes: Implement those functions!
  
☐ Does module have any "return None" with no reason?
  → If yes: Return something meaningful!
  
☐ Does module have any "TODO" comments?
  → If yes: Implement now or raise NotImplementedError!
  
☐ Does module have hardcoded mock/test data?
  → If yes: Make it real or make it parameterized!
  
☐ Does pytest show all tests PASSING?
  → If no: Not done! Keep implementing!
  
☐ Does mypy --strict show 0 errors?
  → If no: Add type hints and fix!
  
☐ Do all functions have Google docstrings?
  → If no: Add docstrings!
  
☐ Do all functions have return type hints?
  → If no: Add return type!
  
☐ Are there any bare "except:" clauses?
  → If yes: Fix to except SpecificException!
```

**Only commit when ALL checks are ✓**

---

## 🎯 COMMIT MESSAGE VERIFICATION

Your commit message is proof of implementation:

```bash
# ✅ GOOD - Shows what was implemented and proof
$ git log
commit abc123def456
Module: conversation_protocol - Implement ConversationProtocol, Turn, 
ConversationState; 35/35 tests passing

# ❌ BAD - No proof of tests passing
$ git log
commit xyz789abc123
Phase E: Create stubs for conversation modules
→ No mention of tests passing!

# ❌ BAD - Tests aren't actually passing
$ git log
commit 111222333444
Module: conversation - "implement" class
→ 35 tests but actually 0 tests passing
```

**Every commit message must say "N tests passing" where N is the actual count.**

---

## 🚫 ABSOLUTE RULES (No Exceptions)

1. **Never commit code with test failures**
   - If pytest shows FAILED, don't commit
   - Keep implementing until all pass

2. **Never commit empty functions**
   - If function only has pass, don't commit
   - Implement first

3. **Never commit without type hints**
   - All parameters must have type hints
   - Return type must be specified
   - mypy --strict must pass

4. **Never commit without docstrings**
   - All public functions need Google docstring
   - All public classes need docstring

5. **Never commit without seeing test RED first**
   - Prove the test exists and fails
   - Prove your implementation fixes it

6. **Never commit if tests aren't run**
   - Always run: pytest tests/.../test_module.py -v
   - See actual test count in output

---

## 📋 FINAL VERIFICATION BEFORE EACH COMMIT

```bash
# 1. Run the module's tests
pytest tests/unit/.../test_module.py -v

# 2. Verify all pass (look for "N passed")
# Expected output:
#   test_method_1 PASSED
#   test_method_2 PASSED
#   ... (all pass)
#   50 passed in 0.45s

# 3. Check type hints
mypy cortex/.../module.py --strict

# 4. Check for stubs
grep "pass$" cortex/.../module.py  # Should be 0

# 5. Commit only if all above pass
git add cortex/.../module.py
git commit -m "Module: name - Implement Classes; N tests passing"
```

If any command fails, don't commit - keep implementing.

---

## 🎬 WHEN YOU START PHASE E

**First thing to do:**

1. Read this document completely
2. Read PHASE-E-IMPLEMENTATION-GUIDE.md
3. Read cortex-builder.prompt.md § CORE-008
4. **Commit this acknowledgment:**
   ```bash
   git commit --allow-empty -m "PHASE-E: Acknowledged stub prevention rules, ready for TDD implementation"
   ```

**Then:**
1. Start with Phase E1 setup
2. Follow the per-module workflow in the guide
3. **Never** create a stub just to move forward
4. **Always** test first, implement second

---

## ✅ SUCCESS DEFINITION

Phase E is successful when:

- ✓ 0 collection errors (pytest --co: "7547 tests collected, 0 errors")
- ✓ ≥98% test pass rate (≥7400/7547 tests passing)
- ✓ 0 type checking errors (mypy cortex/ --strict)
- ✓ 100% docstring coverage
- ✓ No bare except clauses
- ✓ All stubs replaced with working implementations
- ✓ All 125 modules tested and verified
- ✓ Production ready declaration signed

**NOT just "0 collection errors" - that's not enough.**
**Must have test EXECUTION, not just collection.**

---

## 🎯 Remember

Every empty stub you create is:
- 1 test that will fail
- 1 hour debugging why it fails
- 1 hour fixing after you realize it's a stub
- 1 more day to production

**Every proper implementation you create is:**
- N tests that pass immediately
- 0 time debugging
- 0 time fixing
- N less errors to fix later

**Speed comes from doing it right the first time.**

**Not from creating stubs that look right but don't work.**

---

**This is the only document you need to understand Phase E.**

**Read it before each module implementation.**

**Reference it when you're tempted to create a stub.**

**Succeed by following it exactly.**
