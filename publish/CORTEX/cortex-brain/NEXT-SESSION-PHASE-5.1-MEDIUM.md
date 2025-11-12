# Phase 5.1 MEDIUM Priority Tests - Next Session Guide

**Target:** Implement 10 MEDIUM priority integration tests  
**Estimated Time:** 6-7 hours  
**Goal:** Complete Phase 5.1 to 100% (1,544 tests total)

---

## 🎯 Quick Start (5 minutes)

### 1. Review Previous Work
```bash
# Check current test status
pytest tests/integration/test_phase_5_1_high_priority.py -v

# Expected: 8/8 passing ✅

# Check total test count
pytest tests/ --collect-only -q | tail -1
# Expected: ~1,534 tests
```

### 2. Read Completion Summary
```bash
cat cortex-brain/PHASE-5.1-HIGH-PRIORITY-COMPLETE.md
```

### 3. Review Test Design
```bash
# Original design document with all 18 tests
cat tests/integration/PHASE-5.1-TEST-DESIGN.md
```

---

## 📋 MEDIUM Priority Tests to Implement

### Category A: Advanced Workflows (3 tests)

**Test 9: test_refactor_code_quality_workflow** 🔵 MEDIUM
- **User Request:** "Refactor authentication module"
- **Validates:** Architect → CodeExecutor coordination
- **Estimated Time:** 45 minutes

**Test 10: test_document_feature_workflow** 🔵 MEDIUM
- **User Request:** "Document the authentication API"
- **Validates:** Documenter agent workflow
- **Estimated Time:** 35 minutes

**Test 11: test_deploy_feature_workflow** 🔵 MEDIUM
- **User Request:** "Deploy authentication to staging"
- **Validates:** End-to-end deployment workflow
- **Estimated Time:** 40 minutes

### Category B: Parallel Execution (2 tests)

**Test 12: test_parallel_request_isolation** 🔵 MEDIUM
- **Scenario:** Multiple requests in quick succession
- **Validates:** Request isolation, no cross-contamination
- **Estimated Time:** 45 minutes

**Test 13: test_concurrent_sessions** 🔵 MEDIUM
- **Scenario:** Multiple agents active simultaneously
- **Validates:** Session independence
- **Estimated Time:** 50 minutes

### Category C: Session Edge Cases (2 tests)

**Test 14: test_session_timeout_with_resume** 🔵 MEDIUM
- **Scenario:** Resume after timeout (>30 min)
- **Validates:** New session created, context preserved
- **Estimated Time:** 40 minutes

**Test 15: test_session_state_persistence** 🔵 MEDIUM
- **Scenario:** Complex state across multiple requests
- **Validates:** State preserved in Tier 1
- **Estimated Time:** 35 minutes

### Category D: Complex Intent Routing (3 tests)

**Test 16: test_ambiguous_intent_resolution** 🔵 MEDIUM
- **User Request:** "Make it better" (vague)
- **Validates:** Context-based intent clarification
- **Estimated Time:** 40 minutes

**Test 17: test_conflicting_intents** 🔵 MEDIUM
- **User Request:** "Add feature but don't modify code"
- **Validates:** Conflict detection and resolution
- **Estimated Time:** 45 minutes

**Test 18: test_chained_dependent_intents** 🔵 MEDIUM
- **User Request:** "Plan, execute, test, and deploy"
- **Validates:** Sequential intent execution
- **Estimated Time:** 50 minutes

---

## 🔧 Implementation Strategy

### Hour-by-Hour Plan

**Hour 1: Advanced Workflows (Tests 9-10)**
- Implement test_refactor_code_quality_workflow
- Implement test_document_feature_workflow
- Run validation after each

**Hour 2: Advanced Workflows + Parallel Start (Test 11-12)**
- Implement test_deploy_feature_workflow
- Start test_parallel_request_isolation
- Mid-session validation

**Hour 3: Parallel Execution (Test 12-13)**
- Complete test_parallel_request_isolation
- Implement test_concurrent_sessions
- Validate parallelism works

**Hour 4: Session Edge Cases (Tests 14-15)**
- Implement test_session_timeout_with_resume
- Implement test_session_state_persistence
- Validate session management

**Hour 5-6: Complex Intent Routing (Tests 16-18)**
- Implement test_ambiguous_intent_resolution
- Implement test_conflicting_intents
- Implement test_chained_dependent_intents
- Full validation

**Hour 7: Final Validation**
- Run full test suite
- Fix any failures
- Update documentation
- Create completion summary

---

## 📝 Code Template

Based on successful HIGH priority implementation:

```python
def test_new_medium_priority_test(cortex_entry, mock_intent_router):
    """
    Test X (MEDIUM): Description
    
    Validates:
    - Point 1
    - Point 2
    - Point 3
    
    Expected Duration: X minutes
    """
    # ARRANGE: Setup mock response
    mock_response = AgentResponse(
        success=True,
        result={'key': 'value'},
        message="Action completed",
        agent_name="AgentName"
    )
    
    mock_intent_router.execute.return_value = mock_response
    
    # ACT: Process request
    response = cortex_entry.process("User request", resume_session=False)
    
    # ASSERT: Validate response
    assert response is not None
    assert 'keyword' in response.lower()
    
    # ASSERT: Validate Tier 1 logging
    stats = cortex_entry.tier1.get_tier1_statistics()
    assert stats['conversations']['total_messages'] >= 2
```

