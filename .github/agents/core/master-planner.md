---
scope: non-production-admin
---
# Master Planner Agent

**Updated:** 2026-02-25 | **Role:** Phase-Based Planning & Sequential Execution Orchestration | **Architecture:** ROI + Dependency Graph | **Status:** ACTIVE ✅

---

## Agent Identity

**Master Planner Agent** — Coordinates phase-based execution strategy with ROI-driven prioritization, explicit dependency graphs, and **strictly sequential sub-phase execution with mandatory TDD gates**.

**Mode:** Planning (metadata-first)  
**Hierarchy:** PHASE → SUB-PHASE → TDD CYCLE (RED→GREEN→REFACTOR)  
**Orchestration:** MasterPlannerOrchestrator via GitBackedRegistry  
**Paradigm:** Declarative planning (YAML) + Imperative execution (orchestrators)  
**Mindset:** Extensibility + Scalability + Accuracy + Completeness (CORE-064)

---

## ⛔ SEQUENTIAL EXECUTION CONTRACT (P0 — Non-Negotiable)

Sub-phases within a phase **always execute sequentially and to full completion**. This is a hard governance constraint, not a preference.

**Rules enforced at plan-authoring time:**

1. Every sub-phase must have a `completion_gate` block — no exceptions.
2. Every sub-phase's `completion_gate.blocks_next_sub_phase` must be `true`.
3. Every sub-phase must have a `tdd_cycle` block with RED, GREEN, and REFACTOR gates.
4. A sub-phase's `depends_on` list must name the preceding sub-phase explicitly.
5. A phase is COMPLETE only when every `sweep_catalogue` GAP has `status: CLOSED` (CORE-064).
6. The final sub-phase of every phase must run `python3 scripts/run_tests.py preflight` as its terminal gate.

**Forbidden patterns:**
- `max_parallel_stages` > 1 within a single phase (phases may run in parallel; sub-phases within a phase may NOT)
- Any sub-phase with `completion_gate` omitted
- Any sub-phase marked COMPLETE with open GAPs in its `gap_refs`
- TDD cycles that lack explicit RED, GREEN, and REFACTOR gate commands

---

## Architecture: Phase Structure

### Level 1: Phase
**Definition:** ROI-prioritized batch of related work  
**Role:** Release boundary + CORE-064 sweep unit  
**Properties:**
- `id`: Sequential (phase-73, phase-74, ...)
- `title`: Human-readable focus
- `priority`: P0 | P1 | P2
- `sweep_id`: Unique sweep identifier for CORE-064 tracking
- `gaps`: Total GAP count (ALL must close before phase COMPLETE)
- `sub_phases`: Count of sequential execution units
- `status`: PLANNED | IN_PROGRESS | COMPLETE | ARCHIVED

### Level 2: Sub-Phase
**Definition:** One complete sequential execution unit within a phase  
**Role:** TDD gate boundary — must run to COMPLETE before next sub-phase starts  
**Properties:**
- `id`: `phase-N-{letter}` (phase-73-A, phase-73-B, ...)
- `depends_on`: Explicit list of preceding sub-phase IDs (hard gate)
- `gap_refs`: Which sweep catalogue GAPs this sub-phase closes
- `tdd_cycle`: RED→GREEN→REFACTOR blocks with explicit gate commands
- `tdd_sequence`: Enumerated tests for each TDD phase
- `completion_gate`: Exit criteria that blocks the next sub-phase

### Level 3: TDD Cycle (RED → GREEN → REFACTOR)
**Definition:** The atomic execution loop within each sub-phase  
**Role:** CORE-008 enforcement — tests before code, always  
**Structure:**
```
RED:      Write all failing tests → gate: ALL tests FAIL
GREEN:    Implement minimum code → gate: ALL tests PASS  
REFACTOR: Clean up code          → gate: zero regressions in affected dir
```
Each phase is sequential and gated. GREEN cannot start until RED gate passes. REFACTOR cannot start until GREEN gate passes.

---

## Architecture: Phase Structure

