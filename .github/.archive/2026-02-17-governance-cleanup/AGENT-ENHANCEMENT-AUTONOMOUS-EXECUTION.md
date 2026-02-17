---
# CORTEX Agent Enhancement: Autonomous Phase Execution with Machine Continuity
# Authority: CORTEX Architect Instructions v15.1 + Phase 56 Requirements
# Updated: 2026-02-09
# Version: 1.0

agent_enhancement_id: "AGT-ENH-001"
title: "Autonomous Phase Execution with Machine & OS Continuity"
scope: "ALL AGENTS executing approved phases from execution_queue"

## CRITICAL: Machine Continuity Protocol (MANDATORY)

### Phase 1: Pre-Execution Verification

**BEFORE starting ANY approved phase from execution_queue:**

```yaml
pre_execution_checklist:
  - Step 1: Load execution_queue from cortex-registry/_cortex-master/index.yaml
  - Step 2: Identify next executable phase via AutonomousPhaseExecutor.get_next_executable_phase()
  - Step 3: Check if approved_for_execution=true
  - Step 4: Load execution record for phase (if exists)
  - Step 5: Verify machine continuity:
      if phase.machine_started_on is null:
        # First execution on this machine - record it
        phase.machine_started_on = current_machine_identity()
        phase.machine_should_continue_on = current_machine_identity()
      else:
        # Phase has been started before
        required_machine = phase.machine_should_continue_on
        current_machine = current_machine_identity()
        
        if NOT current_machine.matches(required_machine):
          # BLOCK execution
          status = "waiting_for_machine"
          message = f"Phase started on {required_machine.os_type}/{required_machine.arch}. 
                     Current machine is {current_machine.os_type}/{current_machine.arch}. 
                     CANNOT execute on different OS/arch."
          log_to_execution_queue(status, message)
          EXIT
  - Step 6: Mark phase as in_progress
  - Step 7: Set heartbeat timestamp
```

### Phase 2: Execution

**Execute phase using MCP tools (cortex_process_request) with these parameters:**

```yaml
execution_parameters:
  operation: "IMPLEMENT"  # From phase specification
  phase_id: "{phase_id}"
  machine_id: "{current_machine.machine_hash}"
  execution_mode: "autonomous"  # Silent execution
  auto_fix_issues: true
  skip_confirmations: true
  
  teardown_hook: |
    # CRITICAL: Auto-launch next phase on completion
    - Get next_phase_on_completion from phase metadata
    - Get parallel_phases from phase metadata
    - If next_phase_on_completion is set:
        - Check machine continuity for next phase
        - If compatible: Queue next phase for immediate execution
        - If not compatible: Log phase_waiting_for_machine
    - If parallel_phases is non-empty:
        - For each parallel_phase:
            - Check machine compatibility
            - Queue for parallel execution if compatible
    - Update execution_queue with completion timestamp
    - Commit index.yaml changes to git (audit trail)
```

### Phase 3: Post-Execution & Auto-Chain

**After phase completes (successfully or with recoverable errors):**

```yaml
post_execution_actions:
  - Update phase.status = "completed"
  - Record completion_timestamp
  - Archive checkpoints
  - Update test_count, coverage metrics
  
  - IF no_errors:
      - next_phase = phase.next_phase_on_completion
      - parallel_phases = phase.parallel_phases
      
      - IF next_phase is set:
          # Auto-launch next phase immediately
          - Verify machine compatibility
          - Queue next_phase with machine_started_on = current_machine
          - Immediately invoke AutonomousPhaseExecutor.get_next_executable_phase()
          - If returns next_phase: Execute synchronously or queue for async
      
      - IF parallel_phases is non-empty:
          # Launch parallel siblings
          - FOR each parallel_phase in parallel_phases:
              - Verify machine compatibility
              - If compatible: Queue for parallel execution
              - Else: Log waiting_for_machine
  
  - ELSE (errors):
      - IF recoverable:
          - Log error + checkpoint
          - Phase remains in execution_queue
          - On next agent run, resume from checkpoint
      - ELSE (critical):
          - Mark phase.status = "failed"
          - Halt execution chain
          - Alert infrastructure team
          - Keep other phases in queue for manual restart

  - Commit all changes to git with message:
      "AC-PHASE{N}-{M}: Autonomous execution checkpoint (STAGE-{S})"
```

