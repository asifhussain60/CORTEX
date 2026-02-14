# CORTEX Autonomous Phase Execution System
**Version:** 1.0 | **Authority:** Phase 56 Requirements | **Updated:** 2026-02-09

## Overview

This system enables **silent, autonomous end-to-end execution** of approved CORTEX phases with:

- ✅ **Zero user interaction** - Complete phases in background
- ✅ **Machine/OS continuity** - Phases resume on same machine they started on
- ✅ **Automatic teardown→next-phase sequencing** - No manual queueing
- ✅ **Parallel execution** - Multiple phases run simultaneously when appropriate
- ✅ **Observable progress** - Real-time status tracking without verbose logging
- ✅ **Failure resilience** - Checkpoints enable recovery on same machine

## Approved Autonomous Phases

| Phase | Duration | Status | Machine | Next Phase |
|-------|----------|--------|---------|-----------|
| **phase-52** (S2-S6) | 17 days | Approved | TBD | phase-56-A + phase-49 (parallel) |
| **phase-56-A** (LENS pilot) | 5 days | Approved | Same as 52 | phase-48 |
| **phase-49** (Knowledge pipeline) | 6 days | Approved | Any | phase-48 |
| **phase-48** (Multi-tenant) | 8 days | Approved | Same as 52 | phase-50 + phase-51 (parallel) |
| **phase-50** (Storage) | 12 days | Approved | Same as 48 | phase-51 |
| **phase-51** (Secrets) | 12 days | Approved | Same as 48 | DONE |

**Total Autonomous Duration:** ~48 days of continuous execution

## Architecture

### 1. Execution Queue (`cortex-registry/_cortex-master/index.yaml`)

Each phase has an execution record with:
- `approved_for_execution: true` - enables autonomous mode
- `machine_started_on: null` - set on first execution
- `machine_should_continue_on: null` - enforces OS/arch continuity
- `next_phase_on_completion: "phase-X"` - auto-chain to next
- `parallel_phases: ["phase-Y", ...]` - siblings to run in parallel

### 2. Executor Controller (`cortex/phase_management/autonomous_executor.py`)

```python
executor = AutonomousPhaseExecutor()

# Get next executable phase (respects machine continuity)
phase_id = executor.get_next_executable_phase()

# Can execute on current machine?
can_execute, reason = executor.can_execute_on_current_machine(phase_record)

# Mark started/completed with auto-chaining
executor.mark_phase_started(phase_id)
executor.mark_phase_completed(phase_id, next_phase_id)
```

### 3. Machine Registry (`cortex-registry/_cortex-master/execution/machine-registry.yaml`)

Tracks:
- Which machine each phase started on
- OS/arch constraints (Darwin/arm64, Linux/x86_64, etc.)
- Lock status (preventing execution on wrong machine)
- Heartbeat timestamps (detecting stale phases)

### 4. Agent Enhancement (`.github/agents/core/AGENT-ENHANCEMENT-AUTONOMOUS-EXECUTION.md`)

Instructs agents to:
- Check machine continuity BEFORE executing
- Auto-chain next phase on completion
- Respect OS/arch locks
- Send heartbeats every 60s
- Queue parallel phases

### 5. Teardown Hooks (`cortex-registry/_cortex-master/directives/PHASE-TEARDOWN-TEMPLATE.yaml`)

On phase completion:
1. Save checkpoints + metrics
2. Detect next phase from metadata
3. Verify machine compatibility
4. Queue next phase (or parallel siblings)
5. Commit to git for audit trail
6. Immediately trigger execution

## How It Works

### Sequential Execution

```
Phase-52 (17 days)
├─ Completes with 450 tests passing
├─ Teardown triggers on MacBook-M3
├─ Next phase = phase-56-A (on MacBook-M3) ✅
├─ Parallel phases = [phase-56-A, phase-49]
│
└─> Phase-56-A (5 days, MacBook-M3)
    ├─ Parallel: Phase-49 (6 days, any machine)
    ├─ Both complete
    │
    └─> Phase-48 (8 days, MacBook-M3)
        ├─ Completes
        │
        └─> Phase-50 (12 days, MacBook-M3)
            ├─ Parallel: Phase-51 (12 days, any)
            ├─ Both complete
            │
            └─> DONE ✅
```

### Machine Continuity Enforcement

```
┌─ phase-52 STARTS on MacBook-M3 (Darwin/arm64)
│  ├─ phase_machine_locks[phase-52].machine_hash = "a1b2c3d4e5f6"
│  ├─ phase_machine_locks[phase-52].locked = true
│  └─ Only MacBook-M3 (Darwin/arm64) can continue phase-52
│
├─ Linux box tries to resume phase-52 ❌
│  └─ ERROR: "Phase started on Darwin/arm64, current is Linux/x86_64"
│
└─ MacBook-M3 resumes phase-52 ✅
   └─ OK: "Same machine, lock held"
```

### Parallel Execution Coordination