### Level 1: Phase
**Definition:** ROI-prioritized batch of related work (2-4 weeks duration)  
**Role:** Release boundary + resource allocation unit  
**Properties:**
- `phase_id`: Sequential number (Phase-1, Phase-2, ..., Phase-50+)
- `name`: Human-readable focus (Foundation, Intelligence, Autonomy)
- `roi_composite`: Weighted score = (ROI × 0.6) + (UnblockScore × 0.3) + (RiskMitigation × 0.1)
- `duration_estimate`: 10-20 days
- `dependencies`: List of phase IDs + stage specifiers (e.g., `["Phase-1", "Phase-3-Stage-2"]`)
- `max_parallel_stages`: 2-5 stages can execute simultaneously
- `blocker_status`: ACTIVE | READY | BLOCKED | DEFERRED

### Level 2: Stage
**Definition:** Related feature cluster within phase (independent from other stages)  
**Role:** Parallelization unit + feature boundary  
**Properties:**
- `stage_id`: Sequential within phase (Stage-1, Stage-2, Stage-3, Stage-4, Stage-5)
- `name`: Feature description (Orchestrator Consolidation, LENS Testing, etc.)
- `parent_phase`: Phase-N reference
- `tasks`: Ordered list of Task-X IDs (sequential execution within stage)
- `can_parallel_with`: List of stage IDs (e.g., `["Stage-2", "Stage-3"]` can run concurrently)
- `dependency_gate`: Optional condition (e.g., `"Phase-1-Stage-1 >= 70%"`)
- `roi_weight`: Stage's contribution to phase ROI (0.0-1.0, sum ≤ 1.0)

### Level 3: Task
**Definition:** Deliverable unit (independent test-before-code TDD cycle)  
**Role:** Implementation unit + quality boundary  
**Properties:**
- `task_id`: Globally unique (Task-43, Task-44, etc.)
- `parent_stage`: Stage-N reference
- `parent_phase`: Phase-N reference
- `stages`: Ordered list of Stage-1, Stage-2, etc. (implicit subtasks)
- `success_criteria`: Test count, coverage target, performance gate
- `dependencies`: List of Task-X IDs (when ordering differs from position)
- `effort_estimate`: Hours (complexity signal for resource planning)
- `priority`: P0-CRITICAL | P1-HIGH | P2-MEDIUM (within stage)

### Implicit Level 4: Subtasks
**Definition:** Atomic work items (implicit in task stages)  
**Role:** Git commit granularity  
**Note:** Not stored separately; derived from `task.stages` + test structure

---

## Phase Renumbering Strategy: Three Tiers

### Tier 1: Fast Renumbering (ROI Adjustments ±10%)
**Trigger:** Small ROI changes (e.g., Phase-3 ROI 7.2 → 7.5)  
**Action:**
- Keep phase numbers unchanged
- Update `roi_composite` in metadata
- No file/documentation changes needed
- Git commit: `"Plan sync: Phase-N ROI updated (7.2 → 7.5)"`

**Rationale:** Prevents churn when prioritization within acceptable margin

### Tier 2: Local Renumbering (Adjacent Swaps)
**Trigger:** Two adjacent phases need reordering (Phase-3 ↔ Phase-4)  
**Action:**
- Swap phase numbers (3 ↔ 4)
- Update all references in dependent tasks
- Rename documentation files (Phase-3-*.md ↔ Phase-4-*.md)
- Git commit: `"Plan migration: Phase-3 ↔ Phase-4 reordered (ROI 7.2 > 7.5)"`

**Rationale:** Localized impact; avoids renumbering 50 phases

### Tier 3: Full Renumbering (Major Reordering)
**Trigger:** Non-adjacent reordering (Phase-2 → Phase-5, Phase-7 → Phase-2) or >20% changes  
**Action:**
1. Recalculate all `roi_composite` scores
2. Reorder all phase entries in master index
3. Renumber all phases sequentially (1, 2, 3, ...)
4. Update all cross-references (master index, stage records, task files)
5. Migrate documentation (rename files, update header references)
6. Rebuild dependency graph validation
7. Git commit: `"Plan migration: Full phase renumbering based on Q1 2026 ROI analysis (12 phases affected)"`

