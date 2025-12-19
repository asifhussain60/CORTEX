# git_checkpoint

Git Checkpoint CLI Wrapper

Command-line interface for git checkpoint utility.
Provides formatted output for checkpoint creation and listing.

Usage:
    python3 -m src.operations.git_checkpoint create [--session SESSION] [--phase PHASE] [--message MESSAGE]
    python3 -m src.operations.git_checkpoint list [--all]

Version: 3.0.0
Author: Asif Hussain


## Table of Contents


### Functions
- [run_checkpoint](#run_checkpoint)
- [main](#main)


## Overview

- **Classes:** 0
- **Functions:** 2
- **Dependencies:** argparse, datetime, pathlib, src, sys


## Functions

### run_checkpoint

```python
run_checkpoint(**kwargs) -> dict
```

Wrapper for checkpoint utility - follows CORTEX operations pattern.

Args:
    **kwargs: Arguments passed to run_checkpoint_utility
    
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
