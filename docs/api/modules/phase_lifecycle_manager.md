# phase_lifecycle_manager

Phase Lifecycle Manager for CORTEX

Unified phase lifecycle management across all orchestrators.
Handles phase transitions: PENDING → IN PROGRESS → COMPLETE
Auto-completes plans when final phase is done.

Author: Asif Hussain
Version: 2.0.0 - Added automatic plan completion and folder movement


## Table of Contents

### Classes
- [PhaseLifecycleManager](#phaselifecyclemanager)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, logging, pathlib, re, shutil, typing, unified_plan_generator


## Classes

### PhaseLifecycleManager

```python
class PhaseLifecycleManager
```

Unified phase lifecycle management.

Used by all orchestrators for consistent phase transitions.


**Methods:**

  #### `start_phase`

  ```python
  start_phase(self, master_plan_path: Path, phase_number: int) -> Dict[str, Any]
  ```

  Transition phase: PENDING → IN PROGRESS

Args:
    master_plan_path: Path to master plan file
    phase_number: Phase number to start

Returns:
    Result dictionary with success status

  **Parameters:**

  - `self`
  - `master_plan_path` (Path): Path to master plan file
  - `phase_number` (int): Phase number to start


  **Returns:** Dict[str, Any]
    Result dictionary with success status


  #### `complete_phase`

  ```python
  complete_phase(self, master_plan_path: Path, phase_number: int, duration: timedelta, tokens_saved: int, metrics: Optional[Dict]) -> Dict[str, Any]
  ```

  Transition phase: IN PROGRESS → COMPLETE

Args:
    master_plan_path: Path to master plan file
    phase_number: Phase number to complete
    duration: Actual duration (timedelta)
    tokens_saved: Tokens saved in this phase
    metrics: Additional metrics (tests, coverage, etc.)

Returns:
    Result dictionary with success status

  **Parameters:**

  - `self`
  - `master_plan_path` (Path): Path to master plan file
  - `phase_number` (int): Phase number to complete
  - `duration` (timedelta): Actual duration (timedelta)
  - `tokens_saved` (int) = `0`: Tokens saved in this phase
  - `metrics` (Optional[Dict]) = `None`: Additional metrics (tests, coverage, etc.)


  **Returns:** Dict[str, Any]
    Result dictionary with success status


  #### `get_next_phase`

  ```python
  get_next_phase(self, master_plan_path: Path) -> Optional[int]
  ```

  Find next PENDING phase.

Args:
    master_plan_path: Path to master plan file

Returns:
    Next phase number or None if all complete

  **Parameters:**

  - `self`
  - `master_plan_path` (Path): Path to master plan file


  **Returns:** Optional[int]
    Next phase number or None if all complete



---
