# Phase 5.1 Critical Integration Test Design

**Date:** 2025-11-09  
**Phase:** 5.1 - Critical Integration Tests  
**Status:** Design Phase (Task 1 of 5)  
**Goal:** Design 15-20 critical integration tests for high-priority coverage gaps

---

## 🎯 Design Overview

**Total Tests Designed:** 19 tests across 4 categories  
**Estimated Implementation Time:** 5-7 hours  
**Expected Pass Rate:** 100%  
**TDD Compliance:** All tests follow RED → GREEN → REFACTOR

---

## 📋 Test Categories

### A. End-to-End User Workflows (7 tests) - HIGH PRIORITY
**Time Estimate:** 2-3 hours  
**Purpose:** Validate complete user request flows through all system layers

### B. Multi-Agent Coordination (6 tests) - HIGH PRIORITY  
**Time Estimate:** 2-3 hours  
**Purpose:** Ensure agents hand off work correctly and coordinate complex tasks

### C. Session Boundary Management (4 tests) - MEDIUM PRIORITY
**Time Estimate:** 1-2 hours  
**Purpose:** Validate session lifecycle, timeouts, and conversation continuity

### D. Complex Intent Routing (2 tests) - MEDIUM PRIORITY
**Time Estimate:** 1 hour  
**Purpose:** Test multi-intent detection and ambiguous request handling

---

## 🧪 Test Specifications

---

### **Category A: End-to-End User Workflows**

---

#### **Test 1: test_add_authentication_full_workflow**

**Priority:** HIGH  
**Time Estimate:** 30 minutes  
**File:** `tests/integration/test_end_to_end_workflows.py`

**Description:**  
User requests "Add authentication to the app" and CORTEX plans, implements, tests, and documents the feature through coordinated agent execution.

**User Input:**
```python
request = "Add authentication to the app"
```

**Expected Workflow:**
1. IntentRouter detects PLAN + EXECUTE + TEST + DOCUMENT intents
2. WorkPlanner creates implementation plan
3. Executor implements authentication module
4. TestGenerator creates unit tests
5. Documenter updates README
6. Response includes all artifacts

**Success Criteria:**
- ✅ All 4 agents execute in sequence
- ✅ Each agent receives context from previous agent
- ✅ Final response includes plan, code, tests, and docs
- ✅ Conversation saved to Tier 1
- ✅ Pattern learned in Tier 2

**Mock Requirements:**
- Mock `IntentRouter.route_request()` → returns PLAN, EXECUTE, TEST, DOCUMENT
- Mock `WorkPlanner.plan()` → returns structured plan
- Mock `Executor.execute()` → returns code implementation
- Mock `TestGenerator.generate_tests()` → returns test code
- Mock `Documenter.document()` → returns documentation

**Assertions:**
```python
assert result["status"] == "success"
assert "plan" in result["artifacts"]
assert "code" in result["artifacts"]
assert "tests" in result["artifacts"]
assert "documentation" in result["artifacts"]
assert len(result["agent_sequence"]) == 4
```

**Fixtures Needed:**
- `cortex_entry_with_brain` (from test_cortex_entry.py)
- `mock_multi_agent_router`
- `sample_authentication_plan`

---

#### **Test 2: test_continue_work_session_resume**

**Priority:** HIGH  
**Time Estimate:** 30 minutes  
**File:** `tests/integration/test_end_to_end_workflows.py`

**Description:**  
User says "Continue work on exports" and CORTEX resumes previous conversation context, continuing from where it left off.

**User Input:**
```python
# Session 1
request_1 = "I need to add CSV export functionality"
# ... wait 5 minutes ...
# Session 2
request_2 = "Continue work on exports"
```

**Expected Workflow:**
1. First request creates conversation in Tier 1
2. IntentRouter detects EXECUTE intent
3. Executor begins implementation
4. Second request ("Continue") triggers context retrieval
5. Tier 1 returns last conversation + context
6. Executor resumes work with full context

**Success Criteria:**
- ✅ Second request finds first conversation in Tier 1
- ✅ Context from first request injected into second request
- ✅ Same conversation_id used for both requests
- ✅ Executor references previous work ("As we discussed...")
- ✅ No duplicate context (deduplication works)

**Mock Requirements:**
- Mock `Tier1Memory.get_recent_conversations()` → returns first conversation
- Mock `ContextIntelligence.inject_context()` → adds context to request
- Mock `Executor.execute()` → acknowledges previous context

**Assertions:**
```python
assert result_2["conversation_id"] == result_1["conversation_id"]
assert "export" in result_2["context_injected"]
assert result_2["context_source"] == "tier1_memory"
assert result_2["agent"] == "Executor"
```

