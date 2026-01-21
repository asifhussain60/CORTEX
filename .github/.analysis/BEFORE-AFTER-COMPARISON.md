# Before & After Comparison

## Problem: Why Execution Stopped After Each Phase

### Before (chat01.md Pattern)

```
User: "machine:mac. Update status and proceed autonomously and silently"
Assistant: 
  ✓ impl-export-completion: verified complete...
  ✓ impl-circular-import-fix: verified complete...
  ✓ PHASE-E-TDD-IMPLEMENTATION: Started, requires TDD...
  [STOPS - CHAT ENDS - REQUIRES NEW USER MESSAGE]

User: "machine:mac. Update status for complete work. Proceed to next phase."
Assistant:
  [resumes PHASE-E, implements more tests...]
  [STOPS - CHAT ENDS - OUT OF TOKENS OR CONTEXT]

[Pattern repeats every time execution resumes]
```

### Root Cause Chain

```
1. cortex-impl-map.yaml has NO execution state field
   ↓
2. Phase YAML files have NO next_phase_id
   ↓
3. cortex-builder.prompt.md says "auto_advance" but has NO loop algorithm
   ↓
4. Each phase completes as OUTPUT EVENT (end of turn)
   ↓
5. System treats completion as "end of response" not "loop iteration"
   ↓
6. No loop logic → execution stops → waits for next user message
```

### Chat Pattern

```
ITERATION 1 (User: "machine:mac"):
  Load phase 1
  Execute phase 1
  Output phase 1 results
  [NO LOOP LOGIC] → STOP and output ends response
  
ITERATION 2 (User: "machine:mac proceed..."):
  [System doesn't know which phase to resume]
  Guess next phase (or ask user)
  Execute phase
  [NO LOOP LOGIC] → STOP
```

---

## After (Fixed - Autonomous Loop)

### After Pattern

```
User: "continue with machine:mac"
Assistant: 
  ✓ impl-export-completion: Added 44 exports, errors 76→0 → Next: impl-circular-import-fix
  ✓ impl-circular-import-fix: Fixed recursion, errors 15→0 → Next: PHASE-E-TDD-IMPLEMENTATION
  ✓ PHASE-E-TDD-IMPLEMENTATION: 125 modules impl'd, 7547 tests pass → Mac track COMPLETE
  ✓ mac track COMPLETE (3/3 phases)
  
[ALL PHASES IN ONE RESPONSE - NO PAUSING - AUTONOMOUS LOOP]
```

### Root Cause Fix Chain

```
1. ✅ cortex-impl-map.yaml NOW HAS execution state field
   └─ phase_execution_tracking tracks current_phase_index, status, etc.
   
2. ✅ Phase YAML files NOW HAVE next_phase_id
   └─ Each phase knows what comes next
   
3. ✅ cortex-builder.prompt.md NOW HAS explicit loop algorithm
   └─ Pseudocode shows LOOP, not one-time execution
   
4. ✅ Phase completion is now LOOP ITERATION, not OUTPUT EVENT
   └─ After completion, loop continues instead of exiting
   
5. ✅ Explicit loop termination conditions
   └─ BREAK only when all_phases_complete OR blocker_encountered
   
6. ✅ Loop logic present → execution continues → NO stop between phases
```

### Loop Structure

```
machine_mode_execution():
  load cortex-impl-map.yaml
  current_index = 0
  
  WHILE current_index < total_phases AND NOT blocked:  # ← LOOP
    phase = get_phase(current_index)
    check_dependencies(phase)
    execute_phase(phase)
    
    if success:
      current_index += 1
      output("✓ phase: summary → Next: {phase.next_phase_id}")
      CONTINUE  # ← LOOP continues
    else:
      BREAK  # ← Exit only on blocker
  
  output("Track COMPLETE")
  return
```

---

## Detailed Comparison

### cortex-impl-map.yaml

#### BEFORE
```yaml
execution_config:
  autonomous_mode:
    enabled: true
    auto_advance: true        # ← Vague - how?
    
  machine_tracks:
    mac:
      phases: ["impl-export-completion", "impl-circular-import-fix", "PHASE-E-TDD-IMPLEMENTATION"]
      # ← Just a list, no sequencing, no next_phase info, no state tracking
```

