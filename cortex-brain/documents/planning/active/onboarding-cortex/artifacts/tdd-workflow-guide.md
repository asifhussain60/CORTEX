# 🧪 TDD Workflow Guide

**Version:** 4.0.0  
**Created:** 2025-12-29  
**Author:** Asif Hussain

---

## 🎯 Overview

Test-Driven Development (TDD) is a mandatory workflow in CORTEX, enforced by the SKULL protection system. This guide teaches you the RED→GREEN→REFACTOR cycle and how to integrate it into your development process.

---

## 🔴 The Three Phases

### 1. RED Phase: Write Failing Test

**Philosophy:** "Write the test before the code"

**Objective:** Define expected behavior through a test that fails.

**Steps:**
1. Identify the feature to implement
2. Write a test that describes desired behavior
3. Run the test and verify it fails
4. Commit test-first (SKULL requirement)

**Example:**

```python
# tests/test_calculator.py

def test_calculator_add_two_numbers():
    """Test calculator can add two integers."""
    calc = Calculator()
    result = calc.add(2, 3)
    assert result == 5
```

**Run:**
```bash
pytest tests/test_calculator.py::test_calculator_add_two_numbers
```

**Expected Output:**
```
FAILED tests/test_calculator.py::test_calculator_add_two_numbers
ImportError: cannot import name 'Calculator'
```

✅ **RED Phase Complete** - Test fails as expected

---

### 2. GREEN Phase: Minimal Implementation

**Philosophy:** "Make it work, not perfect"

**Objective:** Write the simplest code that makes the test pass.

**Steps:**
1. Create minimal implementation
2. Run test and verify it passes
3. Do NOT add extra features
4. Do NOT optimize yet

**Example:**

```python
# src/calculator.py

class Calculator:
    def add(self, a, b):
        return a + b
```

**Run:**
```bash
pytest tests/test_calculator.py::test_calculator_add_two_numbers
```

**Expected Output:**
```
PASSED tests/test_calculator.py::test_calculator_add_two_numbers
```

✅ **GREEN Phase Complete** - Test passes

---

### 3. REFACTOR Phase: Improve Code

**Philosophy:** "Make it right, make it clean"

**Objective:** Improve code quality while keeping tests passing.

**Steps:**
1. Add type hints
2. Add documentation
3. Improve variable names
4. Extract common patterns
5. Run tests after each change

**Example:**

```python
# src/calculator.py

from typing import Union


class Calculator:
    """
    Simple calculator for basic arithmetic operations.
    
    Supports addition, subtraction, multiplication, and division
    of integers and floats.
    """
    
    def add(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Add two numbers.
        
        Args:
            a: First number
            b: Second number
        
        Returns:
            Sum of a and b
        
        Examples:
            >>> calc = Calculator()
            >>> calc.add(2, 3)
            5
            >>> calc.add(2.5, 3.5)
            6.0
        """
        return a + b
```

**Run:**
```bash
pytest tests/test_calculator.py::test_calculator_add_two_numbers
```

**Expected Output:**
```
PASSED tests/test_calculator.py::test_calculator_add_two_numbers
```

✅ **REFACTOR Phase Complete** - Tests still pass, code improved

---

## 🔄 Complete TDD Cycle

```
┌──────────────────────────────────────────────────────────┐
│                   TDD WORKFLOW CYCLE                     │
└──────────────────────────────────────────────────────────┘

    1. RED Phase
    ├─> Write failing test
    ├─> Run test (verify failure)
    └─> Commit test
         │
         ▼
    2. GREEN Phase
    ├─> Write minimal code
    ├─> Run test (verify pass)
    └─> Commit implementation
         │
         ▼
    3. REFACTOR Phase
    ├─> Improve code quality
    ├─> Run tests (verify still pass)
    ├─> Add documentation
    └─> Create git checkpoint
         │
         ▼
    ✅ Complete
    └─> Feature implemented with tests
```

---

## 🛡️ SKULL Enforcement

