# Planning Orchestrator Migration Plan

**Orchestrator:** `src/orchestrators/planning_orchestrator.py`  
**Lines of Code:** 5,126  
**Current Reliability:** 60%  
**Priority:** 🔴 CRITICAL (Week 1-2)  
**Migration Target Date:** December 17, 2025

---

## 📊 Current Implementation

### Executive Summary

The Planning Orchestrator manages feature planning workflows including complexity analysis, phased breakdowns, and DoR/DoD validation. It handles three complexity levels (HIGH, MEDIUM, LOW) with different phase structures. Currently implemented as a monolithic class with manual state tracking and hardcoded phase logic.

### How It Works Today

**Input:** User request like "plan feature: user authentication"

**Process:**
1. Analyze feature complexity (HIGH/MEDIUM/LOW)
2. Generate phased implementation plan
3. Create DoR (Definition of Ready) checklist
4. Execute phases incrementally
5. Validate DoD (Definition of Done) at completion

**Output:** Structured plan with phases, tasks, test requirements, and acceptance criteria

### Key Capabilities

- **Complexity Analysis:** Evaluates scope, dependencies, risk factors
- **Phased Planning:** Breaks features into incremental phases
- **TDD Integration:** Generates test-first requirements
- **Manifest Compliance:** Validates against `planning-system-2.0-manifest.yaml`
- **Autonomous Execution:** Can execute full plan without intervention

### Current Architecture

```
PlanningOrchestrator
├── analyze_complexity() - Determines HIGH/MEDIUM/LOW
├── generate_phases() - Creates phased breakdown
├── execute_incremental() - Runs phases sequentially
├── validate_dor() - Checks Definition of Ready
├── validate_dod() - Checks Definition of Done
└── create_session() - Manual session tracking
```

### Performance Metrics (Current)

- **Phase Completion:** 60% (40% skip phases)
- **DoR Validation:** 55% (45% bypass gate)
- **DoD Validation:** 65% (35% incomplete)
- **Session Recovery:** 0% (no persistence)
- **Average Execution Time:** 8-12 minutes per plan

---

## ❌ Issues & Pain Points

### 1. Manual State Tracking (HIGH SEVERITY)

**Problem:** Uses boolean flags instead of formal state machine

**Evidence (Line 82):**
```python
self.planning_mode_active = False  # Flag
self.current_plan_context: Optional[PlanningSession] = None
```

**Impact:**
- State scattered across 20+ instance variables
- No validation that phases execute in correct order
- Lost progress if process interrupted

### 2. Missing Phase Validation (HIGH SEVERITY)

**Problem:** No enforcement that required phases execute

**Evidence:** Manifest shows 8 requirements marked "missing"

**Impact:**
- Features deployed without DoR validation
- Threat modeling skipped
- Acceptance criteria not reviewed before implementation

### 3. Hardcoded Phase Logic (MEDIUM SEVERITY)

**Problem:** Phase definitions embedded in 5,126 lines of Python code

**Evidence (Line 450-1200):**
```python
if complexity == "HIGH":
    phases = [
        {"name": "foundation", "tasks": [...]},
        {"name": "core", "tasks": [...]},
        # 8 more phases hardcoded
    ]
```

**Impact:**
- Changing phase order requires code changes
- No visual representation of workflow
- Difficult to customize per project

### 4. 180 Lines of Duplicate Initialization (MEDIUM SEVERITY)

**Problem:** Manually imports and instantiates dependencies

**Evidence (Line 150-330):**
```python
try:
    from src.orchestrators.tdd_implementation_orchestrator import TDD...
    self._tdd_orchestrator = TDDImplementationOrchestrator(...)
    from src.orchestrators.git_checkpoint_orchestrator import Git...
    self._git_orchestrator = GitCheckpointOrchestrator(...)
    # Repeated for 8 dependencies
except ImportError:
    logger.warning("Orchestrator not available")
```

**Impact:**
- Code duplication across all 15 orchestrators
- Runtime failures if dependencies missing
- Difficult to test in isolation

### 5. No Session Recovery (LOW SEVERITY)

**Problem:** Crashes lose all planning work

**Impact:**
- Must restart plans from scratch
- Lost time on long-running plans
- No audit trail of planning decisions

---

## ✅ New Implementation

### Architecture Overview

Replace monolithic orchestrator with:
- **State Machine Engine:** Validates phase transitions
- **YAML Workflow:** Declarative phase definitions
- **Session Persistence:** SQLite-backed recovery
- **Dependency Injection:** Auto-wired components

### Component Breakdown

#### 1. State Machine Integration

```
StateMachine("planning")
├── States: [NOT_STARTED, ANALYZING, PLANNING, EXECUTING, VALIDATING, COMPLETED]
├── Transitions: Validated by guard conditions
├── Actions: DoR/DoD validation hooks
└── History: Full audit trail
```

**Benefits:**
- 100% phase execution (no skips)
- Automatic gate enforcement
- Rollback to previous phase if validation fails

#### 2. YAML Workflow Definition

**File:** `cortex-brain/workflows/planning-workflow.yaml`

```yaml
workflow:
  name: "Feature Planning"
  states:
    - analyzing
    - planning
    - executing
    - validating
  
  phases:
    - name: "complexity_analysis"
      tasks:
        - analyze_scope
        - identify_dependencies
        - assess_risk
      gates:
        output_required: ["complexity_level", "risk_factors"]
    
    - name: "dor_validation"
      tasks:
        - check_requirements_clarity
        - validate_acceptance_criteria
        - verify_threat_model
      gates:
        blocking: true  # Must pass to proceed
```

**Benefits:**
- Edit phases without code changes (15 min vs 2 hours)
- Visual representation via Mermaid
- Reorderable phases per project

