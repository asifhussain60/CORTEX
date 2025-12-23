# GitCheckpoint Orchestrator Guide

**Purpose:** Manages git checkpoints for TDD workflow automation with SKULL Rule #8 compliance.

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)

---

## Overview

The GitCheckpointOrchestrator automates git checkpoint creation and management during TDD workflows, ensuring code safety through automated version control operations. It implements SKULL Rule #8 ("Always create git checkpoint before major refactoring") and provides rollback capabilities for safe experimentation.

**Key Features:**
- **Pre-implementation checkpoints** - Automatic checkpoint before starting each TDD phase
- **Phase completion commits** - Automated commits with rich metadata (session ID, phase, metrics)
- **Rollback capability** - Restore to any previous checkpoint by session or commit SHA
- **SKULL Rule #8 compliance** - Enforces git safety rules
- **Branch preservation** - Maintains current branch context
- **Stash management** - Auto-stash uncommitted changes before checkpoints
- **Metadata tracking** - JSON-based checkpoint history in `.cortex/checkpoints.json`

**Use Cases:**
- TDD workflow automation (RED→GREEN→REFACTOR cycle)
- Experimental feature development with rollback
- Team code review checkpoints
- Compliance tracking for git operations

---

## Natural Language Commands

**Primary Commands:**
- `create checkpoint` - Create checkpoint at current state
- `git checkpoint` - Alias for create checkpoint
- `save checkpoint` - Alias for create checkpoint
- `commit phase` - Commit current TDD phase completion
- `rollback to checkpoint` - Restore to previous checkpoint
- `list checkpoints` - Show all checkpoints for current session
- `validate skull rule 8` - Check SKULL Rule #8 compliance

**Examples:**
```
User: "create checkpoint before refactoring the payment module"
CORTEX: 🔖 Creating checkpoint...
        ✅ Checkpoint created: abc12345 on development
        You can rollback with: rollback to checkpoint abc12345

User: "commit green phase completion"
CORTEX: 💾 Committing GREEN phase...
        ✅ Phase committed: def67890
        Metrics: Duration: 15m, Tests: 8 passing

User: "rollback to last checkpoint"
CORTEX: 🔄 Rolling back to checkpoint abc12345...
        ✅ Rolled back successfully
```

---

## Usage

### Basic Usage (Python API)

```python
from pathlib import Path
from src.orchestrators.git_checkpoint_orchestrator import GitCheckpointOrchestrator

# Initialize with project root
project_root = Path("/path/to/project")
orchestrator = GitCheckpointOrchestrator(project_root)

# Create pre-implementation checkpoint
checkpoint_id = orchestrator.create_checkpoint(
    session_id="tdd-session-123",
    phase="RED",
    message="Starting test implementation"
)
print(f"Checkpoint created: {checkpoint_id}")

# Commit phase completion
commit_sha = orchestrator.commit_phase_completion(
    session_id="tdd-session-123",
    phase="GREEN",
    metrics={"duration": "15m", "tests_passing": 8}
)
print(f"Phase committed: {commit_sha}")

# List all checkpoints for session
checkpoints = orchestrator.list_checkpoints(session_id="tdd-session-123")
for cp in checkpoints:
    print(f"{cp['checkpoint_id'][:8]} - {cp['phase']} - {cp['timestamp']}")

# Rollback to checkpoint
success = orchestrator.rollback_to_checkpoint(
    session_id="tdd-session-123",
    checkpoint_id="abc12345"  # Optional: if None, uses last checkpoint
)
```

### TDD Workflow Integration

```python
# Complete RED→GREEN→REFACTOR cycle with checkpoints

# 1. RED Phase: Write failing test
orchestrator.create_checkpoint("tdd-123", "RED", "Pre-RED: Writing failing test")
# ... write test ...
orchestrator.commit_phase_completion("tdd-123", "RED", {"tests_written": 1})

# 2. GREEN Phase: Make test pass
orchestrator.create_checkpoint("tdd-123", "GREEN", "Pre-GREEN: Implementing feature")
# ... implement feature ...
orchestrator.commit_phase_completion("tdd-123", "GREEN", {"tests_passing": 1})

# 3. REFACTOR Phase: Clean up code
orchestrator.create_checkpoint("tdd-123", "REFACTOR", "Pre-REFACTOR: Code cleanup")
# ... refactor ...
orchestrator.commit_phase_completion("tdd-123", "REFACTOR", {"methods_refactored": 3})

# If refactoring breaks tests, rollback
if tests_failing:
    orchestrator.rollback_to_checkpoint("tdd-123")  # Rolls back to last REFACTOR checkpoint
```

