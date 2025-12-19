# planning

Planning CLI Wrapper

Command-line interface for planning utility.
Provides formatted output for feature planning operations.

Usage:
    python3 -m src.operations.planning create <feature_name> [--description DESC] [--complexity LEVEL]
    python3 -m src.operations.planning validate <plan_file>
    python3 -m src.operations.planning approve <plan_file>
    python3 -m src.operations.planning complete <plan_file>
    python3 -m src.operations.planning view <plan_file> [--markdown]

Version: 3.0.0
Author: Asif Hussain


## Table of Contents


### Functions
- [run_planning](#run_planning)
- [main](#main)


## Overview

- **Classes:** 0
- **Functions:** 2
- **Dependencies:** argparse, json, pathlib, src, sys


## Functions

### run_planning

```python
run_planning(**kwargs) -> dict
```

Wrapper for planning utility - follows CORTEX operations pattern.

Args:
    **kwargs: Arguments passed to planning utility functions
    
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
