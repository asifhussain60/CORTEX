# Phase 5.3 Edge Case Tests - Planning Guide

**Status:** Ready to start  
**Estimated Time:** 4-6 hours  
**Target:** 15-20 edge case tests  
**Expected Test Count After:** ~1,560 tests

---

## 🎯 Quick Start

### Review Phase 5.1 Success
```bash
# Validate Phase 5.1 tests still passing
pytest tests/integration/test_phase_5_1*.py -v

# Expected: 18 passed in ~1s ✅

# Review completion summary
cat cortex-brain/PHASE-5.1-COMPLETE.md
```

### Success Patterns from Phase 5.1
- **Pattern reuse:** Saved 70% implementation time
- **TDD approach:** Design first, implement second
- **Real integration:** Use actual Tier 1/2/3 APIs
- **Zero failures:** Proper patterns = immediate success

---

## 📋 Edge Case Categories

### Category 1: Boundary Conditions (5 tests)

**Test 19: Empty Request**
- Input: "" (empty string)
- Expected: Graceful error handling
- Validates: Input validation

**Test 20: Very Long Request**
- Input: 10,000+ character request
- Expected: Truncation or processing
- Validates: Length limits

**Test 21: Special Characters**
- Input: "Add feature with 🚀💻🔥"
- Expected: Proper unicode handling
- Validates: Character encoding

**Test 22: Maximum Concurrent Sessions**
- Input: 100+ simultaneous sessions
- Expected: Graceful degradation
- Validates: Resource limits

**Test 23: Deeply Nested Context**
- Input: 50+ resumed requests in same session
- Expected: Context window management
- Validates: Memory limits

### Category 2: Race Conditions (3 tests)

**Test 24: Simultaneous Tier 1 Writes**
- Scenario: Multiple threads writing to same conversation
- Expected: No data corruption
- Validates: Thread safety

**Test 25: Session Resume Race**
- Scenario: Two requests trying to resume same session
- Expected: Proper locking/queuing
- Validates: Concurrency control

**Test 26: Brain Protection Race**
- Scenario: Multiple modification requests simultaneously
- Expected: Tier 0 protects brain integrity
- Validates: Protection layer thread safety

### Category 3: Resource Exhaustion (4 tests)

**Test 27: Memory Exhaustion**
- Scenario: Process very large conversation history
- Expected: Graceful degradation
- Validates: Memory management

**Test 28: Disk Space Exhaustion**
- Scenario: Fill temporary brain directory
- Expected: Error handling and cleanup
- Validates: Disk management

**Test 29: Database Connection Exhaustion**
- Scenario: Exhaust SQLite connections
- Expected: Connection pooling works
- Validates: Connection management

**Test 30: Timeout Exhaustion**
- Scenario: Agent takes >60 seconds
- Expected: Timeout and graceful recovery
- Validates: Timeout handling

### Category 4: Malformed Inputs (4 tests)

**Test 31: Invalid JSON Metadata**
- Input: Malformed metadata dictionary
- Expected: Validation and error
- Validates: Input validation

**Test 32: SQL Injection Attempt**
- Input: "'; DROP TABLE conversations; --"
- Expected: Proper escaping
- Validates: Security

**Test 33: Path Traversal Attempt**
- Input: Request with "../../../etc/passwd"
- Expected: Path sanitization
- Validates: Security

**Test 34: XSS Attempt**
- Input: Request with "<script>alert('xss')</script>"
- Expected: Proper escaping
- Validates: Security

### Category 5: Error Recovery (4 tests)

**Test 35: Tier 1 Database Corruption**
- Scenario: Corrupted SQLite database
- Expected: Recovery or fallback
- Validates: Error recovery

**Test 36: Tier 2 YAML Parse Error**
- Scenario: Malformed knowledge graph YAML
- Expected: Graceful fallback
- Validates: Parse error handling

**Test 37: Tier 3 Missing Metrics**
- Scenario: Development context unavailable
- Expected: Degrade gracefully
- Validates: Optional dependency handling

**Test 38: Agent Router Failure**
- Scenario: IntentRouter raises exception
- Expected: Error response to user
- Validates: Exception handling

---

## 🔧 Implementation Strategy

### Reuse Phase 5.1 Patterns

