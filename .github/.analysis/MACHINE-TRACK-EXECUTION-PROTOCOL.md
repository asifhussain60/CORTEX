# Machine-Specific Autonomous Execution Protocol

**Version:** 1.0  
**Date:** 2026-01-21  
**Authority:** cortex-builder.prompt.md § "Autonomous Execution Loop"

## Overview

This document defines the exact algorithm and state management for autonomous phase execution when `machine:mac` or `machine:win` is specified by the user.

## Key Principle

**NO PAUSING. NO USER CONFIRMATION. LOOP UNTIL COMPLETE OR BLOCKED.**

When a user specifies `machine:mac` or `machine:win`, the system enters **autonomous execution mode** and must:
1. Execute all phases for that machine sequentially
2. Continue from one phase to the next without waiting for user input
3. Only output one-line phase completion summaries
4. Loop until all phases complete OR a blocker is encountered
5. Never ask "Proceed to next phase?" or require confirmation

## Phase Execution Tracking State

### Location
`_workspaces/roadmap/cortex-impl-map.yaml` → `phase_execution_tracking.{mac|win}_track_state`

### State Structure
```yaml
{machine}_track_state:
  machine: "mac|win"                    # Which machine this tracks
  current_phase_index: 0                # 0-indexed, incremented after each phase
  total_phases: 3|5                     # Mac=3, Win=5
  phases_completed: 0                   # Incremented on success
  loop_active: false                    # true during execution, false when stopped
  last_execution: null                  # ISO timestamp of last execution
  next_execution: null                  # ISO timestamp of next execution
  
  phase_states:
    - phase_id: "impl-export-completion"
      machine: "mac"
      sequence: 1
      status: "PENDING|EXECUTING|COMPLETED|BLOCKED|SKIPPED"
      executed_by: null                 # Chat session ID or name
      start_time: null                  # ISO timestamp
      end_time: null                    # ISO timestamp
      duration_seconds: null            # end_time - start_time
      passed: false|true                # Phase success/failure
      error_message: null               # If status=="BLOCKED"
      next_phase: "impl-circular-import-fix"
      dependencies: []
```

### Status Transitions
```
PENDING → EXECUTING → COMPLETED → [exit loop]
PENDING → EXECUTING → BLOCKED → [exit loop]
PENDING → SKIPPED → [continue to next] (if explicitly skipped)
```

## Execution Algorithm

### Phase 1: Initialization
```
Input: user specifies "machine:mac" or "machine:win"

1. Load cortex-impl-map.yaml
2. Get machine_track = execution_config.machine_tracks[machine]
3. Get track_state = phase_execution_tracking.{machine}_track_state
4. current_index = track_state.current_phase_index
5. total_phases = machine_track.total_phases

OUTPUT: (none - silent initialization)
```

### Phase 2: Main Execution Loop
```
WHILE current_index < total_phases AND NOT blocked:

  A. GET CURRENT PHASE
     phase_spec = machine_track.phases[current_index]
     phase_id = phase_spec.phase_id
     phase_state = track_state.phase_states[current_index]

  B. CHECK DEPENDENCIES
     FOR EACH dep_phase_id in phase_spec.dependencies:
       dep_state = find_phase_state(dep_phase_id)
       IF dep_state.status != "COMPLETED":
         OUTPUT: "⚠ {phase_id} blocked by {dep_phase_id} (status: {dep_state.status})"
         BREAK LOOP → exit with blocker

  C. LOAD PHASE SPECIFICATION
     phase_yaml = load_file("_workspaces/roadmap/phases/{phase_id}.yaml")
     completion_criteria = phase_yaml.completion_verification.success_criteria

  D. UPDATE STATE TO EXECUTING
     phase_state.status = "EXECUTING"
     phase_state.start_time = now_iso()
     phase_state.executed_by = "chat-session-id"
     write_yaml("cortex-impl-map.yaml", track_state)

  E. EXECUTE PHASE
     result = execute_phase_implementation(phase_yaml)
     
     E1. Implement code from phase specification
     E2. Create/update test files
     E3. Run pytest to verify
     E4. Check all success_criteria pass

  F. VERIFY COMPLETION
     IF all completion_criteria pass:
       GOTO G (success)
     ELSE:
       GOTO H (failure)

  G. ON SUCCESS
     phase_state.status = "COMPLETED"
     phase_state.passed = true
     phase_state.end_time = now_iso()
     phase_state.duration_seconds = end_time - start_time
     track_state.phases_completed += 1
     current_index += 1
     write_yaml("cortex-impl-map.yaml", track_state)
     git_commit("phase {phase_id}: completed")
     
     next_phase_id = phase_spec.next_phase_id
     OUTPUT: "✓ {phase_id}: {summary} → Next: {next_phase_id}"
     CONTINUE LOOP (no pause, no user confirmation)

  H. ON FAILURE
     phase_state.status = "BLOCKED"
     phase_state.passed = false
     phase_state.end_time = now_iso()
     phase_state.error_message = reason_for_failure
     write_yaml("cortex-impl-map.yaml", track_state)
     
     OUTPUT: "⚠ {phase_id}: {failure_reason}"
     BREAK LOOP → exit with blocker
```

