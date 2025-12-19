# temporal_correlator

CORTEX 3.0 Milestone 2 - Temporal Correlation Layer

Implements the fusion layer that cross-references conversations with daemon events
to create complete development narratives. This is the core component of
dual-channel memory that links strategic discussions with tactical execution.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms


## Table of Contents

### Classes
- [CorrelationResult](#correlationresult)
- [ConversationTurn](#conversationturn)
- [AmbientEvent](#ambientevent)
- [TemporalCorrelator](#temporalcorrelator)


## Overview

- **Classes:** 4
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, json, logging, pathlib, re, sqlite3, typing


## Classes

### CorrelationResult

```python
class CorrelationResult
```

**Decorators:** `dataclass`

Result of temporal correlation between conversation and event.


**Attributes:**

- `conversation_id`: str
- `event_id`: int
- `correlation_type`: str
- `confidence_score`: float
- `time_diff_seconds`: int
- `match_details`: Dict[str, Any]



---

### ConversationTurn

```python
class ConversationTurn
```

**Decorators:** `dataclass`

Represents a single conversation turn for correlation.


**Attributes:**

- `turn_id`: str
- `conversation_id`: str
- `content`: str
- `timestamp`: datetime
- `files_mentioned`: List[str]
- `phases_mentioned`: List[str]



---

### AmbientEvent

```python
class AmbientEvent
```

**Decorators:** `dataclass`

Represents an ambient daemon event for correlation.


**Attributes:**

- `event_id`: int
- `session_id`: str
- `event_type`: str
- `file_path`: Optional[str]
- `timestamp`: datetime
- `pattern`: Optional[str]
- `score`: Optional[int]
- `summary`: str
- `metadata`: Dict[str, Any]



---

### TemporalCorrelator

```python
class TemporalCorrelator
```

Core temporal correlation algorithm for CORTEX 3.0 dual-channel memory.

Matches conversation turns with ambient daemon events using:
1. Temporal proximity (±1 hour window)
2. File mention matching (backtick paths in conversations)
3. Plan verification (multi-phase tracking)


**Methods:**

  #### `correlate_conversation`

  ```python
  correlate_conversation(self, conversation_id: str, force_recalculate: bool) -> List[CorrelationResult]
  ```

  Find temporal correlations for a conversation with ambient events.

Args:
    conversation_id: ID of imported conversation to correlate
    force_recalculate: If True, recalculate even if correlations exist
    
Returns:
    List of correlation results ordered by confidence score

  **Parameters:**

  - `self`
  - `conversation_id` (str): ID of imported conversation to correlate
  - `force_recalculate` (bool) = `False`: If True, recalculate even if correlations exist


  **Returns:** List[CorrelationResult]
    List of correlation results ordered by confidence score


  #### `get_conversation_timeline`

  ```python
  get_conversation_timeline(self, conversation_id: str) -> Dict[str, Any]
  ```

  Generate a unified timeline of conversation turns and correlated events.

Args:
    conversation_id: ID of conversation to analyze
    
Returns:
    Timeline data with conversation turns and correlated events

  **Parameters:**

  - `self`
  - `conversation_id` (str): ID of conversation to analyze


  **Returns:** Dict[str, Any]
    Timeline data with conversation turns and correlated events



---
