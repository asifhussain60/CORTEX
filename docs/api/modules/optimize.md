# optimize

CORTEX Optimize Entry Point

Unified CLI wrapper for all optimization operations:
- Token optimization (governance files)
- File system optimization (organization/archives/cache)
- Database consolidation

Usage:
    optimize tokens <command>       # Token optimization
    optimize files <target>         # File system optimization
    optimize all                    # Everything

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 3.0
License: Proprietary


## Table of Contents


### Functions
- [run_optimize](#run_optimize)
- [run_token_optimization](#run_token_optimization)
- [main](#main)


## Overview

- **Classes:** 0
- **Functions:** 3
- **Dependencies:** argparse, operations, pathlib, sys


## Functions

### run_optimize

```python
run_optimize(target: str, aggressive: bool, dry_run: bool, skip_skull_tests: bool)
```

Run CORTEX comprehensive optimize operation.

Args:
    target: What to optimize (organization/archives/cortex/cache/consolidation/all)
    aggressive: Use aggressive optimization for databases
    dry_run: Preview changes without executing
    skip_skull_tests: Skip SKULL test validation (for fast user operations)

Returns:
    Dict with success, message, and optimization results


**Parameters:**

- `target` (str) = `'all'`: What to optimize (organization/archives/cortex/cache/consolidation/all)
- `aggressive` (bool) = `False`: Use aggressive optimization for databases
- `dry_run` (bool) = `False`: Preview changes without executing
- `skip_skull_tests` (bool) = `False`: Skip SKULL test validation (for fast user operations)


---

### run_token_optimization

```python
run_token_optimization(command: str)
```

Run token optimization command.

Args:
    command: Token optimization command (status/auto/quick/full/rollback/validate)


**Parameters:**

- `command` (str): Token optimization command (status/auto/quick/full/rollback/validate)


---

### main

```python
main()
```

CLI entry point.


---
