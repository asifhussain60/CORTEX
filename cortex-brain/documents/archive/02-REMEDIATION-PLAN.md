# 🛠️ CORTEX 4.0 Gap Remediation Plan

**Version:** 1.0.0 | **Author:** Asif Hussain | **Date:** December 30, 2025  
**Parent:** [01-DETAILED-GAPS.md](./01-DETAILED-GAPS.md)  
**Duration:** 6 weeks | **Effort:** 240 hours

---

## 📋 Executive Summary

This plan addresses 5 critical gaps that prevent CORTEX 4.0 from achieving its vision of an **autonomous AI orchestrator**. The remediation transforms CORTEX from a command-driven toolkit into a truly intelligent assistant that:

1. Understands user intent using LLM (not regex)
2. Automatically engages planning when complexity warrants it
3. Builds context incrementally across conversation turns
4. Actively consults knowledge library before code generation
5. Operates cohesively through unified LLM architecture

**Total Tests:** 145 tests (50 new + 95 updated)  
**Target Pass Rate:** 100% (3,000/3,000 tests)  
**Timeline:** 6 weeks (40 hours/week)

---

## 🎯 Remediation Phases

### **Phase 1: LLM Intent Classification** (Week 1)

**Objective:** Replace regex-based intent routing with LLM-powered semantic understanding

**Tasks:**
1. **Task 1.1:** Design LLM intent classification prompt (4h)
   - Define 8 intent types with descriptions
   - Create few-shot examples
   - Add confidence scoring mechanism

2. **Task 1.2:** Implement `LLMIntentClassifier` (8h)
   - Build prompt engineering logic
   - Integrate with OpenAI/Claude API
   - Add response parsing + validation
   - Implement regex fallback

3. **Task 1.3:** Integrate with existing `IntentRouter` (6h)
   - Refactor `_classify_intent_with_rules()`
   - Preserve backward compatibility
   - Add feature flag: `llm_intent_enabled`

4. **Task 1.4:** Build test suite (12h)
   - 15 new tests (semantic understanding, confidence, fallback)
   - Update 32 existing tests
   - Create test data set (100 samples)

5. **Task 1.5:** Performance optimization (6h)
   - Add response caching (5-minute TTL)
   - Batch processing for multiple requests
   - Benchmark: ≤ 300ms per classification

6. **Task 1.6:** Validation + documentation (4h)
   - Accuracy validation: ≥ 95%
   - Update CORTEX.prompt.md
   - Create migration guide

**Deliverables:**
- ✅ `src/cortex_agents/llm_intent_classifier.py` (300 LOC)
- ✅ `tests/cortex_agents/test_llm_intent_classifier.py` (15 tests)
- ✅ Updated `src/cortex_agents/intent_router.py` (integration)
- ✅ Documentation: `docs/llm-intent-classification.md`

**Success Criteria:**
- ✅ 95%+ accuracy on test set (100 samples)
- ✅ Fallback works when LLM unavailable
- ✅ Response time ≤ 300ms (with caching)
- ✅ All 47 tests passing

**Git Checkpoint:** `cortex-gap-remediation-phase-1-llm-intent`

---

### **Phase 2: Auto-Engagement Engine** (Week 2)

**Objective:** Automatically trigger planning for complex requests (no user command needed)

**Tasks:**
1. **Task 2.1:** Design complexity scoring algorithm (6h)
   - Define 5 factors (LOC, domains, security, architecture, history)
   - Weight assignment (30%, 25%, 20%, 15%, 10%)
   - Threshold calibration (LOW/MEDIUM/HIGH/CRITICAL)

2. **Task 2.2:** Implement `AutoEngagementEngine` (10h)
   - Complexity analyzer
   - Domain detection
   - LOC estimation (using LLM)
   - Security/architecture heuristics

3. **Task 2.3:** Integrate with `PlanningOrchestrator` (6h)
   - Add pre-execution check: `should_auto_engage_planning()`
   - Preserve user override: "implement without planning"
   - Log engagement decisions

4. **Task 2.4:** Build test suite (10h)
   - 12 new tests (simple/complex requests, overrides)
   - Create test data set (200 samples)

5. **Task 2.5:** User experience refinement (4h)
   - Add engagement notification: "🎭 Auto-engaging planning (HIGH complexity detected)"
   - User confirmation prompt (optional)
   - Bypass mechanism: `--no-plan` flag

6. **Task 2.6:** Validation + documentation (4h)
   - Engagement accuracy: 90%+
   - False positive rate: ≤ 5%
   - Update CORTEX.prompt.md with auto-engagement rules

