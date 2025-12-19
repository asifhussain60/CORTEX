# operations_orchestrator

Universal Operations Orchestrator - CORTEX 2.0

This orchestrator coordinates ALL CORTEX operations (setup, story refresh, cleanup, etc.)
by executing modules in dependency-resolved order across defined phases.

Design Principles:
    - Single orchestrator for all operations
    - YAML-driven operation definitions
    - Topological sort for dependency resolution
    - Phase-based execution with priorities
    - Parallel execution of independent modules
    - Comprehensive error handling and rollback

Author: Asif Hussain
Version: 3.0.0 (Parallel Execution Optimization)


## Table of Contents

### Classes
- [OperationExecutionReport](#operationexecutionreport)
- [OperationsOrchestrator](#operationsorchestrator)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** concurrent, dataclasses, datetime, logging, pathlib, src, typing


## Classes

### OperationExecutionReport

```python
class OperationExecutionReport
```

**Decorators:** `dataclass`

Report of operation execution.

Universal report for ANY operation (setup, cleanup, story refresh, etc.)

Attributes:
    operation_id: Operation identifier (e.g., 'environment_setup')
    operation_name: Human-readable name
    success: Overall operation success
    modules_executed: List of module IDs that ran
    modules_succeeded: List of module IDs that succeeded
    modules_failed: List of module IDs that failed
    modules_skipped: List of module IDs that were skipped
    module_results: Detailed results for each module
    total_duration_seconds: Total execution time
    timestamp: When operation completed
    context: Final shared context dictionary
    errors: List of error messages
    parallel_execution_count: Number of modules executed in parallel
    parallel_groups_count: Number of parallel execution groups
    time_saved_seconds: Estimated time saved by parallel execution


**Attributes:**

- `operation_id`: str
- `operation_name`: str
- `success`: bool
- `modules_executed`: List[str]
- `modules_succeeded`: List[str]
- `modules_failed`: List[str]
- `modules_skipped`: List[str]
- `module_results`: Dict[str, OperationResult]
- `total_duration_seconds`: float
- `timestamp`: Optional[datetime]
- `context`: Dict[str, Any]
- `errors`: List[str]
- `parallel_execution_count`: int
- `parallel_groups_count`: int
- `time_saved_seconds`: float


**Methods:**


---

### OperationsOrchestrator

```python
class OperationsOrchestrator
```

Universal orchestrator for ALL CORTEX operations.

Coordinates module execution for any operation defined in cortex-operations.yaml:
    - environment_setup (setup command)
    - refresh_cortex_story (story refresh command)
    - workspace_cleanup (cleanup command)
    - update_documentation (docs command)
    - And any future operations

Key Features:
    - Dependency resolution via topological sort
    - Phase-based execution (PRE_VALIDATION → FINALIZATION)
    - Priority ordering within phases
    - Error handling with rollback
    - Comprehensive reporting
    - Copyright header rendering

Example Usage:
    # Setup operation
    orchestrator = OperationsOrchestrator(
        operation_id="environment_setup",
        modules=[platform_mod, vision_mod, brain_mod]
    )
    report = orchestrator.execute_operation(
        context={'project_root': Path('...')}
    )
    
    # Cleanup operation
    orchestrator = OperationsOrchestrator(
        operation_id="workspace_cleanup",
        modules=[scan_mod, cleanup_mod]
    )
    report = orchestrator.execute_operation(
        context={'project_root': Path('...')}
    )


**Methods:**

  #### `execute_operation`

  ```python
  execute_operation(self, context: Optional[Dict[str, Any]]) -> OperationExecutionReport
  ```

  Execute the operation by running all modules in dependency-resolved order.

Args:
    context: Additional context to merge with initialization context

Returns:
    OperationExecutionReport with execution details

  **Parameters:**

  - `self`
  - `context` (Optional[Dict[str, Any]]) = `None`: Additional context to merge with initialization context


  **Returns:** OperationExecutionReport
    OperationExecutionReport with execution details


  #### `get_module_execution_order`

  ```python
  get_module_execution_order(self) -> List[str]
  ```

  Get the execution order of modules without running them.

Returns:
    List of module IDs in execution order

  **Parameters:**

  - `self`


  **Returns:** List[str]
    List of module IDs in execution order



---
