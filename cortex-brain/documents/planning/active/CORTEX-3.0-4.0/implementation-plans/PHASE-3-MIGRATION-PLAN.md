# Phase 3: Orchestrator Consolidation - Migration Plan

**Version:** 1.0  
**Author:** Asif Hussain  
**Created:** December 18, 2025  
**Status:** 🟢 ACTIVE - Week 7 Day 1  
**Phase Duration:** Weeks 9-13 (5 weeks)  
**Current Week:** Week 9 (Phase 3 begins)

---

## 🎯 Phase 3 Overview

**Goal:** Migrate and consolidate 28 orchestrators → 13 CORTEX 4.0 orchestrators

**Prerequisites:** ✅ ALL Phase 1 foundation validation passing (10/10 checks)

**Deliverables:**
1. 13 migrated orchestrators extending BaseOrchestrator
2. Co-located test files with 75-90% coverage per orchestrator
3. Technical documentation with D3.js diagrams for each orchestrator
4. 57% orchestrator reduction (28 → 13)
5. Foundation validation proving Phase 1 complete

---

## 📊 Migration Progress Tracker

**Last Updated:** December 18, 2025 | **Status:** Week 7 Day 1 - ExecutionOrchestrator Migration

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Week 7: Foundation Orchestrators (Days 1-5)          [█░░░░░░░░░░░]  8% │
├─────────────────────────────────────────────────────────────────────────┤
│ ✅ Day 1-3: ExecutionOrchestrator                    [█░░░░]  0%       │
│ ☐ Day 4-5: Technical Documentation Orchestrator     [░░░░░]  0%       │
│ ☐ Day 6-7: TDDOrchestrator                          [░░░░░]  0%       │
├─────────────────────────────────────────────────────────────────────────┤
│ Week 8: Planning System (High-Complexity)            [░░░░░░░░░░░]  0% │
│   Days 1-2: Tiered Routing + Complexity Analysis    [░░░░░]  0%         │
│   Days 3-4: Pre-Planning Discovery                  [░░░░░]  0%         │
│   Day 5: Visual Progress Tracker                    [░░░░░]  0%         │
├─────────────────────────────────────────────────────────────────────────┤
│ ☐ PlanningOrchestrator (1,599 LOC → 4 modules)      [░░░░░]  0%       │
│ ☐ ScaffoldingOrchestrator (5 support modules)       [░░░░░]  0%       │
├─────────────────────────────────────────────────────────────────────────┤
│ Week 9: Domain-Specific Orchestrators                [░░░░░░░░░░░]  0% │
│   Days 1-2: Planning System Core Logic              [░░░░░]  0%         │
│   Day 3: Temporary Plan Manager Integration         [░░░░░]  0%         │
│   Days 4-5: Integration + Testing + Documentation   [░░░░░]  0%         │
├─────────────────────────────────────────────────────────────────────────┤
│ ☐ ADOOrchestrator (3 → 1 consolidation)             [░░░░░]  0%       │
│ ☐ DocumentationOrchestrator (2 → 1 consolidation)   [░░░░░]  0%       │
├─────────────────────────────────────────────────────────────────────────┤
│ Week 10: Operations Orchestrators                    [░░░░░░░░░░░]  0% │
├─────────────────────────────────────────────────────────────────────────┤
│ ☐ MaintenanceOrchestrator (5 → 1 consolidation)     [░░░░░]  0%       │
│ ☐ QAOrchestrator                                     [░░░░░]  0%       │
│ ☐ DevOpsOrchestrator                                 [░░░░░]  0%       │
├─────────────────────────────────────────────────────────────────────────┤
│ Week 11: Supporting Orchestrators                    [░░░░░░░░░░░]  0% │
├─────────────────────────────────────────────────────────────────────────┤
│ ☐ ObservabilityOrchestrator                          [░░░░░]  0%       │
│ ☐ IntelligenceOrchestrator                           [░░░░░]  0%       │
│ ☐ OnboardingOrchestrator (2 → 1 consolidation)      [░░░░░]  0%       │
└─────────────────────────────────────────────────────────────────────────┘

