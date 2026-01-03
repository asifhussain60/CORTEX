# 🔍 Brittleness & Acceptance Criteria Gap Analysis

**Plan ID:** cortex-v5-holistic-refactor  
**Analysis Date:** January 3, 2026  
**Author:** CORTEX Brittleness Validator  
**Status:** 🔴 GAPS IDENTIFIED - Action Required

---

## 📋 Executive Summary

**Overall Status:** Implementation is **43% complete** with **significant gaps** in acceptance criteria validation, test coverage, and brittleness mitigation.

**Key Findings:**
- ✅ **Bootstrap Phase (Phases 0-4.5):** Strong implementation, but missing formal acceptance validation
- ⚠️ **Test Coverage:** Implementation exists but no formal acceptance criteria test execution
- 🔴 **Migration Phase (Phases 6.3-10):** Not yet started - majority of brittleness still present
- 🔴 **REFACTOR Phase (Phase 10):** Critical - No implementation of 18+ cleanup tasks yet

**Brittleness Remaining:** 5 out of 7 critical brittleness categories still present in unimplemented orchestrators (Vacuum, Sanitization, Debug, Refinement, CORTEX Lens).

---

## 🎯 Section 1: Master Orchestrator - Acceptance Validation

### 1.1 Pattern-Based Routing (MO-1.1.*)

| Criterion ID | Status | Evidence | Gap |
|--------------|--------|----------|-----|
| **MO-1.1.1** | ✅ IMPLEMENTED | `PatternRouter` class with regex engine | ❌ No formal test validating ≥90% match rate |
| **MO-1.1.2** | ✅ IMPLEMENTED | Planning patterns in `master-orchestrator.yaml` | ❌ No test suite with 100% detection accuracy metric |
| **MO-1.1.3** | ✅ IMPLEMENTED | Implementation patterns differentiated | ❌ No 100% correct routing validation test |
| **MO-1.1.4** | ✅ IMPLEMENTED | `CrossSessionContextMiddleware` with continuation detection | ❌ No 100% continuation detection test |
| **MO-1.1.5** | ⚠️ PARTIAL | LLM fallback exists but not integrated | ⚠️ No test for <10% fallback trigger rate |

**Evidence Found:**
```python
# src/orchestrators/pattern_router.py (lines 71-340)
class PatternRouter:
    """Machine-readable pattern matching engine"""
    def match_intent(self, user_input: str) -> OrchestratorMatch:
        # Exact and regex matching implemented
```

**Gap Summary:**
- ✅ Core functionality implemented
- 🔴 **Missing:** Formal acceptance test suite (`tests/orchestrators/test_master_orchestrator.py` exists but no validation against acceptance criteria)
- 🔴 **Missing:** Performance metrics collection (match rate, accuracy)
- 🔴 **Missing:** Test report generation comparing actual vs. acceptance targets

**Recommendation:** **Add Task 6.2.1 to Plan** - Create acceptance validation test suite for Master Orchestrator

---

### 1.2 Orchestrator Lifecycle Management (MO-1.2.*)

| Criterion ID | Status | Evidence | Gap |
|--------------|--------|----------|-----|
| **MO-1.2.1** | ⚠️ PARTIAL | Pre-execution hooks in `ExecutionEngine` | ⚠️ No workspace validation logic |
| **MO-1.2.2** | ❌ NOT IMPLEMENTED | No git checkpoint creation | 🔴 Post-execution hooks missing |
| **MO-1.2.3** | ⚠️ PARTIAL | Error handling exists | ⚠️ No artifact cleanup on error |
| **MO-1.2.4** | ✅ IMPLEMENTED | `StateManager` with `PlanningStateDB` | ✅ Cross-orchestrator state sharing works |
| **MO-1.2.5** | ✅ IMPLEMENTED | Metrics tracking in `MasterOrchestrator` | ❌ No formal test asserting metric accuracy |

**Evidence Found:**
```python
# src/orchestrators/master_orchestrator.py (lines 85-90)
self._request_count = 0
self._pattern_match_count = 0
self._llm_fallback_count = 0
self._continuation_count = 0
```

