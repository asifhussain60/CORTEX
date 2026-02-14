# Planning Orchestrator Agent

**Version:** 2.0 | **Updated:** 2026-02-14 | **Role:** Phase Execution & Stage Orchestration | **Architecture:** Dependency-Aware Scheduling | **Status:** ACTIVE ✅

---

## Agent Identity

**Planning Orchestrator Agent (PlanningOrchestrator)** — Executes phase-based plans by reading phase metadata from registry, evaluating dependencies, orchestrating parallel stage execution, and maintaining real-time synchronization with master plan.

**Mode:** Execution Orchestration (imperative)  
**Input Source:** Phase Registry (phase metadata)  
**Output:** Stage + Task execution coordination  
**Paradigm:** Dependency-aware scheduling + Real-time sync  
**Core Responsibility:** Transform declarative phase plans into executable orchestrated tasks

---

## Execution Model

### Phase Lifecycle (Planning Orchestrator Owns)

```
Phase Registration (Phase Registry) 
    ↓
Planning Orchestrator: READ phase metadata
    ├─ Check: All dependencies satisfied?
    └─ IF YES → READY | IF NO → BLOCKED
    ↓
Planning Orchestrator: EVALUATE dependency gate
    ├─ Hard blocks: Wait for Phase-N 100%
    ├─ Soft gates: Wait for Phase-N-Stage-M ≥ 70%
    └─ Parallel: Can start immediately with Stage-N
    ↓
Planning Orchestrator: ALLOCATE resources
    ├─ Assign Stage-1, Stage-2, ... (up to max_parallel_stages)
    └─ Spawn independent executors
    ↓
Planning Orchestrator: EXECUTE stages (parallel)
    ├─ Stage executor: Sequential tasks within stage
    ├─ Task executor: TDD cycle (tests → code → refactor)
    └─ Status updates: Real-time sync to master plan
    ↓
Planning Orchestrator: SYNC completion
    ├─ Verify: All tasks complete, tests passing
    ├─ Update: Phase status → COMPLETE
    └─ Unblock: Dependent phases now ready
```

---

## Component: Dependency Gate Evaluator

### Responsibility
Determine if a phase can start based on its dependency declarations.

### Algorithm

```python
def evaluate_phase_start_condition(phase: Phase) -> bool:
    """
    Evaluate if phase can start. Returns True if all dependencies satisfied.
    """
    if not phase.dependencies:
        return True  # No dependencies, can start immediately
    
    for dependency in phase.dependencies:
        status = get_phase_status(dependency.phase_id)
        
        if dependency.type == "blocks":
            # Hard block: Phase must be 100% complete
            if status != "COMPLETE":
                return False
        
        elif dependency.type == "requires_partial":
            # Soft gate: Check percentage
            progress = get_phase_progress(dependency.phase_id)
            required_pct = extract_percentage(dependency.condition)
            if progress < required_pct:
                return False
        
        elif dependency.type == "parallel_with_gate":
            # Parallel execution with sync point
            # Already allowed; sync will happen at gate boundary
            continue
        
        elif dependency.type == "optional_if":
            # Conditional gate: Check feature flag
            if not evaluate_condition(dependency.condition):
                continue
        
        elif dependency.type == "conflicts_with":
            # Mutual exclusion: Other phase must NOT be running
            other_status = get_phase_status(dependency.phase_id)
            if other_status in ["in_progress", "blocked"]:
                return False
    
    return True  # All dependencies satisfied
```

### Examples

**Hard Block Example (Phase-7 depends on Phase-1):**
```yaml
dependencies:
  - phase_id: 1
    type: "blocks"
    condition: "Phase-1 100% COMPLETE"
```
**Evaluation:** Phase-1 must be fully complete before Phase-7 starts.

**Soft Gate Example (Phase-2 partial gate):**
```yaml
dependencies:
  - phase_id: 1
    type: "requires_partial"
    condition: "Phase-1-Stage-1 >= 70%"
```
**Evaluation:** Phase-2 can start once Stage-1 (not entire Phase-1) reaches 70%.
**Benefit:** Parallelization opportunity; don't wait for all stages to complete.

**Parallel with Sync Example:**
```yaml
dependencies:
  - phase_id: 3
    type: "parallel_with_gate"
    condition: "Phase-3-Stage-2 completion blocks Phase-7-Stage-5 start"
```
**Evaluation:** Phase-7 and Phase-3 run in parallel, but Stage-5 (Phase-7) waits for Stage-2 (Phase-3) completion.

---

## Component: Stage executor (Parallel Coordinator)

### Responsibility
Spawn independent executors for each stages, coordinate progress, handle failures.