---

## API Reference

### Class: GitCheckpointOrchestrator

#### Constructor

```python
GitCheckpointOrchestrator(project_root: Path)
```

**Parameters:**
- `project_root` - Path to git repository root directory

**Initialization:**
- Creates `.cortex/checkpoints.json` if missing
- Validates git repository exists
- Sets up checkpoint tracking

---

#### Methods

##### create_checkpoint()

```python
create_checkpoint(
    session_id: str,
    phase: str,
    message: Optional[str] = None
) -> Optional[str]
```

Create a git checkpoint before starting work. Implements SKULL Rule #8.

**Parameters:**
- `session_id` - TDD session identifier (e.g., "tdd-session-123")
- `phase` - Current phase: "RED", "GREEN", or "REFACTOR"
- `message` - Optional custom checkpoint message

**Returns:**
- Checkpoint ID (commit SHA) or None if failed

**Behavior:**
- Auto-stashes uncommitted changes if present
- Records checkpoint in `.cortex/checkpoints.json`
- Preserves current branch
- Logs checkpoint creation with emoji indicators

**Example:**
```python
checkpoint_id = orchestrator.create_checkpoint(
    session_id="tdd-payment-feature",
    phase="REFACTOR",
    message="Before extracting payment validation logic"
)
# Returns: "abc123def456..." (commit SHA)
```

---

##### commit_phase_completion()

```python
commit_phase_completion(
    session_id: str,
    phase: str,
    metrics: Optional[Dict] = None
) -> Optional[str]
```

Commit phase completion with metadata.

**Parameters:**
- `session_id` - TDD session identifier
- `phase` - Completed phase: "RED", "GREEN", or "REFACTOR"
- `metrics` - Optional metrics dict (duration, tests_passing, lines_changed, etc.)

**Returns:**
- Commit SHA or None if failed

**Commit Message Format:**
```
CORTEX TDD: GREEN phase complete

Session: tdd-payment-feature
Phase: GREEN
Timestamp: 2025-11-25 14:30:00

Metrics:
  duration: 15m
  tests_passing: 8
  lines_changed: 45
```

**Example:**
```python
commit_sha = orchestrator.commit_phase_completion(
    session_id="tdd-payment-feature",
    phase="GREEN",
    metrics={
        "duration": "15m",
        "tests_passing": 8,
        "lines_changed": 45
    }
)
```

---

##### rollback_to_checkpoint()

```python
rollback_to_checkpoint(
    session_id: str,
    checkpoint_id: Optional[str] = None
) -> bool
```

Rollback to a specific checkpoint (hard reset).

**Parameters:**
- `session_id` - TDD session identifier
- `checkpoint_id` - Optional commit SHA. If None, uses last checkpoint for session.

**Returns:**
- True if rollback successful, False otherwise

**Warning:** This performs a hard reset (`git reset --hard`). Uncommitted changes will be lost.

**Example:**
```python
# Rollback to last checkpoint
success = orchestrator.rollback_to_checkpoint("tdd-payment-feature")

# Rollback to specific checkpoint
success = orchestrator.rollback_to_checkpoint(
    session_id="tdd-payment-feature",
    checkpoint_id="abc123def456"
)
```

---

##### list_checkpoints()

```python
list_checkpoints(session_id: Optional[str] = None) -> List[Dict]
```

List all checkpoints, optionally filtered by session.

**Parameters:**
- `session_id` - Optional session ID filter

**Returns:**
- List of checkpoint dictionaries with keys:
  - `checkpoint_id` - Commit SHA
  - `session_id` - TDD session identifier
  - `phase` - Phase at checkpoint creation
  - `branch` - Git branch name
  - `timestamp` - ISO format timestamp
  - `message` - Checkpoint message

**Example:**
```python
# List all checkpoints
all_checkpoints = orchestrator.list_checkpoints()

# List checkpoints for specific session
session_checkpoints = orchestrator.list_checkpoints("tdd-payment-feature")

for cp in session_checkpoints:
    print(f"{cp['checkpoint_id'][:8]} | {cp['phase']} | {cp['timestamp']}")
```

---

##### validate_skull_rule_8()

```python
validate_skull_rule_8(session_id: str) -> bool
```

Validate SKULL Rule #8 compliance for a session.

**Rule #8:** "Always create git checkpoint before major refactoring"

**Parameters:**
- `session_id` - TDD session identifier

