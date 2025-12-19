# ado_planning_demo

ADO Planning Demo Script

Interactive demonstration of ADO work item planning with git history integration.
Shows complete workflow: create work item → git enrichment → template generation → result display.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [ADOPlanningDemo](#adoplanningdemo)

### Functions
- [run_ado_planning_demo](#run_ado_planning_demo)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** datetime, logging, pathlib, typing


## Classes

### ADOPlanningDemo

```python
class ADOPlanningDemo
```

Interactive demonstration of ADO work item planning.

Shows Phase 1 git history integration features:
- Quality scoring (0-100%)
- High-risk file detection
- SME identification
- Related commits and contributors


**Methods:**

  #### `run_demo`

  ```python
  run_demo(self) -> Dict[str, Any]
  ```

  Run complete ADO planning demonstration.

Returns:
    Demo results with examples and explanations

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Demo results with examples and explanations



---

## Functions

### run_ado_planning_demo

```python
run_ado_planning_demo(cortex_root: Path) -> Dict[str, Any]
```

Quick function to run ADO planning demonstration.

Args:
    cortex_root: Path to CORTEX repository
    
Returns:
    Demo results dictionary


**Parameters:**

- `cortex_root` (Path): Path to CORTEX repository


**Returns:** Dict[str, Any]
  Demo results dictionary


---
