# conversation_vault

CORTEX 3.0 - Conversation Vault Manager

Purpose: Manage conversation vault files for manual/automatic capture.
Creates structured markdown files with metadata for easy import to Tier 1.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms


## Table of Contents

### Classes
- [ConversationMetadata](#conversationmetadata)
- [ConversationTurn](#conversationturn)
- [ConversationVaultManager](#conversationvaultmanager)

### Functions
- [create_vault_manager](#create_vault_manager)


## Overview

- **Classes:** 3
- **Functions:** 1
- **Dependencies:** dataclasses, datetime, json, pathlib, typing


## Classes

### ConversationMetadata

```python
class ConversationMetadata
```

**Decorators:** `dataclass`

Metadata for captured conversation.


**Attributes:**

- `conversation_id`: str
- `timestamp`: str
- `quality_score`: int
- `quality_level`: str
- `semantic_elements`: Dict
- `total_turns`: int
- `user_topic`: str



---

### ConversationTurn

```python
class ConversationTurn
```

**Decorators:** `dataclass`

Single turn in a conversation.


**Attributes:**

- `turn_number`: int
- `user_prompt`: str
- `assistant_response`: str
- `timestamp`: str



---

### ConversationVaultManager

```python
class ConversationVaultManager
```

Manages conversation vault files for CORTEX 3.0 hybrid capture.

File Structure:
```
cortex-brain/conversation-vault/
├── 2025-11-13-implement-smart-hints.md
├── 2025-11-13-design-discussion.md
└── metadata/
    ├── conv-20251113-143045.json
    └── conv-20251113-145230.json
```

Each markdown file contains:
- Frontmatter with metadata (YAML)
- Conversation turns (formatted markdown)
- Quality assessment summary
- Import instructions


**Methods:**

  #### `create_conversation_file`

  ```python
  create_conversation_file(self, metadata: ConversationMetadata, turns: List[ConversationTurn], filename: str) -> Path
  ```

  Create conversation file in vault.

Args:
    metadata: Conversation metadata
    turns: List of conversation turns
    filename: Suggested filename
    
Returns:
    Path to created file

  **Parameters:**

  - `self`
  - `metadata` (ConversationMetadata): Conversation metadata
  - `turns` (List[ConversationTurn]): List of conversation turns
  - `filename` (str): Suggested filename


  **Returns:** Path
    Path to created file


  #### `get_conversation_by_id`

  ```python
  get_conversation_by_id(self, conv_id: str) -> Optional[Path]
  ```

  Find conversation file by ID.

Args:
    conv_id: Conversation ID
    
Returns:
    Path to conversation file or None if not found

  **Parameters:**

  - `self`
  - `conv_id` (str): Conversation ID


  **Returns:** Optional[Path]
    Path to conversation file or None if not found


  #### `list_conversations`

  ```python
  list_conversations(self, quality_filter: Optional[str], limit: int) -> List[Dict]
  ```

  List captured conversations with optional filtering.

Args:
    quality_filter: Filter by quality level (EXCELLENT, GOOD, etc.)
    limit: Maximum number to return
    
Returns:
    List of conversation metadata dicts

  **Parameters:**

  - `self`
  - `quality_filter` (Optional[str]) = `None`: Filter by quality level (EXCELLENT, GOOD, etc.)
  - `limit` (int) = `10`: Maximum number to return


  **Returns:** List[Dict]
    List of conversation metadata dicts


  #### `get_vault_stats`

  ```python
  get_vault_stats(self) -> Dict
  ```

  Get statistics about conversation vault.

  **Parameters:**

  - `self`


  **Returns:** Dict



---

## Functions

### create_vault_manager

```python
create_vault_manager(config: Dict) -> ConversationVaultManager
```

Factory function to create vault manager with config.

Args:
    config: Optional configuration dict with 'vault_path' key
    
Returns:
    Configured ConversationVaultManager instance


**Parameters:**

- `config` (Dict) = `None`: Optional configuration dict with 'vault_path' key


**Returns:** ConversationVaultManager
  Configured ConversationVaultManager instance


---