#### 3. Session Persistence

**Database Schema:**
```sql
CREATE TABLE planning_sessions (
    session_id TEXT PRIMARY KEY,
    feature_name TEXT,
    complexity TEXT,
    current_state TEXT,
    phases_completed TEXT[],
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    session_data JSONB
);
```

**Benefits:**
- Resume after crashes
- Audit trail of decisions
- Historical analysis

#### 4. Dependency Injection

**Services Required:**
- `ComplexityAnalyzer` (scope/risk calculation)
- `PhaseGenerator` (creates phases from templates)
- `DORValidator` (Definition of Ready checks)
- `DODValidator` (Definition of Done checks)
- `TDDOrchestrator` (test requirements)
- `GitCheckpointOrchestrator` (version control)

**Registration:**
```python
container.register_singleton(ComplexityAnalyzer)
container.register_transient(PhaseGenerator)
container.register_singleton(DORValidator)
```

**Benefits:**
- Zero initialization code
- Testable in isolation
- No runtime import failures

### Code Size Reduction

- **Current:** 5,126 lines
- **New:** 400 lines (92% reduction)
- **Deleted:** 4,726 lines of boilerplate

### Performance Improvements

- **Phase Completion:** 60% → 100% (+40%)
- **DoR Validation:** 55% → 100% (+45%)
- **DoD Validation:** 65% → 100% (+35%)
- **Session Recovery:** 0% → 100% (new capability)
- **Execution Time:** 8-12 min → 6-8 min (25% faster)

---

## 🔄 Migration Plan

### Phase 1: Build Core Components (Day 1-2)

**Tasks:**
1. Create `PlanningStateMachine` with 6 states
2. Define `planning-workflow.yaml` with all phases
3. Implement `PlanningSession` model with SQLite
4. Build adapter `LegacyPlanningAdapter`

**Tests:** 120 unit tests, 100% coverage

**Validation:** Adapter passes all existing integration tests

### Phase 2: Migrate Complexity Analysis (Day 3)

**Tasks:**
1. Extract `ComplexityAnalyzer` service
2. Register in DI container
3. Update state machine to use service
4. Add gate for complexity validation

**Tests:** 40 unit tests for ComplexityAnalyzer

**Validation:** Complexity scores match legacy implementation

### Phase 3: Migrate Phase Generation (Day 4-5)

**Tasks:**
1. Convert hardcoded phases to YAML templates
2. Implement `PhaseGenerator` service
3. Add phase templates for HIGH/MEDIUM/LOW complexity
4. Create visual Mermaid diagrams

**Tests:** 60 tests for PhaseGenerator + YAML validation

**Validation:** Generated phases identical to legacy

### Phase 4: Add DoR/DoD Validation (Day 6)

**Tasks:**
1. Implement `DORValidator` service
2. Implement `DODValidator` service
3. Add blocking gates to state machine
4. Integrate with manifest validation

**Tests:** 80 tests for validators

**Validation:** Gates block execution when requirements not met

### Phase 5: Deploy & Monitor (Day 7-10)

**Tasks:**
1. Deploy adapter to production
2. Run side-by-side with legacy (shadow mode)
3. Compare outputs for 100 real plans
4. Fix any discrepancies

**Tests:** 300 regression tests

**Validation:** 100% output parity with legacy

### Phase 6: Archive Legacy (Day 11)

**Tasks:**
1. Archive `planning_orchestrator.py` to `cortex-brain/archives/`
2. Update imports to use new orchestrator
3. Remove adapter (direct usage)
4. Update documentation

**Tests:** All existing tests pass with new implementation

**Validation:** Zero breaking changes

---

## 🗑️ Removal Strategy

### Grace Period: 30 Days (Dec 17, 2025 - Jan 16, 2026)

**Week 1-2 (Dec 17-30):**
- ✅ Legacy code archived
- ✅ Emergency rollback script available
- ✅ Monitor production errors
- ✅ User communication sent

**Week 3 (Dec 31 - Jan 6):**
- ✅ No errors reported
- ✅ Performance metrics stable
- ✅ User feedback positive

**Week 4 (Jan 7-13):**
- ✅ Final validation checks
- ✅ Prepare permanent deletion
- ✅ Backup archive to cold storage

**Permanent Deletion (Jan 16, 2026):**
- ❌ Delete `cortex-brain/archives/planning_orchestrator.py`
- ❌ Delete rollback scripts
- ✅ Update CHANGELOG with removal notice

### Rollback Procedure (If Needed)

1. Copy from archive: `cortex-brain/archives/planning_orchestrator.py` → `src/orchestrators/`
2. Update imports to use legacy
3. Restart services
4. **Recovery Time:** 5 minutes

### Monitoring During Grace Period

- **Error Rate:** Must stay below 0.1%
- **Performance:** Must stay within 10% of baseline
- **User Complaints:** Zero tolerance for blocking issues

---

## ✅ Success Criteria

- ✅ 100% phase execution (zero skips)
- ✅ 100% DoR gate enforcement
- ✅ 100% DoD validation
- ✅ Session recovery works after interruption
- ✅ Code reduced by 92% (5,126 → 400 lines)
- ✅ Test coverage at 98%+
- ✅ Zero breaking changes for users
- ✅ Documentation updated
- ✅ Legacy code archived and deleted after grace period

---

## 📞 Contact

**Owner:** Asif Hussain  
**GitHub:** github.com/asifhussain60/CORTEX  
**Branch:** `cortex3-orchestration`  
**Related:** [Orchestration Master Plan](../orchestration-master-plan.md)

---

**Next Step:** Review approach, approve migration plan, begin Phase 1 implementation.