**Fixtures Needed:**
- `cortex_entry_with_brain`
- `sample_export_conversation`
- `mock_context_injection`

---

#### **Test 3: test_fix_bug_debug_workflow**

**Priority:** HIGH  
**Time Estimate:** 25 minutes  
**File:** `tests/integration/test_end_to_end_workflows.py`

**Description:**  
User reports "Fix bug in login form" and CORTEX analyzes the issue, implements fix, validates correctness, and generates regression test.

**User Input:**
```python
request = "Fix bug in login form - password field not validating"
```

**Expected Workflow:**
1. IntentRouter detects DEBUG + FIX + TEST intents
2. HealthValidator analyzes login form code
3. Executor implements fix
4. Validator verifies fix correctness
5. TestGenerator creates regression test

**Success Criteria:**
- ✅ HealthValidator identifies bug location
- ✅ Executor applies minimal fix (SOLID principles)
- ✅ Validator confirms fix works
- ✅ TestGenerator creates regression test
- ✅ All agents coordinate without errors

**Mock Requirements:**
- Mock `HealthValidator.analyze()` → returns bug location
- Mock `Executor.fix()` → returns fixed code
- Mock `Validator.verify()` → returns validation result
- Mock `TestGenerator.generate_regression_test()` → returns test

**Assertions:**
```python
assert result["bug_identified"] == True
assert result["fix_applied"] == True
assert result["validation_passed"] == True
assert "regression_test" in result["artifacts"]
```

**Fixtures Needed:**
- `cortex_entry_with_brain`
- `sample_buggy_login_form`
- `mock_bug_analysis`

---

#### **Test 4: test_refactor_code_quality_workflow**

**Priority:** MEDIUM  
**Time Estimate:** 25 minutes  
**File:** `tests/integration/test_end_to_end_workflows.py`

**Description:**  
User requests "Refactor authentication module" and CORTEX plans refactoring, applies SOLID principles, preserves tests, and documents changes.

**User Input:**
```python
request = "Refactor authentication module - it's too complex"
```

**Expected Workflow:**
1. IntentRouter detects REFACTOR intent
2. Architect analyzes module structure
3. WorkPlanner creates refactoring plan
4. Executor applies refactoring
5. TestGenerator ensures tests still pass
6. Documenter updates docs

**Success Criteria:**
- ✅ Architect identifies complexity hotspots
- ✅ Plan includes SOLID principle applications
- ✅ Executor refactors without breaking tests
- ✅ Code complexity reduced (measurable)
- ✅ Documentation reflects new structure

**Mock Requirements:**
- Mock `Architect.analyze_complexity()` → returns complexity score
- Mock `WorkPlanner.plan_refactoring()` → returns refactoring steps
- Mock `Executor.refactor()` → returns refactored code
- Mock `TestGenerator.verify_tests()` → confirms tests pass

**Assertions:**
```python
assert result["complexity_before"] > result["complexity_after"]
assert result["tests_passing"] == True
assert "SOLID" in result["plan"]["principles_applied"]
assert result["documentation_updated"] == True
```

**Fixtures Needed:**
- `cortex_entry_with_brain`
- `sample_complex_auth_module`
- `mock_complexity_analysis`

---

#### **Test 5: test_complex_feature_multi_session**

**Priority:** HIGH  
**Time Estimate:** 35 minutes  
**File:** `tests/integration/test_end_to_end_workflows.py`

**Description:**  
User works on complex feature across multiple sessions (simulating 30+ minute breaks), validating context preservation across session boundaries.

**User Input:**
```python
# Session 1 (time: 0 min)
request_1 = "Design authentication system with OAuth2"
# Session 2 (time: 35 min - new session)
request_2 = "Add JWT token generation"
# Session 3 (time: 70 min - new session)
request_3 = "Implement refresh token logic"
```

**Expected Workflow:**
1. Session 1: Architect designs OAuth2 system
2. 35 min pass → new session, same conversation_id
3. Session 2: Context from Session 1 injected, Executor adds JWT
4. 35 min pass → new session, same conversation_id
5. Session 3: Context from Sessions 1+2 injected, Executor adds refresh

**Success Criteria:**
- ✅ All 3 sessions share same conversation_id
- ✅ Session 2 references OAuth2 design from Session 1
- ✅ Session 3 references JWT from Session 2
- ✅ No context loss across session boundaries
- ✅ Conversation stored with 3 user turns

**Mock Requirements:**
- Mock `SessionManager.check_timeout()` → enforces 30-min boundary
- Mock `Tier1Memory.append_to_conversation()` → adds turns
- Mock `ContextIntelligence.inject_multi_session_context()` → injects history

