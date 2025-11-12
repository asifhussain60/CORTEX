# CORTEX Phase 5.1 - Critical Test Plan

**Date:** November 9, 2025  
**Phase:** 5.1 - Critical Integration & Edge Case Testing  
**Status:** 🔄 IN PROGRESS  
**Estimated Effort:** 4-6 hours  
**Goal:** Add 25-35 critical tests to reach 765+ total tests

---

## 🎯 Executive Summary

### Current State
- **Total Tests:** 737+ tests across 86 test files
- **Test Coverage:** 100% pass rate
- **Test Types:** Unit (60%), Integration (25%), E2E (15%)

### Identified Gaps
After comprehensive analysis of existing test suite, the following critical gaps were identified:

**1. Cross-Tier Integration (HIGH PRIORITY)**
- ❌ No tests for Tier 1 → Tier 2 → Tier 3 complete flow
- ❌ No tests for error propagation across tier boundaries
- ❌ No tests for transaction rollback across tiers

**2. Modular Entry Point Integration (HIGH PRIORITY)**
- ❌ No tests for module lazy loading
- ❌ No tests for command registry → intent routing pipeline
- ❌ No tests for natural language → slash command expansion

**3. Workflow Pipeline E2E (MEDIUM PRIORITY)**
- ⚠️  Limited tests for checkpoint/resume across sessions
- ⚠️  No tests for workflow state corruption recovery
- ⚠️  No tests for concurrent workflow execution

**4. Plugin System Integration (MEDIUM PRIORITY)**
- ⚠️  Plugin command registration tested, but not full lifecycle
- ⚠️  No tests for plugin failure isolation
- ⚠️  No tests for plugin dependency resolution

**5. Edge Cases (MEDIUM PRIORITY)**
- ❌ No tests for empty/malformed inputs at entry point
- ❌ No tests for resource exhaustion (memory, disk, connections)
- ❌ No tests for concurrent access to brain databases

**6. Platform-Specific Behavior (LOW PRIORITY)**
- ⚠️  Platform detection tested, but not full cross-platform workflows
- ❌ No tests for platform-specific path handling edge cases

---

## 📊 Gap Analysis Summary

| Category | Existing Tests | Missing Tests | Priority | Effort |
|----------|----------------|---------------|----------|--------|
| Cross-Tier Integration | 3 | 8-10 | HIGH | 2-3h |
| Entry Point Integration | 3 | 6-8 | HIGH | 1-2h |
| Workflow E2E | 16 | 4-6 | MEDIUM | 1h |
| Plugin Lifecycle | 7 | 3-4 | MEDIUM | 0.5h |
| Edge Cases | 0 | 5-7 | MEDIUM | 1h |
| Platform-Specific | 1 | 2-3 | LOW | 0.5h |
| **TOTAL** | **30** | **28-38** | - | **6-8h** |

**Revised Estimate:** 4-6 hours (targeting 25-30 tests for Phase 5.1)

---

## 🧪 Test Cases to Implement

### Priority 1: Cross-Tier Integration Tests (8-10 tests, 2-3 hours)

**File:** `tests/integration/test_cross_tier_workflows.py` (NEW)

#### Test 1.1: Complete Read Flow (Tier 1 → Tier 2 → Tier 3)
```python
def test_cross_tier_read_flow(cortex_entry, brain_path):
    """
    Test: User message → Tier 1 lookup → Tier 2 pattern search → Tier 3 context
    
    Flow:
    1. User: "Continue work on authentication"
    2. Tier 1: Find last 3 conversations about "authentication"
    3. Tier 2: Search patterns for "authentication" workflows
    4. Tier 3: Get file hotspots related to auth
    5. Router: Synthesize response with all 3 tiers
    
    Success: All 3 tiers queried, response includes context from each
    """
```

#### Test 1.2: Cross-Tier Error Propagation
```python
def test_cross_tier_error_propagation(cortex_entry, brain_path):
    """
    Test: Error in Tier 2 doesn't crash Tier 1 or Tier 3
    
    Scenario:
    - Corrupt Tier 2 knowledge graph database
    - Process user request
    
    Expected: 
    - Tier 1 succeeds (conversation logged)
    - Tier 2 error caught and logged
    - Tier 3 skipped (depends on Tier 2)
    - User gets degraded response (no pattern suggestions)
    """
```

