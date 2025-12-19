# semantic_search

Semantic Search - Enhanced FTS5 search wrapper with filters

Provides:
- FTS5 full-text search with ranking
- Pattern type filtering
- Namespace filtering
- Performance optimization (<100ms target)

Built on top of KnowledgeGraph FTS5 capabilities.

Author: Asif Hussain


## Table of Contents

### Classes
- [SemanticSearch](#semanticsearch)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** json, time, typing


## Classes

### SemanticSearch

```python
class SemanticSearch
```

Enhanced semantic search with FTS5


**Methods:**

  #### `search`

  ```python
  search(self, query: str, pattern_type: Optional[str], namespaces: Optional[List[str]], limit: int) -> List[Dict[str, Any]]
  ```

  Search patterns with optional filters

Args:
    query: Search query
    pattern_type: Optional filter by pattern type
    namespaces: Optional filter by namespaces
    limit: Maximum results
    
Returns:
    List of matching patterns with scores

  **Parameters:**

  - `self`
  - `query` (str): Search query
  - `pattern_type` (Optional[str]) = `None`: Optional filter by pattern type
  - `namespaces` (Optional[List[str]]) = `None`: Optional filter by namespaces
  - `limit` (int) = `10`: Maximum results


  **Returns:** List[Dict[str, Any]]
    List of matching patterns with scores



---
