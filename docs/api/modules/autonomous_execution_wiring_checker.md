# autonomous_execution_wiring_checker

Autonomous Execution Wiring Checker for CORTEX Align.

Validates that autonomous execution is properly integrated:
- PlanningOrchestrator has execute_plan_autonomously method
- Integration tests exist and pass
- Response templates configured
- Intent router recognizes autonomous commands
- Git checkpoint integration present

Author: GitHub Copilot
Created: 2025-12-06


## Table of Contents

### Classes
- [AutonomousExecutionWiringChecker](#autonomousexecutionwiringchecker)

### Functions
- [check_autonomous_execution_wiring](#check_autonomous_execution_wiring)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** importlib, logging, pathlib, typing, yaml


## Classes

### AutonomousExecutionWiringChecker

```python
class AutonomousExecutionWiringChecker
```

Validates autonomous execution integration in CORTEX.


**Methods:**

  #### `check_autonomous_execution_wiring`

  ```python
  check_autonomous_execution_wiring(self) -> Tuple[bool, List[str], List[str]]
  ```

  Check if autonomous execution is properly wired.

Returns:
    Tuple of (all_checks_passed, successes, warnings)

  **Parameters:**

  - `self`


  **Returns:** Tuple[bool, List[str], List[str]]
    Tuple of (all_checks_passed, successes, warnings)



---

## Functions

### check_autonomous_execution_wiring

```python
check_autonomous_execution_wiring(cortex_root: Path) -> Dict[str, any]
```

Entry point for autonomous execution wiring check.

Args:
    cortex_root: Path to CORTEX root

Returns:
    Dict with check results


**Parameters:**

- `cortex_root` (Path): Path to CORTEX root


**Returns:** Dict[str, any]
  Dict with check results


---
