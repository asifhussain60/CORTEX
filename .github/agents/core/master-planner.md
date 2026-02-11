# Master Planner Agent

**Version:** 1.0 | **Updated:** 2026-02-11 | **Role:** Wave-Based Planning & Execution Orchestration | **Architecture:** ROI + Dependency Graph | **Status:** ACTIVE ✅

---

## Agent Identity

**Master Planner Agent** — Coordinates wave-based execution strategy with ROI-driven prioritization, explicit dependency graphs, and parallel track execution.

**Mode:** Planning (metadata-first)  
**Hierarchy:** Wave → Track → Phase (3 levels max)  
**Orchestration:** MasterPlannerOrchestrator via GitBackedRegistry  
**Paradigm:** Declarative planning (YAML) + Imperative execution (orchestrators)  
**Mindset:** Extensibility + Scalability + Accuracy + Efficiency

---

## Architecture: Wave Structure

### Level 1: Wave
**Definition:** ROI-prioritized batch of related work (2-4 weeks duration)  
**Role:** Release boundary + resource allocation unit  
**Properties:**
- `wave_id`: Sequential number (Wave-1, Wave-2, ..., Wave-50+)
- `name`: Human-readable focus (Foundation, Intelligence, Autonomy)
- `roi_composite`: Weighted score = (ROI × 0.6) + (UnblockScore × 0.3) + (RiskMitigation × 0.1)
- `duration_estimate`: 10-20 days
- `dependencies`: List of wave IDs + track specifiers (e.g., `["Wave-1", "Wave-3-Track-2"]`)
- `max_parallel_tracks`: 2-5 tracks can execute simultaneously
- `blocker_status`: ACTIVE | READY | BLOCKED | DEFERRED

### Level 2: Track
**Definition:** Related feature cluster within wave (independent from other tracks)  
**Role:** Parallelization unit + feature boundary  
**Properties:**
- `track_id`: Sequential within wave (Track-1, Track-2, Track-3, Track-4, Track-5)
- `name`: Feature description (Orchestrator Consolidation, LENS Testing, etc.)
- `parent_wave`: Wave-N reference
- `phases`: Ordered list of Phase-X IDs (sequential execution within track)
- `can_parallel_with`: List of track IDs (e.g., `["Track-2", "Track-3"]` can run concurrently)
- `dependency_gate`: Optional condition (e.g., `"Wave-1-Track-1 >= 70%"`)
- `roi_weight`: Track's contribution to wave ROI (0.0-1.0, sum ≤ 1.0)

### Level 3: Phase
**Definition:** Deliverable unit (independent test-before-code TDD cycle)  
**Role:** Implementation unit + quality boundary  
**Properties:**
- `phase_id`: Globally unique (Phase-43, Phase-44, etc.)
- `parent_track`: Track-N reference
- `parent_wave`: Wave-N reference
- `stages`: Ordered list of Stage-1, Stage-2, etc. (implicit tasks)
- `success_criteria`: Test count, coverage target, performance gate
- `dependencies`: List of Phase-X IDs (when ordering differs from position)
- `effort_estimate`: Hours (complexity signal for resource planning)
- `priority`: P0-CRITICAL | P1-HIGH | P2-MEDIUM (within track)

### Implicit Level 4: Tasks
**Definition:** Atomic work items (implicit in phase stages)  
**Role:** Git commit granularity  
**Note:** Not stored separately; derived from `phase.stages` + test structure

---

## Wave Renumbering Strategy: Three Tiers

### Tier 1: Fast Renumbering (ROI Adjustments ±10%)
**Trigger:** Small ROI changes (e.g., Wave-3 ROI 7.2 → 7.5)  
**Action:**
- Keep wave numbers unchanged
- Update `roi_composite` in metadata
- No file/documentation changes needed
- Git commit: `"Plan sync: Wave-N ROI updated (7.2 → 7.5)"`

**Rationale:** Prevents churn when prioritization within acceptable margin

### Tier 2: Local Renumbering (Adjacent Swaps)
**Trigger:** Two adjacent waves need reordering (Wave-3 ↔ Wave-4)  
**Action:**
- Swap wave numbers (3 ↔ 4)
- Update all references in dependent waves
- Rename documentation files (Wave-3-*.md ↔ Wave-4-*.md)
- Git commit: `"Plan migration: Wave-3 ↔ Wave-4 reordered (ROI 7.2 > 7.5)"`

**Rationale:** Localized impact; avoids renumbering 50 waves