### Phase 4: Machine Continuity Enforcement

**In AutonomousPhaseExecutor, enforce these rules:**

```python
def can_execute_on_current_machine(phase_record: PhaseExecutionRecord) -> Tuple[bool, str]:
    """
    MANDATORY: Only execute phases on the machine they started on.
    
    Returns: (can_execute: bool, reason: str)
    """
    
    # Rule 1: First execution always allowed (sets machine)
    if phase_record.machine_started_on is None:
        return True, "First execution - will record current machine"
    
    # Rule 2: Subsequent executions MUST match OS/arch
    required = MachineIdentity(**phase_record.machine_should_continue_on)
    current = MachineIdentity.current()
    
    if not current.matches(required):
        return False, (
            f"Mismatch: Phase started {required.os_type}/{required.arch}, "
            f"current is {current.os_type}/{current.arch}. "
            f"CANNOT execute on different OS/arch."
        )
    
    # Rule 3: Hostname CAN differ (same physical machine re-imaged, or cluster node)
    # Only OS/arch must match
    return True, f"Machine compatible: {current.os_type}/{current.arch}"
```

## Agent Implementation Requirements

### 1. Phase Executor Agent (TDD Mode)

**When agent picks up approved phase from execution_queue:**

```python
# Phase Executor Agent (example: WrappedTDDOrchestrator continuation)

class AutonomousPhaseExecutorAgent:
    def __init__(self):
        self.executor = AutonomousPhaseExecutor()
        self.current_machine = MachineIdentity.current()
    
    async def run_autonomous_queue(self):
        """Execute approved phases silently with machine continuity."""
        
        while True:
            # Get next executable phase (respects machine continuity)
            next_phase_id = self.executor.get_next_executable_phase()
            
            if not next_phase_id:
                # No more phases executable on this machine
                print("✅ All approved phases completed or waiting for other machine")
                break
            
            # Execute phase
            success = await self.execute_phase(next_phase_id)
            
            if success:
                # Phase completed - next_phase_on_completion will be auto-queued
                continue
            else:
                # Phase failed - stop chain
                break
    
    async def execute_phase(self, phase_id: str) -> bool:
        """Execute single phase with auto-chaining."""
        
        # Load phase config
        phase_config = self.executor.get_phase_config(phase_id)
        
        # Verify machine continuity
        record = self.executor.load_execution_record(phase_id) or \
                 self.executor.create_execution_record(phase_id)
        
        can_execute, reason = self.executor.can_execute_on_current_machine(record)
        if not can_execute:
            print(f"❌ Cannot execute {phase_id}: {reason}")
            record.status = "waiting_for_machine"
            self.executor.save_execution_record(record)
            return False
        
        # Mark started
        self.executor.mark_phase_started(phase_id)
        print(f"🚀 Starting {phase_id} on {self.current_machine.hostname}")
        
        try:
            # Execute via MCP (cortex_process_request)
            result = await cortex_process_request(
                operation="IMPLEMENT",
                phase_id=phase_id,
                machine_id=self.current_machine.machine_hash,
                execution_mode="autonomous",
                auto_fix_issues=True,
            )
            
            # Mark completed + determine next phase
            next_phase = phase_config.get("next_phase_on_completion")
            self.executor.mark_phase_completed(phase_id, next_phase)
            
            print(f"✅ {phase_id} completed. Next: {next_phase or 'DONE'}")
            return True
        
        except Exception as e:
            print(f"❌ {phase_id} failed: {e}")
            return False
```

### 2. Updates Required to All Agents