**Assertions:**
```python
assert result_1["conversation_id"] == result_2["conversation_id"] == result_3["conversation_id"]
assert result_1["session_id"] != result_2["session_id"] != result_3["session_id"]
assert "OAuth2" in result_2["context_injected"]
assert "JWT" in result_3["context_injected"]
```

**Fixtures Needed:**
- `cortex_entry_with_brain`
- `mock_time_progression` (simulates 35-min gaps)
- `sample_multi_session_conversation`

---

#### **Test 6: test_learn_from_error_workflow**

**Priority:** MEDIUM  
**Time Estimate:** 20 minutes  
**File:** `tests/integration/test_end_to_end_workflows.py`

**Description:**  
User encounters error, CORTEX learns from it, and applies learned pattern to prevent future occurrences.

**User Input:**
```python
# Request 1 - causes error
request_1 = "Add API endpoint without authentication"
# (Error occurs - security violation)
# Request 2 - CORTEX remembers
request_2 = "Add another API endpoint"
```

**Expected Workflow:**
1. First request triggers security validation
2. BrainProtector blocks request (no auth)
3. Error logged to Tier 2 as pattern
4. Second request → Tier 2 pattern triggers reminder
5. CORTEX suggests adding authentication

**Success Criteria:**
- ✅ First request blocked by BrainProtector
- ✅ Pattern learned: "API endpoints need authentication"
- ✅ Second request triggers pattern match
- ✅ CORTEX proactively suggests authentication
- ✅ Pattern stored in Tier 2 knowledge graph

**Mock Requirements:**
- Mock `BrainProtector.validate()` → blocks first request
- Mock `Tier2Knowledge.learn_pattern()` → stores security pattern
- Mock `PatternMatcher.find_similar()` → matches second request

**Assertions:**
```python
assert result_1["status"] == "blocked"
assert result_1["reason"] == "security_violation"
assert result_2["suggestions"]["authentication"] == True
assert "API security" in result_2["learned_patterns_applied"]
```

**Fixtures Needed:**
- `cortex_entry_with_brain`
- `mock_security_validation`
- `sample_api_security_pattern`

---

#### **Test 7: test_documentation_sync_workflow**

**Priority:** LOW  
**Time Estimate:** 20 minutes  
**File:** `tests/integration/test_end_to_end_workflows.py`

**Description:**  
User makes code change, CORTEX automatically detects outdated documentation and suggests update.

**User Input:**
```python
request = "Rename function authenticate() to verify_credentials()"
```

**Expected Workflow:**
1. IntentRouter detects REFACTOR intent
2. Executor renames function
3. Tier 3 DevContext detects README mentions old name
4. Documenter suggests documentation update
5. User approves, Documenter updates README

**Success Criteria:**
- ✅ Function renamed successfully
- ✅ Tier 3 detects documentation mismatch
- ✅ Documenter proposes specific change
- ✅ README updated with new function name
- ✅ File relationships updated in Tier 2

**Mock Requirements:**
- Mock `Executor.refactor()` → renames function
- Mock `Tier3DevContext.detect_outdated_docs()` → finds mismatch
- Mock `Documenter.suggest_update()` → proposes change

**Assertions:**
```python
assert result["function_renamed"] == True
assert result["documentation_mismatch_detected"] == True
assert "verify_credentials" in result["suggested_doc_update"]
assert result["documentation_updated"] == True
```

**Fixtures Needed:**
- `cortex_entry_with_brain`
- `sample_function_rename`
- `mock_documentation_detection`

---

### **Category B: Multi-Agent Coordination**

---

#### **Test 8: test_plan_to_execute_handoff**

**Priority:** HIGH  
**Time Estimate:** 25 minutes  
**File:** `tests/integration/test_multi_agent_coordination.py`

**Description:**  
WorkPlanner creates plan, hands off to Executor with structured context.

**User Input:**
```python
request = "Implement user registration"
```

**Expected Workflow:**
1. IntentRouter → WorkPlanner (PLAN intent)
2. WorkPlanner creates detailed plan
3. IntentRouter → Executor (EXECUTE intent)
4. Executor receives plan as context
5. Executor implements based on plan

**Success Criteria:**
- ✅ WorkPlanner produces structured plan (steps, dependencies)
- ✅ Executor receives plan via agent_context
- ✅ Executor follows plan sequence
- ✅ No context loss in handoff
- ✅ Both agents log to same conversation

