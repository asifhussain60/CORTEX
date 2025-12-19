# context_linker

CORTEX 3.0 Phase 2 - IDEA Capture System: Context Linker
Ultra-fast idea-to-ecosystem linking system for CORTEX.

Purpose:
    Create intelligent bridges between captured ideas and CORTEX ecosystem:
    - Link ideas to relevant conversations and projects
    - Connect with knowledge graph patterns
    - Associate with active operations
    - Provide context-aware suggestions

Performance Requirements:
    - Context linking: <2ms (average)
    - Context search: <5ms (average)
    - Link resolution: <1ms (average)


## Table of Contents

### Classes
- [ContextLink](#contextlink)
- [ContextMetadata](#contextmetadata)
- [ConversationContextAnalyzer](#conversationcontextanalyzer)
- [KnowledgeGraphLinker](#knowledgegraphlinker)
- [OperationLinker](#operationlinker)
- [IdeaContextLinker](#ideacontextlinker)

### Functions
- [create_context_linker](#create_context_linker)
- [demo_context_linking](#demo_context_linking)


## Overview

- **Classes:** 6
- **Functions:** 2
- **Dependencies:** asyncio, dataclasses, datetime, idea_queue, json, logging, os, pathlib, re, sqlite3, threading, typing, yaml


## Classes

### ContextLink

```python
class ContextLink
```

**Decorators:** `dataclass`

Represents a link between an idea and CORTEX ecosystem context.


**Attributes:**

- `link_id`: str
- `idea_id`: str
- `context_type`: str
- `context_id`: str
- `context_path`: str
- `relevance_score`: float
- `link_reason`: str
- `created_at`: datetime



---

### ContextMetadata

```python
class ContextMetadata
```

**Decorators:** `dataclass`

Metadata about available context sources.


**Attributes:**

- `source_type`: str
- `source_path`: str
- `last_modified`: datetime
- `content_summary`: str
- `keywords`: Set[str]
- `entity_count`: int



---

### ConversationContextAnalyzer

```python
class ConversationContextAnalyzer
```

Analyzes conversation captures for idea linking.


**Methods:**

  #### `find_relevant_conversations`

  ```python
  find_relevant_conversations(self, idea: IdeaCapture, limit: int) -> List[ContextLink]
  ```

  Find conversations relevant to an idea.

  **Parameters:**

  - `self`
  - `idea` (IdeaCapture)
  - `limit` (int) = `3`


  **Returns:** List[ContextLink]



---

### KnowledgeGraphLinker

```python
class KnowledgeGraphLinker
```

Links ideas with knowledge graph patterns.


**Methods:**

  #### `find_knowledge_links`

  ```python
  find_knowledge_links(self, idea: IdeaCapture, limit: int) -> List[ContextLink]
  ```

  Find knowledge graph patterns relevant to an idea.

  **Parameters:**

  - `self`
  - `idea` (IdeaCapture)
  - `limit` (int) = `3`


  **Returns:** List[ContextLink]



---

### OperationLinker

```python
class OperationLinker
```

Links ideas with active CORTEX operations.


**Methods:**

  #### `find_operation_links`

  ```python
  find_operation_links(self, idea: IdeaCapture, limit: int) -> List[ContextLink]
  ```

  Find operations relevant to an idea.

  **Parameters:**

  - `self`
  - `idea` (IdeaCapture)
  - `limit` (int) = `2`


  **Returns:** List[ContextLink]



---

### IdeaContextLinker

```python
class IdeaContextLinker
```

Main context linking engine for IDEA system.


**Methods:**

  #### `link_idea_to_context`

  ```python
  link_idea_to_context(self, idea: IdeaCapture) -> List[ContextLink]
  ```

  Link an idea to relevant CORTEX ecosystem context.

  **Parameters:**

  - `self`
  - `idea` (IdeaCapture)


  **Returns:** List[ContextLink]


  #### `get_idea_contexts`

  ```python
  get_idea_contexts(self, idea_id: str) -> List[ContextLink]
  ```

  Get all context links for an idea.

  **Parameters:**

  - `self`
  - `idea_id` (str)


  **Returns:** List[ContextLink]


  #### `get_context_insights`

  ```python
  get_context_insights(self, idea_id: str) -> Dict[str, any]
  ```

  Get context insights summary for an idea.

  **Parameters:**

  - `self`
  - `idea_id` (str)


  **Returns:** Dict[str, any]



---

## Functions

### create_context_linker

```python
create_context_linker(cortex_root: str) -> IdeaContextLinker
```

Create a new IdeaContextLinker instance.


**Parameters:**

- `cortex_root` (str)


**Returns:** IdeaContextLinker


---

### demo_context_linking

```python
demo_context_linking()
```

Demonstrate context linking capabilities.


---