#### AFTER
```yaml
execution_config:
  autonomous_mode:
    enabled: true
    auto_advance: true
    
  execution_loop:                          # ← NEW: Loop config
    enabled: true
    mode: "continuous"
    continue_until: "all_phases_complete_or_blocker"
    
  machine_tracks:
    mac:
      phases:
        - phase_id: "impl-export-completion"
          sequence: 1
          required: true
          # ← Clear sequencing
        - phase_id: "impl-circular-import-fix"
          sequence: 2
          required: true
          # ← Knows its position and dependencies
        - phase_id: "PHASE-E-TDD-IMPLEMENTATION"
          sequence: 3
          required: true

phase_execution_tracking:                  # ← NEW: Real-time state
  mac_track_state:
    current_phase_index: 0                 # ← Loop counter
    phases_completed: 0                    # ← Progress tracking
    phase_states:
      - phase_id: "impl-export-completion"
        status: "PENDING"                  # ← Tracks PENDING→EXECUTING→COMPLETED
        next_phase: "impl-circular-import-fix"  # ← Knows what's next
```

### Phase YAML Files

#### BEFORE (impl-export-completion.yaml)
```yaml
metadata:
  phase_id: "impl-export-completion"
  status: "NOT_STARTED"
  blocks_production: true
  # ← No info about what comes next
  # ← No completion verification logic
  # ← No machine assignment
```

#### AFTER (impl-export-completion.yaml)
```yaml
metadata:
  phase_id: "impl-export-completion"
  status: "NOT_STARTED"
  blocks_production: true
  
  execution_metadata:                      # ← NEW
    machine_track: "mac"                   # ← Assigned to mac
    sequence_position: 1                   # ← 1st in sequence
    next_phase_id: "impl-circular-import-fix"  # ← Knows next
    dependencies: []                       # ← No dependencies
    
  completion_verification:                 # ← NEW
    success_criteria:
      - "pytest --collect-only: 0 ImportError"
      - "All 44 exports added"
    on_success: "continue_to_next_phase"   # ← Continue loop
    on_failure: "stop_and_report_blocker"  # ← Exit loop on failure
```

### cortex-builder.prompt.md

#### BEFORE
```markdown
### Execution Protocol (ZERO OUTPUT MODE)
1. **Load** cortex-impl-map.yaml
2. **Execute** all phases sequentially
3. **Output** one sentence per phase
4. **Auto-advance** to next phase without pausing

### Example Session:
User: "continue with machine:mac"
Assistant: ✓ phase-1 ... ✓ phase-2 ...
           [Continues silently until all complete]
```

**Problem:** "Auto-advance" is vague. No algorithm. No loop logic.

#### AFTER
```markdown
### Execution Protocol (ZERO OUTPUT MODE - AUTONOMOUS LOOP)

**Algorithm pseudocode:**
```
WHILE current_index < total_phases AND NOT blocked:
  phase = machine_track.phases[current_index]
  check_dependencies(phase.dependencies)
  execute_phase(phase)
  
  if completion_verification all pass:
    status = COMPLETED
    current_index += 1
    output("✓ {phase_id}: ... → Next: {next_phase}")
    CONTINUE  # ← Explicit loop continuation
  else:
    status = BLOCKED
    BREAK     # ← Explicit loop termination
```

**Termination conditions:**
- If current_index >= total_phases: output "Track COMPLETE"
- If phase.status == BLOCKED: output blocker, exit
- If error: output error, exit
```

**Improvement:** Explicit loop structure, termination conditions, and algorithm.

#### Key Additions

```markdown
### Autonomous Loop Termination Conditions
if all_phases_for_machine.status == "COMPLETED":
  stop_execution()
elif any_phase.status == "BLOCKED":
  stop_execution()
elif error:
  stop_execution()
else:
  continue_to_next_phase()

### Forbidden Actions (NEW/CLARIFIED)
- ❌ **PAUSING between phases for any reason** (CRITICAL)

### Required Actions (NEW/CLARIFIED)
- ✅ **Continue to next phase automatically without pausing** (CRITICAL)

### New Example Showing CORRECT vs WRONG

CORRECT (autonomous):
✓ phase-1 → Next: phase-2
✓ phase-2 → Next: phase-3
✓ phase-3 → COMPLETE
[all in one response]

WRONG (breaks autonomous):
✓ phase-1 [STOPS]
User: "proceed"
✓ phase-2 [STOPS]
❌ FORBIDDEN
```

---

## State Tracking Improvements

### BEFORE
```
No way to know:
- Which phase is executing
- What phase was last completed
- Which phase to execute next
- Whether dependencies are met
- If execution was interrupted, where to resume
```

### AFTER
```yaml
phase_execution_tracking.mac_track_state:
  current_phase_index: 0          # ✅ Which phase next (0-indexed)
  phases_completed: 0             # ✅ How many phases done
  
  phase_states:
    - phase_id: "impl-export-completion"
      status: "PENDING"           # ✅ Current state
      start_time: null            # ✅ When started
      end_time: null              # ✅ When finished
      duration_seconds: null      # ✅ How long took
      passed: false               # ✅ Did it succeed
      error_message: null         # ✅ Why failed
      next_phase: "impl-circular-import-fix"  # ✅ What's next
      dependencies: []            # ✅ Prerequisites met?
```