#### Test 1.3: Cross-Tier Write Coordination
```python
def test_cross_tier_write_coordination(cortex_entry, brain_path):
    """
    Test: Workflow completion updates all 3 tiers
    
    Flow:
    1. Execute "create feature" workflow
    2. Verify writes:
       - Tier 1: Conversation logged
       - Tier 2: Pattern created/updated
       - Tier 3: Git metrics refreshed
    
    Success: All 3 tiers updated in correct order
    """
```

#### Test 1.4: Tier Boundary Enforcement
```python
def test_tier_boundary_enforcement(cortex_entry, brain_path):
    """
    Test: Tier 3 cannot write to Tier 1 database
    
    Scenario:
    - Tier 3 tries to write to tier1/conversations.db
    
    Expected:
    - BrainProtector blocks write
    - Operation fails with clear error
    - No data corruption
    """
```

#### Test 1.5: Cross-Tier Transaction Rollback
```python
def test_cross_tier_transaction_rollback(cortex_entry, brain_path):
    """
    Test: Failed Tier 2 write rolls back Tier 1 changes
    
    Scenario:
    1. Begin conversation (Tier 1 write)
    2. Add pattern (Tier 2 write)
    3. Tier 2 write fails (disk full)
    4. Verify Tier 1 conversation marked as failed
    
    Success: No partial state across tiers
    """
```

#### Test 1.6: Tier Data Consistency Check
```python
def test_tier_data_consistency_check(cortex_entry, brain_path):
    """
    Test: Conversation references in Tier 2 exist in Tier 1
    
    Validation:
    - For all patterns in Tier 2 with conversation_id
    - Verify conversation exists in Tier 1
    
    Success: No orphaned references
    """
```

#### Test 1.7: Concurrent Tier Access
```python
def test_concurrent_tier_access(cortex_entry, brain_path):
    """
    Test: Multiple users accessing different tiers simultaneously
    
    Scenario:
    - Thread 1: Read Tier 1 (conversation history)
    - Thread 2: Write Tier 2 (new pattern)
    - Thread 3: Read Tier 3 (git metrics)
    
    Success: No deadlocks, no data corruption
    """
```

#### Test 1.8: Tier Performance Under Load
```python
def test_tier_performance_under_load(cortex_entry, brain_path):
    """
    Test: Cross-tier operations complete within SLA
    
    Load:
    - 100 requests/minute
    - Each request touches all 3 tiers
    
    Success: 
    - P50 < 200ms
    - P95 < 500ms
    - P99 < 1000ms
    """
```

---

### Priority 2: Entry Point Integration Tests (6-8 tests, 1-2 hours)

**File:** `tests/integration/test_entry_point_integration.py` (NEW)

#### Test 2.1: Module Lazy Loading
```python
def test_module_lazy_loading(cortex_entry):
    """
    Test: Modules loaded only when needed
    
    Scenario:
    1. User: "Show me the story"
    2. Verify only story.md loaded (not setup-guide, technical-reference)
    
    Success: 
    - Token count < 3,000 (story.md ~2,045 tokens)
    - Other modules not in memory
    """
```

#### Test 2.2: Command Registry → Intent Routing
```python
def test_command_registry_intent_routing(cortex_entry):
    """
    Test: Slash commands expanded to natural language
    
    Flow:
    1. User: "/setup"
    2. Command registry expands to "setup environment"
    3. Intent detector: SETUP_ENVIRONMENT
    4. Router: platform_switch plugin
    
    Success: Slash command treated as natural language
    """
```

#### Test 2.3: Natural Language Command Matching
```python
def test_natural_language_command_matching(cortex_entry):
    """
    Test: Natural language triggers correct command
    
    Inputs:
    - "configure my environment" → /setup
    - "where did I leave off" → /resume
    - "show progress" → /status
    
    Success: Intent detection matches registered commands
    """
```

#### Test 2.4: Plugin Command Registration
```python
def test_plugin_command_registration(cortex_entry):
    """
    Test: Plugin registers command and it becomes available
    
    Flow:
    1. Load platform_switch plugin
    2. Verify /setup command registered
    3. Verify natural language equivalents registered
    4. Process "/setup" command
    
    Success: Plugin command routed correctly
    """
```

#### Test 2.5: Entry Point Error Handling
```python
def test_entry_point_error_handling(cortex_entry):
    """
    Test: Entry point handles errors gracefully
    
    Errors:
    - Empty input
    - Malformed JSON
    - Missing required fields
    - Invalid command
    
    Success: User-friendly error messages, no crashes
    """
```