### Phase 3: Loop Termination
```
When WHILE condition becomes false:

IF current_index >= total_phases:
  # All phases completed
  track_state.loop_active = false
  OUTPUT: "✓ {machine} track COMPLETE ({phases_completed}/{total_phases} phases)"
  
ELSE IF blocked:
  # Blocker encountered
  track_state.loop_active = false
  OUTPUT: "⚠ {machine} track blocked at {phase_id}"

ELSE IF error:
  # Unexpected error
  track_state.loop_active = false
  OUTPUT: "⚠ {machine} track error: {error_detail}"

write_yaml("cortex-impl-map.yaml", track_state)
git_commit("machine-track: {machine} execution finished")
```

## Output Format

### Per-Phase Output (during loop)
```
✓ {phase_id}: {8-word-max-summary} → Next: {next_phase_id}
```

### Examples
```
✓ impl-export-completion: Added 44 exports, errors 76→0 → Next: impl-circular-import-fix
✓ impl-circular-import-fix: Fixed recursion, errors 15→0 → Next: PHASE-E-TDD-IMPLEMENTATION
✓ PHASE-E-TDD-IMPLEMENTATION: 125 modules impl'd, 7547 tests pass → Mac track COMPLETE
```

### Blocker Output
```
⚠ impl-circular-import-fix blocked by impl-export-completion (status: BLOCKED)
```

### Final Output
```
✓ mac track COMPLETE (3/3 phases)
```

## Forbidden Outputs (Machine Mode)

❌ Multi-line summaries  
❌ Bullet-point lists  
❌ "Proceed to next phase?" questions  
❌ Executive summaries  
❌ Progress reports  
❌ Any .md files (status, reports, summaries)  
❌ Verbose explanations between phases  
❌ Test output or logs  
❌ Intermediate "what was delivered" paragraphs  

## Required State Updates

### After Each Phase
1. Update `phase_execution_tracking.{machine}_track_state.phase_states[index].status`
2. Update `phase_execution_tracking.{machine}_track_state.current_phase_index`
3. Update `phase_execution_tracking.{machine}_track_state.phases_completed`
4. Write updated YAML to `cortex-impl-map.yaml`
5. Git commit with message format: `{phase_id}: {status}`

### Example Git Commit Sequence
```
Machine mode execution starts:
  git commit -m "machine:mac: loop started at impl-export-completion"

Phase 1 completes:
  git commit -m "impl-export-completion: completed, 76→0 errors"

Phase 2 completes:
  git commit -m "impl-circular-import-fix: completed, 15→0 errors"

Phase 3 completes:
  git commit -m "PHASE-E-TDD-IMPLEMENTATION: completed, 7547/7547 tests pass"

Loop terminates:
  git commit -m "machine:mac track complete, 3/3 phases"
```

## Dependency Management

### Checking Dependencies
```
For each phase:
  dependencies = phase_yaml.execution_metadata.dependencies
  
  FOR EACH dep_phase_id in dependencies:
    dep_status = find_phase_state(dep_phase_id).status
    
    IF dep_status != "COMPLETED":
      BLOCK current phase
      OUTPUT blocker message
      EXIT loop
```

### Example: PHASE-E depends on export-completion + circular-import-fix
```yaml
# PHASE-E-TDD-IMPLEMENTATION.yaml
execution_metadata:
  dependencies: 
    - "impl-export-completion"
    - "impl-circular-import-fix"
```

Before PHASE-E executes:
```
1. Check impl-export-completion.status → must be COMPLETED
2. Check impl-circular-import-fix.status → must be COMPLETED
3. If either is not COMPLETED → BLOCK and EXIT
```

## Example: Complete Mac Track Execution

