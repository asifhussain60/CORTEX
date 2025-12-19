# orchestration_checkpoint_manager

OrchestrationCheckpointManager - Feature 11 Implementation

Purpose: Save/restore/rollback orchestrator workflow state for failure recovery

Key Features:
- JSON-based checkpoint storage in cortex-brain/checkpoints/
- save_checkpoint(): Create checkpoint with state serialization
- restore_checkpoint(): Restore state from checkpoint
- rollback(): Restore state and remove later checkpoints
- cleanup_old_checkpoints(): 30-day retention policy with auto-cleanup
- Thread-safe operations for parallel orchestrators
- Performance: <50ms save/restore operations

Storage Structure:
    cortex-brain/checkpoints/
    ├── planning_orchestrator/
    │   ├── checkpoint-2024-12-13T10-30-00-abc123.json
    │   └── checkpoint-2024-12-13T11-15-00-def456.json
    ├── tdd_orchestrator/
    │   └── checkpoint-2024-12-13T09-45-00-ghi789.json
    └── system_maintenance_orchestrator/
        └── checkpoint-2024-12-13T08-00-00-jkl012.json

Checkpoint Schema:
{
    "checkpoint_id": "checkpoint-2024-12-13T10-30-00-abc123",
    "orchestrator_name": "planning_orchestrator",
    "timestamp": "2024-12-13T10:30:00.123456",
    "phase": "Phase 2: Implementation",
    "state": {
        "phase": 2,
        "current_task": "task_2.1",
        "completed_tasks": ["task_1.1", "task_1.2"],
        "variables": {"feature_name": "Feature 11"}
    }
}

Author: Asif Hussain
Created: December 13, 2024
Phase: 11.2 (GREEN)


## Table of Contents

