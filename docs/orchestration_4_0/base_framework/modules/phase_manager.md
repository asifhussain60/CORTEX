# phase_manager

Phase Manager for CORTEX 4.0 Orchestrators

Handles phase transitions, validation, and state management.


## Table of Contents

### Classes
- [PhaseStatus](#phasestatus)
- [Phase](#phase)
- [PhaseTransition](#phasetransition)
- [PhaseManager](#phasemanager)


## Overview

- **Classes:** 4
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, enum, logging, typing


## Classes

### PhaseStatus

```python
class PhaseStatus(Enum)
```

Phase execution status



---

### Phase

```python
class Phase
```

**Decorators:** `dataclass`

Represents a single phase in an orchestrator workflow.

Attributes:
    name: Phase identifier (e.g., "analyze", "transform")
    description: Human-readable phase description
    required: Whether phase must complete successfully
    validation: Optional validation function to run before phase
    cleanup: Optional cleanup function to run after phase


**Attributes:**

- `name`: str
- `description`: str
- `required`: bool
- `validation`: Optional[Callable[[], bool]]
- `cleanup`: Optional[Callable[[], None]]
- `status`: PhaseStatus
- `started_at`: Optional[datetime]
- `completed_at`: Optional[datetime]
- `error`: Optional[str]
- `result`: Optional[Dict[str, Any]]



---

### PhaseTransition

```python
class PhaseTransition
```

**Decorators:** `dataclass`

Represents a transition between phases.

Attributes:
    from_phase: Source phase name
    to_phase: Target phase name
    condition: Optional condition function (must return True to transition)
    timestamp: When transition occurred


**Attributes:**

- `from_phase`: str
- `to_phase`: str
- `condition`: Optional[Callable[[], bool]]
- `timestamp`: datetime


**Methods:**


---

### PhaseManager

```python
class PhaseManager
```

Manages phase execution and transitions for orchestrators.

Features:
- Phase registration and ordering
- Validation before phase execution
- State tracking (pending → in_progress → completed/failed)
- Transition history
- Rollback support


**Methods:**

  #### `register_phase`

  ```python
  register_phase(self, name: str, description: str, required: bool, validation: Optional[Callable[[], bool]], cleanup: Optional[Callable[[], None]]) -> Phase
  ```

  Register a new phase.

Args:
    name: Phase identifier
    description: Human-readable description
    required: Whether phase must complete successfully
    validation: Optional pre-phase validation
    cleanup: Optional post-phase cleanup
    
Returns:
    Registered Phase object

  **Parameters:**

  - `self`
  - `name` (str): Phase identifier
  - `description` (str): Human-readable description
  - `required` (bool) = `True`: Whether phase must complete successfully
  - `validation` (Optional[Callable[[], bool]]) = `None`: Optional pre-phase validation
  - `cleanup` (Optional[Callable[[], None]]) = `None`: Optional post-phase cleanup


  **Returns:** Phase
    Registered Phase object


  #### `start_phase`

  ```python
  start_phase(self, phase_name: str) -> None
  ```

  Start execution of a phase.

Args:
    phase_name: Name of phase to start
    
Raises:
    ValueError: If phase not found or already started

  **Parameters:**

  - `self`
  - `phase_name` (str): Name of phase to start


  **Returns:** None


  #### `complete_phase`

  ```python
  complete_phase(self, phase_name: str, result: Optional[Dict[str, Any]]) -> None
  ```

  Mark phase as completed.

Args:
    phase_name: Name of phase to complete
    result: Optional result data
    
Raises:
    ValueError: If phase not in progress

  **Parameters:**

  - `self`
  - `phase_name` (str): Name of phase to complete
  - `result` (Optional[Dict[str, Any]]) = `None`: Optional result data


  **Returns:** None


  #### `fail_phase`

  ```python
  fail_phase(self, phase_name: str, error: str) -> None
  ```

  Mark phase as failed.

Args:
    phase_name: Name of phase that failed
    error: Error message
    
Raises:
    ValueError: If phase not in progress

  **Parameters:**

  - `self`
  - `phase_name` (str): Name of phase that failed
  - `error` (str): Error message


  **Returns:** None


  #### `skip_phase`

  ```python
  skip_phase(self, phase_name: str, reason: str) -> None
  ```

  Mark phase as skipped.

Args:
    phase_name: Name of phase to skip
    reason: Why phase was skipped

  **Parameters:**

  - `self`
  - `phase_name` (str): Name of phase to skip
  - `reason` (str): Why phase was skipped


  **Returns:** None


  #### `get_progress`

  ```python
  get_progress(self) -> Dict[str, Any]
  ```

  Get current progress through phases.

Returns:
    Dictionary with progress metrics

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dictionary with progress metrics


  #### `get_phase_status`

  ```python
  get_phase_status(self, phase_name: str) -> PhaseStatus
  ```

  Get status of a specific phase

  **Parameters:**

  - `self`
  - `phase_name` (str)


  **Returns:** PhaseStatus


  #### `reset`

  ```python
  reset(self) -> None
  ```

  Reset all phases to pending state

  **Parameters:**

  - `self`


  **Returns:** None



---
