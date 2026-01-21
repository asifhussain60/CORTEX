# Autonomous Execution Analysis - Why It Stops

## Root Causes Identified

### 1. **No Phase Execution Tracker in cortex-impl-map.yaml**
**Problem:** The `cortex-impl-map.yaml` has no machine-scoped execution state field.
- No way to know which phases have been executed vs pending
- No field to update after each phase completes
- Builder prompt can't distinguish "already done" from "next to do"

**Fix:** Add `execution_state` field to each phase tracking:
```yaml
execution_state:
  machine: "mac"           # Which machine executed this
  executed: false          # Has it been executed?
  start_timestamp: null    # When execution started
  completion_timestamp: null # When execution completed
```

### 2. **No "next_phase" Field in Phase Specs**
**Problem:** Each phase file (impl-export-completion.yaml, etc.) doesn't define what comes next
- Builder has to manually look through cortex-impl-map to find next phase
- No guaranteed sequence - could pick wrong next phase

**Fix:** Add to each phase:
```yaml
execution_metadata:
  next_phase_id: "impl-circular-import-fix"  # What executes next for this machine
  machine_track: "mac"                        # Which machine track this belongs to
  sequence_position: 1                        # 1st, 2nd, 3rd in the mac track
```

### 3. **Chat Stops After Each Phase - User Needs to Re-Prompt**
**Problem:** In chat01.md, after EACH phase the assistant outputs results and stops
```
User: "machine:mac. Update status for complete work."
Assistant: ✓ phase-1... ✓ phase-2...
[STOPS - WAITS FOR NEXT USER MESSAGE]
User: "machine:mac. Update status for complete work. Proceed to next phase."
Assistant: ✓ phase-3...
[STOPS - WAITS FOR NEXT USER MESSAGE]
```

**Root Cause:** Builder prompt says "auto_advance: true" but execution_config doesn't have:
- A loop mechanism to iterate through phases
- A termination condition (when all phases complete)
- A recursion prevention (don't execute same phase twice)

**Fix:** Add to execution_config:
```yaml
execution_loop:
  enabled: true
  continue_until: "all_machine_phases_complete"  # Stop when this condition met
  max_phases_per_invocation: 3                    # Optional batch size
  loop_termination:
    - condition: "status == 'COMPLETED' for all phases in machine_track"
      action: "output final summary, stop"
    - condition: "blocker encountered"
      action: "output blocker detail, stop"
```

### 4. **No Dependency/Blocking Mechanism**
**Problem:** If a phase fails or is blocked, the system doesn't know whether to:
- Skip to next phase
- Stop and report blocker
- Wait for manual intervention

**Fix:** Add to each phase:
```yaml
dependencies:
  requires_completion:
    - phase_id: "impl-export-completion"
      status: "COMPLETED"  # Must be done first
  blocks:
    - phase_id: "PHASE-E-TDD-IMPLEMENTATION"
```

### 5. **Builder Prompt Ambiguity on "Auto-Advance"**
**Problem:** cortex-builder.prompt.md says:
- "Auto-advance to next phase without pausing" ✅
- But then shows example with user re-prompting between phases ❌

**Fix:** Clarify:
```
AUTONOMOUS MODE (machine:mac specified):
- Execute all phases for machine sequentially
- NO user confirmation between phases
- NO pausing or asking "Proceed?"
- Output single line per phase
- LOOP until all phases complete OR blocker encountered
```

### 6. **No Phase Completion Verification**
**Problem:** How does the system know a phase actually succeeded?
- No `completion_criteria` field
- No pass/fail signal
- Can't decide whether to continue or stop

**Fix:** Add to each phase:
```yaml
completion_verification:
  success_criteria:
    - "pytest --collect-only: 0 errors (was 76)"
    - "All exports present and importable"
  on_success: "continue_to_next_phase"
  on_failure: "stop_and_report_blocker"
```

---

## Chat History Pattern (Why It Stops)

**Iteration 1:**
```
User: "machine:mac. Update status and proceed autonomously"
Assistant: 
  ✓ impl-export-completion: ...
  [reads phase file, runs tests, updates map, commits]
  ✓ impl-circular-import-fix: ...
  [reads phase file, runs tests, updates map, commits]
  ✓ PHASE-E-TDD-IMPLEMENTATION: ... large phase, started
  [CHAT ENDS]
```

**Iteration 2:**
```
User: "machine:mac. Update status for complete work. Proceed to next phase."
Assistant:
  [reads map, resumes PHASE-E-TDD-IMPLEMENTATION]
  [implements more tests, commits]
  [CHAT ENDS - ran out of action budget or token limit]
```

**Why:** The builder prompt has no way to:
1. Resume from where it left off within PHASE-E
2. Know if PHASE-E is complete
3. Auto-loop to next phase after PHASE-E
4. Output only when truly autonomous (not waiting for user confirmation)

---

## Solution Summary

### Files to Fix

| File | Fix |
|------|-----|
| `cortex-impl-map.yaml` | Add `execution_state` + `execution_loop` config |
| Phase YAML files | Add `next_phase_id`, `sequence_position`, `completion_verification` |
| `cortex-builder.prompt.md` | Clarify autonomous loop (no pausing), add loop termination logic |

### Key Changes Required

1. **cortex-impl-map.yaml** → Add execution tracking state
2. **Each phase YAML** → Add phase sequencing metadata
3. **cortex-builder.prompt.md** → Add autonomous loop mechanism
4. **New file** → `MACHINE-TRACK-EXECUTION-PROTOCOL.md` (define loop logic)

