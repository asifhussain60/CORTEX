# message_store

Message Store - Handles message storage and retrieval operations.


## Table of Contents

### Classes
- [MessageStore](#messagestore)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** pathlib, sqlite3, typing


## Classes

### MessageStore

```python
class MessageStore
```

Manages message storage and retrieval.


**Methods:**

  #### `add_messages`

  ```python
  add_messages(self, conversation_id: str, messages: List[Dict[str, str]]) -> None
  ```

  Add messages to a conversation.

Args:
    conversation_id: Conversation to add messages to
    messages: List of message dicts with 'role' and 'content'

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation to add messages to
  - `messages` (List[Dict[str, str]]): List of message dicts with 'role' and 'content'


  **Returns:** None


  #### `get_messages`

  ```python
  get_messages(self, conversation_id: str) -> List[Dict[str, Any]]
  ```

  Get all messages for a conversation.

Args:
    conversation_id: Conversation identifier

Returns:
    List of message dicts with role, content, timestamp

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation identifier


  **Returns:** List[Dict[str, Any]]
    List of message dicts with role, content, timestamp


  #### `get_message_count`

  ```python
  get_message_count(self, conversation_id: str) -> int
  ```

  Get the number of messages in a conversation.

Args:
    conversation_id: Conversation identifier

Returns:
    Number of messages

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation identifier


  **Returns:** int
    Number of messages


  #### `delete_messages`

  ```python
  delete_messages(self, conversation_id: str) -> None
  ```

  Delete all messages for a conversation.

Args:
    conversation_id: Conversation identifier

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation identifier


  **Returns:** None



---
