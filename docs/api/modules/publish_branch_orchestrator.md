# publish_branch_orchestrator

Publish Branch Orchestrator Module

Orchestrates CORTEX deployment to remote main branch.
Builds production-ready package in publish/ folder and pushes directly to origin/main.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [PublishBranchOrchestrator](#publishbranchorchestrator)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, logging, pathlib, src, subprocess, sys, typing


## Classes

### PublishBranchOrchestrator

```python
class PublishBranchOrchestrator(BaseOperationModule)
```

Orchestrates CORTEX deployment to remote main branch.

This module builds the CORTEX package in publish/ folder and commits/pushes
directly to origin/main for user distribution.

Features:
    - Builds production package in publish/ folder (excludes tests, dev tools, docs)
    - Commits publish/ folder to main branch
    - Pushes directly to origin/main remote
    - Preserves user's working branch (returns to original after publish)
    - Dry-run mode for preview
    - Fault-tolerant with checkpoints

Branch Preservation:
    CORTEX SHOULD BEGIN AND END ON THE BRANCH IT IS ON.
    - Saves current branch before publish
    - Switches to main only to commit/push
    - Returns to original branch after completion

Usage:
    # Natural language
    "publish cortex"
    "deploy to main"
    
    # Preview mode
    "publish cortex dry run"


**Methods:**

  #### `get_metadata`

  ```python
  get_metadata(self) -> OperationModuleMetadata
  ```

  Get module metadata.

  **Parameters:**

  - `self`


  **Returns:** OperationModuleMetadata


  #### `validate_context`

  ```python
  validate_context(self, context: Dict[str, Any]) -> tuple[bool, str]
  ```

  Validate execution context.

Checks:
    - Project root exists
    - publish_to_branch.py script exists
    - Git repository is clean (if not dry run)

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** tuple[bool, str]


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Execute publish operation to remote main branch.

Process:
1. Run publish_to_branch.py to build package in publish/ folder
2. Save current branch
3. Switch to main branch
4. Commit publish/ folder changes
5. Push to origin/main
6. Return to original branch

IMPORTANT: CORTEX SHOULD BEGIN AND END ON THE BRANCH IT IS ON.
- Saves current branch before publishing
- Switches to main to commit/push publish package
- Switches back to original branch after completion

Args:
    context: Execution context with:
        - project_root: Path to CORTEX repository
        - dry_run: Preview mode (default: False)
        - branch: Target branch name (default: main)
        - resume: Resume from checkpoint (default: False)

Returns:
    OperationResult with publish status

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Execution context with:


  **Returns:** OperationResult
    OperationResult with publish status


  #### `cleanup`

  ```python
  cleanup(self, context: Dict[str, Any]) -> None
  ```

  Cleanup after execution.

Nothing to clean up - publish script handles its own cleanup.

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** None



---