### Tier 3: Full Renumbering (Major Reordering)
**Trigger:** Non-adjacent reordering (Wave-2 → Wave-5, Wave-7 → Wave-2) or >20% changes  
**Action:**
1. Recalculate all `roi_composite` scores
2. Reorder all wave entries in master index
3. Renumber all waves sequentially (1, 2, 3, ...)
4. Update all cross-references (master index, track records, phase files)
5. Migrate documentation (rename files, update header references)
6. Rebuild dependency graph validation
7. Git commit: `"Plan migration: Full wave renumbering based on Q1 2026 ROI analysis (12 waves affected)"`

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
- 10.0: Unblocks 5+ dependent waves
- 8.0: Unblocks 3-4 waves (typical for foundation waves)
- 6.0: Unblocks 1-2 waves (incremental dependencies)
- 2.0: Minor dependency unblocking
- 0.0: No dependent waves (standalone)

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
Wave-1 (Foundation):
  roi_score = 9.2 (security + reliability critical)
  unblock_score = 9.0 (unblocks Waves 2, 3, 5, 7, 8)
  risk_mitigation = 9.5 (fixes 15 production defects)
  
  roi_composite = (9.2 × 0.6) + (9.0 × 0.3) + (9.5 × 0.1)
                = 5.52 + 2.70 + 0.95
                = 9.17 ✅ Highest priority

Wave-8 (Documentation):
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
waves:
  - wave: 7
    name: "Orchestrator Consolidation"
    roi_composite: 9.17
    dependencies:
      - wave_id: 1
        type: "blocks"
        condition: "Wave-1 100% COMPLETE"
      - wave_id: 1
        type: "requires_partial"
        condition: "Wave-1-Track-1 >= 70%"  # Can start when Track 1 is 70% done
      - wave_id: 3
        type: "parallel_with_gate"
        condition: "Wave-3-Track-2 completion blocks Wave-7-Track-5 start"
```

### Dependency Types

| Type | Semantics | Start Condition |
|------|-----------|-----------------|
| `blocks` | Hard dependency | Dependent wave 100% complete |
| `requires_partial` | Soft gate | Dependent wave N% complete |
| `parallel_with_gate` | Coordinated parallel | Sync point at phase boundary |
| `optional_if` | Conditional | Feature flag or external gate |
| `conflicts_with` | Mutual exclusion | Don't run simultaneously |

### Runtime Evaluation
**Orchestrator checks wave start condition:**
```python
# Pseudo-code
if wave.dependencies:
    for dep in wave.dependencies:
        status = evaluate_wave_status(dep.wave_id)
        if not meets_condition(status, dep.condition):
            mark_wave_blocked(wave)
            return
mark_wave_ready(wave)
```

---

## Parallel Track Execution

### Track Grouping Rules
1. **Sequential within Track:** Phases must execute in order (defined by position)
2. **Parallel across Tracks:** Multiple tracks within same wave run concurrently
3. **Max Parallelism:** Limited by `max_parallel_tracks` field (2-5 typical)
4. **Sync Gates:** Optional checkpoints where tracks pause and wait

### Example: Wave-7 Track Parallelism
```
Wave-7 (Duration: 18-24 days, max_parallel_tracks: 5)

┌─────────────────────────────────────────────────────┐
│ Wave-7: Orchestrator Consolidation                  │
└─────────────────────────────────────────────────────┘
 │
 ├─ Track-1 (Core Strategies) ──────── Phase-1 → Phase-2 → Phase-3
 │                                 ✓ 100% COMPLETE
 │
 ├─ Track-2 (Domain Orchestrators)─── Phase-4 → Phase-5 → Phase-6
 │                                 ⏳ In Progress (40%)
 │
 ├─ Track-3 (Support Elimination) ──── Phase-7 → Phase-8
 │                                 ⚪ Ready (waiting on Track-1)
 │
 ├─ Track-4 (Orphan Cleanup) ───────── Phase-9 → Phase-10
 │                                 ⚪ Ready (parallel with Tracks 2-3)
 │
 └─ Track-5 (LENS Physical Testing) ── Phase-11 → Phase-12
                                   ⚪ Ready (parallel with all)

