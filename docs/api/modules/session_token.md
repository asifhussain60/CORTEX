# session_token

CORTEX Tier 1: Session Token Manager
Provides persistent conversation IDs across chat restarts.

Purpose:
- Generate unique, persistent session tokens
- Store token associations with conversations
- Enable "continue" to resume the exact same conversation
- Track session lifecycle (active, paused, completed)
- Bridge chat restarts with continuous context

Usage:
    from src.tier1.session_token import SessionTokenManager
    
    stm = SessionTokenManager()
    
    # Start a new session
    token = stm.create_session("Implementing auth feature")
    print(f"Session Token: {token}")  # SESSION_20251108_143022_a7b3
    
    # Record conversation association
    stm.associate_conversation(token, "github_copilot_conv_12345")
    
    # Later (even after restart)
    session = stm.get_active_session()
    if session:
        print(f"Resume: {session.description}")
        print(f"Conversation ID: {session.conversation_id}")
    
    # End session
    stm.complete_session(token)


## Table of Contents

### Classes
- [SessionStatus](#sessionstatus)
- [Session](#session)
- [SessionTokenManager](#sessiontokenmanager)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, enum, pathlib, secrets, sqlite3, typing


## Classes

### SessionStatus

```python
class SessionStatus(Enum)
```

Status of a session.



---

### Session

```python
class Session
```

**Decorators:** `dataclass`

Represents a persistent session.


**Attributes:**

- `token`: str
- `description`: str
- `status`: SessionStatus
- `created_at`: datetime
- `last_activity`: datetime
- `conversation_id`: Optional[str]
- `work_session_id`: Optional[str]
- `metadata`: Dict[str, Any]


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert to dictionary.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]


  #### `is_stale`

  ```python
  is_stale(self, hours: int) -> bool
  ```

  Check if session is stale.

  **Parameters:**

  - `self`
  - `hours` (int) = `24`


  **Returns:** bool


  #### `age_hours`

  ```python
  age_hours(self) -> float
  ```

  Get session age in hours.

  **Parameters:**

  - `self`


  **Returns:** float



---

### SessionTokenManager

```python
class SessionTokenManager
```

Manages persistent session tokens for conversation continuity.

Features:
- Generate unique session tokens
- Track session lifecycle
- Associate with conversations and work sessions
- Auto-expire stale sessions
- Enable seamless resume across restarts


**Methods:**

  #### `create_session`

  ```python
  create_session(self, description: str, conversation_id: Optional[str], work_session_id: Optional[str], metadata: Optional[Dict[str, Any]]) -> str
  ```

  Create a new session token.

Args:
    description: Human-readable session description
    conversation_id: Optional conversation ID to associate
    work_session_id: Optional work session ID to link
    metadata: Additional context

Returns:
    token: Unique session token (e.g., SESSION_20251108_143022_a7b3)

  **Parameters:**

  - `self`
  - `description` (str): Human-readable session description
  - `conversation_id` (Optional[str]) = `None`: Optional conversation ID to associate
  - `work_session_id` (Optional[str]) = `None`: Optional work session ID to link
  - `metadata` (Optional[Dict[str, Any]]) = `None`: Additional context


  **Returns:** str
    token: Unique session token (e.g., SESSION_20251108_143022_a7b3)


  #### `get_session`

  ```python
  get_session(self, token: str) -> Optional[Session]
  ```

  Retrieve session by token.

Args:
    token: Session token

Returns:
    Session if found, None otherwise

  **Parameters:**

  - `self`
  - `token` (str): Session token


  **Returns:** Optional[Session]
    Session if found, None otherwise


  #### `get_active_session`

  ```python
  get_active_session(self) -> Optional[Session]
  ```

  Get the most recent active session.

Returns:
    Active Session if exists, None otherwise

  **Parameters:**

  - `self`


  **Returns:** Optional[Session]
    Active Session if exists, None otherwise


  #### `associate_conversation`

  ```python
  associate_conversation(self, token: str, conversation_id: str) -> None
  ```

  Associate a conversation ID with a session token.

Args:
    token: Session token
    conversation_id: Conversation identifier from chat system

  **Parameters:**

  - `self`
  - `token` (str): Session token
  - `conversation_id` (str): Conversation identifier from chat system


  **Returns:** None


  #### `associate_work_session`

  ```python
  associate_work_session(self, token: str, work_session_id: str) -> None
  ```

  Associate a work session ID with a session token.

Args:
    token: Session token
    work_session_id: Work session identifier from WorkStateManager

  **Parameters:**

  - `self`
  - `token` (str): Session token
  - `work_session_id` (str): Work session identifier from WorkStateManager


  **Returns:** None


  #### `update_activity`

  ```python
  update_activity(self, token: str) -> None
  ```

  Update last activity timestamp for a session.

Args:
    token: Session token

  **Parameters:**

  - `self`
  - `token` (str): Session token


  **Returns:** None


  #### `pause_session`

  ```python
  pause_session(self, token: str) -> None
  ```

  Pause a session (context switch).

Args:
    token: Session token

  **Parameters:**

  - `self`
  - `token` (str): Session token


  **Returns:** None


  #### `resume_session`

  ```python
  resume_session(self, token: str) -> None
  ```

  Resume a paused session.

Args:
    token: Session token

  **Parameters:**

  - `self`
  - `token` (str): Session token


  **Returns:** None


  #### `complete_session`

  ```python
  complete_session(self, token: str) -> None
  ```

  Mark session as completed.

Args:
    token: Session token

  **Parameters:**

  - `self`
  - `token` (str): Session token


  **Returns:** None


  #### `expire_session`

  ```python
  expire_session(self, token: str) -> None
  ```

  Mark session as expired (auto-cleanup).

Args:
    token: Session token

  **Parameters:**

  - `self`
  - `token` (str): Session token


  **Returns:** None


  #### `get_all_active_sessions`

  ```python
  get_all_active_sessions(self) -> List[Session]
  ```

  Get all active sessions.

Returns:
    List of active Session objects

  **Parameters:**

  - `self`


  **Returns:** List[Session]
    List of active Session objects


  #### `cleanup_stale_sessions`

  ```python
  cleanup_stale_sessions(self, hours: int) -> int
  ```

  Expire stale sessions.

Args:
    hours: Consider sessions stale after this many hours

Returns:
    Number of sessions expired

  **Parameters:**

  - `self`
  - `hours` (int) = `24`: Consider sessions stale after this many hours


  **Returns:** int
    Number of sessions expired


  #### `find_by_conversation`

  ```python
  find_by_conversation(self, conversation_id: str) -> Optional[Session]
  ```

  Find session by conversation ID.

Args:
    conversation_id: Conversation identifier

Returns:
    Session if found, None otherwise

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation identifier


  **Returns:** Optional[Session]
    Session if found, None otherwise


  #### `find_by_work_session`

  ```python
  find_by_work_session(self, work_session_id: str) -> Optional[Session]
  ```

  Find session by work session ID.

Args:
    work_session_id: Work session identifier

Returns:
    Session if found, None otherwise

  **Parameters:**

  - `self`
  - `work_session_id` (str): Work session identifier


  **Returns:** Optional[Session]
    Session if found, None otherwise


  #### `get_statistics`

  ```python
  get_statistics(self) -> Dict[str, Any]
  ```

  Get statistics about sessions.

Returns:
    Dictionary with counts and metrics

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dictionary with counts and metrics



---
