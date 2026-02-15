# Autonomous Execution Guide (ENH-067)

**Authority:** Phase-N Implementation | **Status:** Complete ✅

## Overview

CORTEX Autonomous Execution Engine enables true "approve → done" workflow following CORE-049 silent autonomous execution protocol. Once approved, multi-stage plans execute without mid-execution prompts, with automatic progress tracking and rollback capabilities.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   User Request                          │
│                  "Implement X"                          │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│              IntentRouter + PlanOrchestrator            │
│         Creates multi-stage execution plan              │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│              AutonomousExecutor                         │
│  • Silent execution (no prompts)                        │
│  • Token budget monitoring (75% checkpoint)             │
│  • Error recovery (continue on non-critical)            │
└─────────────────┬───────────────────────────────────────┘
                  │
        ┌─────────┴──────────┐
        ▼                    ▼
┌───────────────┐   ┌────────────────┐
│ProgressTracker│   │ RollbackManager│
│ • Snapshots    │   │ • Checkpoints  │
│ • Dashboard DB │   │ • Git commits  │
└───────────────┘   └────────────────┘
```

## Core Components

### 1. AutonomousExecutor

**Path:** `cortex/execution/autonomous_executor.py`

**Purpose:** Executes multi-stage plans without user intervention

**Key Methods:**
- `execute_plan(plan, silent=True)` - Main execution entry point
- `_execute_stage(stage)` - Execute individual stage
- `_should_checkpoint(tokens)` - Monitor token budget
- `_should_continue_on_error(stage)` - Error recovery logic

**Example:**
```python
from cortex.execution.autonomous_executor import AutonomousExecutor, Plan, Stage
from cortex.models.canonical_enums import IntentType

# Create plan
plan = Plan(
    id="Phase-N",
    name="Autonomous Implementation",
    description="Multi-stage feature implementation",
    stages=[
        Stage("S1", "Implement core", "Core logic", IntentType.IMPLEMENT, estimated_tokens=10000),
        Stage("S2", "Add tests", "Unit tests", IntentType.TEST, estimated_tokens=5000),
        Stage("S3", "Refactor", "Clean up", IntentType.REFACTOR, estimated_tokens=7000),
    ]
)

# Execute autonomously
executor = AutonomousExecutor()
result = executor.execute_plan(plan, silent=True)

# Check result
if result.status == ExecutionStatus.COMPLETED:
    print(f"✅ Success: {result.completed_stages}/{result.total_stages} stages")
elif result.status == ExecutionStatus.CHECKPOINT:
    print(f"⏸️ Checkpoint: Continue with:\n{result.continuation_prompt}")
```

### 2. ProgressTracker

**Path:** `cortex/execution/progress_tracker.py`

**Purpose:** Real-time progress tracking with dashboard integration

**Features:**
- Progress snapshots after each stage
- SQLite dashboard persistence
- Timing metrics collection
- Completion percentage tracking

**Example:**
```python
from cortex.execution.progress_tracker import ProgressTracker
from pathlib import Path

# Initialize with dashboard DB
tracker = ProgressTracker(db_path=Path("cortex_brain/state/dashboard.db"))

# Use with executor
executor = AutonomousExecutor(progress_tracker=tracker)
result = executor.execute_plan(plan)

# Get progress summary
summary = tracker.get_progress_summary()
print(f"Progress: {summary['completion_percentage']:.1f}%")
print(f"Token usage: {summary['token_usage']:,}")
print(f"Avg stage duration: {summary['avg_stage_duration_seconds']:.1f}s")
```

### 3. RollbackManager

**Path:** `cortex/execution/rollback_manager.py`

**Purpose:** Git-backed rollback for execution recovery

**Features:**
- Checkpoint creation after each stage
- Git commit hash tracking
- Rollback to previous checkpoints
- Checkpoint history management

**Example:**
```python
from cortex.execution.rollback_manager import RollbackManager

# Initialize
rollback = RollbackManager()

# Use with executor
executor = AutonomousExecutor(rollback_manager=rollback)
result = executor.execute_plan(plan)

# List checkpoints
checkpoints = rollback.list_checkpoints()
for cp in checkpoints:
    print(f"{cp.id}: {cp.commit_hash[:8]} - {cp.description}")

# Rollback if needed
if something_went_wrong:
    success = rollback.rollback_to_checkpoint("S2")  # Rollback to stage 2
```

## Token Budget Management

**Threshold:** 75% of 1M token budget (750,000 tokens)

**Behavior:**
1. Executor stages token usage across stages
2. Before each stage, checks: `current_usage + next_stage_tokens >= 750k`
3. If threshold exceeded, creates checkpoint and stops
4. Generates continuation prompt with:
   - Completed stages summary
   - Pending stages list
   - Token usage breakdown
   - Continuation command

**Continuation Workflow:**
```bash
# Session 1: Execute until checkpoint
User: "Implement feature X"
→ Executes S1-S5 (700k tokens used)
→ Checkpoint created before S6
→ Displays continuation prompt

# Session 2: Continue from checkpoint
User: [Copy continuation prompt to new Copilot Chat]
→ Resumes from S6
→ Executes S6-S10 to completion
```

## Error Recovery

**Strategy:** Continue on non-critical errors, stop on critical failures

**Non-Critical Stage:**
- Name doesn't contain "critical"
- Stage ID doesn't end with "-critical"
- **Action:** Mark as SKIPPED, continue to next stage

**Critical Stage:**
- Name contains "critical" or ID ends with "-critical"
- **Action:** Stop execution, return failure result

**Example:**
```python
stages = [
    Stage("S1", "Setup", "...", IntentType.IMPLEMENT),
    Stage("S2-critical", "Database migration", "...", IntentType.FIX),  # Critical
    Stage("S3", "Optional analytics", "...", IntentType.REFACTOR),
]

