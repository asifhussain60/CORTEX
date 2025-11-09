# Phase 5.1 Critical Integration Test Design

**Created:** 2025-11-09  
**Status:** Design Phase Complete - Ready for Implementation  
**Target:** 18 critical integration tests (covers all 7 gap areas)  
**Implementation Priority:** HIGH → MEDIUM → LOW

---

## 📋 Design Overview

**Gap Areas Addressed:**
1. ✅ End-to-End CortexEntry Workflows (6 tests)
2. ✅ Multi-Agent Coordination (5 tests)
3. ✅ Session Management Edge Cases (4 tests)
4. ✅ Complex Intent Routing (3 tests)

**Total Tests Designed:** 18 tests  
**Estimated Implementation Time:** 6-8 hours  
**Expected Test Count After:** 1,544 tests (from 1,526)

---

## 🎯 Category A: End-to-End User Workflows (6 tests)

### Test 1: `test_add_authentication_full_workflow` ⭐ HIGH PRIORITY

**User Request:** "Add authentication to the app"

**Expected Workflow:**
1. Intent detected as PLAN
2. WorkPlanner agent invoked
3. Plan created and saved to Tier 2
4. Context from Tier 1 injected (previous conversations)
5. Response includes: plan steps, estimated effort, DoD criteria

**Success Criteria:**
- ✅ Intent correctly identified as PLAN
- ✅ WorkPlanner agent receives request
- ✅ Plan saved to Tier 2 knowledge graph
- ✅ Tier 1 conversation logged
- ✅ Response contains actionable plan

**Mock Requirements:**
- Mock IntentRouter to return PLAN intent
- Mock WorkPlanner agent to return sample plan
- Real Tier 1, 2, 3 databases (temp directories)

**Assertions:**
```python
assert response['intent'] == 'PLAN'
assert response['agent'] == 'WorkPlanner'
assert 'plan' in response['result']
assert tier2.get_pattern_by_title('authentication_plan') is not None
assert tier1.get_summary()['total_messages'] >= 2
```

**Implementation Notes:**
- Use fixture from test_cross_tier_workflows.py
- Test duration: ~45 minutes

---

### Test 2: `test_continue_work_session_resume` ⭐ HIGH PRIORITY

**User Request:** "Continue work on exports"

**Expected Workflow:**
1. Previous conversation exists about "exports"
2. SessionManager finds active or recent session
3. Tier 1 injects last 3 conversations about exports
4. Intent detected (could be EXECUTE, QUERY, etc.)
5. Agent uses previous context to continue work

**Success Criteria:**
- ✅ Previous conversation found in Tier 1
- ✅ Session resumed (same conversation_id)
- ✅ Context from previous session injected
- ✅ Agent receives historical context
- ✅ Response acknowledges continuation

**Setup Requirements:**
1. Create previous conversation about "exports"
2. Add messages to Tier 1
3. Optionally: Set session timeout (simulate resume)

**Assertions:**
```python
# Setup
conv_id = tier1.start_conversation("test_agent")
tier1.process_message(conv_id, "user", "Add export functionality")
tier1.process_message(conv_id, "assistant", "I'll create an export module")

# Test
response = cortex_entry.process("Continue work on exports", resume_session=True)

assert response is not None
assert tier1.get_conversation(conv_id) is not None
assert 'export' in response['message'].lower()
```

**Implementation Notes:**
- Test session resume logic
- Validate conversation_id persistence
- Test duration: ~45 minutes

---

### Test 3: `test_fix_bug_debug_workflow` ⭐ HIGH PRIORITY

**User Request:** "Fix bug in login form"

**Expected Workflow:**
1. Intent detected as FIX or EXECUTE
2. HealthValidator agent analyzes the issue
3. CodeExecutor agent applies fix
4. TestGenerator validates fix
5. Result logged to Tier 1

**Success Criteria:**
- ✅ Intent correctly identified as FIX
- ✅ Multiple agents coordinated
- ✅ Fix validated through tests
- ✅ All tiers updated

**Mock Requirements:**
- Mock HealthValidator to identify "login form bug"
- Mock CodeExecutor to return "fix applied"
- Mock TestGenerator to return "tests passing"

**Assertions:**
```python
assert response['intent'] in ['FIX', 'EXECUTE']
assert 'fix' in response['message'].lower()
assert tier1.get_summary()['total_messages'] >= 2
```

**Implementation Notes:**
- Test multi-agent workflow
- Test duration: ~30 minutes

---

### Test 4: `test_refactor_code_quality_workflow` 🔵 MEDIUM PRIORITY

**User Request:** "Refactor authentication module"

**Expected Workflow:**
1. Intent detected as REFACTOR or PLAN
2. Architect agent analyzes current structure
3. WorkPlanner creates refactoring plan
4. CodeExecutor applies changes
5. TestGenerator ensures tests still pass