**Gap Summary:**
- ⚠️ **CRITICAL GAP:** No git checkpoint enforcement (SKULL rule `GIT_CHECKPOINT_ENFORCEMENT`)
- 🔴 **Missing:** Pre-execution workspace validation
- 🔴 **Missing:** Error cleanup hooks
- 🔴 **Missing:** Lifecycle test suite

**Recommendation:** **Add Task 7.1 to Plan** - Implement orchestrator lifecycle hooks (pre-execution, post-execution, error cleanup)

---

### 1.3 Cross-Session Context Middleware (MO-1.3.*)

| Criterion ID | Status | Evidence | Gap |
|--------------|--------|----------|-----|
| **MO-1.3.1** | ✅ IMPLEMENTED | Tier 1 integration with <200 token limit | ❌ No token counter validation test |
| **MO-1.3.2** | ✅ IMPLEMENTED | Project-level continuation fallback | ❌ No test validating Planning v5 routing |
| **MO-1.3.3** | ✅ IMPLEMENTED | Priority logic (orchestrator > project) | ❌ No dual context test |
| **MO-1.3.4** | ✅ IMPLEMENTED | Continuation patterns in `CONTINUATION_PATTERNS` | ❌ No 100% detection rate test |
| **MO-1.3.5** | ✅ IMPLEMENTED | Context injection with metadata only | ❌ No structure validation test |

**Evidence Found:**
```python
# src/orchestrators/context_middleware.py (lines 58-66)
CONTINUATION_PATTERNS = [
    r'\bcontinue\b',
    r'\bresume\b',
    r'\bkeep going\b',
    r'\bnext phase\b',
    # ... 8 patterns total
]
```

**Gap Summary:**
- ✅ Implementation solid
- 🔴 **Missing:** Formal acceptance test suite (`tests/middleware/test_cross_session_context.py` required)
- 🔴 **Missing:** Token counting validation
- 🔴 **Missing:** Context structure schema validation

**Recommendation:** **Add Task 6.2.2 to Plan** - Create cross-session context acceptance validation tests

---

## 🧠 Section 2: Planning System Orchestrator - Acceptance Validation

### 2.1 Folder Structure Creation (PS-2.1.*)

| Criterion ID | Status | Evidence | Gap |
|--------------|--------|----------|-----|
| **PS-2.1.1** | ✅ IMPLEMENTED | Planning v5 creates 4 subfolders | ✅ Validated in plan execution |
| **PS-2.1.2** | ✅ IMPLEMENTED | `file_name.py` utility enforces sanitization | ✅ 50 tests, 99.15% coverage |
| **PS-2.1.3** | ✅ IMPLEMENTED | Path follows `cortex-brain/documents/planning/active/` | ✅ Correct structure observed |
| **PS-2.1.4** | ✅ IMPLEMENTED | Subfolders: context/, reports/, artifacts/, tracking/ | ✅ All present in current plan |
| **PS-2.1.5** | ⚠️ PARTIAL | `00-MASTER-PLAN-V5.md` exists | ⚠️ Naming should be `00-master-plan.md` (lowercase) |

**Gap Summary:**
- ✅ Strong implementation
- ⚠️ **Minor Gap:** Filename casing inconsistency (`00-MASTER-PLAN-V5.md` vs. `00-master-plan.md`)
- 🔴 **Missing:** Formal filesystem assertion test suite

**Recommendation:** **Add Task 6.2.3 to Plan** - Standardize plan filename casing and create validation tests

---

### 2.2 Mandatory Plan Content (PS-2.2.*)

