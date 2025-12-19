# validate_story_structure_module

Validate Story Structure Module - Story Refresh Operation

This module validates the CORTEX story Markdown structure to ensure
it meets documentation standards.

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture)


## Table of Contents

### Classes
- [ValidateStoryStructureModule](#validatestorystructuremodule)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** logging, pathlib, re, src, typing


## Classes

### ValidateStoryStructureModule

```python
class ValidateStoryStructureModule(BaseOperationModule)
```

Validate story Markdown structure.

This module ensures the CORTEX story has proper Markdown formatting
and meets documentation standards.

What it does:
    1. Validates Markdown syntax
    2. Checks for required sections
    3. Verifies heading hierarchy
    4. Checks for common issues


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
  validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]
  ```

  Validate that transformed story is available.

Args:
    context: Must contain 'transformed_story'

Returns:
    (is_valid, issues_list)

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Must contain 'transformed_story'


  **Returns:** tuple[bool, List[str]]
    (is_valid, issues_list)


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Validate story structure.

Args:
    context: Shared context dictionary
        - Input: transformed_story (str)
        - Output: validation_results (dict), is_valid (bool)

Returns:
    OperationResult with validation status

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Shared context dictionary


  **Returns:** OperationResult
    OperationResult with validation status


  #### `rollback`

  ```python
  rollback(self, context: Dict[str, Any]) -> bool
  ```

  Rollback validation (no-op).

Args:
    context: Shared context dictionary

Returns:
    True (always succeeds)

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Shared context dictionary


  **Returns:** bool
    True (always succeeds)


  #### `should_run`

  ```python
  should_run(self, context: Dict[str, Any]) -> bool
  ```

  Determine if module should run.

Args:
    context: Shared context dictionary

Returns:
    True if not in quick profile

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Shared context dictionary


  **Returns:** bool
    True if not in quick profile


  #### `get_progress_message`

  ```python
  get_progress_message(self) -> str
  ```

  Get progress message.

  **Parameters:**

  - `self`


  **Returns:** str



---