🎯 MILESTONES
├─ ☐ First Orchestrator Migrated (Week 7 Day 3)
├─ ☐ Self-Documentation Active (Week 7 Day 5)
├─ ☐ TDD Orchestrator Complete (Week 7 Day 7)
├─ ☐ Planning System Migrated (Week 8 End) - Core components operational
├─ ☐ Planning System Complete (Week 9 End) - 50+ tests, 85% coverage
├─ ☐ 50% Orchestrators Done (Week 10 End) - 7/14 orchestrators
└─ ☐ Phase 3 Complete (Week 11 End)

📈 METRICS
├─ Orchestrators Migrated: 0/13 (0%)
├─ Test Coverage: 0% (Target: 85%+ average)
├─ Documentation: 0/13 orchestrators documented
└─ Consolidation: 0/28 → 0/13 (Target: 28 → 13, 57% reduction)
```

---

## 🚀 Week 7: Foundation Orchestrators (Days 1-5)

### Day 1-3: ExecutionOrchestrator Migration

**Status:** ⏳ IN PROGRESS (Day 1)

**Why First?**
1. Foundation dependency - all other orchestrators depend on it
2. Multi-orchestrator routing - proves BaseOrchestrator framework works
3. Error handling - centralized recovery for all workflows
4. Foundation validation - first real test of Phase 1

**Source:**
- `src/orchestration_3_0/orchestrators/execution/execution_orchestrator.py` (625 LOC)

**Target:**
- `src/orchestrators/execution/execution_orchestrator.py`
- `src/orchestrators/execution/__init__.py`
- `src/orchestrators/execution/tests/test_execution_orchestrator.py`
- `src/orchestrators/execution/tests/test_dependency_resolution.py`
- `src/orchestrators/execution/tests/test_phase_execution.py`

**Migration Tasks:**

#### Day 1: Core Migration (6 hours)
- [x] Create target directory structure
- [ ] Copy execution_orchestrator.py to new location
- [ ] Update imports to use new structure:
  - `from ...core.base_orchestrator` → `from src.orchestrators.base.base_orchestrator`
  - `from ...core.state_machine` → `from src.core.state_machine`
  - `from ...session.session_manager` → `from src.core.session_manager`
- [ ] Verify ExecutionOrchestrator extends BaseOrchestrator correctly
- [ ] Update __init__.py with proper exports
- [ ] Run initial syntax validation

#### Day 2: DI Container Integration + Test Co-location (6 hours)
- [ ] Wire ExecutionOrchestrator into DI container:
  ```python
  # In src/di/container.py
  from src.orchestrators.execution import ExecutionOrchestrator
  
  container.register("execution_orchestrator", 
                     lambda: ExecutionOrchestrator(
                         session_manager=container.resolve("session_manager"),
                         container=container
                     ))
  ```
- [ ] Create test files:
  - `test_execution_orchestrator.py` - Core orchestrator logic
  - `test_dependency_resolution.py` - Dependency ordering
  - `test_phase_execution.py` - Phase execution pipeline
- [ ] Write comprehensive tests:
  - DoR validation (execution plan, dependencies)
  - Dependency resolution (topological sort)
  - Phase execution (orchestrator routing)
  - Error handling (rollback, recovery)
  - Progress tracking (real-time updates)
  - DoD validation (all phases complete)
- [ ] Target: 85%+ test coverage

#### Day 3: Validation + Documentation (6 hours)
- [ ] Run test suite: `pytest src/orchestrators/execution/tests/ --cov=src/orchestrators/execution`
- [ ] Validate coverage: Must be 85%+
- [ ] Fix any failing tests
- [ ] Generate orchestrator documentation:
  - Primary: Flowchart (phase execution logic)
  - Secondary: Architecture diagram (multi-orchestrator routing)
  - Sections: Phase management, Error handling, Routing strategy
- [ ] Update master plan progress tracker
- [ ] Git commit checkpoint: "✅ ExecutionOrchestrator migrated (Day 3)"

**Success Criteria:**
- ✅ ExecutionOrchestrator extends BaseOrchestrator
- ✅ Multi-orchestrator routing operational
- ✅ Phase execution pipeline working
- ✅ Error handling and recovery tested
- ✅ 85%+ test coverage in co-located tests
- ✅ Foundation validation proves Phase 1 complete

---

### Day 4-5: Technical Documentation Orchestrator Migration

**Why Second?**
1. Self-documenting migration - documents the process as it happens
2. Foundation validation - second orchestrator proves BaseOrchestrator is production-ready
3. Team enablement - generates docs for developers joining migration
4. Pattern establishment - sets standards for remaining 11 orchestrators

**Source:**
- Implementation from Phase 1.5

**Target:**
- `src/orchestrators/documentation/technical_documentation_orchestrator.py`
- `src/orchestrators/documentation/tests/test_technical_documentation_orchestrator.py`

**Tasks:** (TODO Day 4)

---

### Day 6-7: TDDOrchestrator Migration

**Status:** ✅ COMPLETE (December 19, 2025)

**Completed Work:**
- ✅ TDD Orchestrator v4.0 designed and implemented
- ✅ Unified architecture with strategy pattern
- ✅ 11+ language support (adaptive tech discovery)
- ✅ AI-driven test generation
- ✅ Clean code enforcement (SOLID/DRY/KISS/YAGNI)
- ✅ 26/26 tests passing (100% pass rate)
- ✅ 81.5% coverage (target: 90%)
- ✅ Complete documentation (manifest, guide, reference)

**See:** `cortex-brain/documents/planning/active/CORTEX-3.0-4.0/TDD-ORCHESTRATOR-REDESIGN.md`

---

## 🗓️ Week 8: Planning System Migration (Days 1-5)

**Orchestrator:** Planning System 3.0 → 4.0  
**Complexity:** HIGH (1,599 LOC, 9 components)  
**Coverage Target:** 85%+ (50+ tests)  
**Estimated Effort:** 21 hours over 5 days  

**Sub-Plan:** `cortex-brain/documents/planning/active/CORTEX-3.0-4.0/sub-plans/PLANNING-SYSTEM-MIGRATION-WEEK-8-9.md`

### Day 1: Tiered Routing Migration (4 hours)

**Objective:** Migrate TieredRouter + ComplexityAnalyzer to v4.0 structure

**Tasks:**
- [ ] Copy `TieredRouter` from `src/operations/modules/routing/` → `src/orchestrators/planning_system/routing/`
- [ ] Copy `ComplexityAnalyzer` from `src/operations/modules/routing/` → `src/orchestrators/planning_system/routing/`
- [ ] Update imports in both modules
- [ ] Create `src/orchestrators/planning_system/routing/__init__.py`
- [ ] Create `test_tiered_routing.py` (8 tests: Tier 1-4 classification, caching, LLM fallback, edge cases)
- [ ] Run tests: `pytest src/orchestrators/planning_system/tests/test_tiered_routing.py -v --cov`
- [ ] Validate: 90%+ coverage on routing module

**Deliverable:** Tiered routing operational in v4.0 structure with 8 passing tests

### Day 2: Routing Tests & Validation (4 hours)

**Objective:** Complete testing for routing module

**Tasks:**
- [ ] Create `test_complexity_analyzer.py` (8 tests: 4D scoring, thresholds, edge cases)
- [ ] Test code impact dimension (LOC, files, modules)
- [ ] Test risk level dimension (breaking changes, dependencies)
- [ ] Test domain complexity dimension (business logic, algorithms)
- [ ] Test integration scope dimension (external systems, APIs)
- [ ] Test tier classification edge cases (boundary scores)
- [ ] Test LLM fallback behavior (no cache, network error)
- [ ] Run coverage: `pytest src/orchestrators/planning_system/tests/ -v --cov=src/orchestrators/planning_system/routing/`
- [ ] Validate: 90%+ coverage

**Deliverable:** Routing module fully tested (16 tests passing, 90% coverage)

### Day 3: Pre-Planning Discovery Migration (6 hours)

**Objective:** Extract pre-planning discovery logic from archived orchestrator

**Tasks:**
- [ ] Review archived `PlanningOrchestrator.pre_planning_discovery()` in `archive/orchestrators/legacy/`
- [ ] Create `src/orchestrators/planning_system/discovery/` directory
- [ ] Create `pre_planning_discovery.py` - Extract discovery logic
- [ ] Create `plan_matcher.py` - Semantic plan matching (feature slug extraction, similarity scoring)
- [ ] Update imports and dependencies
- [ ] Create `src/orchestrators/planning_system/discovery/__init__.py`
- [ ] Create `test_pre_planning_discovery.py` (9 tests: active/temp/completed search, time ranges, slug extraction)
- [ ] Run tests: `pytest src/orchestrators/planning_system/tests/test_pre_planning_discovery.py -v`

**Deliverable:** Pre-planning discovery operational (9 tests passing)

### Day 4: Discovery Tests & Validation (4 hours)

**Objective:** Complete testing for discovery module

**Tasks:**
- [ ] Test active plan search (exact match, partial match)
- [ ] Test temporary plan search (30-day time range)
- [ ] Test completed plan search (180-day time range)
- [ ] Test feature slug extraction (multiple formats)
- [ ] Test semantic plan matching (confidence scoring)
- [ ] Test edge cases (no plans, multiple matches, old plans)
- [ ] Run coverage: `pytest src/orchestrators/planning_system/tests/ -v --cov=src/orchestrators/planning_system/discovery/`
- [ ] Validate: 85%+ coverage

**Deliverable:** Discovery module fully tested (9 tests passing, 85% coverage)

### Day 5: Visual Progress Tracker (4 hours)

**Objective:** Migrate visual progress tracking to v4.0

**Tasks:**
- [ ] Copy `PlanningSession` from `src/orchestrators/session_model.py` → `src/orchestrators/planning_system/tracking/progress_tracker.py`
- [ ] Create `metrics_collector.py` for phase metrics (timing, tokens, duration)
- [ ] Update imports
- [ ] Create `src/orchestrators/planning_system/tracking/__init__.py`
- [ ] Create `test_progress_tracking.py` (5 tests: phase tracking, metrics, rendering, visual table)
- [ ] Run tests: `pytest src/orchestrators/planning_system/tests/test_progress_tracking.py -v --cov`
- [ ] Validate: 85%+ coverage

**Deliverable:** Progress tracking operational (5 tests passing, 85% coverage)

**Week 8 End Status:**
- ✅ Routing module complete (16 tests, 90% coverage)
- ✅ Discovery module complete (9 tests, 85% coverage)
- ✅ Tracking module complete (5 tests, 85% coverage)
- ✅ 30/50 tests passing (60% complete)

---

## 🗓️ Week 9: Planning System Integration (Days 1-5)

**Objective:** Complete main orchestrator, integrate all modules, achieve 85%+ coverage

### Day 1: Core Planning Orchestrator (Part 1) (6 hours)

**Objective:** Create main orchestrator structure

**Tasks:**
- [ ] Create `src/orchestrators/planning_system/planning_orchestrator.py`
- [ ] Extend `BaseOrchestrator` from Phase 1
- [ ] Implement `__init__()` with DI container wiring
- [ ] Implement `execute()` method (request routing)
- [ ] Integrate `TieredRouter` for request classification
- [ ] Integrate `ComplexityAnalyzer` for scoring
- [ ] Wire in logging and error handling
- [ ] Create initial unit tests (5 tests: init, execute, routing integration)

**Deliverable:** Basic orchestrator structure operational (5 tests passing)

### Day 2: Core Planning Orchestrator (Part 2) (6 hours)

**Objective:** Integrate discovery and tracking

**Tasks:**
- [ ] Integrate `PrePlanningDiscovery` module
- [ ] Implement discovery workflow (search → recommend → user decision)
- [ ] Integrate `ProgressTracker` module
- [ ] Implement phase management (planning → execution)
- [ ] Add comprehensive error handling
- [ ] Add logging for all phases
- [ ] Create integration tests (10 tests: discovery + routing, tracking + execution)
- [ ] Run tests: `pytest src/orchestrators/planning_system/tests/test_planning_orchestrator.py -v`

**Deliverable:** Core orchestrator functionality complete (15 tests passing)

### Day 3: Temporary Plan Manager Integration (4 hours)

**Objective:** Complete lifecycle management

**Tasks:**
- [ ] Copy `TemporaryPlanManager` from `src/operations/modules/orchestration/` → `src/orchestrators/planning_system/management/`
- [ ] Create `plan_lifecycle.py` for lifecycle management (active → completed → archived)
- [ ] Update imports
- [ ] Create `src/orchestrators/planning_system/management/__init__.py`
- [ ] Wire into main orchestrator
- [ ] Create `test_temporary_plan_lifecycle.py` (5 tests: create, approve, reject, archive)
- [ ] Run tests: `pytest src/orchestrators/planning_system/tests/test_temporary_plan_lifecycle.py -v`

**Deliverable:** Temporary plan workflow operational (5 tests passing)

### Day 4: Integration & Wiring (6 hours)

**Objective:** Complete full system integration

**Tasks:**
- [ ] Wire orchestrator into DI container (`src/core/di_container.py`)
- [ ] Update `src/orchestrators/planning_system/__init__.py` exports
- [ ] Create end-to-end integration tests (10 tests: Tier 1-4 workflows)
- [ ] Test complete workflows:
  - Tier 1: Instant execution (<2 sec)
  - Tier 2: Lightweight with inline validation (<10 sec)
  - Tier 3: Documented with pre-planning discovery + single MD
  - Tier 4: Complex with nested plans
- [ ] Run full test suite: `pytest src/orchestrators/planning_system/tests/ -v --cov`
- [ ] Validate: 85%+ overall coverage
- [ ] Fix any failing tests

**Deliverable:** Full integration complete (50+ tests passing, 85%+ coverage)

### Day 5: Testing, Documentation & Validation (6 hours)

**Objective:** Finalize and document

**Tasks:**
- [ ] Run full test suite: `pytest src/orchestrators/planning_system/tests/ -v --cov`
- [ ] Validate 85%+ coverage achieved
- [ ] Fix any coverage gaps
- [ ] Generate documentation (8 docs):
  - Architecture diagram (Mermaid - already created)
  - Workflow flowchart (Mermaid - tiered routing)
  - Sequence diagram (Mermaid - discovery → routing → execution)
  - API reference (from docstrings)
  - Configuration guide (manifest + DI wiring)
  - Migration guide (v3.0 → v4.0)
  - Usage examples (Tier 1-4 scenarios)
  - Testing guide (run tests, write new tests)
- [ ] Create `README.md` for planning_system module
- [ ] Update master plan progress tracker in `MASTER-PLAN.md`
- [ ] Git commit checkpoint

**Git Commit:**
```bash
git add src/orchestrators/planning_system/
git commit -m "✅ Week 9 Complete: Planning System 4.0