CORTEX enforces TDD through the SKULL protection system:

### Rule: TDD_ENFORCEMENT

**What it does:**
- Prevents code commits without tests
- Ensures RED phase completes before GREEN
- Validates test failure before allowing implementation
- Creates automatic git checkpoints

**How it works:**

```python
# In CORTEX orchestrators

def validate_tdd_phase(self, phase: str) -> bool:
    """Validate TDD phase completion."""
    if phase == "GREEN":
        # Cannot proceed to GREEN without failing test
        if not self.has_failing_test():
            raise TDDViolation("RED phase incomplete: No failing test found")
    
    if phase == "REFACTOR":
        # Cannot refactor without passing test
        if not self.has_passing_test():
            raise TDDViolation("GREEN phase incomplete: Test not passing")
    
    return True
```

**Benefits:**
- Prevents untested code
- Ensures test coverage
- Maintains code quality
- Enables confident refactoring

---

## 📝 CORTEX TDD Commands

### Starting TDD Workflow

```
start tdd
```

**What happens:**
1. CORTEX enters RED phase
2. Prompts for feature description
3. Suggests test file location
4. Monitors for test creation

### Progressing Through Phases

```
continue tdd
```

**What happens:**
1. CORTEX validates current phase
2. Runs tests to verify phase completion
3. Advances to next phase
4. Provides guidance for next steps

### Completing TDD Workflow

```
complete tdd
```

**What happens:**
1. CORTEX runs full test suite
2. Validates all phases completed
3. Creates git checkpoint
4. Records to knowledge graph
5. Updates progress tracker

---

## 🎓 Learning Path

### Beginner: Calculator Example

**Time:** 20 minutes

Build a simple calculator with TDD:

1. **Addition** (start with this)
   - RED: Test add(2, 3) == 5
   - GREEN: return a + b
   - REFACTOR: Add type hints, docs

2. **Subtraction**
   - RED: Test subtract(5, 3) == 2
   - GREEN: return a - b
   - REFACTOR: Extract validation logic

3. **Multiplication**
   - RED: Test multiply(2, 3) == 6
   - GREEN: return a * b
   - REFACTOR: Add overflow handling

4. **Division**
   - RED: Test divide(6, 3) == 2
   - GREEN: return a / b
   - REFACTOR: Handle division by zero

### Intermediate: User Authentication

**Time:** 45 minutes

Build user authentication with TDD:

1. **User Model**
   - RED: Test User.create(username, password)
   - GREEN: Implement User class
   - REFACTOR: Add password hashing

2. **Authentication Service**
   - RED: Test AuthService.authenticate(username, password)
   - GREEN: Implement authentication logic
   - REFACTOR: Add token generation

3. **Session Management**
   - RED: Test Session.create(user)
   - GREEN: Implement session storage
   - REFACTOR: Add expiration logic

### Advanced: Payment Processing

**Time:** 90 minutes

Build payment system with TDD:

1. **Payment Gateway Integration**
   - RED: Test multiple payment methods
   - GREEN: Implement gateway abstraction
   - REFACTOR: Add retry logic

2. **Transaction Recording**
   - RED: Test transaction persistence
   - GREEN: Implement database layer
   - REFACTOR: Add audit logging

3. **Refund Processing**
   - RED: Test refund workflows
   - GREEN: Implement refund logic
   - REFACTOR: Add notification system

---

## 🔧 Best Practices

### 1. Write One Test at a Time

❌ **Bad:**
```python
def test_all_calculator_operations():
    calc = Calculator()
    assert calc.add(2, 3) == 5
    assert calc.subtract(5, 3) == 2
    assert calc.multiply(2, 3) == 6
    assert calc.divide(6, 3) == 2
```

✅ **Good:**
```python
def test_calculator_add():
    calc = Calculator()
    assert calc.add(2, 3) == 5

def test_calculator_subtract():
    calc = Calculator()
    assert calc.subtract(5, 3) == 2
```