**Mock Requirements:**
- Mock `WorkPlanner.plan()` → returns structured plan
- Mock `IntentRouter.handoff()` → passes context
- Mock `Executor.execute()` → receives plan

**Assertions:**
```python
assert result["plan_created"] == True
assert result["executor_received_plan"] == True
assert result["plan"]["steps"] == result["executor_context"]["plan"]["steps"]
assert result["conversation_id"] == result["executor_conversation_id"]
```

**Fixtures Needed:**
- `cortex_entry_with_brain`
- `sample_registration_plan`
- `mock_agent_handoff`

---

#### **Test 9: test_execute_to_test_handoff**

**Priority:** HIGH  
**Time Estimate:** 25 minutes  
**File:** `tests/integration/test_multi_agent_coordination.py`

**Description:**  
Executor implements feature, hands off to TestGenerator with code context.

**User Input:**
```python
request = "Implement login function and test it"
```

**Expected Workflow:**
1. Executor implements login function
2. IntentRouter → TestGenerator (TEST intent)
3. TestGenerator receives code as context
4. TestGenerator creates tests for exact implementation

**Success Criteria:**
- ✅ Executor produces working code
- ✅ TestGenerator receives code via agent_context
- ✅ Tests match implementation (not generic)
- ✅ Test assertions cover edge cases
- ✅ Both agents log to same conversation

**Mock Requirements:**
- Mock `Executor.implement()` → returns login function
- Mock `TestGenerator.generate()` → receives code, returns tests

**Assertions:**
```python
assert result["code_implemented"] == True
assert result["tests_generated"] == True
assert "login" in result["test_context"]["code"]
assert len(result["tests"]["assertions"]) >= 5
```

**Fixtures Needed:**
- `cortex_entry_with_brain`
- `sample_login_function`
- `mock_test_generation`

---

#### **Test 10: test_parallel_agent_execution**

**Priority:** MEDIUM  
**Time Estimate:** 30 minutes  
**File:** `tests/integration/test_multi_agent_coordination.py`

**Description:**  
Multiple independent agents work simultaneously on different parts of same request.

**User Input:**
```python
request = "Setup project: create README, add .gitignore, initialize tests/"
```

**Expected Workflow:**
1. IntentRouter detects 3 independent tasks
2. Spawns 3 agents in parallel:
   - Documenter → README
   - Executor → .gitignore
   - TestGenerator → tests/ structure
3. All complete without blocking each other
4. Results merged into single response

**Success Criteria:**
- ✅ 3 agents execute concurrently (not sequentially)
- ✅ No agent blocks another
- ✅ All 3 complete successfully
- ✅ Execution time < sum of individual times (parallelism works)
- ✅ Results merged correctly

**Mock Requirements:**
- Mock `IntentRouter.parallel_route()` → spawns 3 agents
- Mock agents complete in parallel (asyncio or threading)
- Mock result merger

**Assertions:**
```python
assert result["agents_executed"] == 3
assert result["execution_mode"] == "parallel"
assert result["total_time"] < (time_readme + time_gitignore + time_tests)
assert "README" in result["artifacts"]
assert ".gitignore" in result["artifacts"]
```

**Fixtures Needed:**
- `cortex_entry_with_brain`
- `mock_parallel_execution`
- `sample_project_setup_tasks`

---

#### **Test 11: test_agent_conflict_resolution**

**Priority:** MEDIUM  
**Time Estimate:** 30 minutes  
**File:** `tests/integration/test_multi_agent_coordination.py`

**Description:**  
Two agents produce conflicting outputs, corpus callosum resolves conflict using governance rules.

**User Input:**
```python
request = "Optimize database queries" (ambiguous - caching vs indexing?)
```

**Expected Workflow:**
1. Architect suggests "Add database indexes"
2. Executor suggests "Add Redis caching layer"
3. CorpusCallosum detects conflict
4. Governance rules: prefer simplest solution first
5. CorpusCallosum selects Architect's approach
6. Executor implements indexes

**Success Criteria:**
- ✅ Both agents produce valid but different solutions
- ✅ CorpusCallosum detects conflict
- ✅ Governance rules applied (simplicity > complexity)
- ✅ Winning solution executed
- ✅ Losing solution logged (for future reference)

**Mock Requirements:**
- Mock `Architect.suggest()` → returns indexing solution
- Mock `Executor.suggest()` → returns caching solution
- Mock `CorpusCallosum.resolve_conflict()` → applies governance

**Assertions:**
```python
assert result["conflict_detected"] == True
assert result["solutions_proposed"] == 2
assert result["resolution_method"] == "governance_rules"
assert result["selected_solution"] == "database_indexes"
```