#### Test 2.6: Entry Point Response Formatting
```python
def test_entry_point_response_formatting(cortex_entry):
    """
    Test: Responses formatted consistently
    
    Response types:
    - Success (with results)
    - Success (no results)
    - Partial success (with warnings)
    - Failure (with error)
    
    Success: All responses follow format spec
    """
```

---

### Priority 3: Workflow Pipeline E2E Tests (4-6 tests, 1 hour)

**File:** `tests/workflows/test_workflow_edge_cases.py` (NEW)

#### Test 3.1: Checkpoint Resume Across Sessions
```python
def test_checkpoint_resume_across_sessions(workflow_engine, temp_checkpoint_dir):
    """
    Test: Resume workflow after CORTEX restart
    
    Scenario:
    1. Start feature workflow
    2. Complete 3/8 stages
    3. Save checkpoint
    4. Simulate CORTEX restart (new WorkflowEngine instance)
    5. Resume from checkpoint
    
    Success: Workflow resumes from stage 4
    """
```

#### Test 3.2: Workflow State Corruption Recovery
```python
def test_workflow_state_corruption_recovery(workflow_engine, temp_checkpoint_dir):
    """
    Test: Detect and recover from corrupted checkpoint
    
    Scenario:
    1. Start workflow
    2. Save checkpoint
    3. Corrupt checkpoint file (invalid JSON)
    4. Attempt resume
    
    Expected: 
    - Corruption detected
    - Fallback to last good checkpoint
    - Or restart workflow with warning
    """
```

#### Test 3.3: Concurrent Workflow Execution
```python
def test_concurrent_workflow_execution(workflow_engine):
    """
    Test: Multiple workflows running simultaneously
    
    Scenario:
    - Start "feature" workflow (id: workflow-1)
    - Start "bugfix" workflow (id: workflow-2)
    - Complete both
    
    Success: 
    - No interference between workflows
    - Both complete successfully
    - Checkpoints don't overwrite each other
    """
```

#### Test 3.4: Workflow Timeout Handling
```python
def test_workflow_timeout_handling(workflow_engine):
    """
    Test: Workflow stage times out and recovers
    
    Scenario:
    1. Mock stage that hangs for 10 seconds
    2. Set timeout to 2 seconds
    3. Execute workflow
    
    Expected:
    - Stage times out after 2 seconds
    - Workflow retries (if retryable)
    - Or fails gracefully with error
    """
```

---

### Priority 4: Plugin Lifecycle Tests (3-4 tests, 0.5 hour)

**File:** `tests/plugins/test_plugin_lifecycle.py` (NEW)

#### Test 4.1: Plugin Initialization Failure Isolation
```python
def test_plugin_initialization_failure_isolation(plugin_manager):
    """
    Test: One plugin failure doesn't affect others
    
    Scenario:
    - Load 3 plugins: A (valid), B (invalid), C (valid)
    - Plugin B throws exception in initialize()
    
    Expected:
    - Plugins A and C load successfully
    - Plugin B error logged
    - CORTEX continues functioning
    """
```

#### Test 4.2: Plugin Dependency Resolution
```python
def test_plugin_dependency_resolution(plugin_manager):
    """
    Test: Plugins loaded in correct order
    
    Scenario:
    - Plugin B depends on Plugin A
    - Plugin C depends on Plugin B
    - Load order: C, A, B (out of order)
    
    Expected:
    - Plugin manager reorders to: A → B → C
    - All plugins initialize successfully
    """
```

#### Test 4.3: Plugin Command Conflict Detection
```python
def test_plugin_command_conflict_detection(plugin_manager, command_registry):
    """
    Test: Detect conflicting commands from multiple plugins
    
    Scenario:
    - Plugin A registers "/setup"
    - Plugin B also registers "/setup"
    
    Expected:
    - Conflict detected during registration
    - Error raised with clear message
    - First plugin wins, second rejected
    """
```

---

### Priority 5: Edge Case Tests (5-7 tests, 1 hour)

**File:** `tests/integration/test_edge_cases.py` (NEW)

#### Test 5.1: Empty Input Handling
```python
def test_empty_input_handling(cortex_entry):
    """
    Test: Handle empty/whitespace-only inputs
    
    Inputs:
    - ""
    - "   "
    - "\n\n\n"
    - None
    
    Expected: User-friendly error, no crash
    """
```

#### Test 5.2: Malformed JSON Input
```python
def test_malformed_json_input(cortex_entry):
    """
    Test: Handle invalid JSON in API calls
    
    Inputs:
    - "{invalid json}"
    - "{'single': 'quotes'}"
    - Truncated JSON
    
    Expected: Parse error with helpful message
    """
```

