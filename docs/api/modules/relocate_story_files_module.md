# relocate_story_files_module

Relocate Story Files Module - Story Refresh Operation

This module relocates Ancient-Rules.md and CORTEX-FEATURES.md to the story directory
to keep all story-related documentation together.

Author: Asif Hussain
Version: 2.0 (Intelligent file relocation)


## Table of Contents

### Classes
- [RelocateStoryFilesModule](#relocatestoryfilesmodule)

### Functions
- [register](#register)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** datetime, logging, pathlib, shutil, src, typing


## Classes

### RelocateStoryFilesModule

```python
class RelocateStoryFilesModule(BaseOperationModule)
```

Relocate story-related files to docs/story/CORTEX-STORY/.

This module moves:
- Ancient-Rules.md (from cortex-brain/ or docs/)
- CORTEX-FEATURES.md (from cortex-brain/ or docs/)

What it does:
    1. Searches for files in common locations
    2. Creates backups before moving
    3. Relocates files to story directory
    4. Updates any references in other docs (optional)
    5. Verifies successful relocation


**Methods:**

  #### `get_metadata`

  ```python
  get_metadata(self) -> OperationModuleMetadata
  ```

  Get module metadata.

  **Parameters:**

  - `self`


  **Returns:** OperationModuleMetadata


  #### `validate`

  ```python
  validate(self, context: Dict[str, Any]) -> OperationResult
  ```

  Validate prerequisites.

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** OperationResult


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Relocate story files.

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** OperationResult


  #### `rollback`

  ```python
  rollback(self, context: Dict[str, Any]) -> bool
  ```

  Rollback by moving files back to original locations.

Args:
    context: Shared context dictionary

Returns:
    True if rollback succeeded

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Shared context dictionary


  **Returns:** bool
    True if rollback succeeded


  #### `should_run`

  ```python
  should_run(self, context: Dict[str, Any]) -> bool
  ```

  Determine if module should run.

Args:
    context: Shared context dictionary

Returns:
    True if files need relocation

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Shared context dictionary


  **Returns:** bool
    True if files need relocation


  #### `get_progress_message`

  ```python
  get_progress_message(self) -> str
  ```

  Get progress message.

  **Parameters:**

  - `self`


  **Returns:** str



---

## Functions

### register

```python
register() -> BaseOperationModule
```

Register this module.


**Returns:** BaseOperationModule


---