### Initial State
```yaml
mac_track_state:
  current_phase_index: 0
  total_phases: 3
  phases_completed: 0
  phase_states:
    [0]: status: PENDING
    [1]: status: PENDING
    [2]: status: PENDING
```

### User Input
```
"continue with machine:mac"
```

### Execution (no pauses between steps)
```
[Init] Load cortex-impl-map.yaml, get mac_track
[Loop iteration 1]
  [1a] current_index=0, phase_id=impl-export-completion
  [1b] Check dependencies: [] (none)
  [1c] Load phase YAML
  [1d] Set status=EXECUTING
  [1e-f] Execute phase, run tests
  [1g] All criteria pass → status=COMPLETED, current_index=1
  OUTPUT: "✓ impl-export-completion: Added 44 exports, errors 76→0 → Next: impl-circular-import-fix"

[Loop iteration 2]
  [2a] current_index=1, phase_id=impl-circular-import-fix
  [2b] Check dependencies: [impl-export-completion]
       impl-export-completion.status=COMPLETED ✓
  [2c] Load phase YAML
  [2d] Set status=EXECUTING
  [2e-f] Execute phase, run tests
  [2g] All criteria pass → status=COMPLETED, current_index=2
  OUTPUT: "✓ impl-circular-import-fix: Fixed recursion, errors 15→0 → Next: PHASE-E-TDD-IMPLEMENTATION"

[Loop iteration 3]
  [3a] current_index=2, phase_id=PHASE-E-TDD-IMPLEMENTATION
  [3b] Check dependencies: [impl-export-completion, impl-circular-import-fix]
       Both status=COMPLETED ✓
  [3c] Load phase YAML
  [3d] Set status=EXECUTING
  [3e-f] Execute phase, implement 125 modules, run tests
  [3g] All criteria pass → status=COMPLETED, current_index=3
  OUTPUT: "✓ PHASE-E-TDD-IMPLEMENTATION: 125 modules impl'd, 7547 tests pass → Mac track COMPLETE"

[Loop termination]
  current_index=3 >= total_phases=3
  OUTPUT: "✓ mac track COMPLETE (3/3 phases)"
  STOP EXECUTION

Final state:
  all phases: status=COMPLETED
  current_phase_index: 3
  phases_completed: 3
```

## Resuming Interrupted Execution

If execution is interrupted (token limit, network error, etc.):

### Resume Steps
```
1. Load cortex-impl-map.yaml
2. Get mac_track_state.current_phase_index = X
3. Get mac_track_state.phase_states[0..X-1].status
   - All should be COMPLETED (else fix previous phase)
4. Get mac_track_state.phase_states[X].status
   - If EXECUTING: resume from step [2e] (execute phase)
   - If PENDING: resume from step [2a] (start phase)
5. Continue loop from step [2]
```

### Resume Conditions
```
IF phase_state[X].status == "EXECUTING":
  # Incomplete execution - resume from implementation
  
IF phase_state[X].status == "PENDING":
  # Never started - start from beginning
  
IF phase_state[X].status == "COMPLETED":
  # Already done - move to next phase
  INCREMENT current_phase_index
```

## Win Track Dependency

The Win track has a cross-machine dependency:

```yaml
win_track_state:
  blocked_by_dependency: "PHASE-E-TDD-IMPLEMENTATION"
```

All Win phases remain `BLOCKED_BY_DEPENDENCY` until:
```
mac_track_state.phase_states[2].status == "COMPLETED"  # PHASE-E done
```

When Mac track completes:
```
1. Check if any Win track phases in execution queue
2. If yes: Update cortex-impl-map.yaml
3. Output: "✓ mac track complete - Win track unblocked"
4. Wait for user: "continue with machine:win"
```

## Safety Checks

### Max Iterations
```yaml
execution_loop:
  max_iterations: 100  # Prevent infinite loops
```

### Blocker Detection
```
IF phase fails 3 consecutive times:
  BLOCK entire machine track
  OUTPUT: "⚠ {phase_id} failed 3x - manual intervention required"
```

### Timeout Prevention
```
If phase takes > estimated_effort * 2 hours:
  WARN user but continue (phases can exceed estimates)
  OUTPUT: "⚠ {phase_id} running long ({elapsed}h > {estimated}h)"
```

---

## Related Files

- `cortex-impl-map.yaml` - Source of truth for phase execution state
- `phases/*.yaml` - Phase specifications with execution metadata
- `cortex-builder.prompt.md` - Implementation guidance
- `AUTONOMOUS-EXECUTION-ANALYSIS.md` - Problem analysis and root causes

