# session_context_manager

Session Context Manager - Automatic Context Continuity
======================================================

Manages active planning sessions and automatic context loading.

Purpose:
- Track active planning sessions
- Automatic context association (no manual file references)
- Session-based context loading
- User never needs to reference temp plan files explicitly

SKULL Enforcement:
- CONTEXT_CONTINUITY_ENFORCEMENT: Automatic context tracking

Author: Asif Hussain
Date: December 17, 2025
Version: 1.0.0


## Table of Contents

### Classes
- [PlanningSession](#planningsession)
- [SessionContextManager](#sessioncontextmanager)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, json, logging, pathlib, src, typing


## Classes

### PlanningSession

```python
class PlanningSession
```

**Decorators:** `dataclass`

Active planning session tracking.


**Attributes:**

- `session_id`: str
- `plan_id`: str
- `user_request`: str
- `created_at`: str
- `last_updated`: str
- `status`: str
- `complexity_tier`: int
- `temp_plan_path`: str
- `iteration_count`: int


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert to dictionary.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]


  #### `from_dict`

  *Decorators:* `classmethod`

  ```python
  from_dict(cls, data: Dict[str, Any]) -> 'PlanningSession'
  ```

  Create from dictionary.

  **Parameters:**

  - `cls`
  - `data` (Dict[str, Any])


  **Returns:** 'PlanningSession'



---

### SessionContextManager

```python
class SessionContextManager
```

Manages automatic context continuity for planning sessions.

Features:
- Automatic session creation
- Context association without manual file references
- Session persistence
- Automatic cleanup

User Experience:
- User: "Add authentication"
  → Creates session-12345, associates with temp-plans/auth/
- User: "Use OAuth for Google"
  → Automatically loads session-12345 context, updates plan
- User: "approve"
  → Closes session, promotes plan

No manual file references needed!


**Methods:**

  #### `create_session`

  ```python
  create_session(self, plan_id: str, user_request: str, complexity_tier: int, temp_plan_path: Path) -> PlanningSession
  ```

  Create new planning session.

Args:
    plan_id: Plan identifier
    user_request: User's original request
    complexity_tier: Complexity tier (1-4)
    temp_plan_path: Path to temp plan folder
    
Returns:
    PlanningSession object

  **Parameters:**

  - `self`
  - `plan_id` (str): Plan identifier
  - `user_request` (str): User's original request
  - `complexity_tier` (int): Complexity tier (1-4)
  - `temp_plan_path` (Path): Path to temp plan folder


  **Returns:** PlanningSession
    PlanningSession object


  #### `get_active_session_for_plan`

  ```python
  get_active_session_for_plan(self, plan_id: str) -> Optional[PlanningSession]
  ```

  Get active session for plan ID.

Args:
    plan_id: Plan identifier
    
Returns:
    PlanningSession if found, None otherwise

  **Parameters:**

  - `self`
  - `plan_id` (str): Plan identifier


  **Returns:** Optional[PlanningSession]
    PlanningSession if found, None otherwise


  #### `update_session`

  ```python
  update_session(self, session_id: str, status: Optional[str], iteration_count: Optional[int])
  ```

  Update session metadata.

Args:
    session_id: Session ID
    status: New status (optional)
    iteration_count: New iteration count (optional)

  **Parameters:**

  - `self`
  - `session_id` (str): Session ID
  - `status` (Optional[str]) = `None`: New status (optional)
  - `iteration_count` (Optional[int]) = `None`: New iteration count (optional)


  #### `close_session`

  ```python
  close_session(self, session_id: str)
  ```

  Close planning session.

Args:
    session_id: Session ID

  **Parameters:**

  - `self`
  - `session_id` (str): Session ID


  #### `get_all_active_sessions`

  ```python
  get_all_active_sessions(self) -> Dict[str, PlanningSession]
  ```

  Get all active sessions.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, PlanningSession]


  #### `load_context_for_request`

  ```python
  load_context_for_request(self, user_request: str) -> Optional[PlanningSession]
  ```

  Automatically load context for user request.

This is the KEY method for automatic context continuity.
When user provides feedback without referencing the plan,
this method finds the active session automatically.

Args:
    user_request: User's new request/feedback
    
Returns:
    PlanningSession if active session found, None otherwise

  **Parameters:**

  - `self`
  - `user_request` (str): User's new request/feedback


  **Returns:** Optional[PlanningSession]
    PlanningSession if active session found, None otherwise



---
