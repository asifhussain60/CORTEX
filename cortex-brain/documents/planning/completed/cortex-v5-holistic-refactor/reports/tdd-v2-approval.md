# ✅ TDD Orchestrator v2 Approval

**Decision Date:** January 2, 2026  
**Decision:** Approved for AUTONOMOUS conversion  
**Parent Plan:** cortex-v5-holistic-refactor (Phase 6.4)  
**Assessment Plan:** guided-orchestrators-assessment (Phase 1)

---

## 📋 Decision Summary

**TDD Orchestrator v2 has been approved for AUTONOMOUS conversion with Master Orchestrator integration.**

### Approval Details

**Architecture:** AUTONOMOUS execution with Python test runners  
**State Persistence:** PlanningStateDB tracks RED/GREEN/REFACTOR phases  
**Lifecycle Hooks:** Pre-execution (validate test files), Post-execution (coverage report)  
**User Interaction:** Optional approval gates after GREEN phase (configurable)  
**Estimated Effort:** 4 days

### Decision Rationale

| Criterion | Score | Justification |
|-----------|-------|---------------|
| **Operation Complexity** | 9/10 | Test execution, coverage analysis, quality metrics (HIGH → autonomous) |
| **State Management** | 10/10 | Multi-phase rollback required (RED→GREEN→REFACTOR) |
| **Workflow Simplicity** | 7/10 | 3-phase cycle benefits from state machine |
| **User Interaction** | 3/10 | Minimal (optional approval gates) |
| **Maintenance Cost** | 8/10 | Python test frameworks easier to maintain than manifest instructions |

**Weighted Score:** 8.1/10 → **AUTONOMOUS RECOMMENDED**

### Key Benefits

✅ **Transactional State Tracking:** Database-backed phase progression with rollback capability  
✅ **SKULL Enforcement:** Programmatic TDD_ENFORCEMENT (tests must fail before implementation)  
✅ **Master Orchestrator Integration:** Pattern-based routing (`^(tdd|start tdd|run tests).*$`)  
✅ **Coverage Automation:** Integrated coverage.py with automated reporting  
✅ **Code Quality Validation:** REFACTOR phase enforces quality metrics (complexity, duplication)  
✅ **Test Framework Agnostic:** Abstraction layer supports pytest, unittest, etc.

### Architecture Design

**Core Components:**
1. **TDDOrchestratorV2** - Main orchestrator class extending BaseOrchestratorV4.1
2. **TestRunnerAbstraction** - Adapter pattern for pytest/unittest
3. **TDDStateMachine** - RED→GREEN→REFACTOR state transitions
4. **CoverageAnalyzer** - Coverage.py integration with baseline tracking
5. **CodeQualityValidator** - Cyclomatic complexity + duplication checks

**State Database Schema:**
```sql
CREATE TABLE tdd_sessions (
  session_id TEXT PRIMARY KEY,
  phase TEXT CHECK(phase IN ('RED', 'GREEN', 'REFACTOR')),
  test_file TEXT NOT NULL,
  implementation_file TEXT,
  coverage_baseline REAL,
  coverage_current REAL,
  rollback_checkpoint TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Master Orchestrator Routing:**
```yaml
# cortex-brain/config/master-orchestrator.yaml
- pattern: "^(tdd|start tdd|run tests).*$"
  orchestrator: tdd_orchestrator_v2
  confidence: 1.0
  match_type: regex
  priority: 25
  metadata:
    description: "TDD Mastery v2 (RED→GREEN→REFACTOR)"
    autonomous: true
```

---

## 🎯 Implementation Plan

**Migration Plan:** To be generated via Planning v5

**Command:** `/CORTEX Plan TDD Orchestrator v2 Migration`

**Expected Plan Structure:**
```
cortex-brain/documents/planning/active/tdd-v2-migration/
├── 00-master-plan.md
├── context/
│   ├── tdd-v4-manifest-analysis.md
│   ├── test-framework-comparison.md
│   └── state-machine-design.md
├── reports/
│   ├── phase-0-foundation-complete.md
│   ├── phase-1-red-phase-complete.md
│   ├── phase-2-green-phase-complete.md
│   ├── phase-3-refactor-phase-complete.md
│   └── phase-4-integration-complete.md
├── artifacts/
│   ├── test-runner-abstraction-spec.md
│   ├── coverage-analyzer-design.md
│   ├── code-quality-metrics-spec.md
│   └── master-orch-routing-config.yaml
└── tracking/
    └── progress-tracker.json
