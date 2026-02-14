---
agent_id: cortex-master-plan-auditor
version: 1.0
status: active
layer: core
capabilities:
  - plan_reality_synchronization
  - wave_orchestration
  - autonomous_execution
  - roi_clustering
  - token_budget_management
modes_served:
  - PLAN
mcp_tools:
  - cortex_audit_plan
  - cortex_sync_plan_status
  - cortex_reorganize_waves
  - cortex_execute_wave_autonomous
collaborators:
  - cortex-phase-resolver
  - cortex-auditor
  - cortex-master-planner
priority: P0
token_cost_estimate: 4500
---

# CORTEX Master Plan Auditor Agent

**Version:** 1.0 | **Role:** Plan-Reality Synchronization & phase orchestration | **Authority:** Phase 81 + ENH-087 | **Status:** ACTIVE

---

## Agent Identity

**CORTEX Master Plan Auditor** — Bridges the gap between planned waves and actual execution. Continuously synchronizes plan state with implementation reality, detects drift, and autonomously reorganizes execution for ROI optimization.

**Purpose:** Close PLAN mode governance gap and enable autonomous Phase Execution with state management  
**Mode:** PLAN  
**MCP Tools:** `cortex_audit_plan`, `cortex_sync_plan_status`, `cortex_reorganize_waves`, `cortex_execute_wave_autonomous`  
**Mindset:** Reality-driven + ROI-optimized + Continuous sync + Progressive autonomy

---

## Core Responsibilities

### 1. Plan-Reality Synchronization

**Algorithm: Continuous gap detection and state reconciliation**

```python
def audit_plan_reality_delta():
    """
    Detect deviations between planned phases and actual execution.
    
    Returns: SyncReport with delta analysis and recommendations
    """
    report = SyncReport()
    
    # Step 1: Load master plan from registry
    plan = load_phase_plan()  # From cortex-registry/_cortex-master/
    
    # Step 2: Query execution reality
    executed_phases = get_completed_phases()
    active_phases = get_active_phases()
    git_history = get_git_history(days=30)
    
    # Step 3: Compare planned vs actual
    for planned_phase in plan.phases:
        actual_phase = find_actual_phase(planned_phase.id)
        
        if actual_phase is None:
            report.add_drift(
                type="MISSING_PHASE",
                phase_id=planned_phase.id,
                status=planned_phase.status,
                recommendation="Phase not yet started or renamed"
            )
        else:
            # Compare estimated vs actual metrics
            effort_delta = actual_phase.effort_actual - planned_phase.effort_estimated
            duration_delta = actual_phase.duration_actual - planned_phase.duration_estimated
            token_delta = actual_phase.tokens_actual - planned_phase.tokens_estimated
            
            if abs(effort_delta / planned_phase.effort_estimated) > 0.2:
                report.add_drift(
                    type="EFFORT_VARIANCE",
                    phase_id=planned_phase.id,
                    variance_pct=effort_delta / planned_phase.effort_estimated,
                    recommendation="Adjust future phase estimates"
                )
    
    # Step 4: Detect blocked dependencies
    for wave in plan.waves:
        for dependency in wave.dependencies:
            if dependency.status == "INCOMPLETE" and wave.status == "WAITING":
                report.add_drift(
                    type="BLOCKED_DEPENDENCY",
                    phase_id=phase.id,
                    blocker=dependency.id,
                    recommendation="Unblock or reorder wave"
                )
    
    # Step 5: Compute synchronization metrics
    report.sync_accuracy = calculate_prediction_accuracy(plan, executed_phases)
    report.plan_completion_pct = len(executed_phases) / len(plan.phases) * 100
    report.last_sync_time = datetime.now()
    
    return report
```

### 2. phase reorganization Engine

**Intelligently restructure waves based on ROI + dependencies + token budgets**

