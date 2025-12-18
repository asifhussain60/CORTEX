# execution_orchestrator

Execution Orchestrator for CORTEX 4.0

Handles multi-phase execution workflows with:
- Phase validation and execution
- Sub-orchestrator routing
- Progress tracking
- Error recovery


## Table of Contents

### Classes
- [ExecutionOrchestrator](#executionorchestrator)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** logging, src, typing


## Classes

### ExecutionOrchestrator

```python
class ExecutionOrchestrator(BaseOrchestrator)
```

Orchestrates execution of multi-phase workflows.

Features:
- Dynamic phase registration from execution plans
- Sub-orchestrator integration (TDD, Planning, etc.)
- Validation gates between phases
- Rollback support for failed phases
- Progress tracking with visual feedback

Usage:
    orchestrator = ExecutionOrchestrator(
        logger=logger,
        config={"max_retries": 3}
    )
    
    result = orchestrator.execute(context={
        "plan": execution_plan,
        "workspace": "/path/to/workspace"
    })


**Methods:**

  #### `register_sub_orchestrator`

  ```python
  register_sub_orchestrator(self, name: str, orchestrator: Any) -> None
  ```

  Register a sub-orchestrator for use in phases.

Args:
    name: Orchestrator identifier (e.g., "tdd", "planning")
    orchestrator: Orchestrator instance

  **Parameters:**

  - `self`
  - `name` (str): Orchestrator identifier (e.g., "tdd", "planning")
  - `orchestrator` (Any): Orchestrator instance


  **Returns:** None


  #### `register_validator`

  ```python
  register_validator(self, name: str, validator: Callable) -> None
  ```

  Register a phase validator function.

Args:
    name: Validator identifier
    validator: Validation function (should return bool)

  **Parameters:**

  - `self`
  - `name` (str): Validator identifier
  - `validator` (Callable): Validation function (should return bool)


  **Returns:** None



---
