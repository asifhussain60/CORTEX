# rollback

Rollback CLI Wrapper

Command-line interface for rollback utility.
Provides formatted output and user confirmation for rollback operations.

Usage:
    python3 -m src.operations.rollback <checkpoint_id> [--dry-run] [--force] [--yes]

Version: 3.0.0
Author: Asif Hussain


## Table of Contents


### Functions
- [run_rollback](#run_rollback)
- [main](#main)


## Overview

- **Classes:** 0
- **Functions:** 2
- **Dependencies:** argparse, pathlib, src, sys


## Functions

### run_rollback

```python
run_rollback(**kwargs) -> dict
```

Wrapper for rollback utility - follows CORTEX operations pattern.

Args:
    **kwargs: Arguments passed to run_rollback_utility
    
Returns:
    Result dictionary from utility


**Parameters:**

- `**kwargs`


**Returns:** dict
  Result dictionary from utility


---

### main

```python
main()
```

CLI entry point with formatted output.


---
