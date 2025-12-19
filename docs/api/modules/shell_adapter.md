# shell_adapter

Shell syntax adapters for cross-platform command generation.

Provides syntax adaptation for PowerShell, bash, zsh, and cmd.


## Table of Contents

### Classes
- [ShellAdapter](#shelladapter)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** typing


## Classes

### ShellAdapter

```python
class ShellAdapter
```

Utility for adapting command syntax across shells.


**Methods:**

  #### `adapt_command`

  *Decorators:* `staticmethod`

  ```python
  adapt_command(command: str, target_shell: str) -> str
  ```

  Adapt command syntax for target shell.

Args:
    command: Original command
    target_shell: Target shell type
    
Returns:
    Adapted command

  **Parameters:**

  - `command` (str): Original command
  - `target_shell` (str): Target shell type


  **Returns:** str
    Adapted command


  #### `format_env_var`

  *Decorators:* `staticmethod`

  ```python
  format_env_var(var_name: str, shell: str) -> str
  ```

  Format environment variable reference for shell.

Args:
    var_name: Variable name
    shell: Shell type
    
Returns:
    Formatted variable reference

  **Parameters:**

  - `var_name` (str): Variable name
  - `shell` (str): Shell type


  **Returns:** str
    Formatted variable reference


  #### `get_line_continuation`

  *Decorators:* `staticmethod`

  ```python
  get_line_continuation(shell: str) -> str
  ```

  Get line continuation character for shell.

Args:
    shell: Shell type
    
Returns:
    Line continuation character

  **Parameters:**

  - `shell` (str): Shell type


  **Returns:** str
    Line continuation character


  #### `get_path_separator`

  *Decorators:* `staticmethod`

  ```python
  get_path_separator(shell: str) -> str
  ```

  Get path separator for shell.

  **Parameters:**

  - `shell` (str)


  **Returns:** str



---
