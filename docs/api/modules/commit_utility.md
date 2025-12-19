# commit_utility

CommitUtility - Fast commit utility.

Lightweight replacement for CommitOrchestrator.
Design Goals:
- Fast: <3 seconds execution
- Simple: Clear pass/fail
- Safe: Pre-flight checks + checkpoints
- Direct: Minimal dependencies

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary


## Table of Contents

### Classes
- [CommitResult](#commitresult)

### Functions
- [run_commit_utility](#run_commit_utility)


## Overview

- **Classes:** 1
- **Functions:** 6
- **Dependencies:** dataclasses, logging, pathlib, src, subprocess, typing


## Classes

### CommitResult

```python
class CommitResult
```

**Decorators:** `dataclass`

Result from commit utility.


**Attributes:**

- `success`: bool
- `message`: str
- `commit_hash`: Optional[str]
- `checkpoint_created`: bool
- `files_committed`: int
- `details`: Optional[Dict[str, Any]]



---

## Functions

### run_commit_utility

```python
run_commit_utility(auto_add: bool, create_checkpoint: bool) -> Dict[str, Any]
```

Run commit utility.

Args:
    auto_add: Auto-stage all changes
    create_checkpoint: Create safety checkpoint

Returns:
    Dict with success, message, and commit data


**Parameters:**

- `auto_add` (bool) = `True`: Auto-stage all changes
- `create_checkpoint` (bool) = `False`: Create safety checkpoint


**Returns:** Dict[str, Any]
  Dict with success, message, and commit data


---