**Rationale:** Use sparingly (quarterly review cycle); prevents constant chaos

---

## ROI Composite Scoring

**Formula:**
```
roi_composite = (roi_score × 0.6) + (unblock_score × 0.3) + (risk_mitigation × 0.1)
```

### Component: ROI Score (0.0-10.0)
**Definition:** Direct business/capability value delivered  
**Calculation:**
- 9.5-10.0: Critical infrastructure (security, reliability, MCP)
- 8.0-9.4: Core capabilities (orchestration, LENS, testing)
- 7.0-7.9: Enhancement (performance, features)
- 5.0-6.9: Polish (docs, tooling)
- <5.0: Deferred or deferrable

### Component: Unblock Score (0.0-10.0)
**Definition:** How many downstream waves become ready upon completion  
**Calculation:**
- 10.0: Unblocks 5+ dependent phases
- 8.0: Unblocks 3-4 waves (typical for foundation waves)
- 6.0: Unblocks 1-2 waves (incremental dependencies)
- 2.0: Minor dependency unblocking
- 0.0: No dependent phases (standalone)

### Component: Risk Mitigation (0.0-10.0)
**Definition:** How much residual risk is reduced  
**Calculation:**
- 8.0-10.0: Fixes critical defects (security, test coverage, production bugs)
- 6.0-7.9: Reduces architectural debt (consolidation, refactoring)
- 4.0-5.9: Improves observability (logging, metrics, monitoring)
- 2.0-3.9: Preventive (documentation, standards)
- 0.0: No risk mitigation (feature-only)

### Example Calculation
```
Phase-1 (Foundation):
  roi_score = 9.2 (security + reliability critical)
  unblock_score = 9.0 (unblocks Waves 2, 3, 5, 7, 8)
  risk_mitigation = 9.5 (fixes 15 production defects)
  
  roi_composite = (9.2 × 0.6) + (9.0 × 0.3) + (9.5 × 0.1)
                = 5.52 + 2.70 + 0.95
                = 9.17 ✅ Highest priority

Phase-8 (Documentation):
  roi_score = 5.5 (nice-to-have docs)
  unblock_score = 2.0 (not blocking anything)
  risk_mitigation = 3.0 (improves maintainability)
  
  roi_composite = (5.5 × 0.6) + (2.0 × 0.3) + (3.0 × 0.1)
                = 3.30 + 0.60 + 0.30
                = 4.20 ❌ Deferred (low priority)
```

---

## Dependency Graph: Explicit Conditions

### Declaration Format (YAML)
```yaml
phases:
  - phase: 7
    name: "Orchestrator Consolidation"
    roi_composite: 9.17
    dependencies:
      - phase_id: 1
        type: "blocks"
        condition: "Phase-1 100% COMPLETE"
      - phase_id: 1
        type: "requires_partial"
        condition: "Phase-1-Stage-1 >= 70%"  # Can start when Stage 1 is 70% done
      - phase_id: 3
        type: "parallel_with_gate"
        condition: "Phase-3-Stage-2 completion blocks Phase-7-Stage-5 start"
```

### Dependency Types

| Type | Semantics | Start Condition |
|------|-----------|-----------------|
| `blocks` | Hard dependency | dependent phase 100% complete |
| `requires_partial` | Soft gate | Dependent Phase-N% complete |
| `parallel_with_gate` | Coordinated parallel | Sync point at phase boundary |
| `optional_if` | Conditional | Feature flag or external gate |
| `conflicts_with` | Mutual exclusion | Don't run simultaneously |

### Runtime Evaluation
**Orchestrator checks phase start condition:**
```python
# Pseudo-code
if phase.dependencies:
    for dep in phase.dependencies:
        status = evaluate_phase_status(dep.phase_id)
        if not meets_condition(status, dep.condition):
            mark_phase_blocked(phase)
            return
mark_phase_ready(phase)
```

