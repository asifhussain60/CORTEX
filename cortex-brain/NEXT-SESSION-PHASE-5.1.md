# Next Session: Phase 5.1 Critical Integration Tests - Ready to Go! 🚀

**Status:** ✅ READY - All prerequisites complete  
**Estimated Time:** 5-7 hours  
**Phase:** 5.1 - Critical Integration Tests (currently 40% complete)  
**Goal:** Design 15-20 tests, implement 10-15 tests, achieve 1,550+ total tests

---

## 📋 Quick Prep (27 minutes)

Before starting, review these documents:

1. **PHASE-5.1-COVERAGE-ANALYSIS.md** (10 min)
   - Read sections: "Identified Gaps" and "Recommended Test Additions"
   - Focus on 7 critical gap areas

2. **tests/integration/test_cross_tier_workflows.py** (10 min)
   - Review fixture patterns (brain_path, cortex_entry)
   - Study test structure and assertions
   - Note how tier coordination is tested

3. **SELF-REVIEW-2025-11-09-PHASE-5.1.md** (5 min)
   - Review "Lessons Learned" section
   - Note import consistency patterns
   - Review fixture setup requirements

4. **Health Check** (2 min)
   ```bash
   cd /Users/asifhussain/PROJECTS/CORTEX
   python3 -m pytest tests/ --collect-only -q | tail -5
   # Should show: 1526 tests collected
   ```

---

## 🎯 Session Flow (Hour by Hour)

### Hour 1: Design Phase (Test Specifications) 📝

**Deliverable:** `tests/integration/PHASE-5.1-TEST-DESIGN.md`

**Tasks:**
1. Create test design document (30 min)
   - List 15-20 test names with descriptions
   - Define success criteria for each
   - Identify mock/fixture requirements
   - Prioritize high → medium → low

2. Review design against gaps (15 min)
   - Cross-check with PHASE-5.1-COVERAGE-ANALYSIS.md
   - Ensure all 7 gap areas addressed
   - Validate test distribution (5-7 end-to-end, 5-6 agent coordination, etc.)

3. Get approval/validation (15 min)
   - Self-review design
   - Check against TDD principles
   - Ensure tests are independent and isolated

**Output:** Approved test design ready for implementation

---

### Hour 2-3: End-to-End User Workflows (HIGH PRIORITY) 🎯

**Target:** Implement 3-5 tests

**Test 1: `test_add_authentication_full_workflow`** (45 min)
```python
def test_add_authentication_full_workflow(cortex_entry):
    """
    Test: User requests "Add authentication to the app"
    Expected: Plan → Implement → Test → Document workflow
    Validates: Multi-agent handoff, tier coordination
    """
    # RED: Write failing test first
    response = cortex_entry.process("Add authentication to the app")
    
    # Assertions:
    # - Intent detected as PLAN
    # - WorkPlanner agent invoked
    # - Plan saved to Tier 2
    # - Context injected from Tier 1
    
    # GREEN: Implement minimal code to pass
    # REFACTOR: Improve and validate
```

**Test 2: `test_continue_work_session_resume`** (45 min)
```python
def test_continue_work_session_resume(cortex_entry):
    """
    Test: User says "Continue work on exports"
    Expected: Resume previous session, context carried over
    Validates: Session management, conversation memory
    """
    # Setup: Create previous conversation
    # Execute: Resume with "Continue work"
    # Validate: Previous context injected
```

**Test 3: `test_fix_bug_debug_workflow`** (30 min)
```python
def test_fix_bug_debug_workflow(cortex_entry):
    """
    Test: User reports "Fix bug in login form"
    Expected: Analyze → Fix → Validate → Test
    Validates: Error recovery, code analysis
    """
    # Similar structure to test 1
```

**After Each Test:**
- ✅ Run individually: `pytest tests/integration/test_phase_5_1.py::test_name -v`
- ✅ Run full suite: `pytest tests/ -q | tail -10`
- ✅ Commit if passing: `git commit -m "Add test: test_name"`

---

### Hour 4-5: Multi-Agent Coordination (HIGH PRIORITY) 🤖

**Target:** Implement 3-5 tests

**Test 4: `test_plan_to_execute_handoff`** (40 min)
```python
def test_plan_to_execute_handoff(cortex_entry):
    """
    Test: WorkPlanner → Executor handoff
    Validates: Agent context passing
    """
    # Mock WorkPlanner response
    # Execute request that requires execution
    # Validate Executor receives WorkPlanner context
```

**Test 5: `test_execute_to_test_handoff`** (40 min)
**Test 6: `test_agent_context_passing`** (40 min)

**After Each Test:**
- Same validation process as above

---

### Hour 6: Session Boundary Management (MEDIUM PRIORITY) ⏱️

**Target:** Implement 2-3 tests

