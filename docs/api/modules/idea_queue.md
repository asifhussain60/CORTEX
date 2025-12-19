# idea_queue

CORTEX 3.0 - Feature 1: IDEA Capture System - Core Queue

Purpose: Ultra-fast (<5ms) capture of fleeting ideas during active work with
         zero disruption to ongoing operations. SQLite-backed persistence
         with async enrichment.

Architecture:
- Instant capture: <5ms append-only SQLite write
- Zero disruption: Work continues immediately after capture
- Async enrichment: Component detection, priority inference, clustering
- Context preservation: Active file, operation, conversation tracking
- Cross-repository: Projects across multiple repos

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms


## Table of Contents

### Classes
- [IdeaCapture](#ideacapture)
- [IdeaQueue](#ideaqueue)

### Functions
- [create_idea_queue](#create_idea_queue)


## Overview

- **Classes:** 2
- **Functions:** 1
- **Dependencies:** dataclasses, datetime, json, logging, pathlib, re, sqlite3, threading, time, typing, uuid


## Classes

### IdeaCapture

```python
class IdeaCapture
```

**Decorators:** `dataclass`

Single captured idea with instant context and async enrichment.


**Attributes:**

- `idea_id`: str
- `raw_text`: str
- `timestamp`: datetime
- `active_file`: Optional[str]
- `active_line`: Optional[int]
- `active_operation`: Optional[str]
- `conversation_id`: Optional[str]
- `project`: Optional[str]
- `component`: Optional[str]
- `priority`: Optional[str]
- `related_ideas`: List[str]
- `status`: str
- `created_at`: datetime
- `updated_at`: datetime


**Methods:**


---

### IdeaQueue

```python
class IdeaQueue
```

Ultra-fast idea capture queue with SQLite persistence.

Performance Goals:
- Capture: <5ms (critical path)
- Retrieval: <50ms for typical queries
- Enrichment: Async (zero impact on capture)

Design Principles:
- Append-only for maximum speed
- Minimal validation during capture
- Rich functionality in async background processing


**Methods:**

  #### `capture`

  ```python
  capture(self, raw_text: str, context: Optional[Dict[str, Any]]) -> str
  ```

  Capture idea with <5ms performance guarantee.

Args:
    raw_text: User's exact input text
    context: Optional context dict with current state
    
Returns:
    idea_id: UUID for tracking the captured idea
    
Raises:
    PerformanceError: If capture exceeds max_capture_ms

  **Parameters:**

  - `self`
  - `raw_text` (str): User's exact input text
  - `context` (Optional[Dict[str, Any]]) = `None`: Optional context dict with current state


  **Returns:** str
    idea_id: UUID for tracking the captured idea


  #### `get_all_ideas`

  ```python
  get_all_ideas(self, status_filter: Optional[str], limit: Optional[int]) -> List[IdeaCapture]
  ```

  Retrieve all ideas with optional filtering.

Args:
    status_filter: Filter by status (pending, completed, etc.)
    limit: Maximum number of ideas to return
    
Returns:
    List of IdeaCapture objects

  **Parameters:**

  - `self`
  - `status_filter` (Optional[str]) = `None`: Filter by status (pending, completed, etc.)
  - `limit` (Optional[int]) = `None`: Maximum number of ideas to return


  **Returns:** List[IdeaCapture]
    List of IdeaCapture objects


  #### `filter_by_component`

  ```python
  filter_by_component(self, component: str) -> List[IdeaCapture]
  ```

  Filter ideas by component (auth, api, ui, etc.).

  **Parameters:**

  - `self`
  - `component` (str)


  **Returns:** List[IdeaCapture]


  #### `filter_by_project`

  ```python
  filter_by_project(self, project: str) -> List[IdeaCapture]
  ```

  Filter ideas by project/repository.

  **Parameters:**

  - `self`
  - `project` (str)


  **Returns:** List[IdeaCapture]


  #### `get_idea`

  ```python
  get_idea(self, idea_id: str) -> Optional[IdeaCapture]
  ```

  Get specific idea by ID.

  **Parameters:**

  - `self`
  - `idea_id` (str)


  **Returns:** Optional[IdeaCapture]


  #### `complete_idea`

  ```python
  complete_idea(self, idea_id: str) -> bool
  ```

  Mark idea as completed.

  **Parameters:**

  - `self`
  - `idea_id` (str)


  **Returns:** bool


  #### `archive_idea`

  ```python
  archive_idea(self, idea_id: str) -> bool
  ```

  Archive idea (remove from active view).

  **Parameters:**

  - `self`
  - `idea_id` (str)


  **Returns:** bool


  #### `update_priority`

  ```python
  update_priority(self, idea_id: str, priority: str) -> bool
  ```

  Update idea priority.

  **Parameters:**

  - `self`
  - `idea_id` (str)
  - `priority` (str)


  **Returns:** bool


  #### `get_performance_stats`

  ```python
  get_performance_stats(self) -> Dict[str, Any]
  ```

  Get performance statistics.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

## Functions

### create_idea_queue

```python
create_idea_queue(config: Optional[Dict[str, Any]]) -> IdeaQueue
```

Factory function to create IdeaQueue with configuration.

Args:
    config: Optional configuration dict
        - db_path: str (custom database path)
        - enable_enrichment: bool (default: True)
        - max_capture_ms: float (default: 5.0)
        
Returns:
    Configured IdeaQueue instance


**Parameters:**

- `config` (Optional[Dict[str, Any]]) = `None`: Optional configuration dict


**Returns:** IdeaQueue
  Configured IdeaQueue instance


---
