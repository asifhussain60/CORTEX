# Planning System 3.0 → 4.0 Migration Plan

**Version:** 1.0  
**Author:** Asif Hussain  
**Created:** December 19, 2025  
**Status:** 🟢 APPROVED - Week 8-9 Sub-Plan  
**Parent Plan:** CORTEX 3.0 → 4.0 Migration Master Plan  
**Timeline:** 10 days (2 weeks)  
**Complexity:** HIGH - 1,599 LOC, 9 components, 85%+ test coverage target

---

## 📊 MIGRATION PROGRESS TRACKER

**Last Updated:** December 19, 2025 | **Current Day:** Day 0 (Planning) | **Overall:** 0% Complete

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Week 8 Day 1-2: Routing & Complexity Analysis         [░░░░░░░░░░░]  0%    │
│ Week 8 Day 3-4: Pre-Planning Discovery                [░░░░░░░░░░░]  0%    │
│ Week 8 Day 5: Visual Progress Tracker                 [░░░░░░░░░░░]  0%    │
│ Week 9 Day 1-2: Core Planning Logic                   [░░░░░░░░░░░]  0%    │
│ Week 9 Day 3: Temporary Plan Manager                  [░░░░░░░░░░░]  0%    │
│ Week 9 Day 4: Integration & Wiring                    [░░░░░░░░░░░]  0%    │
│ Week 9 Day 5: Testing & Documentation                 [░░░░░░░░░░░]  0%    │
└─────────────────────────────────────────────────────────────────────────────┘

🎯 MILESTONES
├─ ☐ TieredRouter migrated (Day 2)
├─ ☐ Pre-planning discovery operational (Day 4)
├─ ☐ Visual tracker integrated (Day 5)
├─ ☐ Core planning logic migrated (Week 9 Day 2)
├─ ☐ 85%+ test coverage achieved (Week 9 Day 5)
└─ ☐ Planning System 4.0 complete (Week 9 Day 5)

📈 METRICS
├─ Modules Migrated: 0/9 (0%)
├─ Tests Passing: 0/50+ (0%)
├─ Coverage: 0% → Target: 85%+
├─ LOC: 0/1,599 migrated (0%)
└─ Documentation: 0/8 docs generated (0%)
```

---

## 🎯 Executive Summary

**Objective:** Migrate Planning System 3.0 orchestrator to CORTEX 4.0 architecture with enhanced modularity, tiered routing intelligence, and visual progress tracking.

**Current State (v3.0):**
- **Location:** Archived (`archive/orchestrators/legacy/planning_orchestrator.py`)
- **Structure:** Monolithic class (1,599 LOC)
- **Components:** 9 modules (routing, discovery, progress tracking, etc.)
- **Test Coverage:** Unknown (legacy tests in `tests/orchestrators/`)
- **Manifest:** `cortex-brain/manifests/orchestrators/planning-system-3.0-manifest.yaml` (458 lines)

**Target State (v4.0):**
- **Location:** `src/orchestrators/planning_system/`
- **Structure:** Modular with 4 sub-modules
- **Components:** BaseOrchestrator + 9 specialized modules
- **Test Coverage:** 85%+ (50+ tests)
- **Integration:** DI container, logging, response templates v4.0

**Key Features Preserved:**
1. ✅ **Tiered Routing** - 4-tier complexity classification (INSTANT, LIGHTWEIGHT, DOCUMENTED, COMPLEX)
2. ✅ **Pre-Planning Discovery** - Search active/temp/completed plans before creating new ones
3. ✅ **Visual Progress Tracker** - Real-time phase tracking with PlanningSession
4. ✅ **Complexity Analyzer** - 4-dimensional scoring (code impact, risk, domain, integration)
5. ✅ **Temporary Plan Manager** - Implicit planning workflow (create → feedback → approve/reject)

**Breaking Changes:**
- ❌ Old import paths (`src.orchestrators.planning_orchestrator` → `src.orchestrators.planning_system`)
- ❌ Monolithic class replaced with modular architecture
- ✅ API remains compatible (BaseOrchestrator interface)

---

## 🏗️ Current Architecture (v3.0)

**Source Location:** `archive/orchestrators/legacy/planning_orchestrator.py` (ARCHIVED)

**Components:**

```
Planning System 3.0 (ARCHIVED)
├── TieredRouter (src/operations/modules/routing/tiered_router.py) ✅ EXISTS
│   └── 4-tier classification with LLM/cache
├── ComplexityAnalyzer (src/operations/modules/routing/complexity_analyzer.py) ✅ EXISTS
│   └── 4-dimensional scoring (code impact, risk, domain, integration)
├── Pre-Planning Discovery (embedded in PlanningOrchestrator)
│   └── Search active/temp/completed plans
├── Visual Progress Tracker (src/orchestrators/session_model.py::PlanningSession) ✅ EXISTS
│   └── Real-time phase tracking with metrics
├── Temporary Plan Manager (src/operations/modules/orchestration/temporary_plan_manager.py) ✅ EXISTS
│   └── Implicit planning workflow
├── Plan Folder Manager (src/workflows/plan_folder_manager.py) ✅ EXISTS
│   └── Hierarchical folder structure
├── Planning Intelligence Coordinator (src/operations/modules/routing/planning_intelligence_coordinator.py) ✅ EXISTS
│   └── Coordinates complexity analysis + routing
├── Planning Learner (src/operations/modules/learning/planning_learner.py) ✅ EXISTS
│   └── Learn from past plans to improve routing
└── Planning Utility (src/operations/modules/planning/planning_utility.py) ✅ EXISTS
    └── Shared utility functions
