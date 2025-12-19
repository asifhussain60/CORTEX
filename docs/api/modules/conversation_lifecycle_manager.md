# conversation_lifecycle_manager

Conversation Lifecycle Manager - Handles conversation creation, workflow tracking, and closure.

Implements CORTEX 3.0 session-based conversation lifecycle:
- Auto-creates conversations on session start
- Tracks workflow state progression
- Auto-closes conversations on workflow completion
- Detects explicit user commands (new conversation, continue)


## Table of Contents

### Classes
- [WorkflowState](#workflowstate)
- [ConversationLifecycleEvent](#conversationlifecycleevent)
- [ConversationLifecycleManager](#conversationlifecyclemanager)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, enum, pathlib, re, sqlite3, typing


## Classes

### WorkflowState

```python
class WorkflowState(Enum)
```

Workflow states for conversation progression.



---

### ConversationLifecycleEvent

```python
class ConversationLifecycleEvent
```

**Decorators:** `dataclass`

Represents a lifecycle event for a conversation.


**Attributes:**

- `event_type`: str
- `conversation_id`: str
- `session_id`: str
- `timestamp`: datetime
- `old_state`: Optional[str]
- `new_state`: Optional[str]
- `trigger`: str



---

### ConversationLifecycleManager

```python
class ConversationLifecycleManager
```

Manages conversation lifecycle within sessions.


**Methods:**

  #### `detect_command_intent`

  ```python
  detect_command_intent(self, user_request: str) -> Tuple[str, float]
  ```

  Detect explicit command intent from user request.

Args:
    user_request: User's message

Returns:
    Tuple of (intent, confidence) where:
        intent: "new_conversation" | "continue" | "none"
        confidence: 0.0-1.0

  **Parameters:**

  - `self`
  - `user_request` (str): User's message


  **Returns:** Tuple[str, float]
    Tuple of (intent, confidence) where: intent: "new_conversation" | "continue" | "none" confidence: 0.0-1.0


  #### `infer_workflow_state`

  ```python
  infer_workflow_state(self, user_request: str, current_state: Optional[WorkflowState]) -> WorkflowState
  ```

  Infer workflow state from user request.

Args:
    user_request: User's message
    current_state: Current workflow state (if any)

Returns:
    Inferred WorkflowState

  **Parameters:**

  - `self`
  - `user_request` (str): User's message
  - `current_state` (Optional[WorkflowState]) = `None`: Current workflow state (if any)


  **Returns:** WorkflowState
    Inferred WorkflowState


  #### `should_create_conversation`

  ```python
  should_create_conversation(self, session_id: str, user_request: str, has_active_conversation: bool) -> Tuple[bool, str]
  ```

  Determine if new conversation should be created.

Args:
    session_id: Current session ID
    user_request: User's message
    has_active_conversation: Whether session has active conversation

Returns:
    Tuple of (should_create, reason)

  **Parameters:**

  - `self`
  - `session_id` (str): Current session ID
  - `user_request` (str): User's message
  - `has_active_conversation` (bool): Whether session has active conversation


  **Returns:** Tuple[bool, str]
    Tuple of (should_create, reason)


  #### `should_close_conversation`

  ```python
  should_close_conversation(self, conversation_id: str, current_state: WorkflowState, user_request: Optional[str]) -> Tuple[bool, str]
  ```

  Determine if conversation should be closed.

Args:
    conversation_id: Conversation to check
    current_state: Current workflow state
    user_request: Optional user message

Returns:
    Tuple of (should_close, reason)

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation to check
  - `current_state` (WorkflowState): Current workflow state
  - `user_request` (Optional[str]) = `None`: Optional user message


  **Returns:** Tuple[bool, str]
    Tuple of (should_close, reason)


  #### `update_workflow_state`

  ```python
  update_workflow_state(self, conversation_id: str, session_id: str, new_state: WorkflowState, trigger: str) -> None
  ```

  Update conversation workflow state.

Args:
    conversation_id: Conversation to update
    session_id: Associated session
    new_state: New workflow state
    trigger: What triggered the update

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation to update
  - `session_id` (str): Associated session
  - `new_state` (WorkflowState): New workflow state
  - `trigger` (str) = `'auto'`: What triggered the update


  **Returns:** None


  #### `close_conversation`

  ```python
  close_conversation(self, conversation_id: str, session_id: str, reason: str, final_state: WorkflowState) -> None
  ```

  Close a conversation.

Args:
    conversation_id: Conversation to close
    session_id: Associated session
    reason: Reason for closure
    final_state: Final workflow state

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation to close
  - `session_id` (str): Associated session
  - `reason` (str): Reason for closure
  - `final_state` (WorkflowState) = `WorkflowState.COMPLETE`: Final workflow state


  **Returns:** None


  #### `log_conversation_created`

  ```python
  log_conversation_created(self, conversation_id: str, session_id: str, trigger: str, initial_state: WorkflowState) -> None
  ```

  Log conversation creation event.

Args:
    conversation_id: Created conversation
    session_id: Associated session
    trigger: What triggered creation
    initial_state: Initial workflow state

  **Parameters:**

  - `self`
  - `conversation_id` (str): Created conversation
  - `session_id` (str): Associated session
  - `trigger` (str): What triggered creation
  - `initial_state` (WorkflowState) = `WorkflowState.PLANNING`: Initial workflow state


  **Returns:** None


  #### `get_conversation_history`

  ```python
  get_conversation_history(self, conversation_id: str) -> List[ConversationLifecycleEvent]
  ```

  Get lifecycle history for a conversation.

Args:
    conversation_id: Conversation to query

Returns:
    List of lifecycle events

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation to query


  **Returns:** List[ConversationLifecycleEvent]
    List of lifecycle events


  #### `get_session_conversation_history`

  ```python
  get_session_conversation_history(self, session_id: str) -> List[ConversationLifecycleEvent]
  ```

  Get all conversation events for a session.

Args:
    session_id: Session to query

Returns:
    List of lifecycle events

  **Parameters:**

  - `self`
  - `session_id` (str): Session to query


  **Returns:** List[ConversationLifecycleEvent]
    List of lifecycle events



---
