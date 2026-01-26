# MASTER ORCHESTRATOR - PLANNING → TDD Integration Plan
**Date:** 2026-01-25 | **Status:** Design Review | **Authority:** Integration Specification

---

## 1. Architecture Confirmed

### Current State (Implementation Truth - CORE-030)

**MasterOrchestrator (`cortex/orchestrators/core/master_orchestrator.py`):**
- ✅ Singleton pattern (line 118)
- ✅ TDD Orchestrator initialized at startup (line 412-431)
- ✅ execute_operation() router (line 950)
- ✅ Delegates to: register_orchestrator(), coordinate_operation()
- ❌ **GAP:** No planning → TDD orchestration sequence

**TDDOrchestrator (`cortex/orchestrators/core/tdd_orchestrator.py`):**
- ✅ Knowledge loader integrated (TDDKnowledgeLoader class)
- ✅ Loads 35 best practices YAMLs from cortex_brain/tier3/knowledge/TESTING-VALIDATION/
- ✅ Exposes TDD guidance (TDDImplementationGuidance dataclass)
- ✅ Enforces RED → GREEN → REFACTOR workflow (TDDPhase enum)
- ✅ Singleton: `get_tdd_orchestrator()` function

**PlanningOrchestrator (`cortex/orchestrators/domain/planning_orchestrator.py` - Just completed):**
- ✅ Registry-based data loading (cortex-registry/planning/)
- ✅ LENS classification
- ✅ Challenge system (4 types)
- ✅ Execution gates (5 types)
- ✅ Audit trail with hash chain
- ❌ **GAP:** No knowledge YAML integration
- ❌ **GAP:** No TDD orchestration awareness

---

## 2. Your Architecture Decision (Q1-Q3 Answered)

### Q1: MasterOrchestrator is Route Point ✅
- User request → **MasterOrchestrator** (entry point)
- Routes to appropriate orchestrator (planning, tdd, etc.)
- Sequences execution based on operation type

### Q2: KnowledgeRepository is Shared ✅
- **Shared KnowledgeRepository** accessed by all orchestrators
- PlanningOrchestrator uses for planning best practices
- TDDOrchestrator uses for TDD best practices (already wired)
- Orchestrators don't own knowledge - they access it