**Fixtures Needed:**
- `cortex_entry_with_brain`
- `mock_conflicting_agents`
- `sample_governance_rules`

---

#### **Test 12: test_agent_context_passing**

**Priority:** HIGH  
**Time Estimate:** 20 minutes  
**File:** `tests/integration/test_multi_agent_coordination.py`

**Description:**  
Agent B must receive and use specific output from Agent A (validates context pipeline).

**User Input:**
```python
request = "Analyze code complexity then suggest refactoring"
```

**Expected Workflow:**
1. HealthValidator analyzes complexity → score: 8.5/10
2. Architect receives complexity score as context
3. Architect designs refactoring targeting high-complexity areas
4. Refactoring plan references specific complexity score

**Success Criteria:**
- ✅ HealthValidator produces complexity analysis
- ✅ Architect receives analysis via agent_context
- ✅ Architect's plan references specific score
- ✅ Context preserved across agent boundary
- ✅ Both agents share conversation_id

**Mock Requirements:**
- Mock `HealthValidator.analyze()` → returns complexity score
- Mock `Architect.design()` → receives score as context

**Assertions:**
```python
assert result["complexity_score"] == 8.5
assert result["architect_received_score"] == True
assert "8.5" in result["refactoring_plan"]["rationale"]
```

**Fixtures Needed:**
- `cortex_entry_with_brain`
- `sample_complexity_analysis`
- `mock_architect_context`

---

#### **Test 13: test_agent_retry_on_failure**

**Priority:** MEDIUM  
**Time Estimate:** 25 minutes  
**File:** `tests/integration/test_multi_agent_coordination.py`

**Description:**  
Agent fails on first attempt, IntentRouter retries with adjusted context.

**User Input:**
```python
request = "Generate API documentation"
```

**Expected Workflow:**
1. Documenter attempts doc generation → fails (missing API spec)
2. IntentRouter detects failure
3. HealthValidator extracts API spec from code
4. IntentRouter retries Documenter with API spec as context
5. Documenter succeeds

**Success Criteria:**
- ✅ First attempt fails with clear error
- ✅ IntentRouter detects failure reason
- ✅ Helper agent (HealthValidator) provides missing context
- ✅ Retry succeeds with enhanced context
- ✅ Max 3 retries enforced (no infinite loop)

**Mock Requirements:**
- Mock `Documenter.generate()` → fails on first call, succeeds on second
- Mock `IntentRouter.retry_with_context()` → orchestrates retry
- Mock `HealthValidator.extract_api_spec()` → provides missing spec

**Assertions:**
```python
assert result["first_attempt_failed"] == True
assert result["retry_count"] == 1
assert result["final_status"] == "success"
assert "API specification" in result["retry_context"]
```

**Fixtures Needed:**
- `cortex_entry_with_brain`
- `mock_failing_agent`
- `mock_retry_logic`

---

### **Category C: Session Boundary Management**

---

#### **Test 14: test_30_minute_timeout_enforcement**

**Priority:** HIGH  
**Time Estimate:** 20 minutes  
**File:** `tests/integration/test_session_boundaries.py`

**Description:**  
After 30 minutes idle, new session created with same conversation_id.

**User Input:**
```python
# Request 1 at time 0
request_1 = "Design authentication system"
# Request 2 at time 35 minutes
request_2 = "Continue with OAuth implementation"
```

**Expected Workflow:**
1. Request 1 creates session_id_1, conversation_id_1
2. Time passes 35 minutes (simulated)
3. Request 2 creates session_id_2 (new session!)
4. Conversation_id_1 preserved (same conversation)
5. Session manager logs new session with reference to old session

**Success Criteria:**
- ✅ Session 1 and Session 2 have different session_ids
- ✅ Both sessions share conversation_id
- ✅ Session 2 marked as "continuation" of Session 1
- ✅ Timeout boundary exactly 30 minutes
- ✅ Context from Session 1 injected into Session 2

**Mock Requirements:**
- Mock `time.time()` → simulates 35-minute gap
- Mock `SessionManager.check_timeout()` → enforces boundary
- Mock `SessionManager.create_new_session()` → creates session 2

**Assertions:**
```python
assert result_1["session_id"] != result_2["session_id"]
assert result_1["conversation_id"] == result_2["conversation_id"]
assert result_2["session_metadata"]["previous_session"] == result_1["session_id"]
assert result_2["timeout_triggered"] == True
```

**Fixtures Needed:**
- `cortex_entry_with_brain`
- `mock_time_progression`
- `sample_multi_session_request`

---

#### **Test 15: test_session_resume_preserves_conversation_id**

