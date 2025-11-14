# Operation Header Formatter Operation

**Auto-generated:** 2025-11-14 12:46:58

---

## Overview

CORTEX Operation Header Formatter

Provides standardized headers and footers for all CORTEX operation orchestrators.
Ensures consistent branding, copyright attribution, and execution context display.

Consolidates functionality from header_formatter.py and header_utils.py

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

## Usage

```python
from src.operations.operation_header_formatter import OperationHeaderFormatter

operation = OperationHeaderFormatter()
result = operation.execute()
```

## Methods

### `format_minimalist(operation_name, version, profile, mode, timestamp, purpose)`

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

### `format_banner(operation_name, version, profile, mode, timestamp)`

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

### `format_completion(operation_name, success, duration_seconds, summary, accomplishments)`

Format completion footer.

Args:
    operation_name: Name of the operation
    success: Whether operation succeeded
    duration_seconds: Total execution time in seconds
    summary: Optional single-line summary message
    accomplishments: Optional list of bullet points showing what was done

Returns:
    Formatted completion footer

### `print_minimalist(operation_name, version, profile, mode, timestamp, purpose)`

Print minimalist header directly to console.

### `print_banner(operation_name, version, profile, mode, timestamp)`

Print banner header directly to console.

### `print_completion(operation_name, success, duration_seconds, summary, accomplishments)`

Print completion footer directly to console.
