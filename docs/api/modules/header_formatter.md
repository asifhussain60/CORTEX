# header_formatter

CORTEX Orchestrator Header Formatter

Provides standardized headers for all CORTEX entry point orchestrators.
Ensures consistent branding, copyright attribution, and execution context display.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [HeaderFormatter](#headerformatter)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, typing


## Classes

### HeaderFormatter

```python
class HeaderFormatter
```

Format headers for CORTEX orchestrators.


**Methods:**

  #### `format_minimalist`

  *Decorators:* `staticmethod`

  ```python
  format_minimalist(operation_name: str, version: str, profile: str, mode: Literal['LIVE', 'DRY RUN'], timestamp: datetime) -> str
  ```

  Format minimalist header (Option C).

Used for: cleanup, optimization, design sync, story refresh, etc.

Args:
    operation_name: Name of the operation (e.g., "Design Sync")
    version: Version string (e.g., "1.0.0")
    profile: Execution profile (e.g., "comprehensive")
    mode: Execution mode ("LIVE" or "DRY RUN")
    timestamp: Execution start time (defaults to now)

Returns:
    Formatted header string

  **Parameters:**

  - `operation_name` (str): Name of the operation (e.g., "Design Sync")
  - `version` (str): Version string (e.g., "1.0.0")
  - `profile` (str): Execution profile (e.g., "comprehensive")
  - `mode` (Literal['LIVE', 'DRY RUN']): Execution mode ("LIVE" or "DRY RUN")
  - `timestamp` (datetime) = `None`: Execution start time (defaults to now)


  **Returns:** str
    Formatted header string


  #### `format_banner`

  *Decorators:* `staticmethod`

  ```python
  format_banner(operation_name: str, version: str, profile: str, mode: Literal['LIVE', 'DRY RUN'], timestamp: datetime) -> str
  ```

  Format banner-style header (Option D).

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
  - `mode` (Literal['LIVE', 'DRY RUN']): Execution mode ("LIVE" or "DRY RUN")
  - `timestamp` (datetime) = `None`: Execution start time (defaults to now)


  **Returns:** str
    Formatted banner header string


  #### `format_completion`

  *Decorators:* `staticmethod`

  ```python
  format_completion(success: bool, duration_seconds: float, summary: str) -> str
  ```

  Format completion footer.

Args:
    success: Whether operation succeeded
    duration_seconds: Total execution time
    summary: Optional summary message

Returns:
    Formatted completion footer

  **Parameters:**

  - `success` (bool): Whether operation succeeded
  - `duration_seconds` (float): Total execution time
  - `summary` (str) = `None`: Optional summary message


  **Returns:** str
    Formatted completion footer



---
