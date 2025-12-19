# context_display_module

Context Display Module - Makes Tier 1 context visible to users

This module provides visibility into what CORTEX remembers from past conversations,
showing relevance scores, entity overlap, and memory health indicators.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [ContextDisplayModule](#contextdisplaymodule)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, src, typing


## Classes

### ContextDisplayModule

```python
class ContextDisplayModule(BaseOperationModule)
```

Displays loaded Tier 1 context with transparency and control.

Features:
- Show loaded conversations with relevance scores
- Display entity overlap breakdown
- Context quality indicators
- Memory health status


**Methods:**

  #### `get_metadata`

  ```python
  get_metadata(self) -> OperationModuleMetadata
  ```

  Return module metadata.

  **Parameters:**

  - `self`


  **Returns:** OperationModuleMetadata


  #### `execute`

  ```python
  execute(self, operation_data: Dict[str, Any]) -> OperationResult
  ```

  Display loaded Tier 1 context with formatted output.

Args:
    operation_data: Contains:
        - command: "show context" | "context status" | "memory health"
        - context_data: Dict with loaded conversations and scores
        - user_request: Optional - current request for relevance

Returns:
    OperationResult with formatted context display

  **Parameters:**

  - `self`
  - `operation_data` (Dict[str, Any]): Contains:


  **Returns:** OperationResult
    OperationResult with formatted context display


  #### `can_handle`

  ```python
  can_handle(self, operation_type: str) -> bool
  ```

  Check if this module can handle the operation.

  **Parameters:**

  - `self`
  - `operation_type` (str)


  **Returns:** bool



---