**Deliverables:**
- ✅ `src/orchestrators/planning/auto_engagement_engine.py` (400 LOC)
- ✅ `tests/orchestrators/planning/test_auto_engagement_engine.py` (12 tests)
- ✅ Updated `src/orchestrators/planning/planning_orchestrator.py`
- ✅ Documentation: `docs/auto-engagement.md`

**Success Criteria:**
- ✅ 90%+ correct engagement decisions (200-sample test set)
- ✅ False positive rate ≤ 5%
- ✅ User can override engagement
- ✅ All 12 tests passing

**Git Checkpoint:** `cortex-gap-remediation-phase-2-auto-engagement`

---

### **Phase 3: Incremental AST Context** (Week 3)

**Objective:** Build AST context incrementally across conversation turns (not static)

**Tasks:**
1. **Task 3.1:** Design incremental context architecture (4h)
   - Turn-based state machine
   - Entity extraction pipeline
   - Dependency graph builder
   - Search radius expansion (BFS)

2. **Task 3.2:** Implement `IncrementalASTBuilder` (12h)
   - Turn-by-turn context updates
   - AST caching mechanism
   - Dependency discovery
   - Code graph updates

3. **Task 3.3:** Integrate with `PlanningSession` (6h)
   - Refactor `discover_context()` to be incremental
   - Add `process_user_turn()` method
   - Track turn history

4. **Task 3.4:** Build test suite (8h)
   - 10 new tests (turn-by-turn updates, context preservation)
   - Update 18 existing AST tests

5. **Task 3.5:** Performance optimization (4h)
   - AST cache to prevent redundant parsing
   - Incremental dependency updates (not full rebuild)
   - Benchmark: ≤ 500ms per turn

6. **Task 3.6:** Validation + documentation (6h)
   - Verify context grows correctly across 5+ turns
   - Dependencies discovered within 2 turns
   - Update planning system documentation

**Deliverables:**
- ✅ `src/orchestrators/planning/incremental_ast_builder.py` (500 LOC)
- ✅ `tests/orchestrators/planning/test_incremental_ast_builder.py` (10 tests)
- ✅ Updated `src/orchestrators/planning/interactive_session.py`
- ✅ Documentation: `docs/incremental-ast-context.md`

**Success Criteria:**
- ✅ Context grows across turns (no information loss)
- ✅ Dependencies discovered within 2 turns
- ✅ AST cache prevents redundant work
- ✅ All 28 tests passing

**Git Checkpoint:** `cortex-gap-remediation-phase-3-incremental-ast`

---

### **Phase 4: Knowledge Library Integration** (Week 4)

**Objective:** All orchestrators actively consult knowledge library before generation

**Tasks:**
1. **Task 4.1:** Design knowledge consultation architecture (4h)
   - Domain detection algorithm
   - YAML loading strategy
   - Guideline extraction rules
   - Prompt injection format

2. **Task 4.2:** Implement `KnowledgeConsultant` (10h)
   - `consult_best_practices()` method
   - YAML parser with caching
   - Security rule prioritization
   - Prompt injection mechanism

3. **Task 4.3:** Integrate with orchestrators (12h)
   - `PlanningOrchestrator` integration
   - `TDDOrchestrator` integration
   - `ExecutionOrchestrator` integration
   - `CodeSanitizationOrchestrator` integration

4. **Task 4.4:** Build test suite (8h)
   - 8 new tests (consultation, injection, validation)
   - Update 15 existing orchestrator tests