- All 9 components migrated
- 50+ tests passing (85% coverage)
- 8 documentation artifacts generated
- Tiered routing operational (4 tiers)
- Pre-planning discovery operational
- Visual progress tracking integrated"

git add cortex-brain/documents/planning/active/CORTEX-3.0-4.0/MASTER-PLAN.md
git commit -m "📊 Update MASTER-PLAN.md: Week 8-9 Planning System complete"

git push origin CORTEX-4.0
```

**Deliverable:** Planning System 4.0 complete and documented

**Week 9 End Status:**
- ✅ 4/14 orchestrators complete (29%) - Execution, Documentation, TDD, Planning
- ✅ Planning System: 50+ tests, 85% coverage, 8 docs
- ✅ Ready for Week 10: ADO + Sanitization orchestrators

---

## 🗓️ Week 10-13: Remaining Orchestrators (To Be Detailed)

### Week 10: ADO + Code Sanitization

**Orchestrators:**
1. **ADO Operations Orchestrator** (3 days)
2. **Code Sanitization Orchestrator** (2 days)

### Day 6-7: TDDOrchestrator Migration

**Critical Path:** Used by all feature work

**Source:**
- `src/orchestration_3_0/orchestrators/tdd/` (orchestration_3_0 implementation)
- `src/workflows/` (workflows implementation)

**Target:**
- `src/orchestrators/tdd/tdd_orchestrator.py`
- `src/orchestrators/tdd/strategies/` (RED/GREEN/REFACTOR)
- `src/orchestrators/tdd/tests/`

**Architecture:** Strategy pattern with RED/GREEN/REFACTOR strategies

**Tasks:** (TODO Day 6)

---

## 📋 Migration Checklist Template

**For Each Orchestrator:**

### Pre-Migration
- [ ] Identify source files (orchestration_3_0, workflows, operations)
- [ ] List consolidation targets (if merging multiple orchestrators)
- [ ] Review existing tests
- [ ] Determine target coverage % (70-90% based on complexity)

### Migration
- [ ] Create target directory: `src/orchestrators/{name}/`
- [ ] Copy/merge source files to new location
- [ ] Update all imports to new structure
- [ ] Extend BaseOrchestrator if not already
- [ ] Wire into DI container
- [ ] Update __init__.py exports

### Testing
- [ ] Create test directory: `src/orchestrators/{name}/tests/`
- [ ] Write/migrate test files
- [ ] Run test suite with coverage
- [ ] Validate target coverage achieved
- [ ] Fix failing tests

### Documentation
- [ ] Generate flowchart (if phases/workflow)
- [ ] Generate architecture diagram
- [ ] Generate sequence diagram (if multi-component)
- [ ] Add API reference (from docstrings)
- [ ] Add configuration guide
- [ ] Add usage examples

### Validation
- [ ] All tests passing
- [ ] Coverage target met
- [ ] Documentation generated
- [ ] DI container integration working
- [ ] Update master plan progress tracker
- [ ] Git commit checkpoint

---

## 🧪 Test Location Policy

**CORTEX Orchestrator Tests** (in CORTEX repository):
- Location: `src/orchestrators/{orchestrator_name}/tests/`
- Purpose: Test orchestrator logic itself
- Coverage: Orchestrator methods, phase management, error handling

**Application Tests** (in USER repository):
- Location: `{user_repo}/tests/`
- Purpose: Test application code generated by orchestrator
- Coverage: Application business logic, NOT orchestrator logic

**Rule:** Test validates CORTEX behavior → CORTEX repo | Test validates app code → User repo

---

## 📚 Documentation Requirements

**Per Orchestrator:**
- ✅ Architecture diagram (auto-selected based on purpose)
- ✅ Workflow flowchart (if phases/steps)
- ✅ Sequence diagram (if multi-component interactions)
- ✅ API reference (from docstrings)
- ✅ Configuration guide
- ✅ Usage examples
- ✅ Testing guide

---

## 🚨 Common Pitfalls

1. **Import Hell:** Update ALL imports to new structure, not just orchestrator imports
2. **Test Isolation:** Don't mix CORTEX tests with application tests
3. **Coverage Gaps:** Write tests BEFORE claiming "done"
4. **Documentation Debt:** Generate docs as you go, not at the end
5. **Git Discipline:** Commit after each orchestrator, don't batch

---

## 📈 Success Metrics

**Phase 3 Complete When:**
- ✅ 13/13 orchestrators migrated
- ✅ 85%+ average test coverage
- ✅ 13/13 orchestrators documented with diagrams
- ✅ 28 → 13 consolidation achieved (57% reduction)
- ✅ All integration tests passing
- ✅ Foundation validation still passing
- ✅ Master plan progress tracker updated

---

**Next Steps:** Complete ExecutionOrchestrator Day 1 migration tasks
