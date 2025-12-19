# help_command

CORTEX Help Command - Display Available Operations

Provides concise, user-friendly display of all CORTEX operations with:
    - Quick command reference
    - Natural language examples
    - Implementation status
    - Underlying orchestration modules

Author: Asif Hussain
Version: 1.0


## Table of Contents

### Classes
- [HelpCommand](#helpcommand)

### Functions
- [show_help](#show_help)
- [find_command](#find_command)


## Overview

- **Classes:** 1
- **Functions:** 2
- **Dependencies:** logging, pathlib, src, typing


## Classes

### HelpCommand

```python
class HelpCommand
```

Generate help text for CORTEX operations.

Displays:
    - Quick commands (shortest natural language phrase)
    - Natural language example (most common usage)
    - Orchestration module (operation_id)
    - Status (✅ ready, ⏸️ pending, 🎯 planned)


**Methods:**

  #### `generate_help`

  ```python
  generate_help(self, format: str) -> str
  ```

  Generate help text for all CORTEX operations.

Args:
    format: Output format ('table', 'list', 'detailed')

Returns:
    Formatted help text

  **Parameters:**

  - `self`
  - `format` (str) = `'table'`: Output format ('table', 'list', 'detailed')


  **Returns:** str
    Formatted help text


  #### `get_operation_by_command`

  ```python
  get_operation_by_command(self, command: str) -> Dict[str, Any]
  ```

  Find operation by quick command.

Args:
    command: Quick command string

Returns:
    Operation data dictionary

  **Parameters:**

  - `self`
  - `command` (str): Quick command string


  **Returns:** Dict[str, Any]
    Operation data dictionary



---

## Functions

### show_help

```python
show_help(format: str) -> str
```

Convenience function to display CORTEX help.

Args:
    format: Output format ('table', 'list', 'detailed')

Returns:
    Formatted help text

Example:
    print(show_help())
    print(show_help('detailed'))


**Parameters:**

- `format` (str) = `'table'`: Output format ('table', 'list', 'detailed')


**Returns:** str
  Formatted help text


---

### find_command

```python
find_command(command: str) -> Dict[str, Any]
```

Find operation by command.

Args:
    command: Command string to search for

Returns:
    Operation data dictionary

Example:
    op = find_command('setup')
    print(f"Operation: {op['operation_id']}")


**Parameters:**

- `command` (str): Command string to search for


**Returns:** Dict[str, Any]
  Operation data dictionary


---