### Classes
- [CheckpointNotFoundError](#checkpointnotfounderror)
- [CheckpointCorruptedError](#checkpointcorruptederror)
- [OrchestrationCheckpointManager](#orchestrationcheckpointmanager)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** datetime, json, logging, os, pathlib, src, threading, typing, uuid


## Classes

### CheckpointNotFoundError

```python
class CheckpointNotFoundError(Exception)
```

Raised when attempting to restore a non-existent checkpoint.



---

### CheckpointCorruptedError

```python
class CheckpointCorruptedError(Exception)
```

Raised when a checkpoint file is corrupted or invalid JSON.



---

### OrchestrationCheckpointManager

```python
class OrchestrationCheckpointManager
```

Manages checkpoint save/restore/rollback for orchestrator workflows.

Provides recovery capability for long-running orchestrator executions,
allowing workflows to resume from checkpoints after failures.

Thread-safe for concurrent orchestrator operations.


**Methods:**

  #### `save_checkpoint`

  ```python
  save_checkpoint(self, orchestrator_name: str, state: Dict[str, Any], phase: Optional[str]) -> str
  ```

  Save a checkpoint with the current orchestrator state.

Args:
    orchestrator_name: Name of the orchestrator (e.g., 'planning_orchestrator')
    state: Dictionary containing orchestrator state to save
    phase: Optional phase name (e.g., 'Phase 2: Implementation')

Returns:
    str: Unique checkpoint ID for later restoration

Example:
    >>> manager = OrchestrationCheckpointManager()
    >>> state = {'phase': 2, 'tasks': ['task_1', 'task_2']}
    >>> checkpoint_id = manager.save_checkpoint('planning_orchestrator', state, 'Phase 2')
    >>> print(checkpoint_id)
    'checkpoint-2024-12-13T10-30-00-abc123'

  **Parameters:**

  - `self`
  - `orchestrator_name` (str): Name of the orchestrator (e.g., 'planning_orchestrator')
  - `state` (Dict[str, Any]): Dictionary containing orchestrator state to save
  - `phase` (Optional[str]) = `None`: Optional phase name (e.g., 'Phase 2: Implementation')


  **Returns:** str
    str: Unique checkpoint ID for later restoration


  #### `restore_checkpoint`

  ```python
  restore_checkpoint(self, orchestrator_name: str, checkpoint_id: str) -> Dict[str, Any]
  ```

  Restore orchestrator state from a checkpoint.

Args:
    orchestrator_name: Name of the orchestrator
    checkpoint_id: Checkpoint ID returned by save_checkpoint()

Returns:
    Dict[str, Any]: Restored state dictionary

Raises:
    CheckpointNotFoundError: If checkpoint doesn't exist
    CheckpointCorruptedError: If checkpoint file is corrupted

Example:
    >>> manager = OrchestrationCheckpointManager()
    >>> state = manager.restore_checkpoint('planning_orchestrator', checkpoint_id)
    >>> print(state['phase'])
    2

  **Parameters:**

  - `self`
  - `orchestrator_name` (str): Name of the orchestrator
  - `checkpoint_id` (str): Checkpoint ID returned by save_checkpoint()


  **Returns:** Dict[str, Any]
    Dict[str, Any]: Restored state dictionary


  #### `rollback`

  ```python
  rollback(self, orchestrator_name: str, checkpoint_id: str) -> Dict[str, Any]
  ```

  Rollback to a previous checkpoint and remove all later checkpoints.

Used to recover from failed workflow execution by restoring to
a known-good checkpoint and removing checkpoints created after that point.

Args:
    orchestrator_name: Name of the orchestrator
    checkpoint_id: Target checkpoint ID to rollback to

Returns:
    Dict[str, Any]: Restored state from the target checkpoint

Raises:
    CheckpointNotFoundError: If target checkpoint doesn't exist

Example:
    >>> manager = OrchestrationCheckpointManager()
    >>> # Save 3 checkpoints
    >>> cp1 = manager.save_checkpoint('orch', {'phase': 1})
    >>> cp2 = manager.save_checkpoint('orch', {'phase': 2})
    >>> cp3 = manager.save_checkpoint('orch', {'phase': 3})
    >>> # Rollback to checkpoint 1 (removes cp2 and cp3)
    >>> state = manager.rollback('orch', cp1)
    >>> print(state['phase'])
    1

  **Parameters:**

  - `self`
  - `orchestrator_name` (str): Name of the orchestrator
  - `checkpoint_id` (str): Target checkpoint ID to rollback to


  **Returns:** Dict[str, Any]
    Dict[str, Any]: Restored state from the target checkpoint


  #### `list_checkpoints`

  ```python
  list_checkpoints(self, orchestrator_name: str) -> List[Dict[str, Any]]
  ```

  List all checkpoints for an orchestrator in chronological order.

Args:
    orchestrator_name: Name of the orchestrator

Returns:
    List[Dict]: List of checkpoint metadata dictionaries, sorted by timestamp

Example:
    >>> manager = OrchestrationCheckpointManager()
    >>> checkpoints = manager.list_checkpoints('planning_orchestrator')
    >>> for cp in checkpoints:
    ...     print(f"{cp['checkpoint_id']}: {cp['phase']}")

  **Parameters:**

  - `self`
  - `orchestrator_name` (str): Name of the orchestrator


  **Returns:** List[Dict[str, Any]]
    List[Dict]: List of checkpoint metadata dictionaries, sorted by timestamp


  #### `cleanup_old_checkpoints`

  ```python
  cleanup_old_checkpoints(self, retention_days: int) -> int
  ```

  Remove checkpoints older than retention period.

Implements 30-day retention policy by default. Removes checkpoints
across all orchestrators that exceed the retention period.

Args:
    retention_days: Number of days to retain checkpoints (default: 30)

Returns:
    int: Number of checkpoints removed

Example:
    >>> manager = OrchestrationCheckpointManager()
    >>> removed_count = manager.cleanup_old_checkpoints(retention_days=30)
    >>> print(f"Removed {removed_count} old checkpoints")

  **Parameters:**

  - `self`
  - `retention_days` (int) = `30`: Number of days to retain checkpoints (default: 30)


  **Returns:** int
    int: Number of checkpoints removed


  #### `get_latest_checkpoint`

  ```python
  get_latest_checkpoint(self, orchestrator_name: str) -> Optional[str]
  ```

  Get the ID of the most recent checkpoint for an orchestrator.

Args:
    orchestrator_name: Name of the orchestrator

Returns:
    Optional[str]: Latest checkpoint ID, or None if no checkpoints exist

Example:
    >>> manager = OrchestrationCheckpointManager()
    >>> latest_id = manager.get_latest_checkpoint('planning_orchestrator')
    >>> if latest_id:
    ...     state = manager.restore_checkpoint('planning_orchestrator', latest_id)

  **Parameters:**

  - `self`
  - `orchestrator_name` (str): Name of the orchestrator


  **Returns:** Optional[str]
    Optional[str]: Latest checkpoint ID, or None if no checkpoints exist


  #### `delete_checkpoint`

  ```python
  delete_checkpoint(self, orchestrator_name: str, checkpoint_id: str) -> bool
  ```

  Delete a specific checkpoint.

Args:
    orchestrator_name: Name of the orchestrator
    checkpoint_id: Checkpoint ID to delete

Returns:
    bool: True if checkpoint was deleted, False if it didn't exist

Example:
    >>> manager = OrchestrationCheckpointManager()
    >>> success = manager.delete_checkpoint('planning_orchestrator', checkpoint_id)

  **Parameters:**

  - `self`
  - `orchestrator_name` (str): Name of the orchestrator
  - `checkpoint_id` (str): Checkpoint ID to delete


  **Returns:** bool
    bool: True if checkpoint was deleted, False if it didn't exist



---