5. **Task 4.5:** Performance optimization (4h)
   - YAML caching (TTL: 10 minutes)
   - Domain-based filtering (don't load all files)
   - Benchmark: ≤ 100ms latency

6. **Task 4.6:** Validation + documentation (2h)
   - Verify all orchestrators consult library
   - CRITICAL rules always injected
   - Update knowledge library README

**Deliverables:**
- ✅ `src/orchestrators/base/knowledge_consultant.py` (350 LOC)
- ✅ `tests/orchestrators/base/test_knowledge_consultant.py` (8 tests)
- ✅ Updated 4 orchestrators with knowledge integration
- ✅ Documentation: `docs/knowledge-library-integration.md`

**Success Criteria:**
- ✅ All orchestrators consult knowledge library
- ✅ CRITICAL security rules always injected
- ✅ Latency ≤ 100ms
- ✅ Cache hit rate ≥ 80%
- ✅ All 23 tests passing

**Git Checkpoint:** `cortex-gap-remediation-phase-4-knowledge-library`

---

### **Phase 5: Integration + E2E Testing** (Week 5)

**Objective:** Ensure all gaps work together cohesively

**Tasks:**
1. **Task 5.1:** Build integration test suite (12h)
   - 5 E2E tests (full autonomous workflow)
   - Test: LLM intent → Auto-engage → AST context → Knowledge → Plan
   - Test: Multi-turn planning with incremental AST
   - Test: Complex request (OAuth + RBAC + multi-domain)

2. **Task 5.2:** Regression testing (10h)
   - Run full test suite (3,000+ tests)
   - Fix regressions (expected: 10-15 issues)
   - Verify test pass rate ≥ 99.5%

3. **Task 5.3:** Performance benchmarking (6h)
   - E2E latency: ≤ 5 seconds (LLM intent + complexity + AST + knowledge)
   - Memory usage: ≤ 500MB (with caching)
   - Cache hit rates: ≥ 80%

4. **Task 5.4:** User acceptance testing (8h)
   - Test with 10 real-world scenarios
   - Validate autonomous behavior
   - Collect feedback

5. **Task 5.5:** Documentation updates (4h)
   - Update CORTEX.prompt.md with new capabilities
   - Update README.md with autonomous features
   - Create migration guide (3.0 → 4.0)

**Deliverables:**
- ✅ `tests/integration/test_cortex_autonomous_behavior.py` (5 tests)
- ✅ Updated documentation (CORTEX.prompt.md, README.md)
- ✅ Migration guide: `docs/CORTEX-4.0-AUTONOMOUS-MIGRATION.md`

**Success Criteria:**
- ✅ All 5 E2E tests passing
- ✅ Test pass rate: 99.5%+ (2,985+ / 3,000 tests)
- ✅ E2E latency ≤ 5 seconds
- ✅ Zero critical regressions

**Git Checkpoint:** `cortex-gap-remediation-phase-5-integration`

---

### **Phase 6: Maintenance Enforcement** (Week 6)

**Objective:** Update cortex-maintenance.prompt.md to enforce autonomous behavior

**Tasks:**
1. **Task 6.1:** Update maintenance prompt (4h)
   - Add validation: "LLM intent classification enabled?"
   - Add validation: "Auto-engagement functional?"
   - Add validation: "Incremental AST working?"
   - Add validation: "Knowledge library consulted?"

2. **Task 6.2:** Build validation tests (8h)
   - Test: Verify LLM intent classifier is active
   - Test: Verify auto-engagement triggers correctly
   - Test: Verify knowledge library loaded
   - Create 10 validation tests

3. **Task 6.3:** Add SKULL rules (4h)
   - Rule: "LLM intent MUST be used (regex is fallback only)"
   - Rule: "Planning MUST auto-engage for HIGH complexity"
   - Rule: "Knowledge library MUST be consulted before code generation"
   - Update `cortex-brain/brain-protection-rules.yaml`

4. **Task 6.4:** Create monitoring dashboard (12h)
   - Track: LLM classification accuracy over time
   - Track: Auto-engagement rate (% of requests)
   - Track: Knowledge library cache hit rate
   - Track: AST context turn count

5. **Task 6.5:** Documentation finalization (8h)
   - Update all 7 HIGH-priority gaps documentation
   - Create video walkthrough (autonomous behavior demo)
   - Update CORTEX 4.0 story (Git Pages)

6. **Task 6.6:** Final validation (4h)
   - Run full test suite (3,000+ tests)
   - Verify 100% pass rate
   - Sign off on Phase GAPS-1230

**Deliverables:**
- ✅ Updated `cortex-maintenance.prompt.md` with autonomous checks
- ✅ Updated `cortex-brain/brain-protection-rules.yaml` (3 new rules)
- ✅ Monitoring dashboard: `cortex-lens-output/autonomous-behavior-dashboard.html`
- ✅ Final documentation: All gaps closed

**Success Criteria:**
- ✅ Maintenance prompt enforces autonomous behavior
- ✅ 10 validation tests passing
- ✅ 3 new SKULL rules active
- ✅ Dashboard deployed and functional

**Git Checkpoint:** `cortex-gap-remediation-phase-6-maintenance`

---

## 📊 Effort Breakdown

| Phase | Tasks | Estimated Hours | Actual Hours | Variance |
|-------|-------|----------------|--------------|----------|
| **Phase 1** | LLM Intent Classification | 40h | TBD | TBD |
| **Phase 2** | Auto-Engagement Engine | 40h | TBD | TBD |
| **Phase 3** | Incremental AST Context | 40h | TBD | TBD |
| **Phase 4** | Knowledge Library Integration | 40h | TBD | TBD |
| **Phase 5** | Integration + E2E Testing | 40h | TBD | TBD |
| **Phase 6** | Maintenance Enforcement | 40h | TBD | TBD |
| **TOTAL** | - | **240h** | **TBD** | **TBD** |

**Contingency:** 20% buffer (48 hours) for unforeseen issues

---

## ✅ Success Metrics

### Phase-Level Metrics

| Metric | Target | Current | Phase 6 Target |
|--------|--------|---------|----------------|
| Test Pass Rate | 99.5%+ | 99.5% (2,985/3,000) | 100% (3,000/3,000) |
| LLM Intent Accuracy | ≥ 95% | 0% (regex only) | 95%+ |
| Auto-Engagement Accuracy | ≥ 90% | 0% (manual only) | 90%+ |
| Knowledge Consultation Rate | 100% | 0% (passive) | 100% |
| E2E Latency | ≤ 5s | N/A | ≤ 5s |

### Test Coverage Growth

| Area | Current Tests | New Tests | Updated Tests | Final Total |
|------|---------------|-----------|---------------|-------------|
| Intent Router | 32 | 15 | 32 | 47 |
| Auto-Engagement | 0 | 12 | 0 | 12 |
| AST Context | 18 | 10 | 18 | 28 |
| Knowledge Library | 0 | 8 | 15 | 23 |
| E2E Integration | 0 | 5 | 30 | 35 |
| **TOTAL** | **50** | **50** | **95** | **145** |

---

## 🎯 Validation Criteria

### Phase 1 Complete When:
- ✅ LLM intent classifier achieves 95%+ accuracy
- ✅ Fallback to regex works when LLM unavailable
- ✅ Response time ≤ 300ms (with caching)
- ✅ All 47 tests passing

### Phase 2 Complete When:
- ✅ Auto-engagement correctly identifies 90%+ of complex requests
- ✅ False positive rate ≤ 5%
- ✅ User can override engagement
- ✅ All 12 tests passing

### Phase 3 Complete When:
- ✅ AST context grows across 5+ conversation turns
- ✅ Dependencies discovered within 2 turns
- ✅ No information loss between turns
- ✅ All 28 tests passing

### Phase 4 Complete When:
- ✅ All 4 major orchestrators consult knowledge library
- ✅ CRITICAL security rules always injected
- ✅ Latency ≤ 100ms per consultation
- ✅ All 23 tests passing

### Phase 5 Complete When:
- ✅ All 5 E2E tests passing
- ✅ Test pass rate ≥ 99.5% (2,985+ / 3,000 tests)
- ✅ E2E latency ≤ 5 seconds
- ✅ Zero critical regressions

### Phase 6 Complete When:
- ✅ Maintenance prompt enforces autonomous behavior
- ✅ 10 validation tests passing
- ✅ 3 new SKULL rules active
- ✅ 100% test pass rate (3,000/3,000 tests)

---

## 🚀 Deployment Strategy

### Week 1-4: Development + Testing
- Implement Phases 1-4
- Continuous integration testing
- Git checkpoints at end of each phase

### Week 5: Integration
- E2E testing
- Regression fixes
- Performance optimization

### Week 6: Deployment + Validation
- Merge to main branch
- Update maintenance prompt
- Final validation
- Documentation deployment

---

## 📁 Deliverables Summary

**Code Files (8 new):**
1. `src/cortex_agents/llm_intent_classifier.py` (300 LOC)
2. `src/orchestrators/planning/auto_engagement_engine.py` (400 LOC)
3. `src/orchestrators/planning/incremental_ast_builder.py` (500 LOC)
4. `src/orchestrators/base/knowledge_consultant.py` (350 LOC)
5. Integration updates to 4 orchestrators (~200 LOC)

**Test Files (5 new + 95 updated):**
1. `tests/cortex_agents/test_llm_intent_classifier.py` (15 tests)
2. `tests/orchestrators/planning/test_auto_engagement_engine.py` (12 tests)
3. `tests/orchestrators/planning/test_incremental_ast_builder.py` (10 tests)
4. `tests/orchestrators/base/test_knowledge_consultant.py` (8 tests)
5. `tests/integration/test_cortex_autonomous_behavior.py` (5 tests)

**Documentation (7 new):**
1. `docs/llm-intent-classification.md`
2. `docs/auto-engagement.md`
3. `docs/incremental-ast-context.md`
4. `docs/knowledge-library-integration.md`
5. `docs/CORTEX-4.0-AUTONOMOUS-MIGRATION.md`
6. Updated `CORTEX.prompt.md`
7. Updated `cortex-maintenance.prompt.md`

**Total Lines of Code:**
- New code: ~1,750 LOC
- Updated code: ~500 LOC
- Test code: ~1,200 LOC
- **Total: ~3,450 LOC**

---

**Document Status:** ✅ COMPLETE  
**Next:** Link to CORTEX4-STATUS.md as Phase GAPS-1230  
**GitHub:** github.com/asifhussain60/CORTEX
