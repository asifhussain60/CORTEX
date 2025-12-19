# work_state_manager

CORTEX Tier 1: Work State Manager
Tracks in-progress work to enable seamless "continue" functionality.

Purpose:
- Record current task being worked on
- Track files being modified
- Monitor last activity timestamp
- Persist state across sessions
- Enable proactive resume prompts

Usage:
    from src.tier1.work_state_manager import WorkStateManager
    
    wsm = WorkStateManager()
    
    # Start tracking a new task
    wsm.start_task("Implement user authentication", ["src/auth.py", "tests/test_auth.py"])
    
    # Update progress
    wsm.update_progress("Added login endpoint", files_touched=["src/auth.py"])
    
    if wsm.has_incomplete_work():
        state = wsm.get_current_state()
        print(f"Resume: {state.task_description}")
    
    # Mark task complete
    wsm.complete_task()


## Table of Contents

### Classes
- [WorkStatus](#workstatus)
- [WorkState](#workstate)
- [WorkStateManager](#workstatemanager)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, enum, json, pathlib, secrets, sqlite3, typing


## Classes

### WorkStatus

```python
class WorkStatus(Enum)
```

Status of work session.



---

### WorkState

```python
class WorkState
```

**Decorators:** `dataclass`

Represents the current state of in-progress work.


**Attributes:**

- `session_id`: str
- `task_description`: str
- `status`: WorkStatus
- `started_at`: datetime
- `last_activity`: datetime
- `files_touched`: List[str]
- `progress_notes`: List[str]
- `metadata`: Dict[str, Any]


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert to dictionary for serialization.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]


  #### `from_dict`

  *Decorators:* `classmethod`

  ```python
  from_dict(cls, data: Dict[str, Any]) -> 'WorkState'
  ```

  Create WorkState from dictionary.

  **Parameters:**

  - `cls`
  - `data` (Dict[str, Any])


  **Returns:** 'WorkState'


  #### `is_stale`

  ```python
  is_stale(self, hours: int) -> bool
  ```

  Check if work state is stale (no activity for N hours).

  **Parameters:**

  - `self`
  - `hours` (int) = `24`


  **Returns:** bool


  #### `duration_minutes`

  ```python
  duration_minutes(self) -> float
  ```

  Calculate duration of work session in minutes.

  **Parameters:**

  - `self`


  **Returns:** float



---

### WorkStateManager

```python
class WorkStateManager
```

Manages work state tracking for seamless continuation.

Provides:
- Start/stop tracking work sessions
- Update progress with file changes
- Retrieve current state for resume
- Auto-detect stale sessions
- Integration with Tier 1 database


**Methods:**

  #### `start_task`

  ```python
  start_task(self, task_description: str, files: Optional[List[str]], metadata: Optional[Dict[str, Any]]) -> str
  ```

  Start tracking a new work task.

Args:
    task_description: Human-readable description of the task
    files: Initial list of files being worked on
    metadata: Additional context (branch, conversation_id, etc.)

Returns:
    session_id: Unique identifier for this work session

  **Parameters:**

  - `self`
  - `task_description` (str): Human-readable description of the task
  - `files` (Optional[List[str]]) = `None`: Initial list of files being worked on
  - `metadata` (Optional[Dict[str, Any]]) = `None`: Additional context (branch, conversation_id, etc.)


  **Returns:** str
    session_id: Unique identifier for this work session


  #### `update_progress`

  ```python
  update_progress(self, progress_note: str, files_touched: Optional[List[str]], session_id: Optional[str]) -> None
  ```

  Update progress on current work session.

Args:
    progress_note: Description of what was just done
    files_touched: Files modified in this progress step
    session_id: Specific session to update (defaults to current)

  **Parameters:**

  - `self`
  - `progress_note` (str): Description of what was just done
  - `files_touched` (Optional[List[str]]) = `None`: Files modified in this progress step
  - `session_id` (Optional[str]) = `None`: Specific session to update (defaults to current)


  **Returns:** None


  #### `complete_task`

  ```python
  complete_task(self, session_id: Optional[str]) -> None
  ```

  Mark current work session as completed.

Args:
    session_id: Specific session to complete (defaults to current)

  **Parameters:**

  - `self`
  - `session_id` (Optional[str]) = `None`: Specific session to complete (defaults to current)


  **Returns:** None


  #### `pause_task`

  ```python
  pause_task(self, session_id: Optional[str]) -> None
  ```

  Pause current work session (e.g., switching contexts).

Args:
    session_id: Specific session to pause (defaults to current)

  **Parameters:**

  - `self`
  - `session_id` (Optional[str]) = `None`: Specific session to pause (defaults to current)


  **Returns:** None


  #### `abandon_task`

  ```python
  abandon_task(self, session_id: Optional[str], reason: Optional[str]) -> None
  ```

  Mark work session as abandoned (not completed).

Args:
    session_id: Specific session to abandon (defaults to current)
    reason: Optional reason for abandonment

  **Parameters:**

  - `self`
  - `session_id` (Optional[str]) = `None`: Specific session to abandon (defaults to current)
  - `reason` (Optional[str]) = `None`: Optional reason for abandonment


  **Returns:** None


  #### `get_current_state`

  ```python
  get_current_state(self) -> Optional[WorkState]
  ```

  Get the current active work state.

Returns:
    WorkState if there's active work, None otherwise

  **Parameters:**

  - `self`


  **Returns:** Optional[WorkState]
    WorkState if there's active work, None otherwise


  #### `get_state`

  ```python
  get_state(self, session_id: str) -> Optional[WorkState]
  ```

  Get work state for a specific session.

Args:
    session_id: Session identifier

Returns:
    WorkState if found, None otherwise

  **Parameters:**

  - `self`
  - `session_id` (str): Session identifier


  **Returns:** Optional[WorkState]
    WorkState if found, None otherwise


  #### `has_incomplete_work`

  ```python
  has_incomplete_work(self) -> bool
  ```

  Check if there's any incomplete work to resume.

Returns:
    True if there's in-progress or paused work

  **Parameters:**

  - `self`


  **Returns:** bool
    True if there's in-progress or paused work


  #### `get_incomplete_sessions`

  ```python
  get_incomplete_sessions(self, include_stale: bool) -> List[WorkState]
  ```

  Get all incomplete work sessions.

Args:
    include_stale: Include sessions with no activity in 24+ hours

Returns:
    List of WorkState objects for incomplete work

  **Parameters:**

  - `self`
  - `include_stale` (bool) = `False`: Include sessions with no activity in 24+ hours


  **Returns:** List[WorkState]
    List of WorkState objects for incomplete work


  #### `cleanup_stale_sessions`

  ```python
  cleanup_stale_sessions(self, hours: int) -> int
  ```

  Mark stale sessions as abandoned.

Args:
    hours: Consider sessions stale after this many hours of inactivity

Returns:
    Number of sessions marked as abandoned

  **Parameters:**

  - `self`
  - `hours` (int) = `24`: Consider sessions stale after this many hours of inactivity


  **Returns:** int
    Number of sessions marked as abandoned


  #### `get_recent_completed`

  ```python
  get_recent_completed(self, limit: int) -> List[WorkState]
  ```

  Get recently completed work sessions.

Args:
    limit: Maximum number of sessions to return

Returns:
    List of completed WorkState objects

  **Parameters:**

  - `self`
  - `limit` (int) = `10`: Maximum number of sessions to return


  **Returns:** List[WorkState]
    List of completed WorkState objects


  #### `get_statistics`

  ```python
  get_statistics(self) -> Dict[str, Any]
  ```

  Get statistics about work sessions.

Returns:
    Dictionary with counts and metrics

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dictionary with counts and metrics



---