**Priority:** HIGH  
**Time Estimate:** 20 minutes  
**File:** `tests/integration/test_session_boundaries.py`

**Description:**  
User explicitly resumes work, same conversation_id used across sessions.

**User Input:**
```python
# Day 1
request_1 = "Start implementing payment gateway"
# Day 2 (next day)
request_2 = "Resume payment gateway work"
```

**Expected Workflow:**
1. Request 1 saves conversation to Tier 1
2. Next day, Request 2 triggers "resume" intent
3. Tier 1 searches for "payment gateway" conversation
4. Same conversation_id retrieved
5. New session created, old context injected

**Success Criteria:**
- ✅ "Resume" intent detected
- ✅ Tier 1 query finds previous conversation
- ✅ Conversation_id from Day 1 reused
- ✅ New session_id created for Day 2
- ✅ Full context from Day 1 available

**Mock Requirements:**
- Mock `IntentRouter.detect_resume()` → identifies resume intent
- Mock `Tier1Memory.find_conversation()` → returns Day 1 conversation
- Mock `SessionManager.resume_conversation()` → links sessions

**Assertions:**
```python
assert result_2["intent"] == "RESUME"
assert result_2["conversation_id"] == result_1["conversation_id"]
assert "payment gateway" in result_2["context_injected"]
assert result_2["session_resumed"] == True
```

**Fixtures Needed:**
- `cortex_entry_with_brain`
- `sample_resume_conversation`
- `mock_resume_detection`

---

#### **Test 16: test_concurrent_session_handling**

**Priority:** MEDIUM  
**Time Estimate:** 25 minutes  
**File:** `tests/integration/test_session_boundaries.py`

**Description:**  
Multiple sessions (different conversations) running simultaneously don't interfere.

**User Input:**
```python
# Conversation A
request_a1 = "Design authentication system"
# Conversation B (concurrent)
request_b1 = "Implement logging module"
# Conversation A continues
request_a2 = "Add OAuth to authentication"
```

**Expected Workflow:**
1. Request A1 creates conversation_id_a, session_id_a1
2. Request B1 creates conversation_id_b, session_id_b1
3. Both sessions active simultaneously
4. Request A2 continues conversation_id_a (not confused with B)
5. No context leakage between conversations

**Success Criteria:**
- ✅ Two separate conversation_ids created
- ✅ Request A2 retrieves only conversation A context
- ✅ No mention of "logging" in conversation A
- ✅ Both sessions can save to Tier 1 without collision
- ✅ Session isolation maintained

**Mock Requirements:**
- Mock concurrent session manager
- Mock separate Tier 1 conversation threads

**Assertions:**
```python
assert result_a1["conversation_id"] != result_b1["conversation_id"]
assert "authentication" in result_a2["context"]
assert "logging" not in result_a2["context"]
assert result_a2["conversation_id"] == result_a1["conversation_id"]
```

**Fixtures Needed:**
- `cortex_entry_with_brain`
- `mock_concurrent_sessions`
- `sample_multi_conversation_data`

---

#### **Test 17: test_session_metadata_persistence**

**Priority:** MEDIUM  
**Time Estimate:** 20 minutes  
**File:** `tests/integration/test_session_boundaries.py`

**Description:**  
Session metadata (start time, end time, request count) persists across restarts.

**User Input:**
```python
# Session 1
request_1 = "Start project"
request_2 = "Add README"
# (Restart CORTEX)
# Session 2
request_3 = "Continue project setup"
```

**Expected Workflow:**
1. Session 1 logs 2 requests with timestamps
2. Session 1 metadata saved to Tier 1
3. CORTEX restarts (simulated)
4. Session 2 retrieves previous session metadata
5. Metadata shows 2 previous requests

**Success Criteria:**
- ✅ Session 1 metadata saved to database
- ✅ After restart, metadata retrieved
- ✅ Request count accurate (2 requests)
- ✅ Timestamps preserved
- ✅ Session continuity maintained

**Mock Requirements:**
- Mock `SessionManager.save_metadata()` → persists to DB
- Mock `SessionManager.load_metadata()` → retrieves after restart
- Mock system restart (close/reopen CortexEntry)

**Assertions:**
```python
assert result_3["previous_session_metadata"]["request_count"] == 2
assert result_3["previous_session_metadata"]["start_time"] is not None
assert result_3["session_metadata"]["continuation"] == True
```

**Fixtures Needed:**
- `cortex_entry_with_brain`
- `mock_session_persistence`
- `sample_session_metadata`

---

### **Category D: Complex Intent Routing**

---

#### **Test 18: test_multi_intent_request**