```

**Implementation Phases:**
1. **Phase 0:** Core TDDOrchestratorV2 + TestRunnerAbstraction (1 day)
2. **Phase 1:** RED phase automation (0.75 days)
3. **Phase 2:** GREEN phase automation (0.75 days)
4. **Phase 3:** REFACTOR phase automation + quality checks (1 day)
5. **Phase 4:** Master Orch integration + testing (0.5 days)

**Total Duration:** 4 days

---

## 🔗 Integration Points

### Master Orchestrator
- Add TDD v2 routing patterns to `master-orchestrator.yaml`
- Register TDD v2 in OrchestratorRegistry
- Test pattern matching: "tdd X" → TDD v2 executes

### CORTEX.prompt.md
- Update Intent Router: `tdd [x]` → 🛡️ **TDD Mastery v2 (AUTONOMOUS)**
- Change type from 📋 GUIDED → 🛡️ AUTONOMOUS
- Update manifest reference: `tdd-orchestrator-v2-config.yaml`

### PlanningStateDB
- Add `tdd_sessions` table
- Implement state tracking queries
- Add phase transition triggers

### SKULL Rules
- TDD_ENFORCEMENT: Enforce RED-first workflow
- HOLISTIC_DISCOVERY: Search for existing test files
- REFACTOR_CLEANUP: Automated quality checks

---

## 📊 Success Criteria

**Technical:**
- ✅ TDD v2 executes RED→GREEN→REFACTOR workflow autonomously
- ✅ State persisted in PlanningStateDB with rollback capability
- ✅ Coverage.py integrated with baseline/current tracking
- ✅ Code quality metrics enforce REFACTOR phase standards
- ✅ Master Orchestrator routes TDD commands correctly
- ✅ 100% test coverage for TDD v2 implementation

**Operational:**
- ✅ Tests must fail in RED phase before implementation allowed
- ✅ GREEN phase validates all tests pass
- ✅ REFACTOR phase enforces ≥80% coverage + quality gates
- ✅ Atomic rollback on REFACTOR failure (revert to GREEN)
- ✅ Session resumption from any phase

**Documentation:**
- ✅ TDD v2 architecture documented
- ✅ Test runner abstraction API documented
- ✅ State machine transitions documented
- ✅ Master Orchestrator integration guide
- ✅ User guide for TDD v2 workflow

---

## 📝 Next Steps

1. **Generate Migration Plan:**
   ```
   /CORTEX Plan TDD Orchestrator v2 Migration
   ```

2. **Execute Migration (4 days):**
   - Follow generated plan phases sequentially
   - Create git checkpoints after each phase
   - Update progress in PlanningStateDB

3. **Progressive Activation:**
   - After successful testing, add routing to master-orchestrator.yaml
   - Register in OrchestratorRegistry
   - Update CORTEX.prompt.md Intent Router
   - Test end-to-end: "start tdd" → TDD v2 executes

4. **Update Parent Plans:**
   - Mark Phase 6.4 Task 6.5 as complete in V5 Master Plan
   - Update guided-orchestrators-assessment completion status
   - Generate phase completion report

---

## 📚 References

**Parent Plans:**
- `cortex-v5-holistic-refactor/00-MASTER-PLAN-V5.md` (Phase 6.4)
- `guided-orchestrators-assessment/00-master-plan.md` (Phase 1)

**Architecture Documents:**
- `cortex-brain/brain-protection-rules.yaml` (SKULL rules)
- `cortex-brain/manifests/orchestrators/tdd-orchestrator-v4-manifest.yaml` (current TDD)
- `cortex-brain/config/master-orchestrator.yaml` (routing config)

**Key Files:**
- `.github/prompts/CORTEX.prompt.md` (Intent Router)
- `src/orchestrators/base_orchestrator_v4_1.py` (BaseOrchestrator)
- `src/orchestrators/master_orchestrator.py` (Master Orchestrator)
- `src/database/planning_state.db` (State database)

---

**Status:** ✅ Approved - Ready for Planning v5 to generate migration plan  
**Next Action:** Execute `/CORTEX Plan TDD Orchestrator v2 Migration`
