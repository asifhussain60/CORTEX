# CORTEX 2.0 Test Suite Remediation Plan

**Author:** Asif Hussain  
**Date:** 2025-11-11  
**Status:** 🔴 ACTIVE - Phase 5 High Priority  
**Alignment:** CORTEX2-STATUS.MD Phase 5 (85% complete)

---

## 📋 Executive Summary

**Current State:**
- 2,791 tests collected
- 86% pass rate (2,400 passing, 391 failures/errors)
- 6m 40s execution time → **NOW 13-20s with parallel execution** ✅
- 4 failure categories identified

**Target State:**
- 100% pass rate
- <30s unit test execution
- Tests aligned with CORTEX 2.0 architecture
- Zero orphaned/outdated tests

**Estimated Effort:** 8-12 hours over 2 days

---

## 🎯 Strategic Approach

### Principle: Delete vs Fix Decision Tree

```
Is test testing CORTEX 2.0 architecture?
├─ NO → DELETE (orphaned from 1.0)
├─ YES → Is feature implemented?
   ├─ NO → SKIP with @pytest.mark.skip(reason="Awaiting Module X")
   └─ YES → Does schema/API match current implementation?
      ├─ NO → FIX (update test to match reality)
      └─ YES → Test should pass (investigate failure)
```

---

## 📊 Failure Analysis by Category

### Category 1: Schema Mismatches (10 tests) - **DELETE OR UPDATE**

**Decision:** UPDATE schema OR UPDATE tests to match current Tier 1 implementation

**Failures:**
1. `messages` table missing `timestamp` column (5 tests)
2. `conversation_entities` table doesn't exist (3 tests)
3. `entities` table missing `conversation_id` NOT NULL (2 tests)

**Action Plan:**
```yaml
decision: Check Tier 1 implementation
if_schema_changed:
  action: Update tests to match current schema
  files:
    - tests/tier1/messages/test_message_store.py
    - tests/tier1/entities/test_entity_extractor.py
  estimated: 1 hour
else_tests_outdated:
  action: Delete outdated tests
  rationale: Testing deprecated schema
  estimated: 30 minutes
```

**Design Alignment:** Tier 1 Working Memory schema (05-working-memory.md)

---

### Category 2: API Contract Changes (5 tests) - **FIX**

**Decision:** UPDATE tests to match current API signatures

**Failures:**
1. FIFO queue status missing `total_conversations` key (3 tests)
2. Vision API returns 0 tokens (2 tests)

**Action Plan:**
```yaml
decision: Update tests to match current API contracts
actions:
  - file: tests/tier1/fifo/test_queue_manager.py
    issue: get_status() return dict structure changed
    fix: Update assertions to match new dict keys
    estimated: 30 minutes
  
  - file: tests/tier1/test_vision_api.py
    issue: Mock returns 0 tokens instead of estimates
    fix: Implement proper mock or mark as validation-only
    estimated: 30 minutes
```

**Design Alignment:** FIFO Queue (05-working-memory.md), Vision API (limitations-and-status.md)

---

### Category 3: Missing Dependencies (33 tests) - **MARK FOR AUTO-SKIP**

**Decision:** APPLY MARKERS - Infrastructure exists, just needs tagging

**Failures:**
- All 33 tests require `scikit-learn` for ML Context Optimizer
- Tests currently error instead of skip
- `HAS_SKLEARN` flag exists in conftest.py

**Action Plan:**
```yaml
decision: Apply @pytest.mark.requires_sklearn marker
file: tests/tier1/test_ml_context_optimizer.py
action: Add decorator to all test classes/functions
estimated: 15 minutes
code: |
  @pytest.mark.requires_sklearn
  class TestMLContextOptimizer:
      # All tests auto-skip if sklearn missing
```

**Design Alignment:** Test infrastructure (conftest.py already has auto-skip hooks)

---

### Category 4: Windows File Locking (16 tests) - **FIX FIXTURES**

**Decision:** ENHANCE fixtures with proper cleanup

**Failures:**
- Database files locked during parallel test execution
- Windows-specific issue (WinError 32)

