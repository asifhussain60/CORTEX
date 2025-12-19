# cache_commands

Cache Management Commands for CORTEX

Provides CLI commands for managing the ValidationCache:
- cache status: Show cache statistics
- cache clear: Clear all cache entries
- cache invalidate <operation>: Invalidate specific operation cache

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Version: 1.0.0
Date: November 26, 2025


## Table of Contents


### Functions
- [cache_status_command](#cache_status_command)
- [cache_clear_command](#cache_clear_command)
- [cache_invalidate_command](#cache_invalidate_command)
- [register_cache_commands](#register_cache_commands)


## Overview

- **Classes:** 0
- **Functions:** 4
- **Dependencies:** logging, pathlib, src, typing


## Functions

### cache_status_command

```python
cache_status_command(args: Dict[str, Any]) -> str
```

Show cache statistics.

Args:
    args: Optional arguments with 'operation' key for operation-specific stats

Returns:
    Formatted status string


**Parameters:**

- `args` (Dict[str, Any]) = `None`: Optional arguments with 'operation' key for operation-specific stats


**Returns:** str
  Formatted status string


---

### cache_clear_command

```python
cache_clear_command(args: Dict[str, Any]) -> str
```

Clear all cache entries.

Args:
    args: Optional arguments (not used)

Returns:
    Confirmation message


**Parameters:**

- `args` (Dict[str, Any]) = `None`: Optional arguments (not used)


**Returns:** str
  Confirmation message


---

### cache_invalidate_command

```python
cache_invalidate_command(args: Dict[str, Any]) -> str
```

Invalidate specific operation cache.

Args:
    args: Dictionary with 'operation' key (e.g., 'align', 'deploy')

Returns:
    Confirmation message


**Parameters:**

- `args` (Dict[str, Any]): Dictionary with 'operation' key (e.g., 'align', 'deploy')


**Returns:** str
  Confirmation message


---

### register_cache_commands

```python
register_cache_commands(command_router)
```

Register cache management commands with command router.

Args:
    command_router: CommandRouter instance


**Parameters:**

- `command_router`: CommandRouter instance


---
