# build_story_preview_module

Build Story Preview Module - Story Refresh Operation

This module builds an HTML preview of the refreshed CORTEX story using MkDocs.

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture)


## Table of Contents

### Classes
- [BuildStoryPreviewModule](#buildstorypreviewmodule)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** logging, pathlib, src, subprocess, typing


## Classes

### BuildStoryPreviewModule

```python
class BuildStoryPreviewModule(BaseOperationModule)
```

Build HTML preview of story.

This module uses MkDocs to generate an HTML preview of the CORTEX story
for immediate viewing.

What it does:
    1. Runs `mkdocs build` to generate HTML
    2. Verifies site/ directory was created
    3. Checks for story HTML file
    4. Provides preview URL


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

  Validate that story was saved and project root is available.

Args:
    context: Must contain 'story_file_path' and 'project_root'

Returns:
    (is_valid, issues_list)

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Must contain 'story_file_path' and 'project_root'


  **Returns:** tuple[bool, List[str]]
    (is_valid, issues_list)


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Build story preview.

Args:
    context: Shared context dictionary
        - Input: story_file_path (Path), project_root (Path)
        - Output: preview_path (Path), preview_url (str)

Returns:
    OperationResult with build status

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Shared context dictionary


  **Returns:** OperationResult
    OperationResult with build status


  #### `rollback`

  ```python
  rollback(self, context: Dict[str, Any]) -> bool
  ```

  Rollback preview build (no-op - site/ can be rebuilt anytime).

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
    True only for 'full' profile

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Shared context dictionary


  **Returns:** bool
    True only for 'full' profile


  #### `get_progress_message`

  ```python
  get_progress_message(self) -> str
  ```

  Get progress message.

  **Parameters:**

  - `self`


  **Returns:** str



---