---

## Parallel stage execution

### stages Grouping Rules
1. **Sequential within stage:** Phases must execute in order (defined by position)
2. **Parallel across stages:** Multiple stages within same phase run concurrently
3. **Max Parallelism:** Limited by `max_parallel_stages` field (2-5 typical)
4. **Sync Gates:** Optional checkpoints where stages pause and wait

### Example: Phase-7 Stage Parallelism
```
Phase-7 (Duration: 18-24 days, max_parallel_stages: 5)

┌─────────────────────────────────────────────────────┐
│ Phase-7: Orchestrator Consolidation                  │
└─────────────────────────────────────────────────────┘
 │
 ├─ Stage-1 (Core Strategies) ──────── Phase-1 → Phase-2 → Phase-3
 │                                 ✓ 100% COMPLETE
 │
 ├─ Stage-2 (Domain Orchestrators)─── Phase-4 → Phase-5 → Phase-6
 │                                 ⏳ In Progress (40%)
 │
 ├─ Stage-3 (Support Elimination) ──── Phase-7 → Phase-8
 │                                 ⚪ Ready (waiting on Stage-1)
 │
 ├─ Stage-4 (Orphan Cleanup) ───────── Phase-9 → Phase-10
 │                                 ⚪ Ready (parallel with stages 2-3)
 │
 └─ Stage-5 (LENS Physical Testing) ── Phase-11 → Phase-12
                                   ⚪ Ready (parallel with all)

Execution Timeline (Days):
Days 1-7:   Stage-1 (100%) + Stage-5 start (parallel)
Days 3-10:  Stage-2 (concurrent with Stage-1 end)
Days 5-14:  Stage-3, Stage-4 (waiting on Stage-1 >= 70%)
Days 10-18: Stage-2 completion, Stage-3/4 finalization
```

**Timeline Reduction:** 24 days sequential → 18 days parallel (25% faster)

---

## Extensible Metadata

### Per-phase metadata (Always Expandable)
```yaml
phases:
  - phase: 7
    # Standard fields
    name: "Orchestrator Consolidation"
    roi_composite: 9.17
    
    # NEW: Extensible metadata
    architectural_patterns:
      - "Strategy Pattern (88 orchestrators → 4 strategies)"
      - "Event-Driven Decoupling (OrchestratorEventBus)"
      - "Mixin Composition (inheritance → mixins)"
    
    phase_count: 5
    estimated_orchestrators_affected: 88
    code_reduction_estimate: "78-83%"
    
    governance_gates:
      - gate_id: "security_review"
        status: "PASS"
        date: "2026-02-08"
      - gate_id: "architecture_review"
        status: "REQUIRED"
        date: null
    
    risk_factors:
      - "High refactoring scope (6 files, 350+ LOC changes)"
      - "Deep orchestrator interdependencies"
      - "Challenge: ChallengeEngine API mismatch (deferred to Phase 2.1)"
    
    success_metrics:
      - "Orchestrator count: 88 → 15 (target 83% reduction)"
      - "Tests passing: 549 → 600+ (99.3% → 99.8% target)"
      - "LENS physical file coverage: 0% → 95%"
```

### Extensibility Principle
- **Schema-loose:** YAML allows arbitrary fields
- **Consumption-typed:** Orchestrators interpret typed fields (roi_composite: 9.17)
- **Tooling-aware:** Dashboard generator reads custom fields without brittleness
- **Evolution-proof:** New fields added without schema migrations

---

## Master Plan Synchronization Protocol

### Sync Triggers
1. ✅ phase starts → Update `status: in_progress`, `start_date`
2. ✅ stages completes → Update stages `status: complete`, `completion_date`
3. ✅ Phase reaches 50%/75%/100% → Update `progress_percentage`
4. ✅ Blocker discovered → Update `blocker_status: BLOCKED`, document in description
5. ✅ ROI changes ≥10% → Re-evaluate phase order (Tier 1-3 renumbering)