**Priority:** MEDIUM  
**Time Estimate:** 30 minutes  
**File:** `tests/integration/test_complex_intent_routing.py`

**Description:**  
User request contains multiple intents, all detected and executed in correct order.

**User Input:**
```python
request = "Plan, implement, and test user registration with email verification"
```

**Expected Workflow:**
1. IntentRouter detects 3 intents: PLAN, EXECUTE, TEST
2. WorkPlanner creates registration plan
3. Executor implements registration + email verification
4. TestGenerator creates integration tests
5. All agents execute in sequence

**Success Criteria:**
- ✅ All 3 intents detected
- ✅ Correct execution order (plan → execute → test)
- ✅ Each agent receives context from previous agent
- ✅ Final response includes all artifacts
- ✅ Single conversation_id for all agents

**Mock Requirements:**
- Mock `IntentRouter.detect_multi_intent()` → returns 3 intents
- Mock `IntentRouter.order_intents()` → ensures correct sequence
- Mock all 3 agents

**Assertions:**
```python
assert len(result["intents_detected"]) == 3
assert result["execution_order"] == ["PLAN", "EXECUTE", "TEST"]
assert "plan" in result["artifacts"]
assert "code" in result["artifacts"]
assert "tests" in result["artifacts"]
```

**Fixtures Needed:**
- `cortex_entry_with_brain`
- `mock_multi_intent_detection`
- `sample_registration_workflow`

---

#### **Test 19: test_ambiguous_intent_resolution**

**Priority:** LOW  
**Time Estimate:** 25 minutes  
**File:** `tests/integration/test_complex_intent_routing.py`

**Description:**  
User request is ambiguous, CORTEX uses context to disambiguate or asks for clarification.

**User Input:**
```python
# Previous context: working on authentication
request = "Make it better"
```

**Expected Workflow:**
1. IntentRouter detects vague request
2. Tier 1 retrieves recent context (authentication)
3. PatternMatcher infers: "improve authentication"
4. IntentRouter routes to Architect (REFACTOR intent)
5. Architect suggests authentication improvements

**Success Criteria:**
- ✅ Ambiguity detected (confidence < 0.6)
- ✅ Context from Tier 1 used for disambiguation
- ✅ Intent resolved: REFACTOR (authentication)
- ✅ If still ambiguous, clarification requested
- ✅ No random guessing

**Mock Requirements:**
- Mock `IntentRouter.detect_ambiguity()` → flags vague request
- Mock `Tier1Memory.get_recent_context()` → returns auth context
- Mock `PatternMatcher.infer_intent()` → resolves to REFACTOR

**Assertions:**
```python
assert result["ambiguity_detected"] == True
assert result["context_used_for_disambiguation"] == True
assert result["resolved_intent"] == "REFACTOR"
assert "authentication" in result["inferred_topic"]
```

**Fixtures Needed:**
- `cortex_entry_with_brain`
- `sample_ambiguous_request`
- `mock_intent_disambiguation`

---

## 📊 Implementation Summary

### Test Distribution by Priority

| Priority | Count | Estimated Time |
|----------|-------|----------------|
| HIGH | 10 tests | 4-5 hours |
| MEDIUM | 7 tests | 2-3 hours |
| LOW | 2 tests | 1 hour |
| **TOTAL** | **19 tests** | **7-9 hours** |

### Test Distribution by Category

| Category | Count | Time |
|----------|-------|------|
| A. End-to-End Workflows | 7 tests | 2.5 hours |
| B. Multi-Agent Coordination | 6 tests | 2.5 hours |
| C. Session Boundaries | 4 tests | 1.5 hours |
| D. Complex Intent Routing | 2 tests | 1 hour |

---

## 🚀 Implementation Order

### Phase 1: HIGH Priority (Must Have) - 4-5 hours

1. **test_add_authentication_full_workflow** (30 min)
2. **test_continue_work_session_resume** (30 min)
3. **test_fix_bug_debug_workflow** (25 min)
4. **test_plan_to_execute_handoff** (25 min)
5. **test_execute_to_test_handoff** (25 min)
6. **test_agent_context_passing** (20 min)
7. **test_complex_feature_multi_session** (35 min)
8. **test_30_minute_timeout_enforcement** (20 min)
9. **test_session_resume_preserves_conversation_id** (20 min)
10. **test_multi_intent_request** (30 min)

**Subtotal:** 4 hours 40 minutes

---

### Phase 2: MEDIUM Priority (Should Have) - 2-3 hours

