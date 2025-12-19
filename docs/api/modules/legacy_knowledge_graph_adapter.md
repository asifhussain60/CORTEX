# legacy_knowledge_graph_adapter

Legacy Knowledge Graph Adapter

Bridges old KnowledgeGraph API (5-param store_pattern) to new modular facade API.
Enables Phase 7.2 pattern learning components to work with either implementation.

Design:
- Wraps new KnowledgeGraph facade
- Translates old API calls → new API calls
- Maps pattern types and handles namespace translation
- Maintains backward compatibility during migration

Usage:
    # Old code using monolithic API
    kg = KnowledgeGraph(db_path)
    pattern_id = kg.store_pattern(
        title="My Pattern",
        pattern_type="workflow",
        confidence=0.8,
        context={'key': 'value'},
        namespaces=['test']
    )
    
    # New code using adapter
    from src.tier2.legacy_knowledge_graph_adapter import LegacyKnowledgeGraphAdapter
    kg = LegacyKnowledgeGraphAdapter(db_path)
    pattern_id = kg.store_pattern(...)  # Same API, works!

Author: Asif Hussain


## Table of Contents

### Classes
- [LegacyKnowledgeGraphAdapter](#legacyknowledgegraphadapter)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** hashlib, json, pathlib, src, typing, uuid


## Classes

### LegacyKnowledgeGraphAdapter

```python
class LegacyKnowledgeGraphAdapter
```

Adapter wrapping modern KnowledgeGraph facade with legacy API.

Translates old store_pattern(title, pattern_type, confidence, context, scope, namespaces)
to new store_pattern(pattern_id, title, content, pattern_type, confidence, metadata, ...).


**Methods:**

  #### `store_pattern`

  ```python
  store_pattern(self, title: str, pattern_type: str, confidence: float, context: Dict[str, Any], scope: str, namespaces: List[str], pattern_id: str, content: str, metadata: Dict[str, Any], source: str, is_pinned: bool, is_cortex_internal: bool) -> Dict[str, Any]
  ```

  Store pattern using legacy OR modern API signature

LEGACY API (5-param):
    title, pattern_type, confidence, context, scope, namespaces
    
MODERN API (7-param):
    pattern_id, title, content, pattern_type, confidence, metadata, namespaces

Args:
    title: Pattern name/title
    pattern_type: Type (workflow, intent, validation, principle, solution, context)
    confidence: Confidence score (0.0-1.0)
    context: Pattern details (legacy API)
    scope: Scope (cortex or application)
    namespaces: Namespace tags for isolation
    pattern_id: Explicit pattern ID (modern API)
    content: Pattern content string (modern API)
    metadata: Pattern metadata (modern API)
    source: Pattern source (modern API)
    is_pinned: Pin status (modern API)
    is_cortex_internal: Internal flag (modern API)

Returns:
    dict with pattern_id

  **Parameters:**

  - `self`
  - `title` (str) = `None`: Pattern name/title
  - `pattern_type` (str) = `None`: Type (workflow, intent, validation, principle, solution, context)
  - `confidence` (float) = `0.5`: Confidence score (0.0-1.0)
  - `context` (Dict[str, Any]) = `None`: Pattern details (legacy API)
  - `scope` (str) = `'application'`: Scope (cortex or application)
  - `namespaces` (List[str]) = `None`: Namespace tags for isolation
  - `pattern_id` (str) = `None`: Explicit pattern ID (modern API)
  - `content` (str) = `None`: Pattern content string (modern API)
  - `metadata` (Dict[str, Any]) = `None`: Pattern metadata (modern API)
  - `source` (str) = `None`: Pattern source (modern API)
  - `is_pinned` (bool) = `False`: Pin status (modern API)
  - `is_cortex_internal` (bool) = `True`: Internal flag (modern API)


  **Returns:** Dict[str, Any]
    dict with pattern_id


  #### `get_pattern`

  ```python
  get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]
  ```

  Get pattern by ID

Args:
    pattern_id: Pattern identifier
    
Returns:
    Pattern dict or None if not found

  **Parameters:**

  - `self`
  - `pattern_id` (str): Pattern identifier


  **Returns:** Optional[Dict[str, Any]]
    Pattern dict or None if not found


  #### `search_patterns`

  ```python
  search_patterns(self, query: str, pattern_type: Optional[str], min_confidence: float, scope: Optional[str], limit: int, include_confidence_metadata: bool) -> List[Dict[str, Any]]
  ```

  Search patterns using FTS5 (legacy API)

Args:
    query: Search query string
    pattern_type: Filter by pattern type
    min_confidence: Minimum confidence threshold
    scope: Filter by scope (cortex/application)
    limit: Maximum results
    include_confidence_metadata: Include confidence metadata
    
Returns:
    List of matching patterns

  **Parameters:**

  - `self`
  - `query` (str): Search query string
  - `pattern_type` (Optional[str]) = `None`: Filter by pattern type
  - `min_confidence` (float) = `0.7`: Minimum confidence threshold
  - `scope` (Optional[str]) = `None`: Filter by scope (cortex/application)
  - `limit` (int) = `5`: Maximum results
  - `include_confidence_metadata` (bool) = `False`: Include confidence metadata


  **Returns:** List[Dict[str, Any]]
    List of matching patterns


  #### `fts5_search`

  ```python
  fts5_search(self, query: str, pattern_type: Optional[str], namespace_filter: Optional[str], limit: int) -> List[Dict[str, Any]]
  ```

  FTS5 full-text search (legacy API)

Args:
    query: Search query
    pattern_type: Filter by pattern type
    namespace_filter: Filter by namespace
    limit: Maximum results
    
Returns:
    List of matching patterns

  **Parameters:**

  - `self`
  - `query` (str): Search query
  - `pattern_type` (Optional[str]) = `None`: Filter by pattern type
  - `namespace_filter` (Optional[str]) = `None`: Filter by namespace
  - `limit` (int) = `10`: Maximum results


  **Returns:** List[Dict[str, Any]]
    List of matching patterns


  #### `store_relationship`

  ```python
  store_relationship(self, file_a: str, file_b: str, relationship_type: str, strength: float, context: Optional[Dict[str, Any]], relationship_id: Optional[str]) -> str
  ```

  Store relationship between entities (legacy API)

Args:
    file_a: First file path
    file_b: Second file path
    relationship_type: Type of relationship
    strength: Relationship strength (0.0-1.0)
    context: Additional context
    relationship_id: Optional explicit relationship ID
    
Returns:
    Relationship ID

  **Parameters:**

  - `self`
  - `file_a` (str): First file path
  - `file_b` (str): Second file path
  - `relationship_type` (str): Type of relationship
  - `strength` (float) = `1.0`: Relationship strength (0.0-1.0)
  - `context` (Optional[Dict[str, Any]]) = `None`: Additional context
  - `relationship_id` (Optional[str]) = `None`: Optional explicit relationship ID


  **Returns:** str
    Relationship ID


  #### `get_relationships`

  ```python
  get_relationships(self, file_path: Optional[str], file_a: Optional[str], relationship_type: Optional[str]) -> List[Dict[str, Any]]
  ```

  Get relationships with optional filters (legacy API)

Args:
    file_path: Filter by file path (matches file_a or file_b)
    file_a: Alias for file_path
    relationship_type: Filter by relationship type
    
Returns:
    List of relationships

  **Parameters:**

  - `self`
  - `file_path` (Optional[str]) = `None`: Filter by file path (matches file_a or file_b)
  - `file_a` (Optional[str]) = `None`: Alias for file_path
  - `relationship_type` (Optional[str]) = `None`: Filter by relationship type


  **Returns:** List[Dict[str, Any]]
    List of relationships



---