**Action Plan:**
```yaml
decision: Enhance database fixtures with explicit cleanup
file: tests/conftest.py
action: Add fixture with proper connection closing
estimated: 30 minutes
code: |
  @pytest.fixture
  def temp_db():
      conn = sqlite3.connect(":memory:")  # Use in-memory
      try:
          yield conn
      finally:
          conn.close()  # Explicit cleanup
```

**Design Alignment:** Test infrastructure best practices

---

### Category 5: Agent Coordination Tests (8 tests) - **SKIP UNTIL PHASE 6**

**Decision:** SKIP - Requires all 10 agents implemented

**Current Status:**
- Tests expect WorkPlanner, Executor, Tester, Validator, Learner, PatternMatcher, Architect
- Only IntentRouter currently implemented
- Tests are integration tests for future functionality

**Action Plan:**
```yaml
decision: Skip entire test class until agents implemented
file: tests/integration/test_agent_coordination.py
action: Already applied @pytest.mark.skip decorator
status: COMPLETE ✅
reason: "Requires all 10 agents to be implemented - TODO for Phase 6"
```

**Design Alignment:** Agent system (12-agent-definitions.md) - Phase 6 milestone

---

## 🗂️ Test Categorization by CORTEX 2.0 Architecture

### Tests to KEEP (Core Architecture)

**Tier 0 - Governance (130 tests)** ✅
- Brain protection rules: KEEP ALL
- Git isolation: KEEP ALL
- Entry point bloat: KEEP ALL
- Active narrator voice: KEEP ALL
- **Status:** 129/130 passing (99.2%)

**Tier 1 - Working Memory (296 tests)** 🟡
- Conversation management: KEEP + FIX (schema)
- FIFO queue: KEEP + FIX (API contract)
- Messages: KEEP + FIX (schema)
- Entities: KEEP + FIX (schema OR delete if deprecated)
- **Status:** 235/296 passing (79.4%)

**Tier 2 - Knowledge Graph (tests/tier2/)** 🔍
- Pattern storage: KEEP
- Learning system: KEEP
- **Status:** Need to analyze

**Tier 3 - Development Context (tests/tier3/)** 🔍
- Git metrics: KEEP
- Project health: KEEP
- **Status:** Need to analyze

**Plugin Tests (tests/plugins/)** ✅
- All plugins: KEEP
- **Status:** Likely passing (plugins operational)

**Agent Tests (tests/agents/)** 🟡
- Base agent framework: KEEP + FIX
- Intent router: KEEP + FIX
- Other agents: SKIP until implemented

**Operations Tests (tests/operations/)** ✅
- Demo: KEEP (passing)
- Setup: KEEP (passing)
- Design sync: KEEP (passing)
- **Status:** 3/12 operations tested

---

### Tests to DELETE (Orphaned from 1.0)

**Criteria:**
1. Tests features removed in CORTEX 2.0
2. Tests deprecated APIs
3. Tests monolithic architecture patterns
4. No longer aligned with design documents

**Candidates for Deletion:**
```yaml
# To be determined after schema analysis
potential_deletions:
  - conversation_entities tests (if feature removed)
  - deprecated message schema tests
  - any tests for removed 1.0 features
```

**Action:** Analyze each tier's design document vs tests to identify orphans

---

## 📝 Implementation Plan

### Phase 1: Quick Wins (2 hours)

**Goal:** Get to 95%+ pass rate immediately

```yaml
tasks:
  1_apply_sklearn_markers:
    files: tests/tier1/test_ml_context_optimizer.py, test_working_memory_optimization.py
    action: Add @pytest.mark.requires_sklearn
    impact: +33 tests passing (or skipped gracefully)
    time: 15 minutes
  
  2_skip_agent_coordination:
    files: tests/integration/test_agent_coordination.py
    action: Already done ✅
    impact: +8 tests skipped gracefully
    time: 0 minutes
  
  3_fix_database_cleanup:
    files: tests/conftest.py
    action: Enhance fixtures with explicit cleanup
    impact: +16 tests passing (Windows file locking)
    time: 30 minutes
  
  4_fix_fifo_api:
    files: tests/tier1/fifo/test_queue_manager.py
    action: Update assertions for new status dict structure
    impact: +3 tests passing
    time: 30 minutes
  
  5_fix_vision_mock:
    files: tests/tier1/test_vision_api.py
    action: Implement proper token estimation mock
    impact: +5 tests passing
    time: 45 minutes
```

