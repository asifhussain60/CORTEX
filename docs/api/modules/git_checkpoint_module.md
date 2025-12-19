# git_checkpoint_module

Git Checkpoint Module

Creates and validates git checkpoints before development work.
Implements GIT_CHECKPOINT_ENFORCEMENT Tier 0 instinct.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file

This module:
1. Creates git checkpoints (commits or tags) before development
2. Validates checkpoint existence and quality
3. Provides rollback capability
4. Enforces Tier 0 checkpoint governance rule


## Table of Contents

### Classes
- [CheckpointType](#checkpointtype)
- [CheckpointViolation](#checkpointviolation)
- [GitCheckpointModule](#gitcheckpointmodule)

### Functions
- [get_module](#get_module)


## Overview

- **Classes:** 3
- **Functions:** 1
- **Dependencies:** datetime, logging, pathlib, src, subprocess, typing


## Classes

### CheckpointType

```python
class CheckpointType
```

Supported checkpoint types.



---

### CheckpointViolation

```python
class CheckpointViolation(Exception)
```

Raised when checkpoint enforcement is violated.



---

### GitCheckpointModule

```python
class GitCheckpointModule(BaseOperationModule)
```

Creates and validates git checkpoints for development safety.

Features:
- Create commit checkpoints with standardized messages
- Create tag checkpoints with timestamps
- Create stash checkpoints for temporary saves
- Validate checkpoint existence before development
- Check for uncommitted changes
- Provide checkpoint history and rollback info

Example:
    module = GitCheckpointModule()
    
    result = module.execute({
        'operation': 'create',
        'message': 'before authentication implementation',
        'checkpoint_type': 'commit'
    })
    
    result = module.execute({
        'operation': 'validate',
        'required_for': 'authentication feature'
    })
    
    # List recent checkpoints
    result = module.execute({
        'operation': 'list',
        'limit': 10
    })


**Methods:**

  #### `get_metadata`

  ```python
  get_metadata(self) -> OperationModuleMetadata
  ```

  Return metadata describing this module.

Returns:
    OperationModuleMetadata with module information

  **Parameters:**

  - `self`


  **Returns:** OperationModuleMetadata
    OperationModuleMetadata with module information


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Execute git checkpoint operation.

Args:
    context: Operation context with:
        - operation: 'create', 'validate', 'list', or 'rollback'
        - message: Checkpoint message (for create)
        - checkpoint_type: 'commit', 'tag', or 'stash' (for create)
        - required_for: Feature name (for validate)
        - checkpoint_id: Checkpoint to rollback to (for rollback)
        - limit: Number of checkpoints to list (for list)

Returns:
    OperationResult with checkpoint information

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Operation context with:


  **Returns:** OperationResult
    OperationResult with checkpoint information



---

## Functions

### get_module

```python
get_module()
```

Factory function for module registration.


---
