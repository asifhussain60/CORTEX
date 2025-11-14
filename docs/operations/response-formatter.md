# Response Formatter Operation

**Auto-generated:** 2025-11-14 10:58:51

---

## Overview

CORTEX Response Formatter

Automatically formats operation results with appropriate copyright headers
based on execution context. This ensures consistent branding and legal
attribution without requiring user intervention.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

## Usage

```python
from src.operations.response_formatter import ResponseFormatter

operation = ResponseFormatter()
result = operation.execute()
```

## Methods

### `format_operation_result(operation_name, result, context, is_help)`

Format operation result with appropriate header.

Args:
    operation_name: Name of the operation (e.g., "Design Sync")
    result: OperationResult object
    context: Execution context
    is_help: Whether this is a help command
    
Returns:
    Formatted markdown string for Copilot Chat display

### `reset_session()`

Reset session state (for testing or explicit session start).
