# load_story_template_module

Load Story Template Module - Story Refresh Operation

This module loads the CORTEX story template from prompts/shared/story.md
as the first step in the story refresh operation.

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture)


## Table of Contents

### Classes
- [LoadStoryTemplateModule](#loadstorytemplatemodule)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** logging, pathlib, src, typing


## Classes

### LoadStoryTemplateModule

```python
class LoadStoryTemplateModule(BaseOperationModule)
```

Load the CORTEX story template file.

This module is part of the refresh_cortex_story operation and demonstrates
how the universal operations architecture works for non-setup commands.

What it does:
    1. Validates story file exists at prompts/shared/story.md
    2. Loads story content
    3. Validates basic Markdown structure
    4. Stores story content in context for downstream modules

Example Usage:
    # Via operation
    result = execute_operation("refresh_cortex_story")
    
    # Direct
    module = LoadStoryTemplateModule()
    context = {'project_root': Path('/path/to/cortex')}
    result = module.execute(context)
    story_content = context['story_content']


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

  Validate that story file exists.

Args:
    context: Must contain 'project_root'

Returns:
    (is_valid, issues_list)

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Must contain 'project_root'


  **Returns:** tuple[bool, List[str]]
    (is_valid, issues_list)


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Load story template file.

Args:
    context: Shared context dictionary
        - Input: project_root (Path)
        - Output: story_content (str), story_path (Path), story_line_count (int)

Returns:
    OperationResult with story loading status

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Shared context dictionary


  **Returns:** OperationResult
    OperationResult with story loading status


  #### `rollback`

  ```python
  rollback(self, context: Dict[str, Any]) -> bool
  ```

  Rollback story loading (no-op for read operation).

Args:
    context: Shared context dictionary

Returns:
    True (always succeeds for read-only operations)

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Shared context dictionary


  **Returns:** bool
    True (always succeeds for read-only operations)


  #### `should_run`

  ```python
  should_run(self, context: Dict[str, Any]) -> bool
  ```

  Determine if module should run.

Args:
    context: Shared context dictionary

Returns:
    True (always run for story refresh)

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Shared context dictionary


  **Returns:** bool
    True (always run for story refresh)


  #### `get_progress_message`

  ```python
  get_progress_message(self) -> str
  ```

  Get progress message.

  **Parameters:**

  - `self`


  **Returns:** str



---