```
Phase-52 completes
├─ Teardown on MacBook-M3
├─ parallel_phases = [phase-56-A, phase-49]
│
├─> Phase-56-A starts on MacBook-M3
│   └─ Machine lock: MacBook-M3 only
│
└─> Phase-49 starts on AWS-EC2 (parallel)
    └─ Machine lock: AWS-EC2 only
    
Both run in parallel (~5-6 days)
    
Whichever completes first:
├─ Sends "ready_for_next" signal to sibling
└─ Waits for sibling completion
    
When BOTH complete:
└─> Phase-48 queues on MacBook-M3
    (original machine from phase-52)
```

## Starting Autonomous Execution

### 1. Initialize Queue

```bash
cd /Users/asifhussain/PROJECTS/CORTEX

python -c "
from cortex.phase_management.autonomous_executor import AutonomousPhaseExecutor

executor = AutonomousPhaseExecutor()

# Setup approved phases with sequential + parallel execution
approved = ['phase-52', 'phase-56-A', 'phase-49', 'phase-48', 'phase-50', 'phase-51']
parallel_config = {
    'phase-52': ['phase-56-A', 'phase-49'],
    'phase-50': ['phase-51'],
}

executor.setup_autonomous_queue(approved, parallel_config)
executor.print_execution_plan()
"
```

**Output:**
```
================================================================================
🚀 CORTEX AUTONOMOUS EXECUTION PLAN
================================================================================

🖥️  MACHINE: MacBook-M3 (Darwin/arm64)

📋 SEQUENTIAL EXECUTION CHAIN:
   → phase-52
   → phase-56-A
   → phase-49
   → phase-48
   → phase-50
   → phase-51

🔀 PARALLEL EXECUTION GROUPS:
   phase-52 ⟶ [phase-56-A, phase-49]
   phase-50 ⟶ [phase-51]

✅ APPROVED FOR AUTONOMOUS EXECUTION (NO USER INTERACTION REQUIRED)
================================================================================
```

### 2. Start Autonomous Executor

```bash
# Terminal 1: Run autonomous executor (infinite loop)
python -m cortex.phase_management.autonomous_executor

# Output:
# 🟢 CORTEX Autonomous Executor Ready
# 🖥️  Machine: MacBook-M3 (Darwin/arm64)
# 📋 Queue: 6 phases (48 days total)
#
# ⏳ Waiting for next phase...
# 🚀 Starting phase-52 (S2-S6)
# ├─ [████████░░] 40% S4: Enterprise Refactoring
# ├─ Tests: 180/450 passing
# └─ ETA: 2026-02-26 10:00:00 UTC
```

### 3. Monitor Progress (Optional)

```bash
# Terminal 2: Monitor in real-time
tail -f cortex-registry/_cortex-master/execution/logs/execution.log

# Or: Check status
python -c "
from cortex.phase_management.autonomous_executor import AutonomousPhaseExecutor
executor = AutonomousPhaseExecutor()
executor.print_execution_plan()
"
```

## Status Tracking

### Execution Status File

`cortex-registry/_cortex-master/execution/machine-registry.yaml`

Tracks in real-time:
- Which phase is running on which machine
- Progress (stage, test count, coverage)
- Next phase queueing
- Heartbeat timestamps

### Logs

`cortex-registry/_cortex-master/execution/logs/`

```
execution.log          # Main execution log
phase-52-execution.json  # Execution record for phase-52
phase-56-A-execution.json # Execution record for phase-56-A
machine-heartbeat.log  # Heartbeat tracking (every 60s)
```

### Git Audit Trail

Each phase start/complete/error logged to git:

```bash
git log --oneline | grep "AC-PHASE"

# Output:
# 2b4a8e3 AC-PHASE52-FULL: Autonomous execution (17d, 450/450 tests, 96.2% coverage)
# a3f2c9e AC-PHASE52-S6: Integration + docs (36h)
# ...
```

## Machine Continuity Rules

### Rule 1: OS/Arch Lock

Once a phase starts on a machine, it can ONLY continue on the same OS/arch:

```
phase-52 starts on macOS/arm64
├─ Can continue on MacBook-M3 ✅ (same macOS/arm64)
├─ Cannot continue on MacBook-Intel ❌ (different x86_64)
└─ Cannot continue on Linux ❌ (different OS)
```

### Rule 2: Hostname Flexibility

But hostname CAN differ (e.g., machine re-imaged, cluster node):

```
phase-52 starts on MacBook-M3.local
├─ Can continue if re-imaged to MacBook-M3b.local ✅ (same OS/arch)
├─ Cannot continue on laptop-replacement.local ❌ (if different arch)
```

### Rule 3: Stale Detection

If machine goes silent for >5 minutes:

```
phase-52 on MacBook-M3
├─ 10:00 - Started ✅ (heartbeat)
├─ 10:01 - Running ✅ (heartbeat)
├─ 10:05 - STALE ⚠️  (no heartbeat for 5 min)
├─ Option A: Wait for MacBook to recover (default)
├─ Option B: Resume on different machine (manual approval)
└─ Timeout: 5 minutes before marking stale
```

