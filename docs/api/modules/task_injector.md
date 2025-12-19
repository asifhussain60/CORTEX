# task_injector

Task Injector - Standard Task Auto-Injection for Worker Plans

Automatically injects standard tasks into all worker plans:
- Git checkpoints (start/end of phase)
- AST/Lens analysis
- Documentation updates
- TDD validation
- DoD validation

Author: Asif Hussain
Date: December 17, 2025
Version: 1.0.0


## Table of Contents

### Classes
- [StandardTask](#standardtask)
- [TaskInjector](#taskinjector)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** dataclasses, logging, typing


## Classes

### StandardTask

```python
class StandardTask
```

**Decorators:** `dataclass`

Standard task definition.


**Attributes:**

- `task_id`: str
- `title`: str
- `description`: str
- `category`: str
- `position`: str
- `required`: bool



---

### TaskInjector

```python
class TaskInjector
```

Injects standard tasks into worker plans.

Ensures consistency across all plans with:
- Git checkpoints for rollback capability
- AST/Lens analysis for context
- Documentation updates for synchronization
- TDD validation for quality
- DoD validation for completeness


**Methods:**

  #### `inject_standard_tasks`

  ```python
  inject_standard_tasks(self, phase_tasks: List[Dict[str, Any]], phase_number: int, phase_name: str) -> List[Dict[str, Any]]
  ```

  Inject standard tasks into phase task list.

Args:
    phase_tasks: Existing phase tasks
    phase_number: Phase number (1-indexed)
    phase_name: Phase name
    
Returns:
    Updated task list with standard tasks injected

  **Parameters:**

  - `self`
  - `phase_tasks` (List[Dict[str, Any]]): Existing phase tasks
  - `phase_number` (int): Phase number (1-indexed)
  - `phase_name` (str): Phase name


  **Returns:** List[Dict[str, Any]]
    Updated task list with standard tasks injected


  #### `get_standard_task_checklist`

  ```python
  get_standard_task_checklist(self, phase_number: int) -> List[str]
  ```

  Get markdown checklist of standard tasks for phase.

Args:
    phase_number: Phase number
    
Returns:
    List of markdown checkbox items

  **Parameters:**

  - `self`
  - `phase_number` (int): Phase number


  **Returns:** List[str]
    List of markdown checkbox items


  #### `validate_standard_tasks_present`

  ```python
  validate_standard_tasks_present(self, phase_tasks: List[Dict[str, Any]]) -> tuple[bool, List[str]]
  ```

  Validate that all required standard tasks are present.

Args:
    phase_tasks: Phase task list
    
Returns:
    Tuple of (all_present: bool, missing_tasks: List[str])

  **Parameters:**

  - `self`
  - `phase_tasks` (List[Dict[str, Any]]): Phase task list


  **Returns:** tuple[bool, List[str]]
    Tuple of (all_present: bool, missing_tasks: List[str])



---