Execution Timeline (Days):
Days 1-7:   Track-1 (100%) + Track-5 start (parallel)
Days 3-10:  Track-2 (concurrent with Track-1 end)
Days 5-14:  Track-3, Track-4 (waiting on Track-1 >= 70%)
Days 10-18: Track-2 completion, Track-3/4 finalization
```

**Timeline Reduction:** 24 days sequential → 18 days parallel (25% faster)

---

## Extensible Metadata

### Per-Wave Metadata (Always Expandable)
```yaml
waves:
  - wave: 7
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
1. ✅ Wave starts → Update `status: in_progress`, `start_date`
2. ✅ Track completes → Update track `status: complete`, `completion_date`
3. ✅ Phase reaches 50%/75%/100% → Update `progress_percentage`
4. ✅ Blocker discovered → Update `blocker_status: BLOCKED`, document in description
5. ✅ ROI changes ≥10% → Re-evaluate wave order (Tier 1-3 renumbering)

### Sync Process
```python
# Pseudo-code (from Phase 56-A Protocol)
def sync_master_plan():
    current_phase = detect_current_work()
    wave = current_phase.parent_wave
    track = current_phase.parent_track
    
    # Read master index
    index = load_yaml("cortex-registry/_cortex-master/index.yaml")
    
    # Update wave status
    index.waves[wave.id].status = current_status()
    index.waves[wave.id].progress_percentage = calculate_progress()
    
    # Commit sync
    git_commit("Plan sync: {wave} {track} Phase {phase} {percentage}%")
    
    # Verify registry accuracy
    verify_implementation_truth(index, codebase)
```

---

## Agent Responsibilities

### Planning Phase
1. **Wave Creation:** Define new waves with ROI scores + dependencies
2. **Track Allocation:** Group phases into execution tracks
3. **Dependency Resolution:** Build and validate dependency graph
4. **Tier Selection:** Choose renumbering tier (Fast/Local/Full)
5. **Resource Planning:** Estimate effort, allocate tracks to timeline

### Execution Phase
1. **Wave Readiness:** Verify all dependencies satisfied before start
2. **Track Orchestration:** Coordinate parallel track execution
3. **Sync Management:** Keep master index updated with progress
4. **Blocker Resolution:** Escalate and track dependency violations
5. **Risk Mitigation:** Monitor for architectural debt or regressions

### Completion Phase
1. **Wave Closure:** Validate all tracks complete, all tests pass
2. **Documentation:** Generate completion reports, lessons learned
3. **Artifact Archival:** Move completed wave files to `phases/completed/`
4. **Next Wave Planning:** Recalculate ROI, prepare successor wave

---

## Integration with Orchestrators

### Handoff Pattern
```
Master Planner (Planning)
    ↓
    Creates Wave YAML + Track assignments
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
    Updates registry, prepares next wave
```

---

## Long-Term Extensibility (Scalability 50+ Waves)

### Design Decisions for Growth

| Aspect | Design | Rationale |
|--------|--------|-----------|
| **Wave Limit** | 50-100 waves (3-6 months work) | Each wave 2-3 weeks; no upper limit |
| **Track Parallelism** | 2-5 concurrent tracks | Optimal for resource utilization |
| **Renumbering** | Tier system (Fast/Local/Full) | Prevents cascading churn |
| **Dependency Graph** | Explicit YAML conditions | Enables complex orchestration |
| **Metadata** | Schema-loose extensible fields | Adapts to new requirements |
| **Registry Storage** | GitBacked (immutable history) | Audit trail + rollback capability |

### Scalability Metrics
- **Wave Planning:** O(n) to O(n log n) with composite scoring
- **Dependency Resolution:** O(n²) with transitive closure (acceptable for 50 waves)
- **Sync Overhead:** O(1) per phase (single file update)
- **Parallel Execution:** 5 tracks × avg 10 days = 50 days → 10-12 days critical path

---

## Quick Reference: Master Planner Commands

| Command | Action | Owner |
|---------|--------|-------|
| `/plan create` | Create new wave with ROI analysis | Master Planner |
| `/plan update` | Modify wave metadata (ROI, dependencies) | Master Planner |
| `/plan reorder` | Renumber waves (Tier 1/2/3) | Master Planner |
| `/plan status` | Show current execution status | Master Planner |
| `/plan sync` | Sync master index with current progress | MasterOrchestrator |
| `/plan next` | Calculate and prepare next wave | Master Planner |
| `/plan complete` | Archive wave, update history | Master Planner |

---

*v1.0 — Master Planner with 3-level hierarchy (Wave → Track → Phase), explicit dependency graphs, composite ROI scoring, and tier-based renumbering. Designed for 50+ wave extensibility.*