### 2. Test Behavior, Not Implementation

❌ **Bad:**
```python
def test_user_password_hash_uses_bcrypt():
    user = User("test", "password123")
    assert user._hash_algorithm == "bcrypt"  # Testing internal detail
```

✅ **Good:**
```python
def test_user_can_authenticate_with_correct_password():
    user = User("test", "password123")
    assert user.authenticate("password123") == True  # Testing behavior
```

### 3. Keep Tests Independent

❌ **Bad:**
```python
# test_user_workflow.py
class TestUserWorkflow:
    def test_step1_create_user(self):
        self.user = User("test", "password")
    
    def test_step2_login_user(self):
        # Depends on step 1!
        assert self.user.login("password")
```

✅ **Good:**
```python
# test_user.py
class TestUser:
    def test_create_user(self):
        user = User("test", "password")
        assert user.username == "test"
    
    def test_login_user(self):
        user = User("test", "password")
        assert user.login("password") == True
```

### 4. Use Descriptive Test Names

❌ **Bad:**
```python
def test_1():
    ...

def test_user():
    ...
```

✅ **Good:**
```python
def test_user_can_be_created_with_valid_username():
    ...

def test_user_authentication_fails_with_wrong_password():
    ...
```

### 5. Follow AAA Pattern

**Arrange → Act → Assert**

```python
def test_calculator_add():
    # Arrange
    calc = Calculator()
    a = 2
    b = 3
    expected = 5
    
    # Act
    result = calc.add(a, b)
    
    # Assert
    assert result == expected
```

---

## 🚨 Common Pitfalls

### 1. Skipping RED Phase

**Problem:** Writing code before test

**Solution:** SKULL prevents this - always RED first

### 2. Over-Engineering in GREEN Phase

**Problem:** Adding features not covered by test

**Solution:** Write only code needed to pass test

### 3. Refactoring Without Tests Passing

**Problem:** Breaking tests during refactor

**Solution:** Run tests after each refactor step

### 4. Testing Implementation Details

**Problem:** Tests break on internal changes

**Solution:** Test public API and behavior

### 5. Not Running Tests Frequently

**Problem:** Don't catch issues early

**Solution:** Run tests after every change

---

## 📊 TDD Metrics

CORTEX tracks TDD metrics in the knowledge graph:

- **Test Coverage:** % of code covered by tests
- **Cycle Time:** Average time per RED→GREEN→REFACTOR cycle
- **Refactor Frequency:** How often code is improved
- **Test Failures:** Track when tests fail unexpectedly

View metrics:
```
system maintenance
```

---

## 🎯 Success Criteria

You've mastered TDD when you can:

- ✅ Write failing test before any implementation
- ✅ Write minimal code to pass test
- ✅ Refactor confidently with passing tests
- ✅ Maintain >80% test coverage
- ✅ Complete RED→GREEN→REFACTOR in <10 minutes
- ✅ Use TDD for all new features

---

## 📚 Additional Resources

### CORTEX Documentation
- **SKULL Rules:** `cortex-brain/brain-protection-rules.yaml`
- **TDD Manifest:** `cortex-brain/manifests/orchestrators/tdd-orchestrator-v4-manifest.yaml`
- **Test Examples:** `tests/` directory

### External Resources
- **Book:** "Test Driven Development" by Kent Beck
- **Course:** [TDD Course on Test Automation University](https://testautomationu.applitools.com/tdd-tutorial/)
- **Blog:** [Martin Fowler on TDD](https://martinfowler.com/bliki/TestDrivenDevelopment.html)

---

## 🤝 Getting Help

**In CORTEX:**
```
start tdd
```

**Common Issues:**
```
help tdd troubleshooting
```

**Community:**
- GitHub: github.com/asifhussain60/CORTEX
- Docs: https://asifhussain60.github.io/CORTEX/

---

**Guide Version:** 1.0.0  
**Last Updated:** 2025-12-29  
**Maintainer:** Asif Hussain
