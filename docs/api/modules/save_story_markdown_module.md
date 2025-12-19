# save_story_markdown_module

Save Story Markdown Module - Story Refresh Operation

This module saves the transformed CORTEX story to the documentation directory.

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture)


## Table of Contents

### Classes
- [SaveStoryMarkdownModule](#savestorymarkdownmodule)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, logging, pathlib, shutil, src, typing


## Classes

### SaveStoryMarkdownModule

```python
class SaveStoryMarkdownModule(BaseOperationModule)
```

Save transformed story to file.

This module writes the transformed CORTEX story to docs/awakening-of-cortex.md
with backup of existing file.

What it does:
    1. Backs up existing story file (if it exists)
    2. Writes transformed story to docs/awakening-of-cortex.md
    3. Verifies file was written correctly
    4. Stores backup path in context for rollback


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

  Validate that transformed story and project root are available.

Args:
    context: Must contain 'transformed_story' and 'project_root'

Returns:
    (is_valid, issues_list)

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Must contain 'transformed_story' and 'project_root'


  **Returns:** tuple[bool, List[str]]
    (is_valid, issues_list)


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Save story to file.

Args:
    context: Shared context dictionary
        - Input: transformed_story (str), project_root (Path)
        - Output: story_file_path (Path), backup_path (Path or None)

Returns:
    OperationResult with save status

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Shared context dictionary


  **Returns:** OperationResult
    OperationResult with save status


  #### `rollback`

  ```python
  rollback(self, context: Dict[str, Any]) -> bool
  ```

  Rollback story save by restoring backup.

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
    False if dry_run is True

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Shared context dictionary


  **Returns:** bool
    False if dry_run is True


  #### `get_progress_message`

  ```python
  get_progress_message(self) -> str
  ```

  Get progress message.

  **Parameters:**

  - `self`


  **Returns:** str



---