**Fixtures (identical):**
```python
@pytest.fixture
def temp_brain_path():
    """Create temporary brain directory for test isolation."""
    
@pytest.fixture
def mock_intent_router():
    """Mock IntentRouter to control agent responses."""
    
@pytest.fixture
def cortex_entry(temp_brain_path, mock_intent_router):
    """Initialize CortexEntry with isolated brain."""
```

**Test Structure:**
```python
def test_edge_case_name(cortex_entry, mock_intent_router):
    """
    Test X: Description
    
    Validates:
    - Edge case behavior
    - Error handling
    - Recovery mechanism
    """
    # ARRANGE: Setup edge case scenario
    
    # ACT: Trigger edge case
    
    # ASSERT: Validate proper handling
```

### Testing Approach

**Boundary Conditions:**
- Test at limits (0, max, max+1)
- Test with invalid types
- Test with missing required data

**Race Conditions:**
- Use ThreadPoolExecutor for concurrency
- Use locks/semaphores for coordination
- Validate data integrity after

**Resource Exhaustion:**
- Mock resource limits
- Trigger exhaustion
- Verify graceful degradation

**Malformed Inputs:**
- Test actual attack vectors
- Verify sanitization
- Check security logs

**Error Recovery:**
- Corrupt data intentionally
- Verify recovery mechanisms
- Check fallback behavior

---

## 📝 Test Template

```python
def test_empty_request_handling(cortex_entry, mock_intent_router):
    """
    Test 19: Empty request handling
    
    Validates:
    - Input validation
    - Graceful error response
    - No system crash
    """
    # ARRANGE: Setup mock for error response
    mock_error_response = AgentResponse(
        success=False,
        result={'error': 'Empty request'},
        message="Request cannot be empty",
        agent_name="RequestValidator"
    )
    
    mock_intent_router.execute.return_value = mock_error_response
    
    # ACT: Send empty request
    with pytest.raises(ValueError) as exc_info:
        response = cortex_entry.process("")
    
    # ASSERT: Proper error handling
    assert "empty" in str(exc_info.value).lower()
    
    # OR if it returns error response instead of raising:
    # assert response is not None
    # assert 'error' in response.lower() or 'empty' in response.lower()
```

---

## ⏱️ Time Estimates

**Based on Phase 5.1 efficiency (70% faster than planned):**

| Category | Tests | Original Estimate | Efficient Estimate |
|----------|-------|-------------------|-------------------|
| Boundary | 5 | 2h | 0.6h |
| Race Conditions | 3 | 1.5h | 0.5h |
| Resource Exhaustion | 4 | 2h | 0.6h |
| Malformed Inputs | 4 | 1.5h | 0.5h |
| Error Recovery | 4 | 2h | 0.6h |
| **Total** | **20** | **9h** | **2.8h** |

**Conservative estimate:** 4-6 hours (includes documentation)

---

## ✅ Success Criteria

- [ ] 15-20 edge case tests implemented
- [ ] 100% pass rate
- [ ] All edge cases handle gracefully (no crashes)
- [ ] Security tests validate sanitization
- [ ] Concurrency tests validate thread safety
- [ ] Documentation complete

---

## 🚀 Getting Started

```bash
# Create test file
touch tests/integration/test_phase_5_3_edge_cases.py

# Copy Phase 5.1 file as template
cp tests/integration/test_phase_5_1_medium_priority.py \
   tests/integration/test_phase_5_3_edge_cases.py

# Start editing
code tests/integration/test_phase_5_3_edge_cases.py
```

---

## 📚 Reference

- **Phase 5.1 Complete:** `cortex-brain/PHASE-5.1-COMPLETE.md`
- **HIGH Tests:** `tests/integration/test_phase_5_1_high_priority.py`
- **MEDIUM Tests:** `tests/integration/test_phase_5_1_medium_priority.py`
- **Brain Protection:** `cortex-brain/brain-protection-rules.yaml`

---

**Ready to start Phase 5.3!** Apply the same pattern-reuse strategy that worked so well for Phase 5.1.

**Expected outcome:** 2-4 hours implementation, 20 edge case tests, 100% pass rate

---

*Prepared: 2025-11-09*  
*Based on: Phase 5.1 success (70% efficiency gain)*  
*Next: Edge case testing for production readiness*
