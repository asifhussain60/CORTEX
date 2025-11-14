# Header Formatter Operation

**Auto-generated:** 2025-11-14 11:19:45

---

## Overview

CORTEX Orchestrator Header Formatter

Provides standardized headers for all CORTEX entry point orchestrators.
Ensures consistent branding, copyright attribution, and execution context display.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

## Usage

```python
from src.operations.header_formatter import HeaderFormatter

operation = HeaderFormatter()
result = operation.execute()
```

## Methods

### `format_minimalist(operation_name, version, profile, mode, timestamp)`

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

### `format_banner(operation_name, version, profile, mode, timestamp)`

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

### `format_completion(success, duration_seconds, summary)`

Format completion footer.

Args:
    success: Whether operation succeeded
    duration_seconds: Total execution time
    summary: Optional summary message

Returns:
    Formatted completion footer
