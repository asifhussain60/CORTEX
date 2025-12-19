# entity_extractor

Entity Extractor - Handles entity extraction from conversation content.


## Table of Contents

### Classes
- [EntityType](#entitytype)
- [Entity](#entity)
- [EntityExtractor](#entityextractor)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, enum, pathlib, re, sqlite3, typing


## Classes

### EntityType

```python
class EntityType(Enum)
```

Types of entities that can be extracted.



---

### Entity

```python
class Entity
```

**Decorators:** `dataclass`

Represents an extracted entity.


**Attributes:**

- `id`: int
- `entity_type`: EntityType
- `entity_name`: str
- `file_path`: Optional[str]
- `first_seen`: datetime
- `last_accessed`: datetime
- `access_count`: int



---

### EntityExtractor

```python
class EntityExtractor
```

Extracts and manages entities from conversations.


**Methods:**

  #### `extract_entities`

  ```python
  extract_entities(self, conversation_id: str, text: str) -> List[Entity]
  ```

  Extract entities from text.

Args:
    conversation_id: Conversation to link entities to
    text: Text to extract entities from

Returns:
    List of extracted Entity objects

  **Parameters:**

  - `self`
  - `conversation_id` (str): Conversation to link entities to
  - `text` (str): Text to extract entities from


  **Returns:** List[Entity]
    List of extracted Entity objects


  #### `get_conversation_entities`

  ```python
  get_conversation_entities(self, conversation_id: str) -> List[Entity]
  ```

  Get all entities associated with a conversation.

  **Parameters:**

  - `self`
  - `conversation_id` (str)


  **Returns:** List[Entity]


  #### `get_entity_statistics`

  ```python
  get_entity_statistics(self) -> List[Dict[str, Any]]
  ```

  Get statistics on entity usage.

  **Parameters:**

  - `self`


  **Returns:** List[Dict[str, Any]]



---
