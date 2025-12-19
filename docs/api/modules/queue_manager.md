# queue_manager

Queue Manager - Handles FIFO queue enforcement for conversations.


## Table of Contents

### Classes
- [QueueManager](#queuemanager)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** pathlib, sqlite3, src, typing


## Classes

### QueueManager

```python
class QueueManager
```

Manages FIFO queue enforcement (70-conversation limit).


**Methods:**

  #### `enforce_fifo_limit`

  ```python
  enforce_fifo_limit(self, tier2_knowledge_graph) -> None
  ```

  Enforce FIFO limit of 70 conversations.
Evicts oldest inactive, non-pinned conversation if at capacity.
Optionally archives to Tier 2 before eviction.

Args:
    tier2_knowledge_graph: Optional Tier 2 instance for auto-archive

  **Parameters:**

  - `self`
  - `tier2_knowledge_graph` = `None`: Optional Tier 2 instance for auto-archive


  **Returns:** None


  #### `get_eviction_log`

  ```python
  get_eviction_log(self) -> List[Dict[str, Any]]
  ```

  Get the eviction log.

  **Parameters:**

  - `self`


  **Returns:** List[Dict[str, Any]]


  #### `get_queue_status`

  ```python
  get_queue_status(self) -> Dict[str, Any]
  ```

  Get current queue status.

Returns:
    Dict with queue statistics

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict with queue statistics



---