**Success Criteria:**
- ✅ Refactoring plan created
- ✅ SOLID principles validated
- ✅ Tests remain passing
- ✅ Code quality improved

**Implementation Notes:**
- Focus on planning phase
- Test duration: ~30 minutes

---

### Test 5: `test_complex_feature_multi_session` 🔵 MEDIUM PRIORITY

**User Request:** Multiple requests across 3 sessions

**Session 1:** "Add authentication" (plan created)  
**Session 2:** "Implement JWT tokens" (30 min later, continues plan)  
**Session 3:** "Add password reset" (next day, extends feature)

**Expected Workflow:**
1. Session 1: Plan created, saved to Tier 2
2. Session 2: Resume after timeout, continue implementation
3. Session 3: Extend feature, preserve all context

**Success Criteria:**
- ✅ Context preserved across 3 sessions
- ✅ Conversation_id consistent
- ✅ Tier 2 pattern accumulated
- ✅ All work coordinated

**Implementation Notes:**
- Most complex test
- Test duration: ~60 minutes

---

### Test 6: `test_error_recovery_workflow` 🔵 MEDIUM PRIORITY

**User Request:** "Add feature" → Error → Retry

**Expected Workflow:**
1. Initial request fails (mock error)
2. System logs error to Tier 1
3. User retries with more context
4. System recovers and completes

**Success Criteria:**
- ✅ Error logged properly
- ✅ Context preserved after error
- ✅ Retry succeeds
- ✅ No data corruption

**Implementation Notes:**
- Test error resilience
- Test duration: ~30 minutes

---

## 🤖 Category B: Multi-Agent Coordination (5 tests)

### Test 7: `test_plan_to_execute_handoff` ⭐ HIGH PRIORITY

**Workflow:** WorkPlanner → Executor coordination

**Expected Flow:**
1. User requests feature
2. WorkPlanner creates plan
3. Plan saved to Tier 2
4. Executor receives plan context
5. Executor begins implementation

**Success Criteria:**
- ✅ WorkPlanner output saved
- ✅ Executor receives plan as context
- ✅ No context lost in handoff
- ✅ Both agents log to Tier 1

**Assertions:**
```python
# Mock WorkPlanner
plan = {"steps": ["create model", "add view", "write tests"]}
mock_planner.execute.return_value = AgentResponse(
    success=True,
    result={"plan": plan},
    agent_name="WorkPlanner"
)

# Execute workflow
response1 = cortex_entry.process("Plan authentication feature")
response2 = cortex_entry.process("Implement the plan")

# Validate handoff
assert tier2.get_pattern_by_title("authentication_plan") is not None
assert "plan" in response2['context']
```

**Implementation Notes:**
- Test agent context passing
- Test duration: ~40 minutes

---

### Test 8: `test_execute_to_test_handoff` ⭐ HIGH PRIORITY

**Workflow:** Executor → TestGenerator coordination

**Expected Flow:**
1. Executor implements feature
2. Code changes saved
3. TestGenerator receives code context
4. Tests generated for new code
5. Tests executed and validated

**Success Criteria:**
- ✅ Code changes tracked
- ✅ TestGenerator receives code
- ✅ Tests generated
- ✅ Results logged

**Implementation Notes:**
- Test TDD workflow
- Test duration: ~40 minutes

---

### Test 9: `test_parallel_agent_execution` 🔵 MEDIUM PRIORITY

**Workflow:** Multiple agents working simultaneously

**Expected Flow:**
1. Complex request requires multiple agents
2. Architect + WorkPlanner + HealthValidator execute in parallel
3. Results merged
4. No conflicts or race conditions

**Success Criteria:**
- ✅ Agents execute concurrently
- ✅ No database conflicts
- ✅ Results properly merged
- ✅ Performance acceptable

**Implementation Notes:**
- Use threading/async
- Test duration: ~60 minutes

---

### Test 10: `test_agent_conflict_resolution` 🔵 MEDIUM PRIORITY

**Workflow:** Agents produce conflicting outputs

**Expected Flow:**
1. Two agents suggest different approaches
2. System detects conflict
3. Corpus callosum coordinates resolution
4. Best approach selected

**Success Criteria:**
- ✅ Conflict detected
- ✅ Resolution logic invoked
- ✅ Final decision made
- ✅ Rationale documented

**Implementation Notes:**
- Test coordination logic
- Test duration: ~40 minutes

---

### Test 11: `test_agent_context_passing_chain` 🔵 MEDIUM PRIORITY

**Workflow:** A → B → C → D agent chain

**Expected Flow:**
1. Agent A processes request, passes to B
2. Agent B adds context, passes to C
3. Agent C refines, passes to D
4. Agent D completes and returns
5. All context preserved throughout