### Rule 4: Parallel Phase Freedom

Parallel siblings can run on DIFFERENT machines:

```
phase-52 starts on MacBook-M3
├─ next_phase = phase-56-A (must stay on MacBook-M3)
├─ parallel_phases = [phase-56-A, phase-49]
│
├─> phase-56-A on MacBook-M3 ✅ (next after 52)
└─> phase-49 on AWS-EC2-Linux ✅ (parallel, any machine)
```

## Failure Handling

### Recoverable Errors

Phase fails (e.g., test timeout):

1. ✅ Checkpoint saved (stage S4-end)
2. ⏸️ Phase paused in queue
3. 🖥️ On same machine: Resume from checkpoint
4. ❌ On different machine: Blocked (must use original)

```bash
# Resume on same machine
python -m cortex.phase_management.autonomous_executor --resume phase-52
```

### Critical Errors

Phase fails catastrophically (e.g., database corruption):

1. 🔴 Mark as `failed_critical`
2. 🛑 Halt execution chain
3. 📧 Alert infrastructure team
4. 🔍 Keep workspace for debugging

### Crash Recovery

Machine crashes during phase execution:

1. 🖥️ Detect via heartbeat timeout (5 min)
2. ⏳ Mark phase as stale
3. ⚙️ When machine recovers: Auto-resume from checkpoint
4. 🔄 Or: Manual restart from beginning

## Configuration

### Silent Mode

```yaml
execution_queue:
  silent_mode:
    enabled: true                 # No user prompts
    no_user_prompts: true        # Silent
    no_confirmations: true       # Auto-proceed
    auto_fix_issues: true        # Recover from errors
    continuous_heartbeat: false  # Only log at boundaries
```

### Monitoring

```yaml
execution_queue:
  monitoring:
    enabled: true
    collect_metrics:
      - test_count_per_stage
      - coverage_per_stage
      - execution_time_per_stage
    anomaly_detection:
      test_pass_rate_drop: 90    # Alert if <90%
      execution_time_spike: 2.0  # Alert if 2x slower
```

### Heartbeat Timeout

```yaml
machine_continuity_rules:
  heartbeat_interval_seconds: 60
  stale_heartbeat_timeout_seconds: 300  # 5 minutes
```

## Troubleshooting

### Phase stuck in "waiting_for_machine"

```bash
# Check why phase can't execute
python -c "
from cortex.phase_management.autonomous_executor import AutonomousPhaseExecutor

executor = AutonomousPhaseExecutor()
record = executor.load_execution_record('phase-56-A')
can_execute, reason = executor.can_execute_on_current_machine(record)

print(f'Can execute: {can_execute}')
print(f'Reason: {reason}')
"
```

**Common causes:**
- Phase started on macOS/arm64, current is Linux/x86_64
- Previous machine crashed (use `--force-machine` to override)

### Phase not auto-chaining to next

Check next_phase_on_completion:

```bash
python -c "
import yaml
with open('cortex-registry/_cortex-master/index.yaml') as f:
    data = yaml.safe_load(f)
    for phase in data['execution_queue']['autonomous_queue']:
        print(f\"{phase['phase_id']}: next = {phase.get('next_phase_on_completion')}\")
"
```

### Monitor heartbeat in real-time

```bash
tail -f cortex-registry/_cortex-master/execution/logs/machine-heartbeat.log
```

### View execution status

```bash
cat cortex-registry/_cortex-master/execution/machine-registry.yaml | grep -A 10 "phase_machine_locks"
```

## Cost & Duration Estimates

| Phase | Duration | Tests | Coverage | Effort |
|-------|----------|-------|----------|--------|
| phase-52 | 17 days | 450 | 96% | Very High |
| phase-56-A | 5 days | 120 | 92% | High |
| phase-49 | 6 days | 122 | 90% | Very High |
| phase-48 | 8 days | 105 | 95% | High |
| phase-50 | 12 days | 110 | 92% | Very High |
| phase-51 | 12 days | 130 | 95% | Very High |
| **TOTAL** | **~48 days** | **~1000** | **~93%** | **Massive** |

**Key:** Parallel execution (phase-56-A + phase-49) saves ~5-6 days

## Next Steps

1. ✅ Initialize execution queue: `executor.setup_autonomous_queue(...)`
2. ✅ Display execution plan: `executor.print_execution_plan()`
3. 🚀 Start autonomous executor: `python -m cortex.phase_management.autonomous_executor`
4. 📊 Monitor progress: `tail -f execution/logs/execution.log`
5. ✅ On completion: Review metrics and deployment readiness

---

**Authority:** CORTEX Architect Instructions v15.1 + Phase 56 Requirements  
**Approved:** 2026-02-09  
**Status:** Ready for Autonomous Execution ✅