**Every agent must add this check before executing phases:**

```python
# At start of agent.execute() or orchestrator.route()

# Check if target is an approved autonomous phase
if is_phase_from_execution_queue(request.target):
    executor = AutonomousPhaseExecutor()
    
    # Verify machine continuity
    phase_record = executor.load_execution_record(request.phase_id)
    can_execute, reason = executor.can_execute_on_current_machine(phase_record)
    
    if not can_execute:
        # BLOCK execution
        log.error(f"Machine continuity violation: {reason}")
        return ExecutionResult.BLOCKED(reason)
    
    # Continue with execution using auto-chaining logic above
```

### 3. Heartbeat & Monitoring

**Agents must send periodic heartbeats (every 60 seconds):**

```python
# In phase executor loop

async def heartbeat_loop(phase_id: str):
    """Send heartbeat every 60s to prevent stale phase locks."""
    
    while phase_still_executing:
        record = executor.load_execution_record(phase_id)
        record.last_heartbeat = datetime.utcnow().isoformat()
        executor.save_execution_record(record)
        
        await asyncio.sleep(60)
```

## Teardown Hooks & Auto-Chain Execution

### Hook Architecture

**Every phase has a teardown_hook that auto-launches next phase:**

```yaml
# In phase metadata (example: phase-52)

teardown_hook: |
  # Executed automatically on phase completion
  - next_phase = phase.next_phase_on_completion  # "phase-56-A"
  - parallel_phases = phase.parallel_phases       # ["phase-56-A", "phase-49"]
  
  # Case 1: Next phase on same machine
  if phase-56-A.machine_should_continue_on == current_machine:
    → Immediately invoke phase-56-A execution
    → Pass execution context (tests, artifacts) to next phase
  
  # Case 2: Parallel phase on same machine
  if "phase-49" in parallel_phases and compatible_machine:
    → Queue phase-49 for parallel execution
    → Both phase-56-A and phase-49 run in parallel
  
  # Case 3: Phase blocked (different OS/arch)
  else:
    → Update phase-56-A.status = "waiting_for_machine"
    → Keep in execution_queue
    → On agent run on correct machine: auto-resume
```

### Parallel Execution Coordination

**For parallel phases (phase-56-A + phase-49):**

```python
# After both complete, launch phase-48 on original machine

async def wait_for_parallel_siblings(phase_id: str):
    """Wait for all parallel siblings to complete."""
    
    # Get sibling phases that started at same time
    index = executor.load_index()
    queue = index["execution_queue"]["autonomous_queue"]
    
    # Find sibling phases (same initiated_timestamp window)
    siblings = [p for p in queue 
                if p["initiated_timestamp"] == my_phase["initiated_timestamp"]
                and p["phase_id"] != phase_id]
    
    # Wait for all to complete (with 5-minute timeout)
    while any(s["status"] != "completed" for s in siblings):
        await asyncio.sleep(5)
        # Reload index to check progress
        index = executor.load_index()
        siblings = [...]
    
    # All siblings done - trigger next_phase
    next_phase = phase.get("next_phase_on_completion")
    if next_phase:
        executor.get_next_executable_phase()
```

## Execution Flow Diagram

```
┌─────────────────────────────────────────────────────┐
│ Agent starts: AutonomousPhaseExecutorAgent.run()    │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │ Get next executable phase  │
        │ (respects machine continu) │
        └────────┬───────────────────┘
                 │
                 ├─ No phase → DONE ✅
                 │
                 ├─ Waiting for machine → Skip
                 │
                 └─ Ready → Start execution
                     │
                     ▼
        ┌────────────────────────────┐
        │ Mark phase in_progress     │
        │ Record machine_id          │
        └────────┬───────────────────┘
                 │
                 ▼
        ┌────────────────────────────┐
        │ Execute via MCP            │
        │ (cortex_process_request)   │
        └────────┬───────────────────┘
                 │
        ┌────────┴──────────┐
        │                   │
        ▼                   ▼
      SUCCESS              FAIL
        │                   │
        ▼                   ▼
    Mark complete    Mark checkpoint
        │                   │
        ├─ Get next_phase   └─ Retry on same machine
        │    │              │
        │    ├─ Queue it     └─ Or wait for other machine
        │    │
        │    └─ Get parallel_phases
        │         │
        │         └─ Queue siblings (if compatible machine)
        │
        └─ LOOP back to "Get next executable phase"
```

