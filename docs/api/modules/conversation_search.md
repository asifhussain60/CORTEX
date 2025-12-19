# conversation_search

Conversation Search - Handles conversation search operations.


## Table of Contents

### Classes
- [ConversationSearch](#conversationsearch)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** conversation_manager, datetime, pathlib, sqlite3, typing


## Classes

### ConversationSearch

```python
class ConversationSearch
```

Handles conversation search functionality.


**Methods:**

  #### `search_by_keyword`

  ```python
  search_by_keyword(self, keyword: str) -> List[Conversation]
  ```

  Search conversations by keyword in title or messages.

Args:
    keyword: Search keyword

Returns:
    List of matching Conversation objects

  **Parameters:**

  - `self`
  - `keyword` (str): Search keyword


  **Returns:** List[Conversation]
    List of matching Conversation objects


  #### `search_by_date_range`

  ```python
  search_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Conversation]
  ```

  Get conversations within a date range.

Args:
    start_date: Start of date range
    end_date: End of date range

Returns:
    List of Conversation objects

  **Parameters:**

  - `self`
  - `start_date` (datetime): Start of date range
  - `end_date` (datetime): End of date range


  **Returns:** List[Conversation]
    List of Conversation objects


  #### `search_by_entity`

  ```python
  search_by_entity(self, entity_type: str, entity_name: str) -> List[Conversation]
  ```

  Find conversations that mention a specific entity.

Args:
    entity_type: Type of entity (file, class, method, etc.)
    entity_name: Name of entity

Returns:
    List of Conversation objects

  **Parameters:**

  - `self`
  - `entity_type` (str): Type of entity (file, class, method, etc.)
  - `entity_name` (str): Name of entity


  **Returns:** List[Conversation]
    List of Conversation objects



---
