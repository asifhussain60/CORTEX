# context_control_module

Context Control Module - User commands to manage Tier 1 memory

This module provides user control over CORTEX's memory with commands like
forget [topic], clear context, and show context.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [ContextControlModule](#contextcontrolmodule)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** src, typing


## Classes

### ContextControlModule

```python
class ContextControlModule(BaseOperationModule)
```

Provides user control commands for Tier 1 context management.

Commands:
- show context: Display loaded conversations
- forget [topic]: Remove conversations about specific topic
- clear context: Clear all Tier 1 memory (requires confirmation)


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

  Execute context control command.

Args:
    operation_data: Contains:
        - command: show | forget | clear
        - topic: For forget command
        - confirmed: For destructive operations
        - user_request: Original request

Returns:
    OperationResult with command execution result

  **Parameters:**

  - `self`
  - `operation_data` (Dict[str, Any]): Contains:


  **Returns:** OperationResult
    OperationResult with command execution result


  #### `can_handle`

  ```python
  can_handle(self, operation_type: str) -> bool
  ```

  Check if this module can handle the operation.

  **Parameters:**

  - `self`
  - `operation_type` (str)


  **Returns:** bool


  #### `detect_trigger`

  ```python
  detect_trigger(self, user_request: str) -> bool
  ```

  Detect if user request matches any context control triggers.

Args:
    user_request: User's natural language request

Returns:
    True if matches control command trigger

  **Parameters:**

  - `self`
  - `user_request` (str): User's natural language request


  **Returns:** bool
    True if matches control command trigger



---
