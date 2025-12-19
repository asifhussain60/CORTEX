# parallel_orchestration_coordinator

Parallel Orchestration Coordinator

Enables concurrent execution of independent orchestration phases with:
- DAG-based dependency resolution
- Resource locking for concurrent safety
- Error isolation to prevent cascade failures
- Performance optimization (2-3x speedup for independent phases)

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX


## Table of Contents

### Classes
- [DependencyError](#dependencyerror)
- [ResourceLockError](#resourcelockerror)
- [PhaseDefinition](#phasedefinition)
- [ParallelOrchestrationCoordinator](#parallelorchestrationcoordinator)


## Overview

- **Classes:** 4
- **Functions:** 0
- **Dependencies:** asyncio, collections, dataclasses, logging, networkx, time, typing


## Classes

### DependencyError

```python
class DependencyError(Exception)
```

Raised when dependency resolution fails (e.g., circular dependencies).



---

### ResourceLockError

```python
class ResourceLockError(Exception)
```

Raised when resource locking fails or times out.



---

### PhaseDefinition

```python
class PhaseDefinition
```

**Decorators:** `dataclass`

Defines a phase for parallel orchestration.

Attributes:
    phase_id: Unique identifier for the phase
    phase_func: Async function to execute for this phase
    dependencies: List of phase_ids that must complete before this phase
    resources: List of resource names this phase requires (for locking)
    timeout: Maximum execution time in seconds (None = no timeout)
    metadata: Additional metadata for the phase


**Attributes:**

- `phase_id`: str
- `phase_func`: Callable
- `dependencies`: List[str]
- `resources`: List[str]
- `timeout`: Optional[float]
- `metadata`: Dict[str, Any]



---

### ParallelOrchestrationCoordinator

```python
class ParallelOrchestrationCoordinator
```

Coordinates parallel execution of orchestration phases with dependency
resolution, resource locking, and error isolation.

Features:
- Async parallel execution using asyncio.gather()
- DAG-based dependency resolution with topological sort
- Resource-level locking for concurrent safety
- Error isolation (one phase failure doesn't cascade)
- Performance optimization (2-3x speedup for independent phases)

Usage:
    coordinator = ParallelOrchestrationCoordinator()
    
    phases = [
        PhaseDefinition(
            phase_id="phase1",
            phase_func=async_function1,
            dependencies=[],
            resources=["file_a"]
        ),
        PhaseDefinition(
            phase_id="phase2",
            phase_func=async_function2,
            dependencies=["phase1"],
            resources=["file_b"]
        )
    ]
    
    results = await coordinator.execute_parallel_phases(phases)


**Methods:**

  #### `execute_parallel_phases`

  ```python
  execute_parallel_phases(self, phases: List[PhaseDefinition], max_concurrent: Optional[int]) -> Dict[str, Any]
  ```

  Execute phases in parallel with dependency resolution.

Args:
    phases: List of PhaseDefinition objects to execute
    max_concurrent: Maximum number of concurrent phases (None = unlimited)

Returns:
    Dictionary mapping phase_id to result or error
    For success: {phase_id: <result_value>}
    For error: {phase_id: {"error": <error_message>}}
    For skipped: {phase_id: {"status": "skipped", "reason": <reason>}}

Raises:
    DependencyError: If dependency graph has circular dependencies

  **Parameters:**

  - `self`
  - `phases` (List[PhaseDefinition]): List of PhaseDefinition objects to execute
  - `max_concurrent` (Optional[int]) = `None`: Maximum number of concurrent phases (None = unlimited)


  **Returns:** Dict[str, Any]
    Dictionary mapping phase_id to result or error For success: {phase_id: <result_value>} For error: {phase_id: {"error": <error_message>}} For skipped: {phase_id: {"status": "skipped", "reason": <reason>}}


  #### `acquire_resource_lock`

  ```python
  acquire_resource_lock(self, resource: str)
  ```

  Context manager for acquiring resource locks (async context manager).

Usage:
    async with coordinator.acquire_resource_lock("file_a"):
        # ... do work with file_a

Args:
    resource: Resource name to lock

Returns:
    Async context manager for the resource lock

  **Parameters:**

  - `self`
  - `resource` (str): Resource name to lock



---