**Success Criteria:**
- ✅ Context accumulates properly
- ✅ Each agent receives full history
- ✅ Final result includes all insights
- ✅ No information loss

**Implementation Notes:**
- Test context accumulation
- Test duration: ~40 minutes

---

## ⏱️ Category C: Session Management Edge Cases (4 tests)

### Test 12: `test_30_minute_timeout_enforcement` ⭐ HIGH PRIORITY

**Scenario:** Idle timeout triggers new session

**Expected Flow:**
1. Create session at time T
2. Process message
3. Wait 31 minutes (simulated)
4. Process new message
5. Validate new session created
6. Validate conversation_id preserved

**Success Criteria:**
- ✅ New session created after 30 min
- ✅ Conversation_id remains same
- ✅ Session metadata updated
- ✅ Context still accessible

**Assertions:**
```python
# Create session
conv_id = cortex_entry.process("Start task")

# Simulate 31 minutes
with patch('time.time', return_value=time.time() + 1860):
    new_response = cortex_entry.process("Continue task")

# Validate
assert session_manager.get_active_session() != conv_id
assert tier1.get_conversation(conv_id)['session_count'] == 2
```

**Implementation Notes:**
- Mock time.time()
- Test duration: ~30 minutes

---

### Test 13: `test_session_resume_preserves_conversation_id` ⭐ HIGH PRIORITY

**Scenario:** Resume after timeout keeps conversation_id

**Expected Flow:**
1. Create conversation
2. Timeout occurs (new session)
3. Resume with "continue"
4. Validate same conversation_id
5. Validate context carried over

**Success Criteria:**
- ✅ Same conversation_id used
- ✅ Context from previous session available
- ✅ No data loss
- ✅ Session boundary tracked

**Implementation Notes:**
- Test session continuity
- Test duration: ~30 minutes

---

### Test 14: `test_concurrent_session_handling` 🔵 MEDIUM PRIORITY

**Scenario:** Multiple sessions active simultaneously

**Expected Flow:**
1. User A starts session (conv_1)
2. User B starts session (conv_2)
3. Both process messages
4. Validate no interference
5. Validate data isolation

**Success Criteria:**
- ✅ Sessions isolated
- ✅ No data leakage
- ✅ Correct routing
- ✅ Database integrity

**Implementation Notes:**
- Use threading for concurrency
- Test duration: ~45 minutes

---

### Test 15: `test_session_metadata_persistence` 🔵 MEDIUM PRIORITY

**Scenario:** Session survives system restart

**Expected Flow:**
1. Create session
2. Save metadata
3. Simulate restart (recreate CortexEntry)
4. Validate session recoverable
5. Validate context accessible

**Success Criteria:**
- ✅ Session data persists
- ✅ Metadata accurate
- ✅ Context retrievable
- ✅ No corruption

**Implementation Notes:**
- Test database persistence
- Test duration: ~30 minutes

---

## 🧠 Category D: Complex Intent Routing (3 tests)

### Test 16: `test_multi_intent_request` ⭐ HIGH PRIORITY

**User Request:** "Plan and implement authentication"

**Expected Flow:**
1. IntentRouter detects multiple intents (PLAN + EXECUTE)
2. WorkPlanner creates plan first
3. Executor begins implementation
4. Both results returned

**Success Criteria:**
- ✅ Both intents detected
- ✅ Correct execution order
- ✅ Results merged properly
- ✅ Context shared between phases

**Assertions:**
```python
response = cortex_entry.process("Plan and implement authentication")

assert response['intents'] == ['PLAN', 'EXECUTE']
assert 'plan' in response['result']
assert 'implementation' in response['result']
assert tier2.get_pattern_count() > 0
```

**Implementation Notes:**
- Test intent parsing
- Test duration: ~40 minutes

---

### Test 17: `test_ambiguous_intent_resolution` 🔵 MEDIUM PRIORITY

**User Request:** "Make it better"

**Expected Flow:**
1. IntentRouter detects ambiguous intent
2. System checks Tier 1 for context
3. Disambiguates based on recent work
4. Routes to appropriate agent

**Success Criteria:**
- ✅ Ambiguity detected
- ✅ Context used for resolution
- ✅ Correct agent selected
- ✅ User not confused

**Implementation Notes:**
- Test context-based disambiguation
- Test duration: ~40 minutes

---

### Test 18: `test_intent_confidence_thresholds` 🔵 MEDIUM PRIORITY

**User Request:** Unclear request with low confidence

**Expected Flow:**
1. IntentRouter returns confidence < 0.7
2. System requests clarification
3. User provides more detail
4. Intent re-evaluated with higher confidence
5. Workflow proceeds

**Success Criteria:**
- ✅ Low confidence detected
- ✅ Clarification requested
- ✅ Re-evaluation succeeds
- ✅ Workflow completes

**Implementation Notes:**
- Test confidence thresholds
- Test duration: ~30 minutes