### Algorithm

```python
def execute_wave_tracks(phase: Phase) -> WaveExecutionResult:
    """
    Execute all stages in wave. Respects max_parallel_stages limit.
    Returns aggregated result.
    """
    # Step 1: Wait for wave to be ready
    if not evaluate_wave_start_condition(wave):
        mark_phase_blocked(wave)
        return WaveExecutionResult(status="BLOCKED", reason="Dependencies not met")
    
    # Step 2: Mark wave as in_progress
    update_master_plan(phase.id, status="in_progress", start_date=now())
    
    # Step 3: Prepare stages executors
    track_executors = []
    for stages in wave.stages:
        if stages.dependency_gate and not meets_track_gate(stages):
            mark_track_blocked(stages)
            continue
        
        executor = create_track_executor(stages)
        track_executors.append(executor)
    
    # Step 4: Execute stages with parallelism limit
    concurrent = min(len(track_executors), wave.max_parallel_stages)
    results = parallel_map(execute_track, track_executors, max_workers=concurrent)
    
    # Step 5: Aggregate results
    all_passed = all(r.status == "COMPLETE" for r in results)
    
    if all_passed:
        update_master_plan(phase.id, status="complete", completion_date=now())
        return WaveExecutionResult(status="COMPLETE", results=results)
    else:
        failed_tracks = [r for r in results if r.status != "COMPLETE"]
        update_master_plan(phase.id, status="blocked", blocker=failed_tracks)
        return WaveExecutionResult(status="BLOCKED", blocker=failed_tracks)
```

---

## Component: Real-Time Sync to Master Plan

### Responsibility
Keep master registry (PhaseArchitectureAgent) updated with execution progress.

### Sync Events

| Event | Action | Commit Message |
|-------|--------|-----------------|
| phase starts | Set `status: in_progress`, `start_date` | "Plan sync: Phase-N started" |
| stages starts | Update stages progress from 0% | "Plan sync: Phase-N Stage-N started" |
| Phase 50% | Update phase progress, increment test count | "Plan sync: Phase-N Phase-X 50%" |
| Phase complete | Set phase status, aggregate coverage | "Plan sync: Phase-N Phase-X complete" |
| stages complete | Aggregate stages metrics, unblock dependent stages | "Plan sync: Phase-N Stage-N complete" |
| Wave complete | Archive to `completed/`, unblock dependent phases | "Plan sync: Phase-N complete (moved to completed/)" |
| Blocker found | Set `status: blocked`, document reason | "Plan sync: Phase-N blocked - {reason}" |

### Sync Protocol (Per Phase Completion)

```python
def sync_phase_completion(phase: Phase, execution_result: ExecutionResult):
    """
    Called when a phase completes. Updates master plan registry.
    """
    # Step 1: Read current master index
    index = read_yaml("cortex-registry/_cortex-master/index.yaml")
    
    # Step 2: Locate phase entry
    wave = index.phases[phase.parent_phase]
    stages = wave.stages[phase.parent_stage]
    
    # Step 3: Update phase metrics
    stages.phases[phase.id].status = "complete"
    stages.phases[phase.id].completion_date = now()
    stages.phases[phase.id].tests_passing = execution_result.test_count
    stages.phases[phase.id].coverage_pct = execution_result.coverage
    
    # Step 4: Recalculate stages progress
    stages.progress_pct = (count_complete_phases(stages) / len(stages.phases)) * 100
    stages.tests_passing = sum(p.tests_passing for p in stages.phases)
    stages.last_updated = now()
    
    # Step 5: Recalculate phase progress
    wave.progress_pct = (sum(t.progress_pct for t in wave.stages) / len(wave.stages))
    wave.last_updated = now()
    
    # Step 6: Write updated registry
    write_yaml("cortex-registry/_cortex-master/index.yaml", index)
    
    # Step 7: Git commit (immutable history)
    git_commit(f"Plan sync: {phase.parent_phase}-{phase.parent_stage}-{phase.id} complete")
    
    # Step 8: Verify Implementation Truth
    verify_phase_completion_integrity(phase, execution_result)
    
    # Step 9: Check for newly unblocked waves
    for dependent_wave in find_dependent_waves(phase.parent_phase):
        if evaluate_wave_start_condition(dependent_wave):
            notify_wave_ready(dependent_wave)
```

---

## Component: Phase Readiness Broadcaster

### Responsibility
Notify downstream orchestrators when waves become ready (dependency gates satisfied).

### Notification Protocol