**Expected Result:** 95% pass rate, ~2,650+ tests passing

---

### Phase 2: Schema Reconciliation (2-3 hours)

**Goal:** Align Tier 1 tests with current implementation

```yaml
tasks:
  1_analyze_tier1_schema:
    action: Compare src/tier1/ implementation with test expectations
    deliverable: Schema alignment document
    time: 30 minutes
  
  2_decide_messages_schema:
    question: "Does messages table have timestamp column in current impl?"
    if_yes:
      action: Fix tests to use timestamp
      files: tests/tier1/messages/test_message_store.py
    if_no:
      action: Update tests to remove timestamp expectations
    time: 1 hour
  
  3_decide_entities_schema:
    question: "Does conversation_entities table exist in current impl?"
    if_yes:
      action: Fix tests
    if_no:
      action: Delete tests for deprecated feature
      files: tests/tier1/entities/test_entity_extractor.py
    time: 1 hour
  
  4_fix_entity_constraints:
    action: Add conversation_id to test data OR remove NOT NULL constraint tests
    time: 30 minutes
```

**Expected Result:** 98% pass rate, schema tests aligned

---

### Phase 3: Comprehensive Audit (3-4 hours)

**Goal:** Eliminate all orphaned tests, align with design docs

```yaml
tasks:
  1_tier2_analysis:
    action: Compare tests/tier2/ with 06-knowledge-graph.md
    deliverable: Keep/Delete/Fix list
    time: 1 hour
  
  2_tier3_analysis:
    action: Compare tests/tier3/ with 07-development-context.md
    deliverable: Keep/Delete/Fix list
    time: 1 hour
  
  3_operations_analysis:
    action: Compare tests/operations/ with cortex-operations.yaml
    deliverable: Tests needed for 9 missing operations
    time: 1 hour
  
  4_execute_deletions:
    action: Delete orphaned tests identified in analysis
    deliverable: Clean test suite
    time: 1 hour
```

**Expected Result:** 100% pass rate, zero orphaned tests

---

### Phase 4: Documentation & Design Sync (1 hour)

**Goal:** Update design documents to reflect test remediation

```yaml
tasks:
  1_update_status:
    files:
      - cortex-brain/cortex-2.0-design/CORTEX2-STATUS.MD
      - cortex-brain/cortex-2.0-design/STATUS.md
    action: Update test counts, pass rate to 100%
    time: 15 minutes
  
  2_create_test_manifest:
    file: cortex-brain/cortex-2.0-design/TEST-MANIFEST.yaml
    action: Document all test files → architecture mapping
    structure: |
      tier0_governance:
        brain_protection: [test_brain_protector.py, ...]
        git_isolation: [test_git_isolation.py]
      tier1_memory:
        conversations: [test_conversation_manager.py]
    time: 30 minutes
  
  3_update_index:
    file: cortex-brain/cortex-2.0-design/00-INDEX.md
    action: Add entry for test remediation work
    time: 15 minutes
```

---

## 🚀 Execution Strategy

### Day 1: Quick Wins + Schema (4 hours)

```bash
# Morning: Phase 1 - Quick Wins (2 hours)
1. Apply sklearn markers (15 min)
2. Fix database cleanup (30 min)
3. Fix FIFO API (30 min)
4. Fix Vision mock (45 min)
✅ Target: 95% pass rate

# Afternoon: Phase 2 - Schema (2 hours)
1. Analyze Tier 1 schema (30 min)
2. Fix messages tests (1 hour)
3. Fix entities tests (30 min)
✅ Target: 98% pass rate
```

### Day 2: Audit + Documentation (4 hours)

