# user_cleanup_orchestrator

User Cleanup Orchestrator - Lightweight cleanup for user repositories

This module provides safe, conservative cleanup for user repositories with:
- User-safe scanning (logs, temp, cache only)
- Protected path validation (never touch source/configs)
- Interactive prompts for confirmation
- Lightweight reporting

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Version: 3.0.0


## Table of Contents

### Classes
- [CleanupCategory](#cleanupcategory)
- [UserCleanupReport](#usercleanupreport)
- [UserCleanupOrchestrator](#usercleanuporchestrator)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** collections, dataclasses, datetime, logging, pathlib, shutil, src, typing


## Classes

### CleanupCategory

```python
class CleanupCategory
```

**Decorators:** `dataclass`

Category of files to clean up


**Attributes:**

- `name`: str
- `description`: str
- `patterns`: List[str]
- `safe_to_delete`: bool
- `requires_confirmation`: bool



---

### UserCleanupReport

```python
class UserCleanupReport
```

**Decorators:** `dataclass`

Simple cleanup report for user


**Attributes:**

- `generated_at`: datetime
- `categories_cleaned`: List[str]
- `files_deleted`: int
- `space_freed_mb`: float
- `execution_time`: float
- `errors`: List[str]


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict
  ```

  Convert to dictionary

  **Parameters:**

  - `self`


  **Returns:** Dict



---

### UserCleanupOrchestrator

```python
class UserCleanupOrchestrator(BaseOperationModule)
```

Lightweight cleanup orchestrator for user repositories.

Conservative by design:
- Only cleans safe categories (logs, temp, cache, build artifacts)
- Never touches source code, tests, or configs
- Interactive confirmation for non-obvious deletions
- Clear reporting of what was deleted

User-Safe Categories:
✅ Logs (*.log, logs/)
✅ Temporary files (tmp/, temp/, *.tmp)
✅ Cache directories (cache/, .cache/)
✅ Build artifacts (.next/, dist/, build/ with confirmation)
✅ IDE files (.vscode/, .idea/ if auto-generated)
⚠️ Large files (>10 MB, requires confirmation)

Protected Paths (Never Touch):
❌ Source code (src/, lib/, app/)
❌ Tests (tests/, __tests__/, *.test.*)
❌ Configs (*.config.js, *.json, .env)
❌ Dependencies (node_modules/, venv/)
❌ Version control (.git/)
❌ Documentation (docs/, *.md in root)


**Methods:**

  #### `get_metadata`

  ```python
  get_metadata(self) -> OperationModuleMetadata
  ```

  Module metadata

  **Parameters:**

  - `self`


  **Returns:** OperationModuleMetadata


  #### `execute`

  ```python
  execute(self, context: Dict) -> OperationResult
  ```

  Execute user-safe cleanup.

Args:
    context: Execution context with optional:
        - dry_run (bool): Preview mode (default: True)
        - categories (List[str]): Categories to clean (default: all safe)
        - auto_confirm (bool): Skip confirmations (default: False)

Returns:
    OperationResult with cleanup report

  **Parameters:**

  - `self`
  - `context` (Dict): Execution context with optional:


  **Returns:** OperationResult
    OperationResult with cleanup report



---
