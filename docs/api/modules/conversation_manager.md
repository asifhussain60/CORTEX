# conversation_manager

Conversation Manager - Handles conversation CRUD and lifecycle operations.


## Table of Contents

### Classes
- [Conversation](#conversation)
- [ConversationManager](#conversationmanager)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, json, pathlib, sqlite3, typing


## Classes

### Conversation

```python
class Conversation
```

**Decorators:** `dataclass`

Represents a conversation in working memory.


**Attributes:**

- `conversation_id`: str
- `title`: str
- `created_at`: datetime
- `updated_at`: datetime
- `message_count`: int
- `is_active`: bool
- `summary`: Optional[str]
- `tags`: Optional[List[str]]
- `semantic_elements`: Optional[str]



---

### ConversationManager

```python
class ConversationManager
```

Manages conversation CRUD operations and lifecycle.


**Methods:**

  #### `add_conversation`

  ```python
  add_conversation(self, conversation_id: str, title: str, message_count: int, tags: Optional[List[str]]) -> Conversation
  ```

  Add a new conversation.

Args:
    conversation_id: Unique conversation identifier
    title: Conversation title
    message_count: Initial message count
    tags: Optional list of tags

Returns:
    Created Conversation object

  **Parameters:**

  - `self`
  - `conversation_id` (str): Unique conversation identifier
  - `title` (str): Conversation title
  - `message_count` (int) = `0`: Initial message count
  - `tags` (Optional[List[str]]) = `None`: Optional list of tags


  **Returns:** Conversation
    Created Conversation object


  #### `get_conversation`

  ```python
  get_conversation(self, conversation_id: str) -> Optional[Conversation]
  ```

  Get a conversation by ID.

Args:
    conversation_id: Conversation identifier

Returns:
    Conversation object or None if not found

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation identifier


  **Returns:** Optional[Conversation]
    Conversation object or None if not found


  #### `get_recent_conversations`

  ```python
  get_recent_conversations(self, limit: int) -> List[Conversation]
  ```

  Get recent conversations ordered by creation date (newest first).

Args:
    limit: Maximum number of conversations to return

Returns:
    List of Conversation objects

  **Parameters:**

  - `self`
  - `limit` (int) = `20`: Maximum number of conversations to return


  **Returns:** List[Conversation]
    List of Conversation objects


  #### `set_active_conversation`

  ```python
  set_active_conversation(self, conversation_id: str) -> None
  ```

  Mark a conversation as active (deactivates all others).

Args:
    conversation_id: Conversation to mark as active

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation to mark as active


  **Returns:** None


  #### `get_active_conversation`

  ```python
  get_active_conversation(self) -> Optional[Conversation]
  ```

  Get the currently active conversation.

  **Parameters:**

  - `self`


  **Returns:** Optional[Conversation]


  #### `update_conversation`

  ```python
  update_conversation(self, conversation_id: str, title: Optional[str], summary: Optional[str], tags: Optional[List[str]]) -> None
  ```

  Update conversation properties.

Args:
    conversation_id: Conversation to update
    title: New title (if provided)
    summary: New summary (if provided)
    tags: New tags (if provided)

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation to update
  - `title` (Optional[str]) = `None`: New title (if provided)
  - `summary` (Optional[str]) = `None`: New summary (if provided)
  - `tags` (Optional[List[str]]) = `None`: New tags (if provided)


  **Returns:** None


  #### `increment_message_count`

  ```python
  increment_message_count(self, conversation_id: str, count: int) -> None
  ```

  Increment the message count for a conversation.

Args:
    conversation_id: Conversation to update
    count: Number to increment by

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation to update
  - `count` (int) = `1`: Number to increment by


  **Returns:** None


  #### `get_conversation_count`

  ```python
  get_conversation_count(self) -> int
  ```

  Get the total number of conversations.

  **Parameters:**

  - `self`


  **Returns:** int


  #### `delete_conversation`

  ```python
  delete_conversation(self, conversation_id: str) -> None
  ```

  Delete a conversation and all related data.

Args:
    conversation_id: Conversation to delete

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation to delete


  **Returns:** None



---
