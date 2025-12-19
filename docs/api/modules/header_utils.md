# header_utils

CORTEX Orchestrator Header Utilities

Provides standardized copyright headers for all CORTEX entry point orchestrators.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents


### Functions
- [format_minimalist_header](#format_minimalist_header)
- [print_minimalist_header](#print_minimalist_header)
- [print_banner_header](#print_banner_header)
- [format_completion_footer](#format_completion_footer)
- [print_completion_footer](#print_completion_footer)


## Overview

- **Classes:** 0
- **Functions:** 5
- **Dependencies:** datetime, typing


## Functions

### format_minimalist_header

```python
format_minimalist_header(operation_name: str, version: str, profile: str, mode: str, purpose: Optional[str]) -> str
```

Format minimalist header (Option C) for orchestrators.

Returns the header as a string instead of printing.

Args:
    operation_name: Name of the operation (e.g., "Design Sync")
    version: Version number (e.g., "1.0.0")
    profile: Execution profile (e.g., "comprehensive")
    mode: Execution mode description (always "LIVE EXECUTION")
    purpose: Optional 1-2 line description of what will be accomplished

Returns:
    Formatted header string


**Parameters:**

- `operation_name` (str): Name of the operation (e.g., "Design Sync")
- `version` (str): Version number (e.g., "1.0.0")
- `profile` (str): Execution profile (e.g., "comprehensive")
- `mode` (str): Execution mode description (always "LIVE EXECUTION")
- `purpose` (Optional[str]) = `None`: Optional 1-2 line description of what will be accomplished


**Returns:** str
  Formatted header string


---

### print_minimalist_header

```python
print_minimalist_header(operation_name: str, version: str, profile: str, mode: str, purpose: Optional[str]) -> None
```

Print minimalist header (Option C) for orchestrators.

Args:
    operation_name: Name of the operation (e.g., "Design Sync")
    version: Version number (e.g., "1.0.0")
    profile: Execution profile (e.g., "comprehensive")
    mode: Execution mode description (always "LIVE EXECUTION")
    purpose: Optional 1-2 line description of what will be accomplished


**Parameters:**

- `operation_name` (str): Name of the operation (e.g., "Design Sync")
- `version` (str): Version number (e.g., "1.0.0")
- `profile` (str): Execution profile (e.g., "comprehensive")
- `mode` (str): Execution mode description (always "LIVE EXECUTION")
- `purpose` (Optional[str]) = `None`: Optional 1-2 line description of what will be accomplished


**Returns:** None


---

### print_banner_header

```python
print_banner_header(operation_name: str, version: str, profile: str) -> None
```

Print banner-style header (Option D) for help module.

Args:
    operation_name: Name of the operation (e.g., "Help System")
    version: Version number (e.g., "1.0.0")
    profile: Execution profile


**Parameters:**

- `operation_name` (str): Name of the operation (e.g., "Help System")
- `version` (str): Version number (e.g., "1.0.0")
- `profile` (str): Execution profile


**Returns:** None


---

### format_completion_footer

```python
format_completion_footer(operation_name: str, success: bool, duration_seconds: float, summary: Optional[str], accomplishments: Optional[list]) -> str
```

Format completion footer for orchestrators.

Returns the footer as a string instead of printing.

Args:
    operation_name: Name of the operation
    success: Whether operation succeeded
    duration_seconds: Execution duration
    summary: Optional summary message (single line)
    accomplishments: Optional list of bullet points showing what was done

Returns:
    Formatted footer string


**Parameters:**

- `operation_name` (str): Name of the operation
- `success` (bool): Whether operation succeeded
- `duration_seconds` (float): Execution duration
- `summary` (Optional[str]) = `None`: Optional summary message (single line)
- `accomplishments` (Optional[list]) = `None`: Optional list of bullet points showing what was done


**Returns:** str
  Formatted footer string


---

### print_completion_footer

```python
print_completion_footer(operation_name: str, success: bool, duration_seconds: float, summary: Optional[str], accomplishments: Optional[list]) -> None
```

Print completion footer for orchestrators.

Args:
    operation_name: Name of the operation
    success: Whether operation succeeded
    duration_seconds: Execution duration
    summary: Optional summary message (single line)
    accomplishments: Optional list of bullet points showing what was done


**Parameters:**

- `operation_name` (str): Name of the operation
- `success` (bool): Whether operation succeeded
- `duration_seconds` (float): Execution duration
- `summary` (Optional[str]) = `None`: Optional summary message (single line)
- `accomplishments` (Optional[list]) = `None`: Optional list of bullet points showing what was done


**Returns:** None


---