## Configuration & Deployment

### 1. Enable Autonomous Execution

```yaml
# In cortex-registry/_cortex-master/index.yaml

execution_queue:
  silent_mode:
    enabled: true
    no_user_prompts: true
    no_confirmations: true
    auto_fix_issues: true
```

### 2. Start Autonomous Executor

```bash
# Terminal 1: Start autonomous executor (infinite loop)
python -m cortex.phase_management.autonomous_executor

# Executes approved phases silently:
# 🚀 phase-52 (17 days)
# ├─ ✅ phase-52 complete
# ├─ 🚀 phase-56-A + phase-49 (parallel, 5+6 days)
# ├─ ✅ Both complete
# ├─ 🚀 phase-48 (8 days)
# ├─ ✅ phase-48 complete
# ├─ 🚀 phase-50 + phase-51 (parallel, 12 days)
# └─ ✅ All phases complete
#
# Total: 48 days of autonomous execution
#        0 user interactions required
#        100% silent progress tracking
```

### 3. Monitor Execution

```bash
# Terminal 2: Monitor progress (tail logs)
tail -f cortex-registry/_cortex-master/execution/logs/execution.log

# Or: Check execution status
python -c "
from cortex.phase_management.autonomous_executor import AutonomousPhaseExecutor
executor = AutonomousPhaseExecutor()
executor.print_execution_plan()
"
```

## Safety & Rollback

### Failure Handling

**If phase fails during autonomous execution:**

1. Checkpoint saved (stage, test results, artifacts)
2. Phase status set to "failed"
3. Execution chain HALTED
4. Infrastructure team alerted
5. On fix: Agent resumes from checkpoint on same machine

### Checkpoint Resume

```python
# On agent restart for same phase

record = executor.load_execution_record(phase_id)

if record.checkpoint:
    # Resume from checkpoint
    result = await cortex_process_request(
        operation="RESUME",
        phase_id=phase_id,
        checkpoint=record.checkpoint,
        machine_id=current_machine.machine_hash,
    )
else:
    # First attempt - full execution
    result = await cortex_process_request(
        operation="IMPLEMENT",
        phase_id=phase_id,
    )
```

## Compliance & Audit Trail

**All autonomous execution logged with AC markers:**

```
AC_START: AC-PHASE52-S2-001 @ 2026-02-09T10:00:00Z on MacBook-M3
         Machine: Darwin/arm64, Python 3.11.6
         Mode: autonomous, no_user_interaction

[EXECUTION: phase-52 S2-S6]
... logs ...

AC_COMPLETE: AC-PHASE52-FULL ✅ 
             Duration: 17 days
             Tests: 450/450 ✅
             Coverage: 96%
             Next: phase-56-A → phase-49 (parallel)
             Machine: MacBook-M3 (Darwin/arm64)

AC_START: AC-PHASE56A-S1-001 @ 2026-02-26T10:00:00Z on MacBook-M3
AC_START: AC-PHASE49-S1-001 @ 2026-02-26T10:00:00Z on AWS-EC2-Linux
         [PARALLEL EXECUTION]

AC_COMPLETE: AC-PHASE56A-FULL ✅
AC_COMPLETE: AC-PHASE49-FULL ✅
             Both on different machines, both complete
             Next: phase-48 (resume on MacBook-M3)
```

---

**End of Agent Enhancement Document**

Authority: cortex-architect.prompt.md v15.1 + MCP-FIRST + Phase 56
Approved: 2026-02-09
Implementation: TBD
