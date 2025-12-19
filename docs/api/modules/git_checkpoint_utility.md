# git_checkpoint_utility

Git Checkpoint Utility

Fast, lightweight checkpoint management for TDD workflows.
Replaces heavy orchestrator with focused, <2s execution utility.

Features:
- Checkpoint creation with metadata
- List checkpoints with timestamps
- 30-day retention enforcement
- HEAD hash capture for safety

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [CheckpointResult](#checkpointresult)

### Functions
- [run_checkpoint_utility](#run_checkpoint_utility)


## Overview

- **Classes:** 1
- **Functions:** 5
- **Dependencies:** dataclasses, datetime, json, logging, pathlib, src, subprocess, typing


## Classes

### CheckpointResult

```python
class CheckpointResult
```

**Decorators:** `dataclass`

Result of checkpoint operation.


**Attributes:**

- `success`: bool
- `message`: str
- `checkpoint_id`: Optional[str]
- `checkpoint_count`: int
- `checkpoints`: Optional[List[Dict]]
- `details`: Optional[str]



---

## Functions

### run_checkpoint_utility

```python
run_checkpoint_utility(action: str, session_id: Optional[str], phase: Optional[str], message: Optional[str], list_all: bool) -> CheckpointResult
```

Main entry point for git checkpoint utility.

Args:
    action: Operation to perform ("create" or "list")
    session_id: TDD session identifier (for create)
    phase: Current phase (RED, GREEN, REFACTOR)
    message: Optional custom checkpoint message
    list_all: Show all checkpoints including expired
    
Returns:
    CheckpointResult with operation outcome


**Parameters:**

- `action` (str) = `'create'`: Operation to perform ("create" or "list")
- `session_id` (Optional[str]) = `None`: TDD session identifier (for create)
- `phase` (Optional[str]) = `None`: Current phase (RED, GREEN, REFACTOR)
- `message` (Optional[str]) = `None`: Optional custom checkpoint message
- `list_all` (bool) = `False`: Show all checkpoints including expired


**Returns:** CheckpointResult
  CheckpointResult with operation outcome


---
