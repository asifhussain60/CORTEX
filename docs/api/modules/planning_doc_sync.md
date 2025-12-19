# planning_doc_sync

CORTEX Tier 1: Planning Document Sync Engine
Auto-synchronizes SQLite conversation state to markdown planning documents

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary


## Table of Contents

### Classes
- [PlanningDocSyncEngine](#planningdocsyncengine)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, jinja2, json, logging, pathlib, src, typing


## Classes

### PlanningDocSyncEngine

```python
class PlanningDocSyncEngine
```

Synchronizes SQLite conversation state to markdown planning documents

Architecture:
    SQLite (Source of Truth) → Sync Engine → Markdown (User Projection)

Features:
    - Template-based rendering (Jinja2)
    - Auto-sync on conversation events
    - Progress tracking
    - Entity summaries
    - Recent message history

Usage:
    sync_engine = PlanningDocSyncEngine()
    sync_engine.sync_planning_doc(conversation_id="conv-001")


**Methods:**

  #### `sync_planning_doc`

  ```python
  sync_planning_doc(self, conversation_id: str, conversation_manager, force: bool) -> Optional[Path]
  ```

  Regenerate planning document from SQLite conversation state

Args:
    conversation_id: Conversation to sync
    conversation_manager: ConversationManager instance
    force: Force regeneration even if unchanged
    
Returns:
    Path to generated planning document or None if no planning doc associated

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation to sync
  - `conversation_manager`: ConversationManager instance
  - `force` (bool) = `False`: Force regeneration even if unchanged


  **Returns:** Optional[Path]
    Path to generated planning document or None if no planning doc associated



---
