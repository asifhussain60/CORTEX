# Checkpoint & Rollback System - Implementation Guide

**Author:** Asif Hussain  
**Date:** 2025-11-28  
**Status:** Production Ready  
**Version:** 1.0.0

---

## Overview

The Checkpoint & Rollback System provides workflow phase tracking with git-based checkpoints and safe rollback capabilities for CORTEX workflows (Planning, TDD, System Alignment).

**Key Features:**
- ✅ Automated checkpoint creation at phase boundaries
- ✅ Metadata tracking (metrics, timestamps, commit SHAs)
- ✅ Safety checks (uncommitted changes, merge detection)
- ✅ Natural language rollback commands
- ✅ Dry-run mode for preview before rollback
- ✅ Force mode for emergency rollback

---

## Architecture

### Components

```
src/orchestrators/
├── phase_checkpoint_manager.py    # Checkpoint metadata storage
├── rollback_orchestrator.py       # Rollback workflow orchestration
└── rollback_command_parser.py     # Natural language command parsing

src/enrichers/
└── git_history_enricher.py        # Git commit history with caching

src/utils/
├── progress_bar.py                # Visual progress indicators
└── template_renderer.py           # Template rendering with progress

tests/
├── orchestrators/                 # Unit tests for components
├── integration/                   # Integration tests (5 files, 57 tests)
└── e2e/                          # End-to-end workflow tests (11 tests)
```

### Data Flow

```
User Command
    ↓
RollbackCommandParser → parse natural language
    ↓
RollbackOrchestrator → validate & check safety
    ↓
PhaseCheckpointManager → retrieve checkpoint metadata
    ↓
GitCheckpointOrchestrator → execute git reset
    ↓
Result with confirmation/error
```

---

## Component Details

### 1. PhaseCheckpointManager

**Purpose:** Stores and retrieves checkpoint metadata for workflow phases.

**Storage:** `.cortex/phase-checkpoints-{session_id}.json`

**Key Methods:**
```python
from src.orchestrators.phase_checkpoint_manager import PhaseCheckpointManager

# Initialize
manager = PhaseCheckpointManager(cortex_root=Path("/path/to/CORTEX"))

# Store checkpoint
manager.store_checkpoint_metadata(
    session_id="feature-auth-001",
    phase="Implementation",
    checkpoint_id="impl-checkpoint-1",
    commit_sha="abc123def456",
    metrics={"tests_passing": 25, "coverage": 92.5}
)

# Retrieve checkpoint
checkpoint = manager.get_checkpoint_metadata(
    session_id="feature-auth-001",
    phase="Implementation"
)

# List all checkpoints
checkpoints = manager.list_checkpoints(session_id="feature-auth-001")
```

**Metadata Structure:**
```json
{
  "session_id": "feature-auth-001",
  "created_at": "2025-11-28T10:30:00Z",
  "checkpoints": [
    {
      "phase": "DoR",
      "checkpoint_id": "dor-checkpoint",
      "commit_sha": "abc123",
      "created_at": "2025-11-28T10:30:00Z",
      "metrics": {
        "requirements_validated": true,
        "acceptance_criteria_count": 5
      }
    }
  ]
}
```

### 2. RollbackOrchestrator

**Purpose:** Orchestrates rollback operations with validation and safety checks.

**Key Methods:**
```python
from src.orchestrators.rollback_orchestrator import RollbackOrchestrator

# Initialize
orchestrator = RollbackOrchestrator(
    cortex_dir=Path("/path/to/CORTEX"),
    project_root=Path("/path/to/project")
)

# List available checkpoints
checkpoints = orchestrator.list_checkpoints(session_id="feature-auth-001")

# Validate checkpoint exists
is_valid = orchestrator.validate_checkpoint(
    session_id="feature-auth-001",
    checkpoint_id="dor-checkpoint"
)

# Check rollback safety
safety = orchestrator.check_rollback_safety(checkpoint_id="dor-checkpoint")
# Returns: {'safe': bool, 'warning': str, 'details': str}

# Execute rollback (dry-run)
result = orchestrator.execute_rollback(
    checkpoint_id="dor-checkpoint",
    dry_run=True  # Preview only
)

# Execute rollback (force)
result = orchestrator.execute_rollback(
    checkpoint_id="dor-checkpoint",
    force=True  # Bypass safety checks
)
```

**Safety Checks:**
- ✅ Uncommitted changes detection
- ✅ Merge in progress detection
- ✅ Working tree cleanliness
- ✅ Checkpoint existence validation

### 3. RollbackCommandParser