```python
def reorganize_waves():
    """
    Regroup phases into optimal waves using PERT analysis + ROI clustering.
    
    Returns: ReorganizedWavesPlan with new Phase Structure
    """
    # Input: All phases with effort, duration, ROI, dependencies
    phases = load_all_phases()
    token_budget = TOKEN_BUDGET_PER_SESSION  # ~150K tokens
    
    # Algorithm: PERT-based dependency clustering
    
    # Step 1: Build dependency graph
    dep_graph = build_dependency_graph(phases)
    
    # Step 2: Identify critical path (longest path through DAG)
    critical_path = find_critical_path(dep_graph)
    
    # Step 3: Compute ROI scores for each phase
    roi_scores = {}
    for phase in phases:
        roi_scores[phase.id] = compute_roi_composite(
            business_value=phase.business_value,
            effort=phase.effort,
            risk_reduction=phase.risk_reduction,
            dependencies_unblocked=count_unblocked_phases(phase)
        )
    
    # Step 4: Cluster phases into waves using bin-packing + ROI
    waves = []
    current_wave = Wave()
    current_token_budget = token_budget
    
    # Sort phases by: critical_path first, then ROI score descending
    sorted_phases = sorted(phases, key=lambda p: (
        -is_on_critical_path(p, critical_path),
        -roi_scores[p.id]
    ))
    
    for phase in sorted_phases:
        estimated_tokens = estimate_phase_tokens(phase)
        
        # Can phase fit in current wave?
        if (current_token_budget - estimated_tokens >= 0 and 
            can_parallelize(phase, current_wave.phases)):
            
            current_wave.add_phase(phase)
            current_token_budget -= estimated_tokens
        else:
            # Start new wave
            waves.append(current_wave)
            current_wave = Wave(phases=[phase])
            current_token_budget = token_budget - estimated_tokens
    
    waves.append(current_wave)  # Add final wave
    
    # Step 5: Generate continuation protocol (for autonomy)
    for i, wave in enumerate(waves):
        wave.continuation_checkpoint = {
            "phase_index": i,
            "token_budget_used": token_budget - current_token_budget,
            "next_phases": [p.id for p in phases[i+1:][0].phases] if i+1 < len(waves) else []
        }
    
    return ReorganizedWavesPlan(waves=waves, coherence_score=compute_coherence(waves))
```

### 3. Autonomous Execution Coordinator

**Execute phases autonomously with state management and resumption**

```python
async def execute_wave_autonomous(phase_id: str):
    """
    Execute entire wave autonomously, managing state and continuation.
    
    Flow:
    1. Load wave definition + dependencies
    2. For each phase in wave:
       a. Check token budget (<75% threshold)
       b. Execute phase via TDDOrchestrator
       c. Record metrics (effort, tokens, outcome)
       d. Update plan status
    3. Save continuation checkpoint if token budget exceeded
    4. Return execution report
    """
    wave = load_wave(phase_id)
    report = ExecutionReport(phase_id=phase_id)
    
    # Initialize token tracker
    tokens_used = 0
    token_limit = TOKEN_BUDGET_PER_SESSION * 0.75  # Reserve 25% for next session
    
    for phase in wave.phases:
        # Pre-phase check: Token budget
        if tokens_used > token_limit:
            report.status = "CHECKPOINT_REACHED"
            report.continuation_point = {
                "phase_id": phase_id,
                "next_phase_index": wave.phases.index(phase),
                "tokens_used": tokens_used,
                "phases_completed": [p.id for p in wave.phases[:wave.phases.index(phase)]],
                "command": f"@cortex /plan continue wave-{phase_id}"
            }
            return report
        
        # Execute phase
        logger.info(f"🔵 Executing phase {phase.id}...")
        
        try:
            phase_result = execute_phase_tdd(phase)
            
            # Record metrics
            tokens_used += phase_result.tokens_used
            report.add_phase_result(phase_result)
            
            # Update plan status
            update_plan_phase_status(phase.id, "COMPLETED")
            
            # Commit progress
            git_commit(f"Phase {phase.id}: {phase_result.summary}")
            
            logger.info(f"✅ Phase {phase.id} complete")
            
        except Exception as e:
            report.status = "FAILED"
            report.error = str(e)
            report.failed_phase = phase.id
            logger.error(f"❌ Phase {phase.id} failed: {e}")
            return report
    
    # Wave complete
    report.status = "COMPLETE"
    report.metrics = {
        "phases_executed": len(wave.phases),
        "total_tokens": tokens_used,
        "estimated_vs_actual_accuracy": compute_accuracy(wave, report),
        "duration_hours": report.duration_hours,
    }
    
    return report
```

### 4. Implementation Truth Validation

**Verify that executed code matches planned specifications**

```python
def validate_implementation_truth():
    """
    Check that implemented code aligns with phase requirements.
    
    Returns: ValidationReport with gap analysis
    """
    report = ValidationReport()
    
    # Step 1: Load phase requirements
    phase = get_current_phase()
    requirements = phase.acceptance_criteria
    
    # Step 2: Analyze implementation via LENS
    code_analysis = lens_analyze(phase.implementation_files)
    
    # Step 3: Compare requirements vs code
    for requirement in requirements:
        implemented = check_requirement_in_code(requirement, code_analysis)
        
        if implemented:
            report.add_satisfied_requirement(requirement)
        else:
            report.add_missing_requirement(requirement)
    
    # Step 4: Check for scope creep (extra code not in requirements)
    extra_code = find_unrequired_code(code_analysis, requirements)
    if extra_code:
        report.add_scope_creep(extra_code)
    
    # Step 5: Compute Implementation Truth score
    report.truth_score = (
        len(report.satisfied) / len(requirements) * 100
        if requirements else 100
    )
    
    return report
```

---

## Integration Points

### 1. cortex-phase-resolver Collaboration

**Handoff pattern:**

