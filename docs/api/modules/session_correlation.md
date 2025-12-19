# session_correlation

CORTEX 3.0 - Session-Ambient Correlation Layer

Links session-based conversations with ambient capture events to create
complete development narratives.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms


## Table of Contents

### Classes
- [SessionAmbientCorrelator](#sessionambientcorrelator)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, json, logging, pathlib, sqlite3, typing


## Classes

### SessionAmbientCorrelator

```python
class SessionAmbientCorrelator
```

Correlates session-based conversations with ambient capture events.


**Methods:**

  #### `log_ambient_event`

  ```python
  log_ambient_event(self, session_id: str, event_type: str, file_path: Optional[str], pattern: Optional[str], score: Optional[int], summary: Optional[str], conversation_id: Optional[str], metadata: Optional[Dict[str, Any]]) -> int
  ```

  Log ambient capture event linked to session.

Args:
    session_id: Active workspace session ID
    event_type: Type of event (file_change, terminal_command, git_operation)
    file_path: Path to affected file
    pattern: Detected pattern (FEATURE, BUGFIX, etc.)
    score: Activity score (0-100)
    summary: Natural language summary
    conversation_id: Optional active conversation ID
    metadata: Additional event metadata
    
Returns:
    Event ID

  **Parameters:**

  - `self`
  - `session_id` (str): Active workspace session ID
  - `event_type` (str): Type of event (file_change, terminal_command, git_operation)
  - `file_path` (Optional[str]) = `None`: Path to affected file
  - `pattern` (Optional[str]) = `None`: Detected pattern (FEATURE, BUGFIX, etc.)
  - `score` (Optional[int]) = `None`: Activity score (0-100)
  - `summary` (Optional[str]) = `None`: Natural language summary
  - `conversation_id` (Optional[str]) = `None`: Optional active conversation ID
  - `metadata` (Optional[Dict[str, Any]]) = `None`: Additional event metadata


  **Returns:** int
    Event ID


  #### `get_session_events`

  ```python
  get_session_events(self, session_id: str, event_type: Optional[str], min_score: Optional[int]) -> List[Dict[str, Any]]
  ```

  Get all ambient events for a session.

Args:
    session_id: Session ID to query
    event_type: Optional filter by event type
    min_score: Optional minimum activity score
    
Returns:
    List of events with metadata

  **Parameters:**

  - `self`
  - `session_id` (str): Session ID to query
  - `event_type` (Optional[str]) = `None`: Optional filter by event type
  - `min_score` (Optional[int]) = `None`: Optional minimum activity score


  **Returns:** List[Dict[str, Any]]
    List of events with metadata


  #### `get_conversation_events`

  ```python
  get_conversation_events(self, conversation_id: str) -> List[Dict[str, Any]]
  ```

  Get all ambient events that occurred during a conversation.

Args:
    conversation_id: Conversation ID to query
    
Returns:
    List of events with metadata

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation ID to query


  **Returns:** List[Dict[str, Any]]
    List of events with metadata


  #### `generate_session_narrative`

  ```python
  generate_session_narrative(self, session_id: str) -> str
  ```

  Generate complete development narrative for a session.

Combines conversations + ambient events into coherent story.

Args:
    session_id: Session ID to narrate
    
Returns:
    Natural language narrative

  **Parameters:**

  - `self`
  - `session_id` (str): Session ID to narrate


  **Returns:** str
    Natural language narrative



---