### Q3: Plan Execution Uses TDD ✅
- Planning generates orchestration plan (sequence of operations)
- **MasterOrchestrator executes plan** (NOT planning internally calling TDD)
- For each plan step:
  - If type = "IMPLEMENT/FIX/REFACTOR/TEST" → Route to **TDDOrchestrator**
  - TDDOrchestrator uses knowledge YAMLs for guidance
  - Execution gates apply (Q3: planning doesn't need TDD dependency)

### Data Flow
```
┌─────────────────────────────────────────────────────────────┐
│ User Request: "Build auth system"                           │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
         ┌─────────────────────┐
         │ MasterOrchestrator  │
         │ (Route Point)       │
         └────────┬────────────┘
                  │ Route to planning
                  ▼
         ┌──────────────────────────────────┐
         │ PlanningOrchestrator             │
         │ - LENS classify intent           │
         │ - Generate challenges            │
         │ - Execute gates                  │
         │ - Read from cortex-registry/     │
         │ - Returns: Plan { ops: [...] }   │
         └────────┬─────────────────────────┘
                  │ Plan: [
                  │   {type: "IMPLEMENT", target: "auth_service", ...},
                  │   {type: "TEST", target: "auth_service", ...},
                  │   {type: "DEPLOY", target: "staging", ...}
                  │ ]
                  ▼
         ┌──────────────────────────────────┐
         │ MasterOrchestrator               │
         │ Execute Plan (Sequentially)      │
         │                                  │
         │ For each operation:              │
         │  1. IMPLEMENT → TDDOrchestrator  │
         │     └─ Uses TDD knowledge YAMLs  │
         │     └─ RED→GREEN→REFACTOR        │
         │  2. TEST → TDDOrchestrator       │
         │     └─ Test coverage guidance    │
         │  3. DEPLOY → DeployOrchestrator  │
         │     └─ Deployment guidance       │
         └──────────────────────────────────┘
```

---

## 3. Implementation Scope

### Files to Create/Modify

#### A. Create: PlanningRegistry → Knowledge Integration
**File:** `cortex/orchestrators/domain/planning_knowledge_loader.py` (NEW)
- Purpose: Load planning-specific best practices from KnowledgeRepository
- Load from: `cortex_brain/tier3/knowledge/PLANNING/` (NEW YAML domain)
- Similar to TDDKnowledgeLoader pattern
- Exposes: PlanningGuidance dataclass with best practices
- ~200 LOC

#### B. Create: Plan Execution Orchestrator
**File:** `cortex/orchestrators/core/plan_executor.py` (NEW)
- Purpose: Execute plan returned by PlanningOrchestrator
- Responsibility: Sequence orchestrators based on plan steps
- For each step:
  - Match operation type to orchestrator (IMPLEMENT→TDD, DEPLOY→Deploy, etc.)
  - Delegate to MasterOrchestrator.delegate_to_orchestrator()
  - Aggregate results
- ~300 LOC

#### C. Create: Orchestrator Sequencing Configuration
**File:** `cortex-registry/master/orchestration-config.yaml` (NEW)
- Purpose: Declarative routing of operation types to orchestrators
- Content:
  ```yaml
  orchestration_sequence:
    IMPLEMENT:
      primary: tdd_orchestrator
      knowledge_domain: TESTING-VALIDATION
    FIX:
      primary: tdd_orchestrator
      knowledge_domain: TESTING-VALIDATION
    REFACTOR:
      primary: tdd_orchestrator
      knowledge_domain: ARCHITECTURE
    DEPLOY:
      primary: deployment_orchestrator
      knowledge_domain: DEPLOYMENT
    PLAN:
      primary: planning_orchestrator
      knowledge_domain: PLANNING
  ```

#### D. Modify: PlanningOrchestrator Integration
**File:** `cortex/orchestrators/domain/planning_orchestrator.py`
- Add: Import PlanningKnowledgeLoader
- Add: Load planning best practices in __init__
- Add: Use planning guidance in challenge generation
- No changes to core logic (stays pure)
- ~50 LOC additions

#### E. Modify: MasterOrchestrator Extensions
**File:** `cortex/orchestrators/core/master_orchestrator.py`
- Add: New method `delegate_to_orchestrator(operation_type, context)`
- Add: New method `execute_plan(plan_obj)` - sequences execution
- Update: execute_operation() to handle "plan_execution" operation
- ~200 LOC additions

#### F. Create: Shared Knowledge Repository Access
**File:** `cortex/orchestrators/core/knowledge_coordinator.py` (NEW)
- Purpose: Centralized access to shared KnowledgeRepository
- Exposes: get_domain_guidance(domain_name) → guidance object
- Singleton pattern
- ~100 LOC

#### G. Create: TDD Planning Knowledge YAMLs
**Directory:** `cortex_brain/tier3/knowledge/PLANNING/` (NEW)
- Files:
  - `planning-best-practices.yaml` - Planning principles
  - `planning-patterns.yaml` - Planning patterns
  - `planning-anti-patterns.yaml` - What not to do
  - `planning-gates.yaml` - Execution gate guidance
- ~400 lines total YAML

#### H. Create: Integration Tests
**File:** `tests/orchestrators/core/test_master_orchestrator_planning_tdd_integration.py` (NEW)
- Test: Planning → TDD execution flow
- Test: Plan execution sequencing
- Test: Knowledge repository access
- Test: Error handling in orchestration
- ~500 LOC, 25+ tests

---

## 4. TDD Approach (CORE-008)

### RED Phase (Tests First)
1. **test_plan_executor.py** - Test PlanExecutor (15 tests)
   - ✅ Execute plan with valid steps
   - ✅ Route IMPLEMENT to TDDOrchestrator
   - ✅ Route DEPLOY to DeployOrchestrator
   - ✅ Aggregate results
   - ✅ Error handling

2. **test_planning_knowledge_loader.py** - Test PlanningKnowledgeLoader (10 tests)
   - ✅ Load planning YAMLs
   - ✅ Extract planning guidance
   - ✅ Cache management

3. **test_master_orchestrator_planning_tdd_integration.py** - E2E (25 tests)
   - ✅ Full planning → execution flow
   - ✅ Multi-step orchestration
   - ✅ Knowledge repository sharing

### GREEN Phase (Implementation)
1. Create PlanExecutor class with execute_plan()
2. Create PlanningKnowledgeLoader (copy TDD pattern)
3. Create KnowledgeCoordinator singleton
4. Update MasterOrchestrator with delegation methods
5. Update PlanningOrchestrator to use planning knowledge
6. Populate planning YAMLs

### REFACTOR Phase
1. Refactor orchestration sequencing into registry
2. Add caching for knowledge lookups
3. Optimize plan execution (parallel vs sequential)
4. Add telemetry/observability

---

## 5. Governance Compliance

### CORE Rules Applied
- **CORE-008:** TDD (tests before implementation) ✅
- **CORE-011:** Type hints (100% coverage) ✅
- **CORE-012:** Google-style docstrings ✅
- **CORE-013:** No bare except clauses ✅
- **CORE-026:** Git checkpoint before major changes ✅
- **CORE-027:** Audit trail (AC_START → AC_COMPLETE) ✅
- **CORE-030:** Implementation Truth (verified actual code) ✅
- **CORE-035:** Single canonical implementation ✅

### New ACs
- **AC-MO-PLAN-001:** MasterOrchestrator routes planning operations
- **AC-MO-PLAN-002:** Planning doesn't depend on TDD (loose coupling)
- **AC-MO-PLAN-003:** Plan execution sequences through MasterOrchestrator
- **AC-MO-PLAN-004:** Shared KnowledgeRepository (SSOT)
- **AC-MO-PLAN-005:** Orchestration config in cortex-registry (declarative)

---

## 6. Deliverables

| File | Type | LOC | Tests | Status |
|------|------|-----|-------|--------|
| planning_knowledge_loader.py | Implementation | 200 | 10 | 📋 TODO |
| plan_executor.py | Implementation | 300 | 15 | 📋 TODO |
| knowledge_coordinator.py | Implementation | 100 | 5 | 📋 TODO |
| orchestration-config.yaml | Registry | 50 | - | 📋 TODO |
| test_plan_executor.py | Tests | 300 | 15 | 📋 TODO |
| test_planning_knowledge_loader.py | Tests | 250 | 10 | 📋 TODO |
| test_integration.py | Tests | 500 | 25 | 📋 TODO |
| cortex_brain/tier3/knowledge/PLANNING/ | Knowledge | 400 | - | 📋 TODO |
| Modified: planning_orchestrator.py | Update | +50 | - | 📋 TODO |
| Modified: master_orchestrator.py | Update | +200 | - | 📋 TODO |
| **TOTAL** | | **~2400** | **~65** | 📋 Plan Ready |

---

## 7. Questions Before Implementation

### For You to Answer:

1. **Plan Execution Strategy:**
   - Sequential? (one step at a time)
   - Parallel? (multiple steps concurrently)
   - Depends on operation type?

2. **Knowledge YAML Creation:**
   - Should I create planning YAMLs or did CORTEX-4.0 have them?
   - Should I reference existing knowledge or create new?

3. **Error Handling in Plan Execution:**
   - Fail-fast (stop on first error)?
   - Collect-all (run all steps, report all errors)?
   - Configurable per plan?

4. **Registry Location:**
   - Should orchestration-config.yaml be in `cortex-registry/master/` or `cortex-registry/orchestration/`?

---

## ✅ Recommendation

**Proceed with:** Option B (Decoupled via MasterOrchestrator sequencing)
- Planning stays pure (no TDD dependency)
- MasterOrchestrator orchestrates sequence (conductor pattern)
- Shared KnowledgeRepository (CORE-035 compliant)
- Fully testable (each orchestrator independent)
- **Authorization:** User confirmed Q1-Q3

**Next Step:** Quick answers to 4 questions above, then proceed to RED phase (test harness).

---

## 📊 Effort Estimate
- **RED Phase (Tests):** 2 hours (write 50 tests)
- **GREEN Phase (Implementation):** 3 hours (write 2400 LOC)
- **REFACTOR Phase:** 1 hour (optimize, document)
- **Integration Testing:** 1 hour (verify E2E flow)
- **Total:** ~7 hours to production-ready

**Token Budget:** ~30K tokens for full implementation + tests