| Criterion ID | Status | Evidence | Gap |
|--------------|--------|----------|-----|
| **PS-2.2.1** | ✅ IMPLEMENTED | Visual progress tracking present | ✅ Lines 15-43 of 00-MASTER-PLAN-V5.md |
| **PS-2.2.2** | ❌ NOT FOUND | Response template reminder | 🔴 No reference to `response-templates-v4.yaml:863` |
| **PS-2.2.3** | ✅ IMPLEMENTED | Final REFACTOR phase exists | ✅ Phase 10 in plan |
| **PS-2.2.4** | ❌ NOT FOUND | `copilot_instructions` block | 🔴 Missing from 00-MASTER-PLAN-V5.md |
| **PS-2.2.5** | ❌ NOT VALIDATED | REFACTOR phase cleanup tasks | 🔴 Phase 10 not yet executed - can't verify ≥18 tasks |

**Gap Summary:**
- ⚠️ **CRITICAL GAP:** Missing mandatory content blocks (response template reminder, copilot_instructions)
- 🔴 **SKULL VIOLATION:** `PROGRESS_TRACKER_ENFORCEMENT` and `REFACTOR_CODE_CLEANUP_ENFORCEMENT` not fully compliant

**Recommendation:** **URGENT - Add Task 6.2.4 to Plan** - Update 00-MASTER-PLAN-V5.md with missing mandatory content

**Required Additions:**
```markdown
## 🎯 Response Template Reference

**Template:** `response-templates-v4.yaml:863` (autonomous_execution_progress)

---

## 🤖 Copilot Instructions

```yaml
copilot_instructions:
  response_template: "autonomous_execution_progress"
  tdd_enforcement: true
  final_refactor_required: true
  refactor_task_minimum: 18
```
```

---

### 2.3 Governance Integration (PS-2.3.*)

| Criterion ID | Status | Evidence | Gap |
|--------------|--------|----------|-----|
| **PS-2.3.1** | ❌ NOT FOUND | Phase -1 "Knowledge Library" | 🔴 Missing from current plan |
| **PS-2.3.2** | ❌ N/A | Phase -1 execution order | 🔴 N/A - Phase -1 doesn't exist |
| **PS-2.3.3** | ❌ NOT FOUND | Knowledge Library consultation artifact | 🔴 `context/knowledge-library-findings.md` missing |
| **PS-2.3.4** | ❌ N/A | Phase -1 task count | 🔴 N/A - Phase -1 doesn't exist |
| **PS-2.3.5** | ❌ NOT FOUND | DoD includes Knowledge Library review | 🔴 Missing from phase DoDs |

**Gap Summary:**
- 🔴 **CRITICAL GAP:** Phase -1 (Knowledge Library Consultation) completely missing
- 🔴 **SKULL VIOLATION:** `KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT` not implemented

**Recommendation:** **URGENT - Add Task 6.2.5 to Plan** - Insert Phase -1 Knowledge Library Consultation into planning workflow

**Required Phase -1 Structure:**
```markdown
## Phase -1: Knowledge Library Consultation

**Duration:** 1 hour  
**Purpose:** Consult existing knowledge before new work

### Tasks
1. Query Tier 2 knowledge graph for "orchestrator brittleness" patterns
2. Review `lessons-learned.yaml` for similar architectural refactors
3. Check `TRUTH-SOURCES.yaml` for authoritative references (BaseOrchestrator v4.1, Master Orchestrator design)
4. Query brain-protection-rules.yaml for applicable SKULL rules
5. Document findings in `context/knowledge-library-findings.md`

### Definition of Done
- [ ] Knowledge Library reviewed
- [ ] ≥3 relevant patterns identified
- [ ] Findings documented
- [ ] Lessons learned applied to plan phases
```

---

### 2.4 AST Scanning During Planning (PS-2.4.*)

| Criterion ID | Status | Evidence | Gap |
|--------------|--------|----------|-----|
| **PS-2.4.1** | ❌ NOT IMPLEMENTED | AST scan in Phase 0 | 🔴 No AST scanning during plan creation |
| **PS-2.4.2** | ❌ NOT IMPLEMENTED | Scan results schema | 🔴 No JSON output with function/class counts |
| **PS-2.4.3** | ❌ NOT IMPLEMENTED | Duplicate code detection | 🔴 No duplicate detection in planning |
| **PS-2.4.4** | ❌ NOT IMPLEMENTED | Orphaned code detection | 🔴 No orphaned function identification |
| **PS-2.4.5** | ❌ NOT IMPLEMENTED | AST findings artifact | 🔴 `context/ast-analysis.json` missing |