**Returns:**
- True if at least one checkpoint exists for session

**Example:**
```python
is_compliant = orchestrator.validate_skull_rule_8("tdd-payment-feature")
if not is_compliant:
    print("⚠️ SKULL Rule #8 violation: No checkpoint before refactoring")
```

---

## Configuration

### Checkpoint Storage

Checkpoints are tracked in `.cortex/checkpoints.json`:

```json
{
  "checkpoints": [
    {
      "checkpoint_id": "abc123def456...",
      "session_id": "tdd-payment-feature",
      "phase": "REFACTOR",
      "branch": "development",
      "timestamp": "2025-11-25T14:30:00.123456",
      "message": "Before extracting payment validation logic"
    }
  ]
}
```

**File Location:** `{project_root}/.cortex/checkpoints.json`

**Persistence:** File survives across sessions and git operations

**Backup:** Include `.cortex/` in your backups (but exclude from git via `.gitignore`)

---

### Git Configuration

**Required:**
- Git repository initialized
- User name and email configured (`git config user.name` and `git config user.email`)

**Recommended `.gitignore` entries:**
```gitignore
# CORTEX working files (exclude from git)
.cortex/checkpoints.json
.cortex/sessions/

# CORTEX brain data (user-specific)
CORTEX/cortex-brain/tier1/
CORTEX/cortex-brain/logs/
```

---

## Integration Points

### TDD Workflow Orchestrator

GitCheckpointOrchestrator is integrated with TDDWorkflowOrchestrator:

```python
from src.orchestrators.tdd_workflow_orchestrator import TDDWorkflowOrchestrator

# TDD orchestrator automatically creates checkpoints
tdd = TDDWorkflowOrchestrator()
tdd.start_red_phase()  # Automatically creates RED checkpoint
tdd.complete_green_phase()  # Automatically commits GREEN phase
```

**Automatic checkpoint creation at:**
- Start of RED phase
- Start of GREEN phase
- Start of REFACTOR phase
- After lint validation passes
- Before running tests

---

### Lint Validation Integration

Checkpoints are created before and after lint validation:

```python
# Before lint validation
orchestrator.create_checkpoint(session_id, "PRE_LINT", "Before lint validation")

# Run lint validation
lint_result = run_linter()

if lint_result.passed:
    # Commit lint-clean code
    orchestrator.commit_phase_completion(session_id, "LINT_PASS")
else:
    # Rollback to pre-lint state
    orchestrator.rollback_to_checkpoint(session_id)
```

---

### Session Completion Integration

Session reports include checkpoint history:

```python
from src.orchestrators.session_completion_orchestrator import SessionCompletionOrchestrator

session_report = SessionCompletionOrchestrator().generate_report(session_id)

# Report includes:
# - Total checkpoints created
# - Checkpoint IDs and timestamps
# - Rollback history (if any)
# - SKULL Rule #8 compliance status
```

---

## Troubleshooting

### Issue: "Failed to create checkpoint - uncommitted changes"

**Cause:** Uncommitted changes exist and auto-stash failed

**Solution:**
```bash
# Manually stash changes
git stash push -m "Manual stash before checkpoint"

# Or commit changes first
git add .
git commit -m "WIP: Intermediate work"
```

---

### Issue: "Rollback failed - checkpoint not found"

**Cause:** Checkpoint ID doesn't exist or session ID mismatch

**Solution:**
```python
# List all checkpoints to find correct ID
checkpoints = orchestrator.list_checkpoints()
for cp in checkpoints:
    print(f"{cp['checkpoint_id'][:8]} - {cp['session_id']}")

# Use correct session ID and checkpoint ID
orchestrator.rollback_to_checkpoint(
    session_id="correct-session-id",
    checkpoint_id="abc123..."
)
```

---

### Issue: "Checkpoint file corrupted"

**Cause:** `.cortex/checkpoints.json` file corrupted or invalid JSON

**Solution:**
```python
# Backup corrupted file
import shutil
shutil.copy(".cortex/checkpoints.json", ".cortex/checkpoints.json.backup")

# Recreate file
orchestrator._ensure_checkpoints_file()
```

---

### Issue: "Git command failed with code 128"

**Cause:** Not in a git repository or git not installed

**Solution:**
```bash
# Initialize git repository if needed
git init

# Configure user (required for commits)
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Or use global config
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## Best Practices

### 1. Checkpoint Naming Convention

Use descriptive phase and message:
```python
# Good
orchestrator.create_checkpoint(
    "tdd-payment-123",
    "REFACTOR",
    "Before extracting PaymentValidator class"
)