**Purpose:** Parses natural language rollback commands into structured data.

**Supported Formats:**
```
1. Standard: "rollback to checkpoint dor-checkpoint session feature-auth-001"
2. Session: "rollback session feature-auth-001 to dor-checkpoint"
3. Shorthand: "rollback dor-checkpoint"
```

**Usage:**
```python
from src.orchestrators.rollback_command_parser import RollbackCommandParser

parser = RollbackCommandParser()

# Parse command
result = parser.parse_command("rollback to checkpoint dor-checkpoint session feature-auth-001")

# Result structure:
{
    'valid': True,
    'checkpoint_id': 'dor-checkpoint',
    'session_id': 'feature-auth-001',
    'flags': {},
    'error': None
}
```

---

## Integration with Orchestrators

### Planning Orchestrator

Checkpoints created at:
- **DoR Phase:** After requirements validation
- **Implementation Phase:** After feature completion
- **DoD Phase:** After all acceptance criteria met

```python
from src.orchestrators.planning_orchestrator import PlanningOrchestrator

orchestrator = PlanningOrchestrator()

# Checkpoint automatically created when phase completes
orchestrator.complete_phase(
    session_id="plan-001",
    phase="DoR",
    metrics={"requirements_validated": True}
)
# Creates checkpoint: .cortex/phase-checkpoints-plan-001.json
```

### TDD Orchestrator

Checkpoints created at:
- **RED Phase:** After test fails
- **GREEN Phase:** After test passes
- **REFACTOR Phase:** After code cleanup

```python
from src.orchestrators.tdd_workflow_orchestrator import TDDWorkflowOrchestrator

orchestrator = TDDWorkflowOrchestrator()

# Checkpoint automatically created at each phase
orchestrator.complete_red_phase(
    session_id="tdd-001",
    metrics={"tests_failing": 3}
)
# Creates checkpoint: .cortex/phase-checkpoints-tdd-001.json
```

### System Alignment Orchestrator

Checkpoints created at:
- **Discovery Phase:** After catalog features discovered
- **Validation Phase:** After integrations scored

---

## Usage Scenarios

### Scenario 1: Rollback from Failed Implementation

**Situation:** Implementation went wrong, need to return to DoR.

```python
# 1. List available checkpoints
checkpoints = orchestrator.list_checkpoints(session_id="feature-auth-001")
# Shows: dor-checkpoint, impl-checkpoint-1, impl-checkpoint-2

# 2. Preview rollback
result = orchestrator.execute_rollback(
    checkpoint_id="dor-checkpoint",
    dry_run=True
)
print(result['preview'])  # Shows git diff

# 3. Execute rollback
result = orchestrator.execute_rollback(
    checkpoint_id="dor-checkpoint"
)
# Returns: {'executed': True, 'message': 'Rollback completed successfully'}
```

### Scenario 2: Rollback During TDD Refactoring

**Situation:** Refactoring broke tests, need to return to GREEN phase.

```python
# 1. Check safety
safety = orchestrator.check_rollback_safety(checkpoint_id="green-checkpoint")
if not safety['safe']:
    print(f"Warning: {safety['warning']}")
    # Commit changes or use force=True

# 2. Rollback to last GREEN
result = orchestrator.execute_rollback(
    checkpoint_id="green-checkpoint"
)
# Tests now passing again
```

### Scenario 3: Resume Workflow After Interruption

**Situation:** Work interrupted, need to resume from last checkpoint.

```python
# 1. List checkpoints to find last state
checkpoints = orchestrator.list_checkpoints(session_id="feature-auth-001")
last_checkpoint = checkpoints[-1]

print(f"Last checkpoint: {last_checkpoint['phase']}")
print(f"Metrics: {last_checkpoint['metrics']}")

# 2. Continue from this point
# (No rollback needed, just continue with next phase)
```

---

## Error Handling

### Common Errors

**1. Uncommitted Changes**
```python
# Error message:
"Safety check failed: Uncommitted changes detected
Files: file1.py, file2.py
Commit or stash changes before rollback."

# Solution: Commit or force
git add .
git commit -m "WIP"
# OR
result = orchestrator.execute_rollback(checkpoint_id="...", force=True)
```

**2. Merge in Progress**
```python
# Error message:
"Safety check failed: Merge in progress - resolve conflicts first"

# Solution: Complete or abort merge
git merge --abort
# OR complete the merge, then rollback
```

**3. Checkpoint Not Found**
```python
# Error message:
"Invalid checkpoint: dor-checkpoint not found"

# Solution: List available checkpoints
checkpoints = orchestrator.list_checkpoints(session_id="...")
print([cp['checkpoint_id'] for cp in checkpoints])
```