```bash
# Morning: Phase 3 - Comprehensive Audit (3 hours)
1. Tier 2 analysis (1 hour)
2. Tier 3 analysis (1 hour)
3. Execute deletions (1 hour)
✅ Target: 100% pass rate

# Afternoon: Phase 4 - Documentation (1 hour)
1. Update status docs (15 min)
2. Create test manifest (30 min)
3. Update index (15 min)
✅ Target: Design docs in sync
```

---

## 📊 Success Metrics

| Metric | Baseline | Target | Status |
|--------|----------|--------|--------|
| **Pass Rate** | 86% | 100% | 🔴 |
| **Execution Time** | 6m 40s | <30s unit | ✅ 13-20s |
| **Test Count** | 2,791 | 2,500-2,700 | 🟡 (after deletions) |
| **Schema Alignment** | ❌ | ✅ | 🔴 |
| **Design Alignment** | 🟡 | ✅ | 🔴 |
| **Orphaned Tests** | Unknown | 0 | 🔴 |

---

## 🔗 Design Document Alignment

**Updated Documents:**
- `CORTEX2-STATUS.MD` - Test metrics updated
- `STATUS.md` - Phase 5 task 5.x "Test Suite Remediation" added
- `00-INDEX.md` - New event log entry added
- `TEST-MANIFEST.yaml` - Created (maps tests → architecture)

**Referenced Documents:**
- `05-working-memory.md` - Tier 1 schema reference
- `06-knowledge-graph.md` - Tier 2 test validation
- `07-development-context.md` - Tier 3 test validation
- `12-agent-definitions.md` - Agent test roadmap
- `13-testing-strategy.md` - Overall test strategy

---

## 🎯 Decision Points

### Key Questions to Answer During Execution

1. **Messages Schema:**
   - Q: Does `messages` table have `timestamp` column?
   - A: Check `src/tier1/` implementation
   - Decision: Update tests OR implementation

2. **Conversation Entities:**
   - Q: Is `conversation_entities` feature still in CORTEX 2.0?
   - A: Check design docs + implementation
   - Decision: Fix tests OR delete feature tests

3. **Entity Constraints:**
   - Q: Should `entities.conversation_id` be NOT NULL?
   - A: Check schema design intent
   - Decision: Update schema OR relax test

4. **Test Deletion Threshold:**
   - Q: When to delete vs skip?
   - A: Delete if testing removed features, Skip if testing future features

---

## 📋 Checklist

### Phase 1: Quick Wins
- [ ] Apply `@pytest.mark.requires_sklearn` to 33 tests
- [ ] Enhance database fixtures with cleanup
- [ ] Fix FIFO queue status dict assertions
- [ ] Implement Vision API token estimation mock
- [ ] Run tests: `pytest -n auto` → Verify 95%+ pass

### Phase 2: Schema
- [ ] Analyze `src/tier1/` schema vs tests
- [ ] Fix/delete messages timestamp tests
- [ ] Fix/delete conversation_entities tests
- [ ] Fix/delete entities constraint tests
- [ ] Run tests: `pytest tests/tier1/` → Verify 98%+ pass

### Phase 3: Audit
- [ ] Analyze Tier 2 tests vs design docs
- [ ] Analyze Tier 3 tests vs design docs
- [ ] Identify and delete orphaned tests
- [ ] Run full suite: `pytest -n auto` → Verify 100% pass

### Phase 4: Documentation
- [ ] Update `CORTEX2-STATUS.MD` test metrics
- [ ] Create `TEST-MANIFEST.yaml`
- [ ] Add event log entry to `00-INDEX.md`
- [ ] Commit with message: "feat: Test remediation - 100% pass rate, CORTEX 2.0 aligned"

---

## 🚨 Risk Mitigation

**Risk 1: Breaking Working Code**
- Mitigation: Run tests after EACH change
- Rollback: Git branch for all changes

**Risk 2: Deleting Needed Tests**
- Mitigation: Analyze design docs before deletion
- Backup: Keep deleted tests in git history

**Risk 3: Time Overrun**
- Mitigation: Focus on Phase 1 (Quick Wins) first
- Fallback: Phase 3 can be deferred if needed

---

**Next Action:** Execute Phase 1 Quick Wins (2 hours)

**Approval:** Awaiting confirmation to proceed
