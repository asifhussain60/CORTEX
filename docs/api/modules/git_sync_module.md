# git_sync_module

Git Synchronization Setup Module

Synchronizes CORTEX project with remote repository.

SOLID Principles:
- Single Responsibility: Only handles git synchronization
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [GitSyncModule](#gitsyncmodule)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, os, pathlib, src, subprocess, typing


## Classes

### GitSyncModule

```python
class GitSyncModule(BaseOperationModule)
```

Setup module for git repository synchronization.

Responsibilities:
1. Verify git is installed and available
2. Check if project is a git repository
3. Fetch latest changes from remote
4. Pull changes if safe to do so
5. Report sync status


**Methods:**

  #### `get_metadata`

  ```python
  get_metadata(self) -> OperationModuleMetadata
  ```

  Return module metadata.

  **Parameters:**

  - `self`


  **Returns:** OperationModuleMetadata


  #### `validate_prerequisites`

  ```python
  validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]
  ```

  Validate prerequisites for git sync.

Checks:
1. Project root exists
2. Git command available (not blocking)

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** Tuple[bool, List[str]]


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Execute git synchronization.

Steps:
1. Check if git is installed
2. Verify project is a git repository
3. Check for uncommitted changes
4. Fetch remote changes
5. Pull if safe (no conflicts)

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** OperationResult



---