# If S1 fails → skip, continue to S2
# If S2 fails → stop (critical failure)
# If S3 fails → skip (non-critical)
```

## Progress Dashboard Integration

**Database Schema:**

```sql
-- Execution plans
CREATE TABLE execution_plans (
    plan_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    total_stages INTEGER,
    start_time REAL,
    status TEXT
);

-- Stage tracking
CREATE TABLE execution_stages (
    stage_id TEXT PRIMARY KEY,
    plan_id TEXT,
    name TEXT NOT NULL,
    status TEXT,
    start_time REAL,
    end_time REAL,
    FOREIGN KEY (plan_id) REFERENCES execution_plans (plan_id)
);

-- Progress snapshots
CREATE TABLE progress_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id TEXT,
    timestamp REAL,
    completed_stages INTEGER,
    failed_stages INTEGER,
    token_usage INTEGER,
    FOREIGN KEY (plan_id) REFERENCES execution_plans (plan_id)
);
```

**Query Examples:**

```python
import sqlite3

conn = sqlite3.connect("cortex_brain/state/dashboard.db")
cursor = conn.cursor()

# Get all plans
cursor.execute("SELECT * FROM execution_plans ORDER BY start_time DESC")
plans = cursor.fetchall()

# Get plan progress
cursor.execute("""
    SELECT completed_stages, total_stages, token_usage
    FROM progress_snapshots
    WHERE plan_id = ?
    ORDER BY timestamp DESC
    LIMIT 1
""", ("Phase-N",))
progress = cursor.fetchone()

# Get stage timings
cursor.execute("""
    SELECT stage_id, (end_time - start_time) as duration
    FROM execution_stages
    WHERE plan_id = ? AND end_time IS NOT NULL
    ORDER BY start_time
""", ("Phase-N",))
timings = cursor.fetchall()
```

## Testing

**Unit Tests:** 18 tests in `tests/unit/execution/test_autonomous_executor.py`
- Stage/Plan model tests
- Execution result calculations
- Single/multi-stage execution
- Token budget checkpointing
- Error recovery scenarios

**Integration Tests:** 13 tests in `tests/integration/test_progress_and_rollback.py`
- Progress tracking with snapshots
- Dashboard persistence
- Rollback checkpoint creation
- Integrated executor + tracker + rollback

**Run Tests:**
```bash
# Unit tests
pytest tests/unit/execution/test_autonomous_executor.py -v

# Integration tests
pytest tests/integration/test_progress_and_rollback.py -v

# All autonomous execution tests
pytest tests/unit/execution/ tests/integration/test_progress_and_rollback.py -v
```

## Success Metrics

**Target:** 25 tests | **Achieved:** 31 tests (124%)

| Metric | Target | Achieved | Status |
|--------|--------|----------|--------|
| **Tests** | 25 | 31 | ✅ 124% |
| **Commits** | 3 | Pending | ⚪ |
| **Token Budget** | <190k | ~58k | ✅ 30% |
| **Silent Execution** | Yes | Yes | ✅ |
| **Checkpointing** | 75% | 75% | ✅ |
| **Error Recovery** | Yes | Yes | ✅ |

## CORE-049 Compliance

**Silent Autonomous Execution:**
- ✅ No mid-execution prompts
- ✅ ASCII progress bars only
- ✅ Completion/error reporting
- ✅ Automatic checkpoint creation
- ✅ Continuation prompts generated

**Forbidden:**
- ❌ "Shall I proceed?" questions
- ❌ Mid-execution approvals
- ❌ Multi-paragraph narration
- ❌ Exit options during execution

## Integration with CORTEX

**MasterOrchestrator Integration:**
```python
# In cortex/orchestrators/master_orchestrator.py

from cortex.execution.autonomous_executor import AutonomousExecutor, Plan, Stage

class MasterOrchestrator:
    def execute_autonomous_plan(self, user_request: str):
        # 1. Classify intent
        intent = self.intent_classifier.classify(user_request)
        
        # 2. Create multi-stage plan
        plan = self.plan_orchestrator.create_plan(intent)
        
        # 3. Execute autonomously
        executor = AutonomousExecutor(
            progress_tracker=self.progress_tracker,
            rollback_manager=self.rollback_manager
        )
        
        result = executor.execute_plan(plan, silent=True)
        
        # 4. Return result
        return result
```

## Future Enhancements

**Potential Improvements:**
1. **Parallel Stage Execution** - Execute independent stages concurrently
2. **Dynamic Token Estimation** - Machine learning for better token predictions
3. **Smart Rollback** - Auto-rollback on test failures
4. **Progress Streaming** - WebSocket updates for real-time dashboard
5. **Stage Dependencies** - Advanced DAG-based execution order

## Related Documentation

- `.github/copilot-instructions.md` § Silent Autonomous Execution
- `cortex-registry/_cortex-master/index.yaml` § Phase-N specification
- `.github/prompts/CORTEX.prompt.md` § MCP-FIRST architecture

---

**Version:** 1.0.0  
**Updated:** 2026-02-12  
**Authors:** Asif Hussain  
**Reviewed:** Phase-N-20260212-01