11. **test_refactor_code_quality_workflow** (25 min)
12. **test_learn_from_error_workflow** (20 min)
13. **test_parallel_agent_execution** (30 min)
14. **test_agent_conflict_resolution** (30 min)
15. **test_agent_retry_on_failure** (25 min)
16. **test_concurrent_session_handling** (25 min)
17. **test_session_metadata_persistence** (20 min)

**Subtotal:** 2 hours 55 minutes

---

### Phase 3: LOW Priority (Nice to Have) - 1 hour

18. **test_documentation_sync_workflow** (20 min)
19. **test_ambiguous_intent_resolution** (25 min)

**Subtotal:** 45 minutes

---

## 🎯 Success Criteria

**Phase 5.1 Complete When:**
- ✅ All 19 tests designed (this document)
- ✅ 15+ tests implemented (85%+ completion)
- ✅ 100% pass rate maintained
- ✅ Total test count: 1,540+ tests
- ✅ Integration coverage: 95%+
- ✅ All HIGH priority tests passing

**Quality Gates:**
- ✅ Every test follows TDD (RED → GREEN → REFACTOR)
- ✅ All tests use isolated fixtures (no shared state)
- ✅ Mock requirements documented and implemented
- ✅ Assertions comprehensive (5+ per test minimum)
- ✅ Test names descriptive and searchable

---

## 📝 Common Fixtures to Create

### Fixture 1: `cortex_entry_with_brain`
```python
@pytest.fixture
def cortex_entry_with_brain():
    """
    Creates temporary brain directory with tier subdirectories.
    Returns initialized CortexEntry instance.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        brain = Path(tmpdir)
        (brain / "tier1").mkdir(parents=True)
        (brain / "tier2").mkdir(parents=True)
        (brain / "tier3").mkdir(parents=True)
        
        entry = CortexEntry(brain_path=str(brain), enable_logging=False)
        yield entry
```

### Fixture 2: `mock_multi_agent_router`
```python
@pytest.fixture
def mock_multi_agent_router(mocker):
    """
    Mocks IntentRouter to return multiple agent sequences.
    """
    router = mocker.patch('src.agents.intent_router.IntentRouter')
    router.route_request.return_value = {
        "intents": ["PLAN", "EXECUTE", "TEST"],
        "agents": ["WorkPlanner", "Executor", "TestGenerator"],
        "confidence": 0.95
    }
    return router
```

### Fixture 3: `mock_time_progression`
```python
@pytest.fixture
def mock_time_progression(mocker):
    """
    Simulates time passing for session timeout tests.
    """
    times = [0, 35*60]  # 0 min, 35 min
    mocker.patch('time.time', side_effect=times)
    return times
```

---

## 🔧 Testing Patterns to Follow

### Pattern 1: TDD - RED → GREEN → REFACTOR
```python
# Step 1: Write failing test
def test_add_authentication_full_workflow(cortex_entry_with_brain):
    result = cortex_entry_with_brain.process_request("Add authentication")
    assert result["status"] == "success"  # FAILS (not implemented)

# Step 2: Minimal implementation to pass
# (Implement just enough to make test pass)

# Step 3: Refactor (improve code without breaking test)
```

### Pattern 2: Isolated Fixtures
```python
# ✅ GOOD - Each test gets fresh instance
@pytest.fixture
def fresh_brain():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

# ❌ BAD - Shared state between tests
brain_path = "/tmp/shared_brain"
```

### Pattern 3: Comprehensive Assertions
```python
# ✅ GOOD - Multiple assertions validate behavior
assert result["status"] == "success"
assert len(result["artifacts"]) == 4
assert "plan" in result["artifacts"]
assert result["conversation_id"] is not None
assert result["agents_executed"] == ["WorkPlanner", "Executor"]

# ❌ BAD - Single assertion, incomplete validation
assert result is not None
```

---

## 📚 Reference Documents

**Before Implementing Tests, Review:**
1. `tests/integration/test_cross_tier_workflows.py` - Integration test examples
2. `tests/entry_point/test_cortex_entry.py` - Entry point patterns
3. `PHASE-5.1-COVERAGE-ANALYSIS.md` - Gap analysis
4. `tests/tier0/test_brain_protector.py` - Brain protection patterns (100% passing)

---

## ✅ Design Phase Complete

**Design Document:** ✅ COMPLETE  
**Tests Designed:** 19 tests  
**Categories Covered:** 4 (A, B, C, D)  
**Estimated Implementation Time:** 7-9 hours  
**Next Step:** Begin implementing Phase 1 (HIGH priority tests)

**Ready to proceed:** Design → Implement 🚀

---

*Document Created: 2025-11-09*  
*Phase: 5.1 - Critical Integration Tests*  
*Status: Design phase complete, ready for implementation*