**Gap Summary:**
- 🔴 **CRITICAL GAP:** AST scanning not integrated into Planning System v5
- 🔴 **SKULL VIOLATION:** `HOLISTIC_CODE_DISCOVERY_ENFORCEMENT` not implemented

**Recommendation:** **Add Phase 6.4 to Plan** - Integrate AST Scanning into Planning System v5

**Implementation Requirements:**
1. Create `src/cortex_agents/ast_scanner.py` (300-500 lines)
2. Add Phase 0 task: "Run AST scan on workspace"
3. Generate `context/ast-analysis.json` with schema per acceptance criteria
4. Surface findings in plan (duplicates, orphans, complexity)

---

## 🧪 Section 3: TDD Mastery Orchestrator - Acceptance Validation

**Status:** ⚠️ TDD Orchestrator exists but not migrated to v5 pure autonomous architecture yet.

### 3.1 TDD Cycle Enforcement (TDD-3.1.*)

| Criterion ID | Status | Evidence | Gap |
|--------------|--------|----------|-----|
| **TDD-3.1.1** | ⚠️ PARTIAL | TDD workflow exists | ⚠️ No automated RED phase validation |
| **TDD-3.1.2** | ⚠️ PARTIAL | GREEN phase works | ⚠️ No complexity metric enforcement |
| **TDD-3.1.3** | ⚠️ PARTIAL | GREEN phase blocking | ⚠️ No over-engineering detection |
| **TDD-3.1.4** | ❌ NOT IMPLEMENTED | REFACTOR orphan removal | 🔴 No AST diff analysis |
| **TDD-3.1.5** | ❌ NOT IMPLEMENTED | REFACTOR duplicate elimination | 🔴 No clone detection |

**Gap Summary:**
- ⚠️ **Brittleness Present:** TDD orchestrator not yet migrated to v5 (Phase 6.5 pending approval)
- 🔴 **Missing:** Automated RED→GREEN→REFACTOR enforcement
- 🔴 **Missing:** REFACTOR phase code cleanup automation

**Recommendation:** **Phase 6.5 (Debug v2 Migration)** - When approved, include TDD migration with REFACTOR automation

---

## 🧹 Section 4: ADO Operations Orchestrator - Acceptance Validation

### 4.1 Work Item Generation (ADO-4.1.*)

| Criterion ID | Status | Evidence | Gap |
|--------------|--------|----------|-----|
| **ADO-4.1.1** | ✅ IMPLEMENTED | ADO v2 wizard validates format | ✅ Phase 6.1 complete |
| **ADO-4.1.2** | ✅ IMPLEMENTED | Acceptance criteria ≥3 items | ✅ Wizard enforces minimum |
| **ADO-4.1.3** | ✅ IMPLEMENTED | Fibonacci estimation | ✅ Wizard validates points |
| **ADO-4.1.4** | ✅ IMPLEMENTED | Task breakdown | ✅ Wizard prompts for tasks |

**Gap Summary:**
- ✅ **Strong implementation** - ADO v2 migration complete with high acceptance compliance
- ❌ **Missing:** Formal acceptance test suite execution and report

**Recommendation:** **Add Task 6.2.6 to Plan** - Run ADO v2 acceptance validation tests and generate report

---

## 🚨 Brittleness Remaining Analysis

### Brittleness Addressed (Phases 0-6.2 Complete)

| Brittleness Category | Status | Solution Implemented |
|----------------------|--------|----------------------|
| **1. State Management** | ✅ RESOLVED | SQLite PlanningStateDB with ACID transactions |
| **2. Control Flow Ambiguity** | ✅ RESOLVED | Master Orchestrator + Pattern Router |
| **5. Intent Classification** | ✅ RESOLVED | Pattern-based routing (90%+) + LLM fallback |
| **6. Base Class Inconsistency** | ✅ RESOLVED | BaseOrchestrator v4.1 with shared patterns |

