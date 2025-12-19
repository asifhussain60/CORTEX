# session_manager

Session Manager - Handles workspace session lifecycle and boundary detection.

Implements session-based conversation boundaries for CORTEX 3.0 Tier 1.
Sessions map to workspace contexts and provide natural conversation segmentation.


## Table of Contents

### Classes
- [Session](#session)
- [SessionManager](#sessionmanager)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, json, pathlib, sqlite3, typing


## Classes

### Session

```python
class Session
```

**Decorators:** `dataclass`

Represents a workspace session.


**Attributes:**

- `session_id`: str
- `workspace_path`: str
- `start_time`: datetime
- `end_time`: Optional[datetime]
- `conversation_count`: int
- `is_active`: bool
- `last_activity`: datetime



---

### SessionManager

```python
class SessionManager
```

Manages workspace session lifecycle and boundaries.


**Methods:**

  #### `detect_or_create_session`

  ```python
  detect_or_create_session(self, workspace_path: str) -> Session
  ```

  Detect existing active session or create new one.

Creates new session if:
- No active session exists for workspace
- Last activity exceeds idle threshold (>2 hours default)
- Previous session explicitly ended

Args:
    workspace_path: Absolute path to workspace

Returns:
    Active Session object

  **Parameters:**

  - `self`
  - `workspace_path` (str): Absolute path to workspace


  **Returns:** Session
    Active Session object


  #### `get_active_session`

  ```python
  get_active_session(self, workspace_path: str) -> Optional[Session]
  ```

  Get active session for workspace.

Args:
    workspace_path: Absolute path to workspace

Returns:
    Active Session or None

  **Parameters:**

  - `self`
  - `workspace_path` (str): Absolute path to workspace


  **Returns:** Optional[Session]
    Active Session or None


  #### `get_session`

  ```python
  get_session(self, session_id: str) -> Optional[Session]
  ```

  Get session by ID.

Args:
    session_id: Session identifier

Returns:
    Session object or None

  **Parameters:**

  - `self`
  - `session_id` (str): Session identifier


  **Returns:** Optional[Session]
    Session object or None


  #### `end_session`

  ```python
  end_session(self, session_id: str, reason: str) -> None
  ```

  End a session.

Args:
    session_id: Session to end
    reason: Reason for ending (manual, idle_timeout, workspace_close)

  **Parameters:**

  - `self`
  - `session_id` (str): Session to end
  - `reason` (str) = `'manual'`: Reason for ending (manual, idle_timeout, workspace_close)


  **Returns:** None


  #### `increment_conversation_count`

  ```python
  increment_conversation_count(self, session_id: str) -> None
  ```

  Increment conversation count for session.

Args:
    session_id: Session to update

  **Parameters:**

  - `self`
  - `session_id` (str): Session to update


  **Returns:** None


  #### `get_recent_sessions`

  ```python
  get_recent_sessions(self, workspace_path: Optional[str], limit: int) -> List[Session]
  ```

  Get recent sessions.

Args:
    workspace_path: Optional filter by workspace
    limit: Maximum number of sessions

Returns:
    List of Session objects ordered by start time (newest first)

  **Parameters:**

  - `self`
  - `workspace_path` (Optional[str]) = `None`: Optional filter by workspace
  - `limit` (int) = `10`: Maximum number of sessions


  **Returns:** List[Session]
    List of Session objects ordered by start time (newest first)


  #### `cleanup_old_sessions`

  ```python
  cleanup_old_sessions(self, retention_days: int) -> int
  ```

  Cleanup sessions older than retention period.

Args:
    retention_days: Number of days to retain sessions

Returns:
    Number of sessions deleted

  **Parameters:**

  - `self`
  - `retention_days` (int) = `90`: Number of days to retain sessions


  **Returns:** int
    Number of sessions deleted



---
