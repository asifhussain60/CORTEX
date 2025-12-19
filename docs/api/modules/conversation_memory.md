# conversation_memory

CORTEX Tier 1: Conversation Memory
Persistent storage of conversation history using SQLite

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [ConversationMemory](#conversationmemory)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** contextlib, datetime, json, pathlib, sqlite3, src, typing


## Classes

### ConversationMemory

```python
class ConversationMemory
```

Tier 1 Working Memory: Last 20 conversations with FIFO queue

Storage: SQLite database at cortex-brain/tier1/conversations.db
Performance: <50ms per query (target: 18ms actual)


**Methods:**

  #### `store_conversation`

  ```python
  store_conversation(self, user_message: str, assistant_response: str, intent: str, context: Dict[str, Any]) -> str
  ```

  Store a conversation in memory

Args:
    user_message: User's input
    assistant_response: CORTEX response
    intent: Detected intent (PLAN, EXECUTE, etc.)
    context: Additional context (files, entities, etc.)

Returns:
    conversation_id: Unique identifier for this conversation

  **Parameters:**

  - `self`
  - `user_message` (str): User's input
  - `assistant_response` (str) = `None`: CORTEX response
  - `intent` (str) = `None`: Detected intent (PLAN, EXECUTE, etc.)
  - `context` (Dict[str, Any]) = `None`: Additional context (files, entities, etc.)


  **Returns:** str
    conversation_id: Unique identifier for this conversation


  #### `get_conversation`

  ```python
  get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]
  ```

  Retrieve a specific conversation

  **Parameters:**

  - `self`
  - `conversation_id` (str)


  **Returns:** Optional[Dict[str, Any]]


  #### `get_recent_conversations`

  ```python
  get_recent_conversations(self, limit: int) -> List[Dict[str, Any]]
  ```

  Get recent conversations (FIFO queue)

Args:
    limit: Maximum number of conversations (default: 20)

Returns:
    List of conversations ordered by timestamp (newest first)

  **Parameters:**

  - `self`
  - `limit` (int) = `20`: Maximum number of conversations (default: 20)


  **Returns:** List[Dict[str, Any]]
    List of conversations ordered by timestamp (newest first)


  #### `search_conversations`

  ```python
  search_conversations(self, query: str, limit: int) -> List[Dict[str, Any]]
  ```

  Search conversations by text query

Args:
    query: Search string
    limit: Maximum results

Returns:
    Matching conversations

  **Parameters:**

  - `self`
  - `query` (str): Search string
  - `limit` (int) = `10`: Maximum results


  **Returns:** List[Dict[str, Any]]
    Matching conversations


  #### `track_entity`

  ```python
  track_entity(self, conversation_id: str, entity_type: str, entity_value: str, context: str)
  ```

  Track an entity mentioned in conversation

Args:
    conversation_id: Associated conversation
    entity_type: Type (file, class, method, component)
    entity_value: Entity name/value
    context: Additional context

  **Parameters:**

  - `self`
  - `conversation_id` (str): Associated conversation
  - `entity_type` (str): Type (file, class, method, component)
  - `entity_value` (str): Entity name/value
  - `context` (str) = `None`: Additional context


  #### `get_entities`

  ```python
  get_entities(self, conversation_id: str) -> List[Dict[str, Any]]
  ```

  Get all entities for a conversation

  **Parameters:**

  - `self`
  - `conversation_id` (str)


  **Returns:** List[Dict[str, Any]]


  #### `get_queue_status`

  ```python
  get_queue_status(self) -> Dict[str, Any]
  ```

  Get FIFO queue status

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---