**Test 7: `test_30_minute_timeout_enforcement`** (30 min)
```python
def test_30_minute_timeout_enforcement(cortex_entry):
    """
    Test: New session created after 30 min idle
    Validates: Session timeout logic
    """
    # Create session
    # Simulate 30+ min idle
    # Validate new session created
    # Validate conversation_id preserved
```

**Test 8: `test_session_resume_preserves_conversation_id`** (30 min)

---

### Hour 7: Validation & Documentation (FINAL) 📊

**Tasks:**

1. **Run Full Test Suite** (10 min)
   ```bash
   pytest tests/ -v --tb=short
   # Target: 1,540-1,550 tests, 100% pass rate
   ```

2. **Update Metrics** (15 min)
   - Update STATUS.md with new test count
   - Update Phase 5.1 progress (40% → 70-80%)
   - Document any issues encountered

3. **Create Session Summary** (20 min)
   - List tests implemented
   - Document patterns discovered
   - Note any technical debt
   - Identify remaining work for Phase 5.1

4. **Commit & Push** (15 min)
   ```bash
   git add tests/integration/test_phase_5_1.py
   git add cortex-brain/cortex-2.0-design/STATUS.md
   git commit -m "Phase 5.1: Implement 10-15 critical integration tests"
   git push origin CORTEX-2.0
   ```

---

## 📊 Success Criteria

**Must Achieve:**
- ✅ 15-20 tests designed (design document)
- ✅ 10-15 tests implemented (code written)
- ✅ 100% pass rate (no failures)
- ✅ 1,540+ total tests (from 1,526)
- ✅ 3-4 gap areas addressed

**Nice to Have:**
- ✅ All 15-20 tests implemented (if time permits)
- ✅ 1,550 total tests achieved
- ✅ All 7 gap areas partially addressed

---

## 🚨 Troubleshooting Guide

### Issue: Import Errors
**Solution:** Always use absolute imports: `from src.module`

### Issue: Fixture Failures
**Solution:** Create tier subdirectories:
```python
brain = Path(tmpdir)
(brain / "tier1").mkdir(parents=True)
(brain / "tier2").mkdir(parents=True)
(brain / "tier3").mkdir(parents=True)
```

### Issue: Database Errors
**Solution:** Use temporary directories for each test:
```python
with tempfile.TemporaryDirectory() as tmpdir:
    # Test code here
```

### Issue: Tests Interfering
**Solution:** Ensure fixtures yield inside `with` block:
```python
with tempfile.TemporaryDirectory() as tmpdir:
    entry = CortexEntry(brain_path=str(brain))
    yield entry  # Inside with block!
```

---

## 🎓 Key Patterns (From Today's Session)

### Pattern 1: Fixture Setup
```python
@pytest.fixture
def cortex_entry():
    with tempfile.TemporaryDirectory() as tmpdir:
        brain = Path(tmpdir)
        (brain / "tier1").mkdir(parents=True)
        (brain / "tier2").mkdir(parents=True)
        (brain / "tier3").mkdir(parents=True)
        
        entry = CortexEntry(brain_path=str(brain), enable_logging=False)
        
        # Optional: Mock dependencies
        entry.router.execute = Mock(...)
        
        yield entry
```

### Pattern 2: TDD Cycle
```python
# 1. RED: Write failing test
def test_feature():
    result = function_under_test()
    assert result == expected  # Fails initially

# 2. GREEN: Minimal implementation
def function_under_test():
    return expected  # Just enough to pass

# 3. REFACTOR: Improve
def function_under_test():
    # Proper implementation
    return calculated_result
```

### Pattern 3: Integration Test Structure
```python
def test_integration_scenario(cortex_entry, brain_path):
    """
    Test: User action
    Expected: System behavior
    Validates: Specific aspect
    """
    # Setup: Create necessary data in tiers
    tier1 = cortex_entry.tier1
    tier1.start_conversation("test")
    
    # Execute: Process user request
    response = cortex_entry.process("user request")
    
    # Validate: Check all tiers updated
    assert response is not None
    assert tier1.get_summary()['total_conversations'] > 0
```

---

## 🏁 Ready to Start!

**Current State:**
- ✅ 1,526 tests (0 errors)
- ✅ All entry point tests passing
- ✅ Coverage gaps documented
- ✅ Patterns learned and documented

**Next Action:**
1. Run health check (2 min)
2. Review prep documents (25 min)
3. Start Hour 1: Design Phase (60 min)

**Expected End State:**
- ✅ 1,540-1,550 tests (+14-24 tests)
- ✅ 70-80% Phase 5.1 complete
- ✅ 3-4 critical gaps addressed
- ✅ Foundation for Phase 5.3 established

---

**Let's build some excellent integration tests! 🚀**

*Created: 2025-11-09 (Evening)*  
*For: Next CORTEX development session*  
*Phase: 5.1 - Critical Integration Tests*
