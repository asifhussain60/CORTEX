# import_handler

Conversation Import Handler (Feature 5 - Phase 1: Manual Capture)

Handles the second step of two-step conversation capture workflow:
1. User has created file with /CORTEX Capture and pasted conversation
2. User says "/CORTEX Import this conversation"
3. This handler reads the file
4. Parses conversation structure (Track A pipeline)
5. Imports to Tier 1 SQLite database
6. Updates Tier 2 knowledge graph
7. Returns import statistics

Part of CORTEX 3.0 Track 1 - Feature 5: Conversation Tracking & Capture
Roadmap: cortex-brain/cortex-3.0-design/CORTEX-3.0-ROADMAP.yaml

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0.0


## Table of Contents

### Classes
- [ConversationImportHandler](#conversationimporthandler)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, logging, pathlib, re, typing


## Classes

### ConversationImportHandler

```python
class ConversationImportHandler
```

Handles conversation import from captured markdown files.

Reads markdown file from conversation-captures directory, parses
conversation structure, and imports to CORTEX brain (Tier 1 SQLite
+ Tier 2 knowledge graph).

Workflow:
    1. User triggers "/CORTEX Import this conversation"
    2. Find most recent pending capture file
    3. Read and parse conversation content
    4. Extract metadata, messages, entities
    5. Call Track A import pipeline
    6. Update Tier 1 working memory
    7. Extract patterns for Tier 2 knowledge graph
    8. Return import statistics

Usage:
    handler = ConversationImportHandler(
        cortex_brain_path,
        working_memory,
        knowledge_graph
    )
    result = handler.import_conversation(file_path="20251116-roadmap.md")
    
    # Returns: {
    #   "success": True,
    #   "conversation_id": "conv-20251116-143052",
    #   "messages_imported": 15,
    #   "entities_tracked": 3,
    #   "quality_score": 8.5
    # }


**Methods:**

  #### `import_conversation`

  ```python
  import_conversation(self, file_path: Optional[str], auto_detect: bool) -> Dict[str, Any]
  ```

  Import conversation from markdown file to CORTEX brain.

Args:
    file_path: Specific file to import (filename or relative path)
    auto_detect: If True and file_path is None, import most recent pending file

Returns:
    Dict with:
        - success: bool
        - conversation_id: str (generated ID)
        - file_path: str (file that was imported)
        - messages_imported: int
        - entities_tracked: int
        - quality_score: float (if calculable)
        - message: str (user-facing message)
        - timestamp: str (import timestamp)

  **Parameters:**

  - `self`
  - `file_path` (Optional[str]) = `None`: Specific file to import (filename or relative path)
  - `auto_detect` (bool) = `True`: If True and file_path is None, import most recent pending file


  **Returns:** Dict[str, Any]
    Dict with: - success: bool - conversation_id: str (generated ID) - file_path: str (file that was imported) - messages_imported: int - entities_tracked: int - quality_score: float (if calculable) - message: str (user-facing message) - timestamp: str (import timestamp)



---
