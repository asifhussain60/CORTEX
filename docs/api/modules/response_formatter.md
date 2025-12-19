# response_formatter

CORTEX Response Formatter

Automatically formats operation results with appropriate copyright headers
based on execution context. This ensures consistent branding and legal
attribution without requiring user intervention.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [ResponseFormatter](#responseformatter)

### Functions
- [format_for_copilot](#format_for_copilot)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** datetime, pathlib, typing


## Classes

### ResponseFormatter

```python
class ResponseFormatter
```

Intelligent response formatter that adapts headers based on context.

Header Strategy:
- First operation in session: Full header
- Help/documentation: Banner header (ASCII art)
- Regular operations: Minimal footer
- Error situations: No header (focus on problem)


**Methods:**

  #### `format_operation_result`

  *Decorators:* `staticmethod`

  ```python
  format_operation_result(operation_name: str, result: Any, context: Dict[str, Any], is_help: bool) -> str
  ```

  Format operation result with appropriate header.

Args:
    operation_name: Name of the operation (e.g., "Design Sync")
    result: OperationResult object
    context: Execution context
    is_help: Whether this is a help command
    
Returns:
    Formatted markdown string for Copilot Chat display

  **Parameters:**

  - `operation_name` (str): Name of the operation (e.g., "Design Sync")
  - `result` (Any): OperationResult object
  - `context` (Dict[str, Any]): Execution context
  - `is_help` (bool) = `False`: Whether this is a help command


  **Returns:** str
    Formatted markdown string for Copilot Chat display


  #### `reset_session`

  *Decorators:* `staticmethod`

  ```python
  reset_session()
  ```

  Reset session state (for testing or explicit session start).


---

## Functions

### format_for_copilot

```python
format_for_copilot(operation_name: str, result: Any, context: Dict[str, Any]) -> str
```

Convenience function to format operation results for Copilot Chat display.

Args:
    operation_name: Name of the operation
    result: OperationResult object
    context: Optional execution context
    
Returns:
    Formatted markdown string


**Parameters:**

- `operation_name` (str): Name of the operation
- `result` (Any): OperationResult object
- `context` (Dict[str, Any]) = `None`: Optional execution context


**Returns:** str
  Formatted markdown string


---