---

## 📊 Implementation Summary

### By Priority:

**HIGH Priority (8 tests - Start Here):**
1. test_add_authentication_full_workflow (45 min)
2. test_continue_work_session_resume (45 min)
3. test_fix_bug_debug_workflow (30 min)
4. test_plan_to_execute_handoff (40 min)
5. test_execute_to_test_handoff (40 min)
6. test_30_minute_timeout_enforcement (30 min)
7. test_session_resume_preserves_conversation_id (30 min)
8. test_multi_intent_request (40 min)

**MEDIUM Priority (10 tests - Second Round):**
9. test_refactor_code_quality_workflow (30 min)
10. test_complex_feature_multi_session (60 min)
11. test_error_recovery_workflow (30 min)
12. test_parallel_agent_execution (60 min)
13. test_agent_conflict_resolution (40 min)
14. test_agent_context_passing_chain (40 min)
15. test_concurrent_session_handling (45 min)
16. test_session_metadata_persistence (30 min)
17. test_ambiguous_intent_resolution (40 min)
18. test_intent_confidence_thresholds (30 min)

### Total Estimates:
- **HIGH Priority:** 5 hours 20 minutes (8 tests)
- **MEDIUM Priority:** 6 hours 25 minutes (10 tests)
- **TOTAL:** 11 hours 45 minutes (18 tests)

### Recommended Phases:

**Phase 1 (Next Session - 5-7 hours):**
- Implement all 8 HIGH priority tests
- Target: 1,534 tests total
- Coverage: End-to-end workflows, basic coordination, session basics

**Phase 2 (Future Session - 3-4 hours):**
- Implement 5-6 MEDIUM priority tests
- Target: 1,540-1,544 tests total
- Coverage: Advanced scenarios, edge cases

**Phase 3 (Future Session - 2-3 hours):**
- Implement remaining 4-5 MEDIUM tests
- Final validation
- Target: 1,544 tests total

---

## 🔧 Shared Test Infrastructure

### Common Fixtures Needed:

```python
@pytest.fixture
def brain_path():
    """Create temporary brain directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        brain = Path(tmpdir)
        (brain / "tier1").mkdir(parents=True)
        (brain / "tier2").mkdir(parents=True)
        (brain / "tier3").mkdir(parents=True)
        yield brain

@pytest.fixture
def cortex_entry(brain_path):
    """Create CORTEX entry point."""
    entry = CortexEntry(brain_path=str(brain_path), enable_logging=False)
    return entry

@pytest.fixture
def mock_agent_router(cortex_entry):
    """Mock IntentRouter for predictable testing."""
    with patch.object(cortex_entry.router, 'execute') as mock:
        yield mock

@pytest.fixture
def tier_apis(cortex_entry):
    """Provide direct tier API access."""
    return {
        'tier1': cortex_entry.tier1,
        'tier2': cortex_entry.tier2,
        'tier3': cortex_entry.tier3
    }
```

### Common Patterns:

**Pattern 1: Agent Response Mocking**
```python
mock_agent_router.return_value = AgentResponse(
    success=True,
    result={"data": "test"},
    message="Success",
    agent_name="TestAgent"
)
```

**Pattern 2: Time Simulation**
```python
with patch('time.time', return_value=base_time + 1860):
    # 31 minutes later
    response = cortex_entry.process("continue")
```

**Pattern 3: Context Setup**
```python
conv_id = tier1.start_conversation("test")
tier1.process_message(conv_id, "user", "request")
tier1.process_message(conv_id, "assistant", "response")
```

---

## ✅ Design Validation Checklist

- [x] All 7 gap areas addressed
- [x] Test priorities assigned (HIGH/MEDIUM)
- [x] Success criteria defined for each test
- [x] Mock requirements identified
- [x] Assertions specified
- [x] Implementation time estimated
- [x] Common infrastructure designed
- [x] TDD approach planned (RED → GREEN → REFACTOR)
- [x] Total count achievable (1,544 tests)
- [x] Coverage target achievable (95%+)

---

## 🎯 Next Steps

1. **Create test file:** `tests/integration/test_phase_5_1_critical.py`
2. **Start with HIGH priority tests** (Tests 1-8)
3. **Follow TDD:** Write test → Run (RED) → Implement → Run (GREEN) → Refactor
4. **Validate incrementally:** After each test, run full suite
5. **Document patterns:** Capture reusable patterns as you go

---

**Design Complete!** Ready for implementation. 🚀

**Expected Outcome:**
- ✅ 1,534-1,544 total tests (from 1,526)
- ✅ 95%+ integration coverage
- ✅ All critical workflows tested
- ✅ Phase 5.1: 70-80% complete

*Created: 2025-11-09*  
*Status: Ready for Implementation*  
*Confidence: HIGH*