#### Test 5.3: Database Connection Exhaustion
```python
def test_database_connection_exhaustion(cortex_entry, brain_path):
    """
    Test: Handle connection pool exhaustion
    
    Scenario:
    - SQLite connection limit reached (default: 20)
    - New request arrives
    
    Expected:
    - Wait for connection (timeout: 5s)
    - Or return error with retry guidance
    """
```

#### Test 5.4: Disk Space Exhaustion
```python
def test_disk_space_exhaustion(cortex_entry, brain_path):
    """
    Test: Handle disk full condition
    
    Scenario:
    - Mock disk at capacity
    - Attempt to write to Tier 1/2/3
    
    Expected:
    - Write fails with clear error
    - No data corruption
    - Guidance for user to free space
    """
```

#### Test 5.5: Memory Pressure Handling
```python
def test_memory_pressure_handling(cortex_entry):
    """
    Test: Handle low memory condition
    
    Scenario:
    - Allocate memory until threshold (90% used)
    - Process large request (load all modules)
    
    Expected:
    - Graceful degradation (skip non-critical modules)
    - Or fail with clear memory error
    """
```

#### Test 5.6: Concurrent Database Access
```python
def test_concurrent_database_access(cortex_entry, brain_path):
    """
    Test: Handle concurrent writes to same database
    
    Scenario:
    - 10 threads writing to Tier 1 conversations.db
    - 5 threads writing to Tier 2 knowledge-graph.db
    
    Expected:
    - No database locks
    - All writes succeed (serialized)
    - No data corruption
    """
```

---

### Priority 6: Platform-Specific Tests (2-3 tests, 0.5 hour)

**File:** `tests/plugins/test_platform_edge_cases.py` (NEW)

#### Test 6.1: Path Handling Edge Cases
```python
def test_platform_path_handling_edge_cases(platform_switch_plugin):
    """
    Test: Handle edge cases in path resolution
    
    Edge cases:
    - Paths with spaces: "/Users/My Folder/CORTEX"
    - Paths with unicode: "/Users/José/CORTEX"
    - Paths with symlinks: "/Users/link → /real/path"
    - Windows UNC paths: "\\\\server\\share\\CORTEX"
    
    Expected: All paths resolved correctly per platform
    """
```

#### Test 6.2: Cross-Platform Line Ending Handling
```python
def test_cross_platform_line_endings(cortex_entry, brain_path):
    """
    Test: Handle different line endings gracefully
    
    Scenarios:
    - Unix files (LF) on Windows
    - Windows files (CRLF) on Mac
    - Mixed line endings in same file
    
    Expected: Parsing works regardless of line endings
    """
```

---

## ✅ Success Criteria

### Quantitative Metrics
- [ ] 25-30 new tests written (total: 762-767 tests)
- [ ] 100% pass rate maintained
- [ ] Test execution time < 60 seconds (full suite)
- [ ] Code coverage maintained >80%

### Qualitative Metrics
- [ ] All HIGH priority gaps addressed (cross-tier + entry point)
- [ ] At least 2 MEDIUM priority categories covered
- [ ] Tests follow existing naming conventions
- [ ] Tests include docstrings with clear scenarios
- [ ] Tests use proper fixtures and mocks

### Risk Mitigation
- [ ] No regressions in existing tests
- [ ] New tests catch real bugs (validate with intentional failures)
- [ ] Tests are deterministic (no flaky tests)
- [ ] Tests run on all platforms (Mac, Windows, Linux)

---

## 🗓️ Implementation Plan

### Session 1 (2-3 hours): Cross-Tier Integration
**File:** `tests/integration/test_cross_tier_workflows.py`
- [ ] Test 1.1: Complete Read Flow
- [ ] Test 1.2: Error Propagation
- [ ] Test 1.3: Write Coordination
- [ ] Test 1.4: Boundary Enforcement
- [ ] Test 1.5: Transaction Rollback
- [ ] Test 1.6: Data Consistency
- [ ] Test 1.7: Concurrent Access
- [ ] Test 1.8: Performance Under Load

**Validation:** Run `pytest tests/integration/test_cross_tier_workflows.py -v`

---

### Session 2 (1-2 hours): Entry Point & Plugins
**Files:** 
- `tests/integration/test_entry_point_integration.py`
- `tests/plugins/test_plugin_lifecycle.py`