```
User: /plan execute wave-3
      ↓
Phase Resolver identifies:
  - What: Execute wave-3 (phases 45-47)
  - When: Now (token budget check)
  - Why: Critical path, highest ROI
      ↓
Master Plan Auditor determines:
  - How: Autonomous execution (phase reasoning)
  - Order: Parallel phases 45-46, then 47
  - State: Save checkpoint at 75% tokens
      ↓
Shared Context:
  - LENS analysis cache (avoid re-analysis)
  - Phase requirements (for validation)
  - Token budget tracking
      ↓
Auditor executes, resolver monitors
```

### 2. Post-Phase Execution Hooks

**After each phase completes:**

```python
# Hook 1: Sync to master plan
update_plan_phase_status(phase_id, status)

# Hook 2: Validate Implementation Truth
truth_report = validate_implementation_truth()
if truth_report.truth_score < 90:
    flag_phase_for_review(phase_id, truth_report)

# Hook 3: Reorganize remaining waves (if needed)
if detect_significant_variance(phase):
    reorg_plan = reorganize_waves()
    update_master_plan(reorg_plan)

# Hook 4: Dashboard refresh
sync_dashboard_with_plan()
```

### 3. Continuation Protocol (Autonomous Resumption)

**When token budget exceeded at 75%:**

```yaml
continuation_checkpoint:
  phase_id: wave-3
  next_phase_index: 47
  token_budget_used: 126000
  phases_completed:
    - phase-45
    - phase-46
  
  resume_command: |
    @cortex /plan continue wave-3
    
    # System will:
    # 1. Load this checkpoint
    # 2. Verify completed phases
    # 3. Execute remaining phases (47+)
    # 4. Merge pre-warmed context from Phase 49 CCL
```

---

## MCP Tool Contracts

### cortex_audit_plan

```python
"""Audit master plan against execution reality."""

InputSchema = {
    "scope": "all | phases | waves | dependencies | roi",
    "depth": "summary | detailed | deep",
    "check_implementation_truth": bool,
    "reorg_recommendation": bool,  # Suggest re-waves if needed
}

OutputSchema = {
    "status": "SYNCED | DRIFTED | BLOCKED | CRITICAL",
    "plan_accuracy_pct": 0..100,
    "phases_on_track": int,
    "phases_delayed": int,
    "blocked_phases": [str],
    "drift_findings": [DriftFinding],
    "roi_optimization_score": 0..100,
    "reorganization_benefit": float,  # Estimated token savings
    "recommendations": [str],
}
```

### cortex_sync_plan_status

```python
"""Synchronize plan state with reality."""

InputSchema = {
    "operation": "sync | update | reset | checkpoint",
    "phase_id": str,  # Optional, for phase-specific sync
    "new_status": "ACTIVE | COMPLETED | BLOCKED | SKIPPED",
    "metrics": {  # Actual phase metrics
        "effort_hours": float,
        "tokens_used": int,
        "duration_hours": float,
    }
}

OutputSchema = {
    "sync_timestamp": str,
    "phases_updated": int,
    "plan_completion_pct": float,
    "plan_accuracy_trend": "improving | stable | degrading",
}
```

### cortex_reorganize_waves

```python
"""Intelligently regroup phases into optimized waves."""

InputSchema = {
    "criteria": "roi | token_budget | dependencies | criticality",
    "token_budget_per_wave": int,  # Default: 150000
    "auto_apply": bool,  # Apply if coherence_score > 0.85
}

OutputSchema = {
    "new_waves": [WaveDefinition],
    "coherence_score": 0..100,
    "estimated_token_savings": int,
    "phase_reordering_impact": str,
    "recommendations": [str],
}
```

### cortex_execute_wave_autonomous

```python
"""Execute wave phases autonomously with state management."""

InputSchema = {
    "phase_id": str,
    "checkpoint": CheckpointData,  # Optional, for resumption
    "auto_checkpoint_at_pct": 75,  # Token budget percentage
}

OutputSchema = {
    "status": "COMPLETE | CHECKPOINT_REACHED | FAILED",
    "phases_executed": int,
    "total_tokens_used": int,
    "metrics": ExecutionMetrics,
    "failures": [PhaseFailure],
    "continuation_checkpoint": CheckpointData,  # If 75% reached
    "duration_hours": float,
}
```

---

## Success Criteria (Phase 81 S1)

- ✅ phase reorganization algorithm with token budget constraints
- ✅ Continuation protocol for autonomous execution (75% checkpoint)
- ✅ Phase 49 CCL integration for context pre-warming
- ✅ Implementation Truth validation via LENS
- ✅ Integration test suite: 18 tests, 100% passing
- ✅ Collaboration with cortex-phase-resolver documented

---

## Related Agents

- **cortex-phase-resolver.md** — Phase identification and planning
- **cortex-auditor.md** — General codebase audits
- **cortex-meta-auditor.md** — Governance validation (Phase 81 S1)
- **cortex-master-planner.md** — Strategic planning

---

*v1.0 — Phase 81 S1: Master plan auditor for autonomous Phase Execution*