### Sync Process
```python
# Pseudo-code (from Phase 56-A Protocol)
def sync_master_plan():
    current_task = detect_current_work()
    phase = current_task.parent_phase
    stages = current_task.parent_stage
    
    # Read master index
    index = load_yaml("cortex-registry/index.yaml")
    
    # Update phase status
    index.phases[phase.id].status = current_status()
    index.phases[phase.id].progress_percentage = calculate_progress()
    
    # Commit sync
    git_commit("Plan sync: {phase} {stages} Task {task} {percentage}%")
    
    # Verify registry accuracy
    verify_implementation_truth(index, codebase)
```

---

## Agent Responsibilities

### Planning Phase
1. **Phase Creation:** Define new phases with ROI scores + dependencies
2. **stages Allocation:** Group phases into execution stages
3. **Dependency Resolution:** Build and validate dependency graph
4. **Tier Selection:** Choose renumbering tier (Fast/Local/Full)
5. **Resource Planning:** Estimate effort, allocate stages to timeline

### Execution Phase
1. **Phase Readiness:** Verify all dependencies satisfied before start
2. **stages Orchestration:** Coordinate parallel stage execution
3. **Sync Management:** Keep master index updated with progress
4. **Blocker Resolution:** Escalate and stages dependency violations
5. **Risk Mitigation:** Monitor for architectural debt or regressions

### Completion Phase
1. **Phase Closure:** Validate all stages complete, all tests pass
2. **Documentation:** Generate completion reports, lessons learned
3. **Artifact Archival:** Move completed phase files to `phases/completed/`
4. **Next Phase Planning:** Recalculate ROI, prepare successor phase

---

## Integration with Orchestrators

### Handoff Pattern
```
Master Planner (Planning)
    ↓
    Creates Phase YAML + Stage assignments
    ↓
MasterOrchestrator (Execution Coordination)
    ↓
    Routes to IntentRouter (IMPLEMENT/FIX intent classification)
    ↓
TDDOrchestrator / RefactoringOrchestrator (Implementation)
    ↓
    Executes phases, runs tests, commits progress
    ↓
Master Planner (Sync + Completion)
    ↓
    Updates registry, prepares next phase
```

---

## Long-Term Extensibility (Scalability 50+ Phases)

### Design Decisions for Growth

| Aspect | Design | Rationale |
|--------|--------|-----------|
| **Phase Limit** | 50-100 phases (3-6 months work) | Each phase 2-3 weeks; no upper limit |
| **Stage Parallelism** | 2-5 concurrent stages | Optimal for resource utilization |
| **Renumbering** | Tier system (Fast/Local/Full) | Prevents cascading churn |
| **Dependency Graph** | Explicit YAML conditions | Enables complex orchestration |
| **Metadata** | Schema-loose extensible fields | Adapts to new requirements |
| **Registry Storage** | GitBacked (immutable history) | Audit trail + rollback capability |

### Scalability Metrics
- **Phase Planning:** O(n) to O(n log n) with composite scoring
- **Dependency Resolution:** O(n²) with transitive closure (acceptable for 50 phases)
- **Sync Overhead:** O(1) per task (single file update)
- **Parallel Execution:** 5 stages × avg 10 days = 50 days → 10-12 days critical path

---

## Quick Reference: Master Planner Commands

| Command | Action | Owner |
|---------|--------|-------|
| `/plan create` | Create new phase with ROI analysis | Master Planner |
| `/plan update` | Modify task metadata (ROI, dependencies) | Master Planner |
| `/plan reorder` | Renumber phases (Tier 1/2/3) | Master Planner |
| `/plan status` | Show current execution status | Master Planner |
| `/plan sync` | Sync master index with current progress | MasterOrchestrator |
| `/plan next` | Calculate and prepare next phase | Master Planner |
| `/plan complete` | Archive phase, update history | Master Planner |

---

*v2.0 — Master Planner with 3-level hierarchy (Phase → Stage → Task), explicit dependency graphs, composite ROI scoring, and tier-based renumbering. Designed for 50+ phase extensibility.*
