# 🧪 Testing Strategies in CORTEX

**Estimated Time:** 30 minutes  
**Difficulty:** Intermediate  
**Prerequisites:** [TDD Workflow](./tdd-workflow.md), Basic testing knowledge  
**Last Reviewed:** December 6, 2025

---

## 🚧 Work in Progress

This learning path is currently under development and will be available soon.

**Planned Topics:**
- Unit testing vs Integration testing vs E2E testing
- Test isolation and independence
- Mocking and stubbing
- Test fixtures and factories
- Testing async code
- Test coverage and quality metrics
- Testing strategies in CORTEX

---

## 🎯 What You'll Learn (Coming Soon)

- Different types of tests and when to use each
- How to write effective test cases
- Mocking external dependencies
- Test organization and structure
- CORTEX's testing architecture
- Code coverage best practices
- Common testing anti-patterns

---

## 📚 Temporary Resources

While this guide is being developed, here are excellent external resources:

### Video Resources
- [Python Testing (20 min)](https://www.youtube.com/watch?v=6tNS--WetLI) - Corey Schafer - pytest basics
- [Test-Driven Development (12 min)](https://www.youtube.com/watch?v=Jv2uxzhPFl4) - Fun Fun Function
- [Testing Best Practices (45 min)](https://www.youtube.com/watch?v=DhUpxWjOhME) - ArjanCodes - Comprehensive

### Documentation
- [pytest Documentation](https://docs.pytest.org/) - Official pytest docs
- [unittest Mock](https://docs.python.org/3/library/unittest.mock.html) - Python mocking
- [Testing Best Practices](https://testdriven.io/blog/testing-best-practices/) - Comprehensive guide

### Books (Free Resources)
- [Python Testing with pytest](https://pragprog.com/titles/bopytest/python-testing-with-pytest/) - Sample chapters
- [Test-Driven Development with Python](https://www.obeythetestinggoat.com/) - Free online book

---

## 🔍 CORTEX Testing Architecture (Preview)

### Test Organization

```
tests/                           # CORTEX internal tests only
├── test_tier1_working_memory.py
├── test_tier2_knowledge_graph.py
├── test_tier3_context.py
├── test_agents/
│   ├── test_profile_agent.py
│   ├── test_planning_agent.py
│   └── test_tdd_agent.py
└── test_orchestrators/

user_repo/tests/                 # Application tests (isolated)
├── test_features.py
├── test_integration.py
└── test_e2e.py
```

### Testing Principles in CORTEX

1. **Test Isolation:**
   - CORTEX tests in `tests/` directory
   - Application tests in user repo
   - No cross-contamination (enforced by pytest.ini)

2. **Test-First Development:**
   - Brain Protector enforces RED-GREEN-REFACTOR
   - Tests must fail before implementation
   - 94% success rate with test-first approach

3. **Mock External Dependencies:**
   - Database connections → :memory: SQLite
   - File system → temp directories
   - Network → mock responses

### Current Test Examples

**Unit Test Example:**
```python
# tests/test_agents/test_profile_agent.py
def test_profile_agent_updates_experience_level():
    """Test ProfileAgent updates experience level correctly"""
    # Arrange
    agent = ProfileAgent(db_path=":memory:")
    request = AgentRequest(
        user_message="set experience to junior",
        intent=IntentType.UPDATE_PROFILE
    )
    
    # Act
    response = agent.execute(request)
    
    # Assert
    assert response.success is True
    assert response.result["experience_level"] == "junior"
```

**Integration Test Example:**
```python
# tests/test_orchestrators/test_setup_orchestrator.py
def test_setup_orchestrator_executes_modules_in_order():
    """Test SetupOrchestrator runs modules in correct phase order"""
    orchestrator = SetupOrchestrator()
    orchestrator.register_modules([
        BrainInitModule(),
        VisionAPIModule(),
        OnboardingModule()
    ])
    
    context = {'project_root': temp_dir}
    report = orchestrator.execute_setup(context)
    
    assert report.overall_success is True
    assert len(report.results) == 3
```

---

## 🧪 Test Types in CORTEX

### Unit Tests
**Purpose:** Test individual components in isolation  
**Example:** ProfileAgent.execute() method  
**Speed:** Fast (<1ms per test)  
**Coverage:** Highest (80%+ of tests)

### Integration Tests
**Purpose:** Test multiple components working together  
**Example:** SetupOrchestrator + modules  
**Speed:** Medium (10-100ms per test)  
**Coverage:** Medium (15-20% of tests)

### End-to-End Tests
**Purpose:** Test complete workflows  
**Example:** Full onboarding process  
**Speed:** Slow (>100ms per test)  
**Coverage:** Lowest (<5% of tests)

---

## 📊 Expected Completion

**Target Date:** Q1 2025  
**Estimated Content:** 600-700 lines  
**Structure:** Comprehensive guide with CORTEX-specific examples

**Will Include:**
- Testing pyramid explanation
- Mocking patterns with examples
- Test fixtures and factories
- Code coverage interpretation
- Performance testing
- Testing async code
- CORTEX test suite walkthrough

---

## 🚀 In the Meantime

1. **Review TDD Workflow:**
   - [TDD Workflow](./tdd-workflow.md) - Foundation for testing

2. **Explore CORTEX Tests:**
   - `tests/test_agents/` - Agent test examples
   - `tests/test_tier1_working_memory.py` - Database testing
   - `pytest.ini` - Test configuration

3. **Run CORTEX Tests:**
   ```bash
   # Run all tests
   pytest tests/
   
   # Run with coverage
   pytest --cov=src tests/
   
   # Run specific test file
   pytest tests/test_agents/test_profile_agent.py
   ```

4. **Learn from pytest Docs:**
   - Start with [pytest documentation](https://docs.pytest.org/)
   - Watch Corey Schafer's pytest video

5. **Ask CORTEX:**
   - "explain testing in CORTEX"
   - "show me test examples"
   - "run tests"

---

## 📖 Quick Testing Checklist (Preview)

While the full guide is being developed, here's a quick checklist:

- [ ] Tests are independent (no shared state)
- [ ] Tests use Arrange-Act-Assert pattern
- [ ] External dependencies are mocked
- [ ] Test names describe what they test
- [ ] One assertion per test (when possible)
- [ ] Tests run fast (<100ms for unit tests)
- [ ] Coverage >80% for critical code
- [ ] Tests document behavior

---

## 📢 Stay Updated

This document will be updated as the learning path is developed. Check back soon!

**Questions?** Ask CORTEX: `"when will testing-strategies be available?"` or provide feedback via `cortex feedback`.

---

**Status:** 🚧 Under Development  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
