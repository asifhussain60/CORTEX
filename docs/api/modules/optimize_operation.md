# optimize_operation

CORTEX Optimize Operation Module

Provides comprehensive CORTEX system optimization capabilities.
Implements all optimizations from CORTEX-OPTIMIZATION-PLAN-2025-12-01.md

Features:
- File organization (move scattered tests/scripts to proper directories)
- Build artifact cleanup (dist/, publish/, *.db files)
- Archive consolidation (old backups, temporary files)
- Duplicate file removal (templates, logos)
- Database optimization (vacuum, cleanup)
- Cache optimization (YAML cache, temporary files)
- Automated maintenance tasks

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary


## Table of Contents

### Classes
- [OptimizeOperation](#optimizeoperation)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** base_operation_module, datetime, hashlib, json, logging, pathlib, re, shutil, sqlite3, src, typing


## Classes

### OptimizeOperation

```python
class OptimizeOperation(BaseOperationModule)
```

Optimization operation for CORTEX and user code.

Features:
- Code optimization suggestions
- CORTEX brain cleanup
- Cache optimization
- Database vacuum
- Token usage optimization

Usage:
    User says: "optimize" or "optimize code" or "optimize cortex"
    CORTEX routes to this module


**Methods:**

  #### `get_metadata`

  ```python
  get_metadata(self) -> OperationModuleMetadata
  ```

  Return operation metadata.

  **Parameters:**

  - `self`


  **Returns:** OperationModuleMetadata


  #### `validate`

  ```python
  validate(self) -> OperationResult
  ```

  Validate optimization operation can run.

Returns:
    OperationResult with validation status

  **Parameters:**

  - `self`


  **Returns:** OperationResult
    OperationResult with validation status


  #### `execute`

  *Decorators:* `with_progress`

  ```python
  execute(self, **kwargs) -> OperationResult
  ```

  Execute comprehensive optimization operations with progress monitoring.

Implements all fixes from CORTEX-OPTIMIZATION-PLAN-2025-12-01.md:
- Phase 1: File organization and cleanup (root files → proper directories)
- Phase 2: Archive consolidation and duplicate removal
- Database optimization (vacuum, cleanup)
- Cache optimization

Args:
    target: What to optimize (organization/archives/cortex/cache/all)
    aggressive: Use aggressive optimization
    dry_run: Preview changes without executing (default: False)
    skip_skull_tests: Skip SKULL test validation for fast user operations (default: False)

Returns:
    OperationResult with optimization summary

  **Parameters:**

  - `self`
  - `**kwargs`


  **Returns:** OperationResult
    OperationResult with optimization summary


  #### `rollback`

  ```python
  rollback(self) -> OperationResult
  ```

  Rollback optimization (not applicable).

Returns:
    OperationResult indicating rollback not supported

  **Parameters:**

  - `self`


  **Returns:** OperationResult
    OperationResult indicating rollback not supported



---