---

## 🎨 Patterns from HIGH Priority Tests

### 1. Session Management
```python
# First request
response_1 = cortex_entry.process("Request 1", resume_session=False)

# Get stats before continuation
stats_before = cortex_entry.tier1.get_tier1_statistics()
messages_before = stats_before['conversations']['total_messages']

# Continue in same session
response_2 = cortex_entry.process("Request 2", resume_session=True)

# Validate accumulation
stats_after = cortex_entry.tier1.get_tier1_statistics()
assert stats_after['conversations']['total_messages'] >= messages_before + 2
```

### 2. Multi-Phase Workflows
```python
# Phase 1: Planning
mock_intent_router.execute.return_value = plan_response
plan_result = cortex_entry.process("Plan feature")
assert 'plan' in plan_result.lower()

# Phase 2: Execution
mock_intent_router.execute.return_value = execute_response
execute_result = cortex_entry.process("Execute plan", resume_session=True)
assert 'execut' in execute_result.lower()
```

### 3. Stats Validation
```python
# Get tier statistics
stats = cortex_entry.tier1.get_tier1_statistics()

# Validate conversations
convs = stats['conversations']['total_conversations']
assert convs >= 1

# Validate messages
msgs = stats['conversations']['total_messages']
assert msgs >= 2  # request + response
```

---

## ⚠️ Common Pitfalls to Avoid

1. **Stats Dictionary Structure**
   - ❌ `stats['total_messages']`
   - ✅ `stats['conversations']['total_messages']`

2. **AgentResponse Parameters**
   - ❌ `data=...` (wrong parameter)
   - ✅ `result=...` (correct parameter)

3. **Module Imports**
   - ❌ `from src.tier1.conversation_manager import ConversationManager`
   - ✅ `from src.tier1.working_memory import WorkingMemory`

4. **Session Resume**
   - Remember: `resume_session=True` continues existing conversation
   - Remember: `resume_session=False` creates new conversation

---

## 🚀 Getting Started

```bash
# Create new test file
touch tests/integration/test_phase_5_1_medium_priority.py

# Copy HIGH priority file as template
cp tests/integration/test_phase_5_1_high_priority.py \
   tests/integration/test_phase_5_1_medium_priority.py

# Start editing
code tests/integration/test_phase_5_1_medium_priority.py
```

---

## ✅ Success Criteria

**After implementing all 10 MEDIUM priority tests:**

- [ ] All 10 tests passing (100% pass rate)
- [ ] Total tests: 1,544 (+10 from current 1,534)
- [ ] Phase 5.1 progress: 70% → 100%
- [ ] Documentation updated
- [ ] Completion summary created

---

## 📊 Progress Tracking

### Checkpoint 1 (After 2 hours)
- [ ] Tests 9-11 implemented
- [ ] 3/10 tests passing
- [ ] Mid-session validation complete

### Checkpoint 2 (After 4 hours)
- [ ] Tests 12-15 implemented
- [ ] 7/10 tests passing
- [ ] Session management validated

### Checkpoint 3 (After 6 hours)
- [ ] Tests 16-18 implemented
- [ ] 10/10 tests passing
- [ ] Full suite validated

### Final (After 7 hours)
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Ready for Phase 5.3

---

## 📚 Reference Documentation

- **Design:** `tests/integration/PHASE-5.1-TEST-DESIGN.md`
- **HIGH Complete:** `cortex-brain/PHASE-5.1-HIGH-PRIORITY-COMPLETE.md`
- **Coverage Analysis:** `cortex-brain/PHASE-5.1-COVERAGE-ANALYSIS.md`
- **Status:** `cortex-brain/cortex-2.0-design/STATUS.md`

---

## 🎯 After Completion

1. **Update STATUS.md**
   - Phase 5.1: 100% complete
   - Overall progress: Update percentage
   - Test count: 1,544 tests

2. **Create Completion Summary**
   - Similar to PHASE-5.1-HIGH-PRIORITY-COMPLETE.md
   - Document challenges and solutions
   - Capture lessons learned

3. **Prepare for Phase 5.3**
   - Edge case test planning
   - Boundary condition analysis
   - Resource exhaustion scenarios

---

**Ready to start?** Begin with test_refactor_code_quality_workflow!

**Estimated completion:** 6-7 hours of focused work  
**Target:** Phase 5.1 at 100%, 1,544 tests total  
**Next phase:** 5.3 - Edge Case Tests

---

*Prepared: 2025-11-09*  
*Based on: HIGH priority success (8/8 passing)*  
*Strategy: Incremental TDD with real tier integration*
