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
├─────────────────────────────────────────────────────────────────────────┤
│ ☐ PlanningOrchestrator (1,599 LOC → 4 modules)      [░░░░░]  0%       │
│ ☐ ScaffoldingOrchestrator (5 support modules)       [░░░░░]  0%       │
├─────────────────────────────────────────────────────────────────────────┤
│ Week 9: Domain-Specific Orchestrators                [░░░░░░░░░░░]  0% │
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
├─ ☐ Planning System Migrated (Week 8 End)
├─ ☐ 50% Orchestrators Done (Week 9 End)
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