---

## Performance Characteristics

**Benchmark Results (from test_performance.py):**

| Operation | Target | Actual | Status |
|-----------|--------|--------|--------|
| Checkpoint creation | <500ms | <100ms | ✅ |
| Checkpoint listing | <100ms | <50ms | ✅ |
| Git history (20 commits) | <2s | 0.7s | ✅ |
| Bulk checkpoints (100) | <5s | 1.5s | ✅ |
| Progress bar render | <10ms | <1ms | ✅ |
| Template render | <50ms | <10ms | ✅ |

**Caching:**
- Git history cached (1.2-1.4x speedup)
- Checkpoint metadata cached in memory
- Progress calculations memoized

---

## Testing

### Test Coverage

**Unit Tests (25 tests):**
- `test_phase_checkpoint_manager_extended.py` (9 tests)
- `test_rollback_orchestrator_extended.py` (16 tests)

**Integration Tests (57 tests):**
- `test_orchestrator_wiring.py` (7 tests)
- `test_user_commands.py` (12 tests)
- `test_template_progress.py` (12 tests)
- `test_error_handling.py` (15 tests)
- `test_performance.py` (11 tests)

**End-to-End Tests (11 tests):**
- `test_full_workflow_scenarios.py` (11 tests)

**Run Tests:**
```bash
# All tests
pytest tests/orchestrators/test_phase_checkpoint_manager_extended.py -v
pytest tests/integration/test_orchestrator_wiring.py -v
pytest tests/e2e/test_full_workflow_scenarios.py -v

# With coverage
pytest tests/ --cov=src.orchestrators.phase_checkpoint_manager --cov-report=term-missing
```

---

## Best Practices

### 1. Checkpoint Naming

✅ **Good:**
```python
checkpoint_id = "dor-validated-2025-11-28"
checkpoint_id = "impl-feature-a-complete"
checkpoint_id = "green-all-tests-passing"
```

❌ **Bad:**
```python
checkpoint_id = "checkpoint1"  # Not descriptive
checkpoint_id = "temp"  # Not meaningful
```

### 2. Metrics Tracking

✅ **Good:**
```python
metrics = {
    "tests_passing": 25,
    "tests_failing": 0,
    "coverage": 92.5,
    "duration_s": 45.2
}
```

❌ **Bad:**
```python
metrics = {}  # No information tracked
metrics = {"status": "done"}  # Too generic
```

### 3. Session ID Format

✅ **Good:**
```python
session_id = "feature-auth-001"  # Feature-based
session_id = "bugfix-issue-123"  # Issue-based
session_id = "plan-2025-11-28"   # Date-based
```

### 4. Safety Check Usage

✅ **Always check safety before rollback:**
```python
safety = orchestrator.check_rollback_safety(checkpoint_id)
if not safety['safe']:
    print(f"Warning: {safety['warning']}")
    # Get user confirmation or abort
```

---

## Troubleshooting

### Issue: Checkpoint file corrupted

**Symptom:** `json.JSONDecodeError` when listing checkpoints

**Solution:**
```bash
# Backup corrupted file
cp .cortex/phase-checkpoints-session-001.json .cortex/backup/

# Reinitialize from git history
python -c "
from src.orchestrators.phase_checkpoint_manager import PhaseCheckpointManager
manager = PhaseCheckpointManager()
# Recreate checkpoints from git log
"
```

### Issue: Git reset fails

**Symptom:** `Git reset failed: error message`

**Solution:**
```bash
# Check git status
git status

# Ensure clean working tree
git stash

# Retry rollback
```

### Issue: Performance degradation

**Symptom:** Checkpoint operations slow

**Solution:**
```python
# Clear cache
from src.enrichers.git_history_cache import GitHistoryCache
cache = GitHistoryCache()
cache.clear()

# Compact checkpoint files
# (Remove old sessions not needed)
```

---

## API Reference

See component docstrings for detailed API documentation:

- `src/orchestrators/phase_checkpoint_manager.py`
- `src/orchestrators/rollback_orchestrator.py`
- `src/orchestrators/rollback_command_parser.py`

---

## Future Enhancements

**Planned Features:**
1. Checkpoint compression for old sessions
2. Remote checkpoint storage (GitHub Gist)
3. Checkpoint diffing (compare two checkpoints)
4. Automatic cleanup of old checkpoints
5. Checkpoint export/import for sharing

---

**For Support:** See user documentation in `user-guide-rollback-commands.md`