```python
def notify_dependent_waves(completed_wave: Wave):
    """
    After wave completes, check all downstream waves for readiness.
    Send notifications to any waves that became ready.
    """
    # Find all waves that depend on completed_wave
    dependent_waves = find_waves_depending_on(completed_wave.id)
    
    for wave in dependent_waves:
        # Evaluate if this wave can now start
        if evaluate_wave_start_condition(wave):
            # Notify MasterOrchestrator that wave is ready
            event = WaveReadyEvent(
                phase_id=phase.id,
                trigger_wave=completed_wave.id,
                timestamp=now()
            )
            publish_event("wave.ready", event)
            
            # Log for audit trail
            log_audit(f"Wave {phase.id} unblocked by Wave {completed_wave.id}")
```

---

## Component: Failure Recovery & Retry

### Responsibility
Handle phase/stages failures gracefully, enable retries, prevent cascading failures.

### Recovery Strategy

```python
def handle_phase_failure(phase: Phase, error: Exception) -> PhaseRecoveryAction:
    """
    Determine recovery action for failed phase.
    Returns: RETRY | ESCALATE | SKIP | ROLLBACK
    """
    # Step 1: Classify failure
    failure_type = classify_failure(error)
    
    # Step 2: Check retry eligibility
    retry_count = get_retry_count(phase)
    max_retries = 3  # Configurable
    
    if failure_type == "transient" and retry_count < max_retries:
        return PhaseRecoveryAction(action="RETRY", delay_seconds=60)
    
    elif failure_type == "test_failure":
        # Test failure is not transient - needs code fix
        return PhaseRecoveryAction(action="ESCALATE", reason="Test failure - code fix required")
    
    elif failure_type == "infrastructure":
        # Infrastructure failure - escalate to ops
        return PhaseRecoveryAction(action="ESCALATE", reason="Infrastructure issue")
    
    else:
        # Unknown failure - escalate to engineer
        return PhaseRecoveryAction(action="ESCALATE", reason=str(error))
```

### Cascading Failure Prevention

```python
def execute_track(stages: stages) -> TrackExecutionResult:
    """
    Execute stages phases sequentially. Stop on first failure to prevent cascade.
    """
    results = []
    
    for phase in stages.phases:
        try:
            result = execute_phase(phase)
            results.append(result)
            
            if result.status != "COMPLETE":
                # Stop execution; don't cascade failure to next phases
                mark_track_blocked(stages, reason=f"Phase {phase.id} failed")
                return TrackExecutionResult(
                    status="BLOCKED",
                    failed_phase=phase.id,
                    results=results
                )
        
        except Exception as e:
            recovery = handle_phase_failure(phase, e)
            
            if recovery.action == "RETRY":
                # Retry this phase
                continue  # Will retry in next iteration
            else:
                # Escalate - stop stages
                mark_track_blocked(stages, reason=recovery.reason)
                return TrackExecutionResult(
                    status="BLOCKED",
                    failed_phase=phase.id,
                    error=recovery.reason,
                    results=results
                )
    
    # All phases passed
    return TrackExecutionResult(status="COMPLETE", results=results)
```

---

## Integration with Other Orchestrators

### MasterOrchestrator Handoff
```
User Request (e.g., "/plan implement wave-7")
    ↓
MasterOrchestrator: Route to Planning Orchestrator
    ├─ Intent: PLAN
    └─ Target: Phase-7
    ↓
Planning Orchestrator: Evaluate Phase Readiness
    ├─ Check dependencies: Phase-1 complete? YES
    └─ Allocate stages: 5 concurrent
    ↓
Planning Orchestrator: Spawn TDDOrchestrator for each stages
    ├─ Stage-1: TDDOrchestrator (Phase-1 → Phase-2 → Phase-3)
    ├─ Stage-2: TDDOrchestrator (Phase-4 → Phase-5)
    └─ ...
    ↓
Planning Orchestrator: Real-time sync + blocker handling
    ├─ Phase complete → Update master registry
    ├─ stages complete → Notify dependent stages
    └─ Wave complete → Unblock downstream waves
    ↓
Result: Phase Execution complete, master plan synchronized
```

### stages-to-Phase Delegation
```
Stage executor
    ├─ Phase-1: Delegate to PhaseExecutor (TDD)
    │   ├─ Setup environment
    │   ├─ RED: Failing tests
    │   ├─ GREEN: Implementation
    │   ├─ REFACTOR: Quality improvement
    │   └─ Cleanup: Tests passing, coverage met
    │
    └─ Phase-2: Delegate to PhaseExecutor (TDD)
        ├─ Same TDD cycle
        └─ On completion, resume stages flow
```

---

## Parallel Execution Example: Phase-7