### Brittleness Remaining (Phases 6.3-10 Not Started)

| Brittleness Category | Status | Orchestrators Affected | Severity |
|----------------------|--------|------------------------|----------|
| **3. Failure Recovery** | 🔴 UNRESOLVED | Vacuum, Sanitization, Debug, Refinement, CORTEX Lens | CRITICAL |
| **4. Configuration Parsing** | 🔴 UNRESOLVED | Vacuum, Sanitization (manifests still hybrid) | HIGH |
| **7. Testing Gap** | 🔴 UNRESOLVED | All unmigrated orchestrators | HIGH |

**Impact:** 5 orchestrators still exhibit critical brittleness:
1. **Vacuum v2** - Hybrid manifest, no state management
2. **Sanitization** - No failure recovery
3. **Debug v2** - Pending migration approval
4. **Refinement** - GUIDED orchestrator (assessed as keep GUIDED)
5. **CORTEX Lens** - GUIDED orchestrator (assessed as keep GUIDED)

**User Experience Impact:**
- 🔴 Users cannot resume failed Vacuum operations
- 🔴 Sanitization crashes require full restart
- 🔴 No automatic recovery for any GUIDED orchestrator

---

## 🎯 Critical Gaps Requiring Immediate Action

### Priority 1: URGENT (Blocking Progress)

| Gap ID | Description | Impact | Recommendation |
|--------|-------------|--------|----------------|
| **GAP-1** | Phase -1 Knowledge Library missing | SKULL violation | Add Phase -1 to 00-MASTER-PLAN-V5.md |
| **GAP-2** | Mandatory plan content missing | Non-compliant plan | Update plan with copilot_instructions, template reference |
| **GAP-3** | Git checkpoint hooks not implemented | No phase rollback | Add Task 7.1 to implement lifecycle hooks |

### Priority 2: HIGH (Acceptance Validation)

| Gap ID | Description | Impact | Recommendation |
|--------|-------------|--------|----------------|
| **GAP-4** | No formal acceptance test execution | Can't validate compliance | Add Task 6.2.1-6.2.6 for acceptance tests |
| **GAP-5** | AST scanning not in Planning v5 | Missing holistic discovery | Add Phase 6.4 for AST integration |
| **GAP-6** | Phase 10 REFACTOR not started | Orphaned/duplicate code remains | Execute Phase 10 after migrations |

### Priority 3: MEDIUM (Migration Phase)

| Gap ID | Description | Impact | Recommendation |
|--------|-------------|--------|----------------|
| **GAP-7** | Vacuum v2 not started (Phase 6.3) | Users can't use deep cleanup | Execute Phase 6.3 next |
| **GAP-8** | Sanitization v2 not started (Phase 6.4) | No sanitization available | Execute Phase 6.4 after Vacuum |
| **GAP-9** | Debug v2 pending approval (Phase 6.5) | No debug orchestrator v2 | Await approval, then execute |

---

## 📊 Acceptance Criteria Scorecard

### Overall Compliance

| Section | Total Criteria | Implemented | Partial | Missing | Compliance % |
|---------|----------------|-------------|---------|---------|--------------|
| **Master Orchestrator (1)** | 15 | 8 | 4 | 3 | 53% |
| **Planning System (2)** | 20 | 9 | 2 | 9 | 45% |
| **TDD Mastery (3)** | 10 | 0 | 5 | 5 | 0% |
| **ADO Operations (4)** | 5 | 4 | 0 | 1 | 80% |
| **Overall** | **50** | **21** | **11** | **18** | **42%** |

**Interpretation:**
- ✅ **Bootstrap Phase (Sections 1-2):** 49% compliant (strong foundation)
- ⚠️ **Migration Phase (Sections 3-4):** 20% compliant (work in progress)
- 🔴 **REFACTOR Phase (Section 10):** 0% compliant (not started)

---

