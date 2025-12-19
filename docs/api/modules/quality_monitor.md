# quality_monitor

CORTEX 3.0 - Real-Time Conversation Quality Monitor

Purpose: Monitor conversation quality in real-time to detect valuable conversations
         worthy of capture. Integrates with Smart Hint system to prompt users.

Architecture:
- Tracks conversation turns in real-time
- Analyzes quality using ConversationQualityAnalyzer
- Detects valuable conversations (≥7/10 quality score)
- Triggers Smart Hint generation when threshold met
- Learns from user acceptance/rejection patterns

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms


## Table of Contents

### Classes
- [ConversationTurn](#conversationturn)
- [MonitoringSession](#monitoringsession)
- [QualityMonitor](#qualitymonitor)

### Functions
- [create_monitor](#create_monitor)


## Overview

- **Classes:** 3
- **Functions:** 1
- **Dependencies:** dataclasses, datetime, logging, pathlib, src, typing


## Classes

### ConversationTurn

```python
class ConversationTurn
```

**Decorators:** `dataclass`

A single conversation turn (user + assistant).


**Attributes:**

- `user_message`: str
- `assistant_response`: str
- `timestamp`: datetime
- `turn_number`: int



---

### MonitoringSession

```python
class MonitoringSession
```

**Decorators:** `dataclass`

Active conversation monitoring session.


**Attributes:**

- `session_id`: str
- `turns`: List[ConversationTurn]
- `started_at`: datetime
- `last_quality_check`: Optional[QualityScore]
- `hint_shown`: bool
- `user_response`: Optional[str]



---

### QualityMonitor

```python
class QualityMonitor
```

Real-time conversation quality monitor.

Detects valuable conversations and triggers Smart Hint prompts.

Quality Thresholds:
- EXCELLENT (≥19 points): Exceptional strategic value
- GOOD (≥10 points): Solid strategic conversation
- FAIR (≥2 points): Some value
- LOW (<2 points): Minimal strategic content

Default hint threshold: GOOD (≥10 points, maps to ~7/10 in roadmap docs)


**Methods:**

  #### `start_session`

  ```python
  start_session(self, session_id: Optional[str]) -> str
  ```

  Start a new monitoring session.

Args:
    session_id: Optional custom session ID
    
Returns:
    Session ID

  **Parameters:**

  - `self`
  - `session_id` (Optional[str]) = `None`: Optional custom session ID


  **Returns:** str
    Session ID


  #### `add_turn`

  ```python
  add_turn(self, user_message: str, assistant_response: str) -> Dict[str, Any]
  ```

  Add a conversation turn and check quality.

Args:
    user_message: User's input
    assistant_response: CORTEX's response
    
Returns:
    Dict with quality analysis and hint recommendation

  **Parameters:**

  - `self`
  - `user_message` (str): User's input
  - `assistant_response` (str): CORTEX's response


  **Returns:** Dict[str, Any]
    Dict with quality analysis and hint recommendation


  #### `record_user_response`

  ```python
  record_user_response(self, response: str) -> None
  ```

  Record user's response to Smart Hint.

Args:
    response: 'accepted', 'rejected', or 'ignored'

  **Parameters:**

  - `self`
  - `response` (str): 'accepted', 'rejected', or 'ignored'


  **Returns:** None


  #### `end_session`

  ```python
  end_session(self) -> Optional[MonitoringSession]
  ```

  End current monitoring session.

Returns:
    Completed session or None if no active session

  **Parameters:**

  - `self`


  **Returns:** Optional[MonitoringSession]
    Completed session or None if no active session


  #### `get_current_quality`

  ```python
  get_current_quality(self) -> Optional[QualityScore]
  ```

  Get current session's quality score.

Returns:
    Latest quality score or None if no session

  **Parameters:**

  - `self`


  **Returns:** Optional[QualityScore]
    Latest quality score or None if no session


  #### `get_session_stats`

  ```python
  get_session_stats(self) -> Dict[str, Any]
  ```

  Get statistics about monitoring sessions.

Returns:
    Dict with session statistics

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict with session statistics



---

## Functions

### create_monitor

```python
create_monitor(config: Optional[Dict[str, Any]]) -> QualityMonitor
```

Factory function to create quality monitor.

Args:
    config: Optional configuration dict
        - min_turns_before_check: int (default: 5)
        - quality_threshold: str (default: "GOOD")
        
Returns:
    Configured QualityMonitor instance


**Parameters:**

- `config` (Optional[Dict[str, Any]]) = `None`: Optional configuration dict


**Returns:** QualityMonitor
  Configured QualityMonitor instance


---
