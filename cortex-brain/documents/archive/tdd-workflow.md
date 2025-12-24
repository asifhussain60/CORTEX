# 🔴🟢♻️ TDD Workflow: RED-GREEN-REFACTOR

**Estimated Time:** 25 minutes  
**Difficulty:** Intermediate  
**Prerequisites:** Basic testing knowledge, [SOLID Principles](./solid-principles.md)  
**Last Reviewed:** December 6, 2025

---

## 🎯 What You'll Learn

- The RED-GREEN-REFACTOR cycle
- Why test-first development works
- How CORTEX enforces TDD with Brain Protector
- Common TDD mistakes and how to avoid them
- Advanced refactoring techniques

---

## 📚 What is TDD?

**Test-Driven Development (TDD):** Write tests BEFORE writing implementation code.

**The Cycle:**
```
RED → GREEN → REFACTOR → RED → GREEN → REFACTOR → ...
```

### Why TDD?

**Data from CORTEX Brain Protector:**
- Test-first: **94% success rate** (fewer bugs, better design)
- Implementation-first: **67% success rate** (more bugs, tight coupling)

**Benefits:**
1. **Better Design:** Tests force you to think about interfaces first
2. **Higher Confidence:** If tests pass, code works
3. **Regression Prevention:** Tests catch future breaks
4. **Documentation:** Tests show how code should be used
5. **Refactor Safely:** Tests verify behavior doesn't change

---

## 🔄 The Three Phases

### 🔴 RED: Write a Failing Test

**Goal:** Write a test that fails because feature doesn't exist yet.