## 🛠️ Recommended Plan Updates

### New Tasks to Add

**Phase 6.2 (Current) - Acceptance Validation:**
- **Task 6.2.1:** Create Master Orchestrator acceptance validation test suite (4h)
- **Task 6.2.2:** Create cross-session context acceptance validation tests (3h)
- **Task 6.2.3:** Standardize plan filename casing and create validation tests (2h)
- **Task 6.2.4:** Update 00-MASTER-PLAN-V5.md with mandatory content (2h)
- **Task 6.2.5:** Insert Phase -1 Knowledge Library Consultation (1h)
- **Task 6.2.6:** Run ADO v2 acceptance validation tests and generate report (2h)

**Phase 6.4 (New) - AST Integration:**
- **Task 6.4.1:** Create AST scanner agent (6h)
- **Task 6.4.2:** Integrate AST scanning into Planning System v5 Phase 0 (4h)
- **Task 6.4.3:** Generate context/ast-analysis.json with acceptance schema (2h)
- **Task 6.4.4:** Surface AST findings in plan generation (2h)

**Phase 7.1 (New) - Orchestrator Lifecycle Hooks:**
- **Task 7.1.1:** Implement pre-execution workspace validation hook (3h)
- **Task 7.1.2:** Implement post-execution git checkpoint hook (4h)
- **Task 7.1.3:** Implement error cleanup hook (3h)
- **Task 7.1.4:** Test lifecycle hooks with all orchestrators (4h)

**Phase 10 Expansion - REFACTOR Automation:**
- **Task 10.1:** Automated orphaned function detection and removal (6h)
- **Task 10.2:** Automated duplicate code detection and consolidation (8h)
- **Task 10.3:** Unused import removal (2h)
- **Task 10.4:** Code smell detection and refactoring (8h)
- **Task 10.5:** Complexity reduction (cyclomatic complexity ≤10) (6h)
- **Task 10.6:** Extract magic numbers to constants (4h)
- **Task 10.7:** Type hint validation and addition (4h)
- **Task 10.8:** Docstring completeness check (3h)
- **Task 10.9:** Final acceptance criteria validation (6h)

---

## 🎯 Next Steps

### Immediate Actions (This Session)

1. ✅ **Create this gap analysis document** (Done)
2. ⏭️ **Update 00-MASTER-PLAN-V5.md** with:
   - Phase -1 Knowledge Library Consultation
   - Mandatory content blocks (copilot_instructions, template reference)
   - New tasks (6.2.1-6.2.6, 6.4, 7.1, 10.1-10.9)
3. ⏭️ **Execute Phase 6.2 acceptance validation tasks** (14h total)

### Short-Term Actions (Next 1-2 Sessions)

4. Execute Phase 6.3: Vacuum v2 Migration (5 days)
5. Execute Phase 6.4: AST Integration (14h)
6. Execute Phase 7.1: Lifecycle Hooks (14h)

### Long-Term Actions (Remaining Plan)

7. Complete Migration Phase (Phases 6.3-6.5)
8. Execute Integration & Testing (Phases 7-8)
9. Execute Phase 10: REFACTOR Automation with 18+ tasks
10. Generate final acceptance report

---

## 🎉 Summary

**Current State:**
- ✅ Strong foundation (Bootstrap Phase 43% complete)
- ⚠️ Gaps in acceptance validation and mandatory content
- 🔴 Critical brittleness remains in unmigrated orchestrators

**Path Forward:**
- **Immediate:** Fix mandatory content gaps (Phase -1, copilot_instructions)
- **Short-term:** Execute acceptance validation and lifecycle hooks
- **Long-term:** Complete migrations and REFACTOR automation

**Timeline Impact:** +2 days for acceptance validation and lifecycle hooks (42.5 days total)

**Success Metric:** 100% acceptance criteria compliance before plan completion (Phase 10)

---

**Generated:** January 3, 2026  
**Validator:** CORTEX Brittleness & Acceptance Analyzer  
**Next Review:** After Phase 6.2 completion
