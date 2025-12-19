# rollback_utility

Rollback Utility

Fast, lightweight rollback management for TDD workflows.
Replaces heavy orchestrator with focused, <3s execution utility.

Features:
- Checkpoint validation before rollback
- Git reset to checkpoint with safety checks
- Uncommitted changes detection
- Dry-run mode for preview
- User confirmation prompts

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [RollbackResult](#rollbackresult)

### Functions
- [run_rollback_utility](#run_rollback_utility)


## Overview

- **Classes:** 1
- **Functions:** 7
- **Dependencies:** dataclasses, datetime, json, logging, pathlib, src, subprocess, typing


## Classes

### RollbackResult

```python
class RollbackResult
```

**Decorators:** `dataclass`

Result of rollback operation.


**Attributes:**

- `success`: bool
- `message`: str
- `checkpoint_id`: Optional[str]
- `executed`: bool
- `safe`: bool
- `warning`: Optional[str]
- `details`: Optional[str]



---

## Functions

### run_rollback_utility

```python
run_rollback_utility(checkpoint_id: str, dry_run: bool, force: bool, skip_confirmation: bool) -> RollbackResult
```

Main entry point for rollback utility.

Args:
    checkpoint_id: Checkpoint SHA to rollback to
    dry_run: If True, preview changes without executing
    force: If True, bypass safety checks (dangerous!)
    skip_confirmation: If True, skip user confirmation prompt
    
Returns:
    RollbackResult with operation outcome


**Parameters:**

- `checkpoint_id` (str): Checkpoint SHA to rollback to
- `dry_run` (bool) = `False`: If True, preview changes without executing
- `force` (bool) = `False`: If True, bypass safety checks (dangerous!)
- `skip_confirmation` (bool) = `False`: If True, skip user confirmation prompt


**Returns:** RollbackResult
  RollbackResult with operation outcome


---
