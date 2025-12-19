# apply_narrator_voice_module

Apply Narrator Voice Module - Story Refresh Operation

This module transforms the CORTEX story by rebuilding it with current
architecture state, implementation metrics, and feature availability.

Author: Asif Hussain
Version: 2.0 (Universal Operations Architecture - Live Transformation)


## Table of Contents

### Classes
- [ApplyNarratorVoiceModule](#applynarratorvoicemodule)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, logging, pathlib, re, src, typing, yaml


## Classes

### ApplyNarratorVoiceModule

```python
class ApplyNarratorVoiceModule(BaseOperationModule)
```

Transform story with current CORTEX architecture state.

This module rebuilds the CORTEX story from scratch using current implementation data:
- Module counts and completion percentages
- Response template statistics
- Natural language interface capabilities
- Test coverage and implementation status
- Feature availability and roadmap

What it does:
    1. Gathers current architecture state from multiple sources
    2. Rebuilds story sections with actual metrics
    3. Preserves narrative voice and engaging style
    4. Optimizes for 25-30 minute read time target
    5. Validates structure and content quality

Data Sources:
- cortex-operations.yaml - Module definitions and operations
- response-templates.yaml - Template count and coverage
- knowledge-graph.yaml - Learned patterns
- implementation status files - Actual progress metrics


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

  Validate that story content is available.

Args:
    context: Must contain 'story_content'

Returns:
    (is_valid, issues_list)

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Must contain 'story_content'


  **Returns:** tuple[bool, List[str]]
    (is_valid, issues_list)


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Transform story with current CORTEX architecture state.

This is a LIVE transformation operation that rebuilds the story from scratch.

Steps:
1. Load current architecture state (modules, templates, features)
2. Extract key metrics and implementation status
3. Rebuild story sections with actual data
4. Preserve narrative voice and engaging style
5. Validate read time (25-30 minutes target)
6. Return transformed content

Args:
    context: Shared context dictionary
        - Input: story_content (str) - Original story template
        - Output: transformed_story (str) - Rebuilt story with current data

Returns:
    OperationResult with transformation status and metrics

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Shared context dictionary


  **Returns:** OperationResult
    OperationResult with transformation status and metrics


  #### `rollback`

  ```python
  rollback(self, context: Dict[str, Any]) -> bool
  ```

  Rollback narrator voice transformation.

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