**Can now:**
- ✅ Know exact position in execution
- ✅ Resume interrupted execution
- ✅ Validate dependencies before proceeding
- ✅ Track completion progress
- ✅ Diagnose failures

---

## Loop Execution Walkthrough

### Before (No Loop)

```
PHASE 1 EXECUTION:
  Load impl-export-completion.yaml
  Execute code
  Test passes
  Output result
  [END - No more code to execute]
  
PHASE 2 EXECUTION (Requires New User Message):
  ???  (System doesn't know to go to phase 2)
  If user re-prompts:
    Load impl-circular-import-fix.yaml
    Execute code
    Test passes
    Output result
    [END - No more code to execute]
```

**Result:** 2 separate user messages, 2 separate responses.

### After (Explicit Loop)

```
MACHINE MODE EXECUTION:
  Load cortex-impl-map.yaml
  current_index = 0
  
  LOOP ITERATION 1:
    phase = mac_track.phases[0] = "impl-export-completion"
    Execute phase 1
    Success → current_index = 1
    Output phase 1 summary
    CONTINUE (no break) ↓

  LOOP ITERATION 2:
    phase = mac_track.phases[1] = "impl-circular-import-fix"
    Check dependency: phase[0].status == COMPLETED ✓
    Execute phase 2
    Success → current_index = 2
    Output phase 2 summary
    CONTINUE (no break) ↓

  LOOP ITERATION 3:
    phase = mac_track.phases[2] = "PHASE-E-TDD-IMPLEMENTATION"
    Check dependencies: phase[0] and [1] both COMPLETED ✓
    Execute phase 3
    Success → current_index = 3
    Output phase 3 summary
    CONTINUE (no break) ↓

  LOOP TERMINATION:
    current_index (3) >= total_phases (3)
    Output "Track COMPLETE"
    BREAK (exit loop)

[SINGLE RESPONSE with 3 phase summaries]
```

**Result:** 3 phases in one response, no user re-prompting needed.

---

## Dependency Management

### Before
```
Phase 2 has:
  depends_on: ["impl-export-completion"]

But nowhere to check this:
  - Is impl-export-completion actually done?
  - What if it failed?
  - Can we proceed anyway?
  - How do we handle the error?
```

### After
```
Phase 2 has:
  dependencies: ["impl-export-completion"]

Loop checks before execution:
  BEFORE phase 2 starts:
    dep_state = find_phase_state("impl-export-completion")
    IF dep_state.status != "COMPLETED":
      OUTPUT "⚠ Phase 2 blocked by Phase 1 (status: {dep_state.status})"
      BREAK (exit loop - don't proceed)
    ELSE:
      CONTINUE (proceed with phase 2)

Result: Clear blocking logic, no silent failures
```

---

## Impact on Win Track

### Before
```
Win track just listed in machine_tracks:
  phases: ["cortex-registry-001-migration", "impl-e2e-validation", ...]
  
But no way to express:
  - Win track depends on PHASE-E completion
  - So don't start Win until Mac completes PHASE-E
```

### After
```yaml
win_track_state:
  blocked_by_dependency: "PHASE-E-TDD-IMPLEMENTATION"
  
  phase_states:
    - phase_id: "cortex-registry-001-migration"
      status: "BLOCKED_BY_DEPENDENCY"
      dependencies: ["PHASE-E-TDD-IMPLEMENTATION"]

Before Win track starts:
  IF phase_state("PHASE-E-TDD-IMPLEMENTATION").status != "COMPLETED":
    All Win phases remain BLOCKED_BY_DEPENDENCY
  
After Mac completes PHASE-E:
    Win phases change to PENDING
    OUTPUT "✓ Mac track complete - Win track unblocked"
    Ready for: "continue with machine:win"

Result: Clear dependency between machine tracks
```

---

## Summary of Improvements

| Aspect | Before | After |
|--------|--------|-------|
| **Loop Logic** | Implicit (vague "auto-advance") | Explicit (WHILE loop with termination) |
| **Phase Sequencing** | Flat list | Numbered sequence with order |
| **Next Phase Info** | Must search files | Each phase knows next_phase_id |
| **Execution State** | None | Real-time tracking in cortex-impl-map |
| **Dependency Checking** | Documented but not enforced | Checked before each phase |
| **Loop Termination** | Implicit (stop on output) | Explicit (until all_complete or blocker) |
| **Resumption Logic** | None | Can resume from last completed phase |
| **Win Track Blocking** | No clear dependency | Explicit BLOCKED_BY_DEPENDENCY |
| **Success Criteria** | Undefined | Clear completion_verification |
| **Failure Handling** | Stops silently | Outputs blocker with reason |

