# operation_header_formatter

CORTEX Operation Header Formatter

Provides standardized headers and footers for all CORTEX operation orchestrators.
Ensures consistent branding, copyright attribution, and execution context display.

Consolidates functionality from header_formatter.py and header_utils.py

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [OperationHeaderFormatter](#operationheaderformatter)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, typing


## Classes

### OperationHeaderFormatter

```python
class OperationHeaderFormatter
```

Format headers and footers for CORTEX operation orchestrators.


**Methods:**

  #### `format_minimalist`

  *Decorators:* `staticmethod`

  ```python
  format_minimalist(operation_name: str, version: str, profile: str, mode: Literal['LIVE', 'DRY RUN'], timestamp: Optional[datetime], purpose: Optional[str]) -> str
  ```

  Format minimalist header for operations.

Used for: cleanup, optimization, design sync, story refresh, etc.

Args:
    operation_name: Name of the operation (e.g., "Design Sync")
    version: Version string (e.g., "1.0.0")
    profile: Execution profile (e.g., "comprehensive")
    mode: Execution mode ("LIVE" or "DRY RUN")
    timestamp: Execution start time (defaults to now)
    purpose: Optional 1-2 line description of operation purpose

Returns:
    Formatted header string

  **Parameters:**

  - `operation_name` (str): Name of the operation (e.g., "Design Sync")
  - `version` (str): Version string (e.g., "1.0.0")
  - `profile` (str): Execution profile (e.g., "comprehensive")
  - `mode` (Literal['LIVE', 'DRY RUN']) = `'LIVE'`: Execution mode ("LIVE" or "DRY RUN")
  - `timestamp` (Optional[datetime]) = `None`: Execution start time (defaults to now)
  - `purpose` (Optional[str]) = `None`: Optional 1-2 line description of operation purpose


  **Returns:** str
    Formatted header string


  #### `format_banner`

  *Decorators:* `staticmethod`

  ```python
  format_banner(operation_name: str, version: str, profile: str, mode: Literal['LIVE', 'DRY RUN'], timestamp: Optional[datetime]) -> str
  ```

  Format banner-style header with ASCII art logo.

Used for: help module and other high-visibility entry points.

Args:
    operation_name: Name of the operation (e.g., "Help System")
    version: Version string (e.g., "1.0.0")
    profile: Execution profile (e.g., "standard")
    mode: Execution mode ("LIVE" or "DRY RUN")
    timestamp: Execution start time (defaults to now)

Returns:
    Formatted banner header string

  **Parameters:**

  - `operation_name` (str): Name of the operation (e.g., "Help System")
  - `version` (str): Version string (e.g., "1.0.0")
  - `profile` (str): Execution profile (e.g., "standard")
  - `mode` (Literal['LIVE', 'DRY RUN']) = `'LIVE'`: Execution mode ("LIVE" or "DRY RUN")
  - `timestamp` (Optional[datetime]) = `None`: Execution start time (defaults to now)


  **Returns:** str
    Formatted banner header string


  #### `format_completion`

  *Decorators:* `staticmethod`

  ```python
  format_completion(operation_name: str, success: bool, duration_seconds: float, summary: Optional[str], accomplishments: Optional[List[str]]) -> str
  ```

  Format completion footer.

Args:
    operation_name: Name of the operation
    success: Whether operation succeeded
    duration_seconds: Total execution time in seconds
    summary: Optional single-line summary message
    accomplishments: Optional list of bullet points showing what was done

Returns:
    Formatted completion footer

  **Parameters:**

  - `operation_name` (str): Name of the operation
  - `success` (bool): Whether operation succeeded
  - `duration_seconds` (float): Total execution time in seconds
  - `summary` (Optional[str]) = `None`: Optional single-line summary message
  - `accomplishments` (Optional[List[str]]) = `None`: Optional list of bullet points showing what was done


  **Returns:** str
    Formatted completion footer


  #### `print_minimalist`

  *Decorators:* `staticmethod`

  ```python
  print_minimalist(operation_name: str, version: str, profile: str, mode: Literal['LIVE', 'DRY RUN'], timestamp: Optional[datetime], purpose: Optional[str]) -> None
  ```

  Print minimalist header directly to console.

  **Parameters:**

  - `operation_name` (str)
  - `version` (str)
  - `profile` (str)
  - `mode` (Literal['LIVE', 'DRY RUN']) = `'LIVE'`
  - `timestamp` (Optional[datetime]) = `None`
  - `purpose` (Optional[str]) = `None`


  **Returns:** None


  #### `print_banner`

  *Decorators:* `staticmethod`

  ```python
  print_banner(operation_name: str, version: str, profile: str, mode: Literal['LIVE', 'DRY RUN'], timestamp: Optional[datetime]) -> None
  ```

  Print banner header directly to console.

  **Parameters:**

  - `operation_name` (str)
  - `version` (str)
  - `profile` (str)
  - `mode` (Literal['LIVE', 'DRY RUN']) = `'LIVE'`
  - `timestamp` (Optional[datetime]) = `None`


  **Returns:** None


  #### `print_completion`

  *Decorators:* `staticmethod`

  ```python
  print_completion(operation_name: str, success: bool, duration_seconds: float, summary: Optional[str], accomplishments: Optional[List[str]]) -> None
  ```

  Print completion footer directly to console.

  **Parameters:**

  - `operation_name` (str)
  - `success` (bool)
  - `duration_seconds` (float)
  - `summary` (Optional[str]) = `None`
  - `accomplishments` (Optional[List[str]]) = `None`


  **Returns:** None



---
