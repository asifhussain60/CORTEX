# deploy

CORTEX Deploy Operation - CLI Entry Point

Runs CORTEX deployment with validation gates.
Wrapper for scripts/deploy_cortex.py to enable module execution pattern.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents


### Functions
- [run_deploy](#run_deploy)
- [main](#main)


## Overview

- **Classes:** 0
- **Functions:** 2
- **Dependencies:** argparse, deploy_cortex, io, pathlib, src, sys


## Functions

### run_deploy

```python
run_deploy(dry_run: bool, branch: str, skip_align: bool)
```

Run CORTEX deploy operation with validators.

ALL DEPLOYMENT GATES MANDATORY - No skipping allowed.
All 19 gates must pass for production deployment.

Args:
    dry_run: Preview only, don't make changes
    branch: Target branch name (default: main)
    skip_align: Skip pre-flight alignment check (not recommended)

Returns:
    dict: Operation result with success status


**Parameters:**

- `dry_run` (bool) = `False`: Preview only, don't make changes
- `branch` (str) = `PUBLISH_BRANCH`: Target branch name (default: main)
- `skip_align` (bool) = `False`: Skip pre-flight alignment check (not recommended)


---

### main

```python
main()
```

CLI entry point for module execution.


---