### Wave Configuration
```yaml
wave: 7
name: "Orchestrator Consolidation"
max_parallel_stages: 5
duration_estimate: 18 days

stages:
  - stages: 1
    name: "Core Strategies"
    phases: [Phase-1, Phase-2, Phase-3]
    can_parallel_with: [Stage-2, Stage-3, Stage-4, Stage-5]
  
  - stages: 2
    name: "Domain Orchestrators"
    phases: [Phase-4, Phase-5, Phase-6]
    dependency_gate: "Phase-7-Stage-1 >= 70%"  # Soft gate
    can_parallel_with: [Stage-3, Stage-4, Stage-5]
  
  - stages: 3
    name: "Support Elimination"
    phases: [Phase-7, Phase-8]
    dependency_gate: "Phase-7-Stage-1 >= 70%"
    can_parallel_with: [Stage-2, Stage-4, Stage-5]
  
  - stages: 4
    name: "Orphan Cleanup"
    phases: [Phase-9, Phase-10]
    can_parallel_with: [Stage-2, Stage-3, Stage-5]
  
  - stages: 5
    name: "LENS Physical Testing"
    phases: [Phase-11, Phase-12]
    can_parallel_with: [Stage-1, Stage-2, Stage-3, Stage-4]
```

### Execution Timeline
```
Day 0: Phase-7 starts
├─ Stage-1 (Core): Phase-1 → Phase-2 → Phase-3 (Days 1-7)
├─ Stage-5 (LENS): Phase-11 → Phase-12 (Days 1-5, parallel)
│
Day 3: Stage-1 reaches 70%, gates open
├─ Stage-2 (Domain): Phase-4 → Phase-5 → Phase-6 (Days 3-10)
├─ Stage-3 (Support): Phase-7 → Phase-8 (Days 3-9)
│
Day 8: Stage-1 complete (100%)
├─ All stages continue independently
│
Day 10: Stage-5 (LENS) complete, Stage-2 midway
├─ No blocking dependency; continue
│
Day 14: Stage-2, Stage-3, Stage-4 complete
│
Day 18: Phase-7 complete

Total Timeline: 18 days (vs 24 sequential)
Efficiency Gain: 25% timeline reduction
```

---

## Configuration & Tunables

### Wave Configuration (Per-Wave)
```yaml
wave: N
max_parallel_stages: 5           # How many stages concurrent
retry_policy:
  max_retries: 3
  backoff_seconds: 60
timeout_policy:
  per_phase: 3600                # Seconds per phase
  per_track: 86400               # Seconds per stages
  per_wave: 1728000              # Seconds per wave (20 days)
sync_frequency: 300              # Sync to master plan every 5 min
blocker_escalation_delay: 600    # Escalate to engineer after 10 min
```

### Global Configuration
```yaml
planning_orchestrator:
  max_concurrent_waves: 2        # Run max 2 waves in parallel
  phase_executor_pool_size: 10   # Executor thread pool
  sync_buffer_size: 100          # Buffer phase events before flush
  dependency_check_interval: 60  # Check Phase Readiness every 60s
```

---

## Monitoring & Observability

### Metrics Emitted
```
planning_orchestrator_waves_active{phase_id="7"}
planning_orchestrator_tracks_running{phase_id="7", stage_id="1"}
planning_orchestrator_phase_duration_seconds{phase_id="7", phase_id="1"}
planning_orchestrator_sync_lag_seconds  # Lag between execution and registry update
planning_orchestrator_dependency_gates_blocking{phase_id="8"}
planning_orchestrator_failures_total{failure_type="transient|test|infrastructure"}
```

### Dashboard Views
- phase progress (% complete, ETA)
- Stage Parallelism utilization (active stages vs max)
- Dependency graph (visual, unblocking events)
- Blocker alerts (escalation triggers)
- Phase execution timeline (Gantt chart)

---

## Quick Reference

| Concept | Definition | Owner |
|---------|-----------|-------|
| **Wave** | ROI batch (2-4 weeks) | PhaseArchitectureAgent |
| **stages** | Parallel execution unit | PlanningOrchestrator |
| **Phase** | TDD deliverable | TDDOrchestrator (delegated) |
| **Dependency** | Condition for wave start | PlanningOrchestrator (evaluates) |
| **Sync** | Registry update | PlanningOrchestrator (executes) |
| **Failure Recovery** | Retry/Escalate logic | PlanningOrchestrator |

---

*v1.0 — Planning Orchestrator for dependency-aware Phase Execution, parallel stage orchestration, real-time registry sync, and failure recovery. Consumes declarative wave plans from PhaseArchitectureAgent, transforms to executable orchestrated tasks.*
