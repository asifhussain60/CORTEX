# Help Command Operation

**Auto-generated:** 2025-11-15 10:21:10

---

## Overview

CORTEX Help Command - Display Available Operations

Provides concise, user-friendly display of all CORTEX operations with:
    - Quick command reference
    - Natural language examples
    - Implementation status
    - Underlying orchestration modules

Author: Asif Hussain
Version: 1.0

## Usage

```python
from src.operations.help_command import HelpCommand

operation = HelpCommand()
result = operation.execute()
```

## Methods

### `generate_help(self, format)`

Generate help text for all CORTEX operations.

Args:
    format: Output format ('table', 'list', 'detailed')

Returns:
    Formatted help text

### `get_operation_by_command(self, command)`

Find operation by quick command.

Args:
    command: Quick command string

Returns:
    Operation data dictionary