```

**Key Observations:**
1. **Most components already exist** - TieredRouter, ComplexityAnalyzer, TemporaryPlanManager are standalone modules
2. **PlanningOrchestrator is ARCHIVED** - Main orchestrator class removed in cleanup
3. **Tests exist but scattered** - 50+ test files across `tests/orchestrators/`, `tests/integration/`
4. **Manifest is comprehensive** - 458-line YAML defines all components

---

## 🎨 Target Architecture (v4.0)

**Target Location:** `src/orchestrators/planning_system/`

**Modular Structure:**

```
src/orchestrators/planning_system/
├── __init__.py                      # Public API exports
├── planning_orchestrator.py         # Main orchestrator (extends BaseOrchestrator)
├── routing/
│   ├── __init__.py
│   ├── tiered_router.py            # REUSE from src/operations/modules/routing/
│   └── complexity_analyzer.py      # REUSE from src/operations/modules/routing/
├── discovery/
│   ├── __init__.py
│   ├── pre_planning_discovery.py   # NEW - Extract from archived PlanningOrchestrator
│   └── plan_matcher.py             # NEW - Semantic plan matching
├── tracking/
│   ├── __init__.py
│   ├── progress_tracker.py         # REUSE src/orchestrators/session_model.py
│   └── metrics_collector.py        # NEW - Collect phase metrics
├── management/
│   ├── __init__.py
│   ├── temporary_plan_manager.py   # REUSE from src/operations/modules/orchestration/
│   └── plan_lifecycle.py           # NEW - Active → Completed → Archived
├── tests/
│   ├── __init__.py
│   ├── test_planning_orchestrator.py
│   ├── test_tiered_routing.py
│   ├── test_pre_planning_discovery.py
│   ├── test_progress_tracking.py
│   └── test_temporary_plans.py
└── README.md                        # Module documentation
```

**Design Principles:**
1. **Reuse Over Rewrite** - Leverage existing modules (TieredRouter, ComplexityAnalyzer, etc.)
2. **Extract Discovery Logic** - Move pre-planning discovery from archived orchestrator to new module
3. **Co-Located Tests** - All tests in `src/orchestrators/planning_system/tests/`
4. **Clear Module Boundaries** - routing/, discovery/, tracking/, management/

---

## 📋 Component Migration Map (v3.0 → v4.0)

| Component | v3.0 Location | v4.0 Location | Action | Effort |
|-----------|--------------|---------------|---------|--------|
| **TieredRouter** | `src/operations/modules/routing/tiered_router.py` | `src/orchestrators/planning_system/routing/tiered_router.py` | COPY + Update imports | 2h |
| **ComplexityAnalyzer** | `src/operations/modules/routing/complexity_analyzer.py` | `src/orchestrators/planning_system/routing/complexity_analyzer.py` | COPY + Update imports | 1h |
| **Pre-Planning Discovery** | Embedded in archived `PlanningOrchestrator` | `src/orchestrators/planning_system/discovery/pre_planning_discovery.py` | EXTRACT from archive | 4h |
| **Visual Progress Tracker** | `src/orchestrators/session_model.py` | `src/orchestrators/planning_system/tracking/progress_tracker.py` | COPY PlanningSession class | 2h |
| **Temporary Plan Manager** | `src/operations/modules/orchestration/temporary_plan_manager.py` | `src/orchestrators/planning_system/management/temporary_plan_manager.py` | COPY + Update imports | 1h |
| **Planning Intelligence Coordinator** | `src/operations/modules/routing/planning_intelligence_coordinator.py` | Integrate into `planning_orchestrator.py` | MERGE logic | 3h |
| **Planning Learner** | `src/operations/modules/learning/planning_learner.py` | Use as dependency (Tier 2) | NO MIGRATION | 0h |
| **Planning Utility** | `src/operations/modules/planning/planning_utility.py` | Use as shared utility | NO MIGRATION | 0h |
| **Plan Folder Manager** | `src/workflows/plan_folder_manager.py` | Use as dependency | NO MIGRATION | 0h |
| **Main Orchestrator** | Archived | `src/orchestrators/planning_system/planning_orchestrator.py` | REWRITE using BaseOrchestrator | 8h |

**Total Migration Effort:** ~21 hours (2.6 days)

---

## 🧪 Testing Strategy

**Target Coverage:** 85%+ (50+ tests)

### Test Categories

**1. Unit Tests (30 tests)** - Test individual modules
- `test_tiered_routing.py` - 8 tests (Tier 1-4 classification, caching, LLM fallback)
- `test_complexity_analyzer.py` - 8 tests (4 dimensions, scoring, thresholds)
- `test_pre_planning_discovery.py` - 9 tests (active/temp/completed plan search, time ranges)
- `test_progress_tracking.py` - 5 tests (phase tracking, metrics, rendering)

**2. Integration Tests (15 tests)** - Test module interactions
- `test_planning_orchestrator_integration.py` - 10 tests (end-to-end workflows)
- `test_temporary_plan_lifecycle.py` - 5 tests (create → approve → archive)

**3. End-to-End Tests (5 tests)** - Test full planning workflows
- `test_planning_system_e2e.py` - 5 tests (Tier 1-4 workflows, real scenarios)

**Test Infrastructure:**
- ✅ Fixtures: Use Phase 1 test infrastructure (`tests/conftest.py`)
- ✅ Mocking: Mock BrainInterface, file I/O, LLM calls
- ✅ Coverage: Use pytest-cov (target: 85%+)

---

## 📅 Implementation Timeline (10 Days)

### Week 8: Core Components (Days 1-5)

#### **Day 1: Tiered Routing Migration** (4 hours)
- [ ] Copy `TieredRouter` to `src/orchestrators/planning_system/routing/`
- [ ] Copy `ComplexityAnalyzer` to `src/orchestrators/planning_system/routing/`
- [ ] Update imports in both modules
- [ ] Create `test_tiered_routing.py` (8 tests)
- [ ] Run tests, achieve 90%+ coverage on routing module
- **Deliverable:** Tiered routing operational in v4.0 structure

#### **Day 2: Routing Tests & Validation** (4 hours)
- [ ] Create `test_complexity_analyzer.py` (8 tests)
- [ ] Test 4-dimensional scoring
- [ ] Test tier classification edge cases
- [ ] Validate LLM fallback behavior
- [ ] Run coverage report (target: 90%+)
- **Deliverable:** Routing module fully tested

#### **Day 3: Pre-Planning Discovery Migration** (6 hours)
- [ ] Review archived `PlanningOrchestrator.pre_planning_discovery()`
- [ ] Extract logic to `src/orchestrators/planning_system/discovery/pre_planning_discovery.py`
- [ ] Create `plan_matcher.py` for semantic plan matching
- [ ] Update imports and dependencies
- [ ] Create `test_pre_planning_discovery.py` (9 tests)
- **Deliverable:** Pre-planning discovery operational

#### **Day 4: Discovery Tests & Validation** (4 hours)
- [ ] Test active/temp/completed plan search
- [ ] Test time range filtering (30 days, 180 days)
- [ ] Test feature slug extraction
- [ ] Test semantic matching
- [ ] Run coverage report (target: 85%+)
- **Deliverable:** Discovery module fully tested

#### **Day 5: Visual Progress Tracker** (4 hours)
- [ ] Copy `PlanningSession` from `session_model.py` to `tracking/progress_tracker.py`
- [ ] Create `metrics_collector.py` for phase metrics
- [ ] Update imports
- [ ] Create `test_progress_tracking.py` (5 tests)
- [ ] Run tests, achieve 85%+ coverage
- **Deliverable:** Progress tracking operational

---

### Week 9: Integration & Completion (Days 1-5)

#### **Day 1: Core Planning Orchestrator (Part 1)** (6 hours)
- [ ] Create `planning_orchestrator.py` extending BaseOrchestrator
- [ ] Implement `__init__()` with DI container wiring
- [ ] Implement `execute()` method
- [ ] Integrate TieredRouter for request classification
- [ ] Wire in ComplexityAnalyzer
- **Deliverable:** Basic orchestrator structure operational

#### **Day 2: Core Planning Orchestrator (Part 2)** (6 hours)
- [ ] Integrate Pre-Planning Discovery
- [ ] Integrate Visual Progress Tracker
- [ ] Implement phase management (planning → execution)
- [ ] Add error handling and logging
- [ ] Create initial tests (5 tests)
- **Deliverable:** Core orchestrator functionality complete

#### **Day 3: Temporary Plan Manager Integration** (4 hours)
- [ ] Copy `TemporaryPlanManager` to `management/temporary_plan_manager.py`
- [ ] Create `plan_lifecycle.py` for lifecycle management
- [ ] Wire into main orchestrator
- [ ] Create `test_temporary_plan_lifecycle.py` (5 tests)
- [ ] Run tests, achieve 80%+ coverage
- **Deliverable:** Temporary plan workflow operational

#### **Day 4: Integration & Wiring** (6 hours)
- [ ] Wire orchestrator into DI container (`src/core/di_container.py`)
- [ ] Update `__init__.py` exports
- [ ] Create integration tests (10 tests)
- [ ] Test end-to-end workflows (Tier 1-4)
- [ ] Run full test suite (target: 85%+)
- **Deliverable:** Full integration complete

#### **Day 5: Testing, Documentation & Validation** (6 hours)
- [ ] Run full test suite (50+ tests)
- [ ] Validate 85%+ coverage achieved
- [ ] Generate documentation (8 docs)
  - Architecture diagram
  - Workflow flowchart (tiered routing)
  - Sequence diagram (discovery → routing → execution)
  - API reference
  - Configuration guide
  - Migration guide (v3.0 → v4.0)
  - Usage examples
  - Testing guide
- [ ] Update master plan progress tracker
- [ ] Git commit checkpoint
- **Deliverable:** Planning System 4.0 complete and documented

---

## 📊 Success Criteria

**Planning System 4.0 Complete When:**
- ✅ All 9 components migrated to v4.0 structure
- ✅ 50+ tests passing (100% pass rate)
- ✅ 85%+ test coverage achieved
- ✅ 8 documentation artifacts generated
- ✅ Integration tests passing (end-to-end workflows)
- ✅ DI container wiring operational
- ✅ Response templates v4.0 integrated
- ✅ Foundation validation still passing
- ✅ Master plan progress tracker updated

**Validation Checklist:**
- [ ] `pytest src/orchestrators/planning_system/tests/ -v --cov` → 85%+
- [ ] All imports resolve correctly
- [ ] No circular dependencies
- [ ] Logging configured correctly
- [ ] Error handling comprehensive
- [ ] Documentation complete
- [ ] Git commit checkpoint created

---

## 🚨 Risk Mitigation

**Risk 1: Pre-Planning Discovery Extraction (HIGH)**
- **Impact:** Logic embedded in archived orchestrator, may be complex to extract
- **Mitigation:** Review archive carefully, extract incrementally, TDD approach
- **Contingency:** Simplify discovery logic if extraction exceeds 6 hours

**Risk 2: Test Coverage Gap (MEDIUM)**
- **Impact:** Legacy tests scattered, may miss edge cases
- **Mitigation:** Write new tests for all modules, target 85%+ coverage
- **Contingency:** Focus on critical paths first (Tier 2-4 routing)

**Risk 3: Integration Complexity (MEDIUM)**
- **Impact:** Multiple modules must work together seamlessly
- **Mitigation:** Integration tests early (Day 4), incremental validation
- **Contingency:** Roll back to previous working state if integration fails

**Risk 4: Timeline Overrun (MEDIUM)**
- **Impact:** 10 days is aggressive for 1,599 LOC + 9 components
- **Mitigation:** Reuse existing modules (TieredRouter, ComplexityAnalyzer), parallel tasks
- **Contingency:** Extend to Week 10 Day 1-2 if needed (2-day buffer)

---

## 🔗 Dependencies

**Phase 1 Prerequisites (MUST be complete):**
1. ✅ BaseOrchestrator framework
2. ✅ DI container (`CortexContainer`)
3. ✅ Response templates v4.0
4. ✅ Logging system
5. ✅ Testing infrastructure
6. ✅ Brain interface

**External Dependencies:**
- `src/operations/modules/routing/tiered_router.py` (exists)
- `src/operations/modules/routing/complexity_analyzer.py` (exists)
- `src/orchestrators/session_model.py` (exists)
- `src/operations/modules/orchestration/temporary_plan_manager.py` (exists)
- `src/workflows/plan_folder_manager.py` (exists)
- `src/operations/modules/learning/planning_learner.py` (exists, Tier 2)

**No Blockers** - All dependencies exist and operational

---

## 📚 Documentation Requirements

**Per Orchestrator (8 docs):**
1. ✅ Architecture diagram (Mermaid - component structure)
2. ✅ Workflow flowchart (Mermaid - tiered routing decision tree)
3. ✅ Sequence diagram (Mermaid - discovery → routing → execution)
4. ✅ API reference (from docstrings)
5. ✅ Configuration guide (manifest YAML + DI wiring)
6. ✅ Migration guide (v3.0 → v4.0 for users)
7. ✅ Usage examples (Tier 1-4 scenarios)
8. ✅ Testing guide (how to run tests, write new tests)

**Auto-Generation:**
- Architecture/workflow/sequence diagrams → `DocumentationOrchestrator` (completed Week 7)
- API reference → Docstring extraction
- Configuration/usage/testing guides → Template-based generation

---

## 🔄 Git Commit Strategy

**Commit Policy (CORTEX 4.0 Standard):**

```bash
# Day 1: Tiered Routing Migration
git add src/orchestrators/planning_system/routing/
git commit -m "✅ Planning System Week 8 Day 1: Tiered routing migrated