# Avoid
orchestrator.create_checkpoint("session1", "R", "refactor")
```

---

### 2. Session ID Format

Use consistent session ID format across your team:
```python
# Format: tdd-{feature-name}-{date}
session_id = f"tdd-payment-validation-{datetime.now().strftime('%Y%m%d')}"
```

---

### 3. Metrics Tracking

Include rich metrics in phase commits:
```python
metrics = {
    "duration": "15m",
    "tests_passing": 8,
    "tests_failing": 0,
    "lines_changed": 45,
    "methods_added": 2,
    "coverage_pct": 85.5
}
orchestrator.commit_phase_completion(session_id, "GREEN", metrics)
```

---

### 4. Regular Checkpoint Cleanup

Periodically clean old checkpoints:
```python
# Keep only last 30 days of checkpoints
from datetime import datetime, timedelta

cutoff = datetime.now() - timedelta(days=30)
checkpoints = orchestrator.list_checkpoints()

recent_checkpoints = [
    cp for cp in checkpoints
    if datetime.fromisoformat(cp['timestamp']) > cutoff
]

orchestrator._save_checkpoints(recent_checkpoints)
```

---

## Related Documentation

- **TDD Workflow Guide:** `.github/prompts/modules/tdd-workflow-orchestrator-guide.md`
- **SKULL Rules:** `cortex-brain/brain-protection-rules.yaml` (Rule #8)
- **Lint Validation Guide:** `.github/prompts/modules/lint-validation-orchestrator-guide.md`
- **Session Completion Guide:** `.github/prompts/modules/session-completion-orchestrator-guide.md`

---

**Version:** 1.0.0  
**Last Updated:** 2025-11-25  
**Maintainer:** Asif Hussain  
**License:** Source-Available (Use Allowed, No Contributions)

### Class: `GitCheckpointOrchestrator`

Orchestrates git checkpoint creation and management for TDD workflows.

#### Methods

**`__init__()`**

No description available

**Parameters:**
- [param]: [description]

**Returns:**
- [return type]: [description]

---

**`_ensure_checkpoints_file()`**

No description available

**Parameters:**
- [param]: [description]

**Returns:**
- [return type]: [description]

---

**`_run_git_command()`**

No description available

**Parameters:**
- [param]: [description]

**Returns:**
- [return type]: [description]

---

**`_get_current_branch()`**

No description available

**Parameters:**
- [param]: [description]

**Returns:**
- [return type]: [description]

---

**`_get_current_commit_sha()`**

No description available

**Parameters:**
- [param]: [description]

**Returns:**
- [return type]: [description]

---

**`_has_uncommitted_changes()`**

No description available

**Parameters:**
- [param]: [description]

**Returns:**
- [return type]: [description]

---

**`_load_checkpoints()`**

No description available

**Parameters:**
- [param]: [description]

**Returns:**
- [return type]: [description]

---

**`_save_checkpoints()`**

No description available

**Parameters:**
- [param]: [description]

**Returns:**
- [return type]: [description]

---

**`create_checkpoint()`**

No description available

**Parameters:**
- [param]: [description]

**Returns:**
- [return type]: [description]

---

**`commit_phase_completion()`**

No description available

**Parameters:**
- [param]: [description]

**Returns:**
- [return type]: [description]

---

**`rollback_to_checkpoint()`**

No description available

**Parameters:**
- [param]: [description]

**Returns:**
- [return type]: [description]

---

**`list_checkpoints()`**

No description available

**Parameters:**
- [param]: [description]

**Returns:**
- [return type]: [description]

---

**`validate_skull_rule_8()`**

No description available

**Parameters:**
- [param]: [description]

**Returns:**
- [return type]: [description]

---

## Configuration

**Required:**
- [Configuration item 1]
- [Configuration item 2]

**Optional:**
- [Configuration item 3]

---

## Examples

### Example 1: [Scenario Name]

```python
# [Example code]
```

**Output:**
```
[Expected output]
```

---

## Integration

**Entry Points:**
- [Entry point 1]
- [Entry point 2]

**Dependencies:**
- [Dependency 1]
- [Dependency 2]

**See Also:**
- [Related documentation]

---

## Troubleshooting

**Issue:** [Common problem]  
**Solution:** [How to fix]

**Issue:** [Another problem]  
**Solution:** [How to fix]

---

**Last Updated:** [Date]  
**Version:** 1.0