**Rules:**
1. Test MUST fail initially (if it passes, you're testing nothing!)
2. Write simplest test that describes next small behavior
3. Test only ONE thing
4. Commit AFTER verifying test fails

**Example:**

```python
# Step 1: Write failing test
def test_profile_agent_updates_experience_level():
    """Test that ProfileAgent can update user's experience level"""
    
    # Arrange
    agent = ProfileAgent(db_path=":memory:")
    request = AgentRequest(
        user_message="set my experience level to junior",
        intent=IntentType.UPDATE_PROFILE
    )
    
    # Act
    response = agent.execute(request)
    
    # Assert
    assert response.success is True
    assert "junior" in response.message.lower()
    assert response.result["experience_level"] == "junior"

# Run test - should FAIL (feature doesn't exist yet)
# Output: AttributeError: 'ProfileAgent' object has no attribute 'execute'
```

**Verify Failure:**
```bash
pytest tests/test_profile_agent.py::test_profile_agent_updates_experience_level

# Expected: FAILED (1 failed, 0 passed)
```

**Commit RED Phase:**
```bash
git add tests/test_profile_agent.py
git commit -m "RED: Add test for profile experience level update"
```

---

### 🟢 GREEN: Make Test Pass (Minimum Code)

**Goal:** Write JUST enough code to make test pass. No more, no less.

**Rules:**
1. Write simplest implementation (even if ugly/hardcoded)
2. Make test pass FAST
3. Don't add features not required by tests
4. Commit AFTER test passes

**Example:**

```python
# Step 2: Minimal implementation
class ProfileAgent(BaseAgent):
    def __init__(self, db_path=None):
        super().__init__("ProfileAgent")
        self.db_path = db_path
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """Minimal implementation - just make test pass"""
        
        # Hardcoded to make test pass (we'll refactor later)
        if "junior" in request.user_message.lower():
            return AgentResponse(
                success=True,
                result={"experience_level": "junior"},
                message="Experience level set to junior",
                agent_name=self.name
            )
        
        # Default fallback
        return AgentResponse(
            success=False,
            result={},
            message="Could not parse request",
            agent_name=self.name
        )

# Run test - should PASS now
```

**Verify Pass:**
```bash
pytest tests/test_profile_agent.py::test_profile_agent_updates_experience_level

# Expected: PASSED (1 passed, 0 failed)
```

**Commit GREEN Phase:**
```bash
git add src/cortex_agents/profile_agent.py
git commit -m "GREEN: Implement basic profile experience level update"
```

---

### ♻️ REFACTOR: Improve Code While Keeping Tests Green

**Goal:** Clean up code without changing behavior. Tests MUST stay green.

**Rules:**
1. Tests must pass before refactoring
2. Tests must pass after refactoring
3. Remove duplication
4. Apply SOLID principles
5. Improve naming
6. Commit AFTER successful refactoring

**Example:**

```python
# Step 3: Refactor to proper implementation
class ProfileAgent(BaseAgent):
    def __init__(self, db_path=None):
        super().__init__("ProfileAgent")
        self.profile_manager = UserProfileManager(db_path)
        self.experience_levels = ["junior", "mid", "senior", "expert"]
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """Refactored implementation - clean, extensible"""
        
        # Extract experience level from message
        updates = self._parse_update_request(request.user_message)
        
        if not updates:
            return AgentResponse(
                success=False,
                result={},
                message="Could not parse request",
                agent_name=self.name
            )
        
        # Delegate to profile manager (Single Responsibility)
        success = self.profile_manager.update_profile(updates)
        
        if success:
            return AgentResponse(
                success=True,
                result=updates,
                message=f"Experience level set to {updates['experience_level']}",
                agent_name=self.name
            )
        
        return AgentResponse(
            success=False,
            result={},
            message="Update failed",
            agent_name=self.name
        )
    
    def _parse_update_request(self, message: str) -> Dict[str, Any]:
        """Extract update fields from natural language"""
        updates = {}
        message_lower = message.lower()
        
        # Extract experience level
        for level in self.experience_levels:
            if level in message_lower:
                updates["experience_level"] = level
                break
        
        return updates

# Run test - should STILL PASS
```

**Verify Tests Still Pass:**
```bash
pytest tests/test_profile_agent.py

# Expected: PASSED (all tests pass)
```

**Commit REFACTOR Phase:**
```bash
git add src/cortex_agents/profile_agent.py
git commit -m "REFACTOR: Extract parsing logic, delegate to UserProfileManager"
```

---

## 🧠 CORTEX Brain Protector Enforcement

CORTEX enforces TDD through **Brain Protector** (Tier 0 instinct: `TDD_ENFORCEMENT`).

### How It Works

**1. RED Phase Validation**
```python
# Brain Protector checks:
# - Was test committed BEFORE implementation?
# - Did test fail initially?
# - Is there evidence of failure in commit history?

# If violated, Brain Protector challenges:
"""
⚠️ Brain Protector Challenge: RED Phase Violation

Evidence suggests test was not written first or never failed.

Historical Data:
- Test-first development: 94% success rate
- Implementation-first: 67% success rate
- Test-first produces 40% fewer bugs

Recommendation: Delete implementation, verify test fails, then proceed.
"""
```

**2. GREEN Phase Validation**
```python
# Brain Protector checks:
# - Does implementation make test pass?
# - Is implementation minimal (not over-engineered)?
# - Was implementation committed separately from test?

# If violated:
"""
⚠️ Brain Protector Challenge: GREEN Phase Violation

Test and implementation committed together. This violates TDD workflow.

Correct sequence:
1. Commit failing test (RED)
2. Commit minimal implementation (GREEN)
3. Commit refactored code (REFACTOR)
"""
```

**3. REFACTOR Phase Validation**
```python
# Brain Protector checks:
# - Do all tests still pass?
# - Was behavior preserved?
# - Were SOLID principles applied?

# If violated:
"""
⚠️ Brain Protector Challenge: REFACTOR Phase Violation

Tests failing after refactoring. Behavior changed unexpectedly.

Action Required: Revert refactoring or fix tests.
"""
```

---

## 🎯 TDD Best Practices

### 1. Keep Tests Small and Focused

```python
# ❌ BAD - Tests multiple things
def test_profile_agent():
    agent = ProfileAgent()
    
    # Tests experience level update
    response1 = agent.execute(request1)
    assert response1.success
    
    # Tests tech stack update
    response2 = agent.execute(request2)
    assert response2.success
    
    # Tests interaction mode update
    response3 = agent.execute(request3)
    assert response3.success

# ✅ GOOD - One test per behavior
def test_profile_agent_updates_experience_level():
    """Test ONLY experience level update"""
    agent = ProfileAgent()
    response = agent.execute(request)
    assert response.success
    assert response.result["experience_level"] == "junior"

def test_profile_agent_updates_tech_stack():
    """Test ONLY tech stack update"""
    agent = ProfileAgent()
    response = agent.execute(request)
    assert response.success
    assert response.result["tech_stack"] == "Azure"

def test_profile_agent_updates_interaction_mode():
    """Test ONLY interaction mode update"""
    agent = ProfileAgent()
    response = agent.execute(request)
    assert response.success
    assert response.result["interaction_mode"] == "guided"
```

### 2. Use Arrange-Act-Assert Pattern

```python
def test_profile_agent_updates_experience_level():
    # ARRANGE - Set up test data
    agent = ProfileAgent(db_path=":memory:")
    request = AgentRequest(
        user_message="set experience to junior",
        intent=IntentType.UPDATE_PROFILE
    )
    
    # ACT - Execute behavior under test
    response = agent.execute(request)
    
    # ASSERT - Verify expected outcome
    assert response.success is True
    assert response.result["experience_level"] == "junior"
```

### 3. Test Behavior, Not Implementation

```python
# ❌ BAD - Tests internal implementation
def test_profile_agent_calls_parse_method():
    agent = ProfileAgent()
    agent._parse_update_request = Mock()  # Mocking internal method
    
    agent.execute(request)
    
    agent._parse_update_request.assert_called_once()  # Testing HOW it works

# ✅ GOOD - Tests external behavior
def test_profile_agent_updates_experience_level():
    agent = ProfileAgent()
    request = AgentRequest(user_message="set experience to junior")
    
    response = agent.execute(request)
    
    assert response.result["experience_level"] == "junior"  # Testing WHAT it does
```

### 4. Make Tests Independent

```python
# ❌ BAD - Tests depend on each other
class TestProfileAgent:
    agent = ProfileAgent()  # Shared state!
    
    def test_update_experience_level(self):
        self.agent.execute(request1)  # Modifies shared agent
    
    def test_update_tech_stack(self):
        # Depends on previous test's state!
        self.agent.execute(request2)

# ✅ GOOD - Tests are independent
class TestProfileAgent:
    def test_update_experience_level(self):
        agent = ProfileAgent()  # Fresh instance
        agent.execute(request1)
    
    def test_update_tech_stack(self):
        agent = ProfileAgent()  # Fresh instance
        agent.execute(request2)
```

---

## 🚨 Common TDD Mistakes

### Mistake 1: Writing Tests After Implementation

**Problem:** Tests become validation of existing code, not specification of desired behavior.

**Fix:** Delete implementation, write test first, watch it fail, then implement.

### Mistake 2: Skipping RED Phase

**Problem:** Can't verify test actually tests anything if you never see it fail.

**Fix:** ALWAYS verify test fails before writing implementation.

### Mistake 3: Over-Engineering in GREEN Phase

**Problem:** Adding features not required by tests.

**Fix:** Write simplest code to pass test. Add features in next RED-GREEN-REFACTOR cycle.

### Mistake 4: Refactoring Without Green Tests

**Problem:** Can't verify behavior preserved if tests aren't passing.

**Fix:** Only refactor when ALL tests are green.

### Mistake 5: Not Committing Each Phase

**Problem:** Can't track TDD workflow, harder to revert mistakes.

**Fix:** Commit after RED, GREEN, and REFACTOR phases separately.

---

## 🎥 Video Resources

- [TDD Explained (12 min)](https://www.youtube.com/watch?v=Jv2uxzhPFl4) - Fun Fun Function - Practical intro
- [TDD in Python (11 min)](https://www.youtube.com/watch?v=ULxMQ57engo) - Real Python - Python-specific
- [Test-Driven Development (28 min)](https://www.youtube.com/watch?v=58jGpV2Cg50) - Continuous Delivery - Deep dive

---

## 📖 Further Reading

- [Test-Driven Development by Example](https://www.oreilly.com/library/view/test-driven-development/0321146530/) - Kent Beck (Book)
- [Growing Object-Oriented Software, Guided by Tests](http://www.growing-object-oriented-software.com/) - Classic TDD book
- [pytest Documentation](https://docs.pytest.org/) - Python testing framework

---

## ✅ TDD Checklist

For every feature:

- [ ] Write failing test (RED) ✅ Verify it fails ✅ Commit
- [ ] Write minimal implementation (GREEN) ✅ Verify test passes ✅ Commit
- [ ] Refactor code (REFACTOR) ✅ Verify tests still pass ✅ Commit
- [ ] Tests are small and focused (one behavior per test)
- [ ] Tests use Arrange-Act-Assert pattern
- [ ] Tests are independent (no shared state)
- [ ] Tests verify behavior, not implementation

---

## 🚀 Next Steps

1. **Practice:** Use CORTEX TDD workflow - `start tdd`
2. **Deep Dive:** Learn [Testing Strategies](./testing-strategies.md) for advanced techniques
3. **Refactor:** Learn advanced refactoring in next section

---

**Questions?** Ask CORTEX: `"start tdd"` to begin guided TDD workflow with automatic enforcement.