- Copied TieredRouter + ComplexityAnalyzer to v4.0 structure
- Updated imports
- 8 routing tests passing (90% coverage)"

# Day 3: Pre-Planning Discovery
git add src/orchestrators/planning_system/discovery/
git commit -m "✅ Planning System Week 8 Day 3: Pre-planning discovery migrated

- Extracted discovery logic from archived orchestrator
- 9 discovery tests passing (85% coverage)"

# Week 9 Day 5: Complete
git add src/orchestrators/planning_system/
git commit -m "✅ Planning System Week 9 Day 5: Complete

- All 9 components migrated
- 50+ tests passing (85% coverage)
- 8 documentation artifacts generated"

# Update master plan
git add cortex-brain/documents/planning/active/CORTEX-3.0-4.0/MASTER-PLAN.md
git commit -m "📊 Update MASTER-PLAN.md: Week 8-9 Planning System complete"

git push origin CORTEX-4.0
```

---

## 🎯 Next Steps (After Completion)

**Week 10: Domain-Specific Orchestrators**
1. Migrate ADO Operations Orchestrator
2. Migrate Code Sanitization Orchestrator
3. Migrate Scaffolding Orchestrator

**Phase 3 Progress After Week 9:**
- Orchestrators: 4/14 (29%) - Execution, Documentation, TDD, Planning
- Test Coverage: ~80% average
- Timeline: On track for Phase 3 completion Week 13

---

**Ready to Execute:** Planning System migration ready to start Week 8 Day 1.

**Questions Before Starting:**
1. Should we defer any components to simplify scope? (Recommendation: NO - all components essential)
2. Should we extend timeline to 12 days for safety? (Recommendation: NO - 10 days achievable with reuse)
3. Should we run foundation validation before starting? (Recommendation: YES - confirm Phase 1 still stable)

---

**Auto-Update Instructions (For Orchestrators):**

All work on this sub-plan MUST update the progress tracker:

```python
from src.core.progress_tracker import update_master_plan_progress

update_master_plan_progress(
    phase="3",
    week="8",  # or "9"
    completion_percentage=50,  # Day completion %
    milestone_completed="Planning System 4.0 Complete",
    metrics={
        "orchestrators_migrated": 4,
        "test_coverage": "50+ tests, 85% coverage",
        "docs_generated": 8
    }
)
```

**Manual Update (Development):**
- Edit progress bars in tracker at top
- Update "Last Updated" timestamp
- Mark milestones as ✅ when achieved
- Update MASTER-PLAN.md after Week 9 Day 5