**Entry Point Tests:**
- [ ] Test 2.1: Module Lazy Loading
- [ ] Test 2.2: Command Registry Routing
- [ ] Test 2.3: Natural Language Matching
- [ ] Test 2.4: Plugin Command Registration
- [ ] Test 2.5: Error Handling
- [ ] Test 2.6: Response Formatting

**Plugin Tests:**
- [ ] Test 4.1: Initialization Failure Isolation
- [ ] Test 4.2: Dependency Resolution
- [ ] Test 4.3: Command Conflict Detection

**Validation:** Run `pytest tests/integration/test_entry_point_integration.py tests/plugins/test_plugin_lifecycle.py -v`

---

### Session 3 (1 hour): Workflows & Edge Cases
**Files:** 
- `tests/workflows/test_workflow_edge_cases.py`
- `tests/integration/test_edge_cases.py`

**Workflow Tests:**
- [ ] Test 3.1: Checkpoint Resume
- [ ] Test 3.2: State Corruption Recovery
- [ ] Test 3.3: Concurrent Execution
- [ ] Test 3.4: Timeout Handling

**Edge Case Tests:**
- [ ] Test 5.1: Empty Input
- [ ] Test 5.2: Malformed JSON
- [ ] Test 5.3: Connection Exhaustion
- [ ] Test 5.4: Disk Space Exhaustion
- [ ] Test 5.5: Memory Pressure

**Validation:** Run `pytest tests/workflows/test_workflow_edge_cases.py tests/integration/test_edge_cases.py -v`

---

### Session 4 (0.5 hour): Platform-Specific + Final Validation
**File:** `tests/plugins/test_platform_edge_cases.py`

- [ ] Test 6.1: Path Handling Edge Cases
- [ ] Test 6.2: Line Ending Handling

**Final Validation:**
- [ ] Run full test suite: `pytest -v`
- [ ] Verify 100% pass rate
- [ ] Check execution time < 60s
- [ ] Update STATUS.md metrics

---

## 📊 Expected Outcomes

### Before Phase 5.1
- Total Tests: 737
- Test Files: 86
- Coverage: Unit (60%), Integration (25%), E2E (15%)
- Critical Gaps: 6 categories

### After Phase 5.1
- Total Tests: 762-767 (+25-30 new tests)
- Test Files: 91 (+5 new files)
- Coverage: Unit (57%), Integration (31%), E2E (12%)
- Critical Gaps: 2 categories (LOW priority only)

### Risk Reduction
- ✅ Cross-tier failures caught before production
- ✅ Entry point edge cases handled gracefully
- ✅ Workflow corruption detected early
- ✅ Plugin failures isolated
- ✅ Platform-specific issues prevented

---

## 🚨 Risks & Mitigation

### Risk 1: Test Suite Execution Time
**Impact:** Longer CI/CD pipelines  
**Likelihood:** MEDIUM  
**Mitigation:**
- Mark slow tests with `@pytest.mark.slow`
- Run in parallel where possible
- Target: Full suite < 60 seconds

### Risk 2: Flaky Tests
**Impact:** False positives in CI/CD  
**Likelihood:** LOW (due to mocking)  
**Mitigation:**
- Use deterministic mocks
- Avoid time-based assertions
- Run tests 10x locally before committing

### Risk 3: Platform-Specific Test Failures
**Impact:** Tests pass locally but fail in CI  
**Likelihood:** LOW  
**Mitigation:**
- Test on all platforms before push
- Use platform-agnostic paths (`Path` object)
- Mock platform-specific behavior

---

## 📝 Definition of Done

- [ ] All 25-30 tests implemented
- [ ] 100% pass rate on Mac, Windows, Linux
- [ ] Test execution time < 60 seconds
- [ ] Code review complete (self-review)
- [ ] Documentation updated (STATUS.md)
- [ ] Completion report created (PHASE-5.1-COMPLETION-REPORT.md)

---

## 📚 Related Documents

- **Status:** cortex-brain/cortex-2.0-design/STATUS.md
- **Roadmap:** cortex-brain/cortex-2.0-design/25-implementation-roadmap.md
- **Phase 3 Validation:** prompts/validation/PHASE-3-BEHAVIORAL-VALIDATION-COMPLETE.md
- **Brain Protection Tests:** tests/tier0/test_brain_protector.py (43 tests - example)

---

*Phase 5.1 Test Plan - Critical Integration & Edge Case Coverage*  
*Created: 2025-11-09 | Status: IN PROGRESS | Est. Duration: 4-6 hours*
