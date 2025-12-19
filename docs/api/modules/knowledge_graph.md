# knowledge_graph

CORTEX Tier 2: Knowledge Graph
Pattern learning and workflow storage using SQLite + FTS5

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [KnowledgeGraph](#knowledgegraph)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** contextlib, datetime, json, pathlib, sqlite3, src, typing


## Classes

### KnowledgeGraph

```python
class KnowledgeGraph
```

Tier 2 Long-Term Memory: Pattern learning and workflow templates

Storage: SQLite database at cortex-brain/tier2/knowledge-graph.db
Performance: <150ms per search (target: 92ms actual)
Features: FTS5 full-text search, pattern decay, namespace isolation


**Methods:**

  #### `store_pattern`

  ```python
  store_pattern(self, title: str, pattern_type: str, confidence: float, context: Dict[str, Any], scope: str, namespaces: List[str]) -> str
  ```

  Store a learned pattern

Args:
    title: Pattern name/title
    pattern_type: Type (workflow, intent, validation)
    confidence: Confidence score (0.0-1.0)
    context: Pattern details (files, steps, etc.)
    scope: Scope (cortex or application)
    namespaces: Namespace tags for isolation

Returns:
    pattern_id: Unique identifier

  **Parameters:**

  - `self`
  - `title` (str): Pattern name/title
  - `pattern_type` (str): Type (workflow, intent, validation)
  - `confidence` (float) = `0.5`: Confidence score (0.0-1.0)
  - `context` (Dict[str, Any]) = `None`: Pattern details (files, steps, etc.)
  - `scope` (str) = `'application'`: Scope (cortex or application)
  - `namespaces` (List[str]) = `None`: Namespace tags for isolation


  **Returns:** str
    pattern_id: Unique identifier


  #### `search_patterns`

  ```python
  search_patterns(self, query: str, pattern_type: Optional[str], min_confidence: float, scope: Optional[str], limit: int, include_confidence_metadata: bool) -> List[Dict[str, Any]]
  ```

  Search patterns using FTS5 full-text search

Args:
    query: Search query
    pattern_type: Filter by type (optional)
    min_confidence: Minimum confidence threshold
    scope: Filter by scope (optional)
    limit: Maximum results
    include_confidence_metadata: Include metadata for confidence scoring (NEW in Lean 3.1)

Returns:
    List of matching patterns with match scores
    
    If include_confidence_metadata=True, each result includes:
    - pattern_count: Total number of matching patterns (for all results)
    - success_rate: Historical success rate of this pattern (0.0-1.0)
    - usage_count: Number of times pattern has been used
    - last_used: DateTime when pattern was last used

  **Parameters:**

  - `self`
  - `query` (str): Search query
  - `pattern_type` (Optional[str]) = `None`: Filter by type (optional)
  - `min_confidence` (float) = `0.7`: Minimum confidence threshold
  - `scope` (Optional[str]) = `None`: Filter by scope (optional)
  - `limit` (int) = `5`: Maximum results
  - `include_confidence_metadata` (bool) = `False`: Include metadata for confidence scoring (NEW in Lean 3.1)


  **Returns:** List[Dict[str, Any]]
    List of matching patterns with match scores If include_confidence_metadata=True, each result includes: - pattern_count: Total number of matching patterns (for all results) - success_rate: Historical success rate of this pattern (0.0-1.0) - usage_count: Number of times pattern has been used - last_used: DateTime when pattern was last used


  #### `track_relationship`

  ```python
  track_relationship(self, file_a: str, file_b: str, relationship_type: str, strength: float, context: str)
  ```

  Track file co-modification relationship

Args:
    file_a: First file path
    file_b: Second file path
    relationship_type: Type (co_modification, dependency)
    strength: Relationship strength (0.0-1.0)
    context: Additional context

  **Parameters:**

  - `self`
  - `file_a` (str): First file path
  - `file_b` (str): Second file path
  - `relationship_type` (str) = `'co_modification'`: Type (co_modification, dependency)
  - `strength` (float) = `0.5`: Relationship strength (0.0-1.0)
  - `context` (str) = `None`: Additional context


  #### `get_file_relationships`

  ```python
  get_file_relationships(self, file_path: str, min_strength: float) -> List[Dict[str, Any]]
  ```

  Get all relationships for a file

Args:
    file_path: File to query
    min_strength: Minimum relationship strength

Returns:
    List of related files

  **Parameters:**

  - `self`
  - `file_path` (str): File to query
  - `min_strength` (float) = `0.5`: Minimum relationship strength


  **Returns:** List[Dict[str, Any]]
    List of related files


  #### `store_workflow_template`

  ```python
  store_workflow_template(self, name: str, phases: List[Dict[str, Any]], success_rate: float, avg_duration_hours: float) -> str
  ```

  Store workflow template

Args:
    name: Workflow name
    phases: List of phase definitions
    success_rate: Historical success rate
    avg_duration_hours: Average completion time

Returns:
    workflow_id: Unique identifier

  **Parameters:**

  - `self`
  - `name` (str): Workflow name
  - `phases` (List[Dict[str, Any]]): List of phase definitions
  - `success_rate` (float) = `0.0`: Historical success rate
  - `avg_duration_hours` (float) = `0.0`: Average completion time


  **Returns:** str
    workflow_id: Unique identifier


  #### `get_workflow_template`

  ```python
  get_workflow_template(self, name: str) -> Optional[Dict[str, Any]]
  ```

  Retrieve workflow template by name

  **Parameters:**

  - `self`
  - `name` (str)


  **Returns:** Optional[Dict[str, Any]]


  #### `boost_pattern`

  ```python
  boost_pattern(self, pattern_id: str, boost_amount: float)
  ```

  Increase pattern confidence after successful use

Args:
    pattern_id: Pattern to boost
    boost_amount: Confidence increase (default: 0.05)

  **Parameters:**

  - `self`
  - `pattern_id` (str): Pattern to boost
  - `boost_amount` (float) = `0.05`: Confidence increase (default: 0.05)


  #### `apply_decay`

  ```python
  apply_decay(self, decay_rate: float, min_confidence: float)
  ```

  Apply pattern decay to unused patterns

Args:
    decay_rate: Confidence decrease per period (default: 0.05)
    min_confidence: Don't decay below this (default: 0.3)

  **Parameters:**

  - `self`
  - `decay_rate` (float) = `0.05`: Confidence decrease per period (default: 0.05)
  - `min_confidence` (float) = `0.3`: Don't decay below this (default: 0.3)


  #### `store_tdd_cycle_pattern`

  ```python
  store_tdd_cycle_pattern(self, feature: str, test_strategy: str, implementation_approach: str, refactoring_type: str, confidence: float) -> str
  ```

  Store a completed TDD cycle as a pattern for future reference.

Part of Phase 3 Deliverable 3.2: Pattern Learning from TDD Cycles

Args:
    feature: Feature name that was implemented
    test_strategy: Testing strategy used (e.g., 'happy_path_first', 'edge_cases_first')
    implementation_approach: Implementation approach (e.g., 'minimal_then_extend')
    refactoring_type: Type of refactoring performed (e.g., 'extract_method')
    confidence: Initial confidence score (default: 0.7)

Returns:
    pattern_id: Unique identifier for the stored pattern

  **Parameters:**

  - `self`
  - `feature` (str): Feature name that was implemented
  - `test_strategy` (str): Testing strategy used (e.g., 'happy_path_first', 'edge_cases_first')
  - `implementation_approach` (str): Implementation approach (e.g., 'minimal_then_extend')
  - `refactoring_type` (str): Type of refactoring performed (e.g., 'extract_method')
  - `confidence` (float) = `0.7`: Initial confidence score (default: 0.7)


  **Returns:** str
    pattern_id: Unique identifier for the stored pattern


  #### `get_pattern`

  ```python
  get_pattern(self, pattern_id: str) -> Optional[Dict[str, Any]]
  ```

  Retrieve a specific pattern by ID.

Args:
    pattern_id: Pattern identifier

Returns:
    Pattern dictionary or None if not found

  **Parameters:**

  - `self`
  - `pattern_id` (str): Pattern identifier


  **Returns:** Optional[Dict[str, Any]]
    Pattern dictionary or None if not found


  #### `get_implementation_dependencies`

  ```python
  get_implementation_dependencies(self, feature: str) -> List[Dict[str, Any]]
  ```

  Get implementation dependencies captured during GREEN phase.

Args:
    feature: Feature name to retrieve dependencies for

Returns:
    List of dependency dictionaries

  **Parameters:**

  - `self`
  - `feature` (str): Feature name to retrieve dependencies for


  **Returns:** List[Dict[str, Any]]
    List of dependency dictionaries


  #### `get_implementation_decisions`

  ```python
  get_implementation_decisions(self, feature: str) -> List[Dict[str, Any]]
  ```

  Get implementation decisions captured during GREEN phase.

Args:
    feature: Feature name to retrieve decisions for

Returns:
    List of decision dictionaries with rationale

  **Parameters:**

  - `self`
  - `feature` (str): Feature name to retrieve decisions for


  **Returns:** List[Dict[str, Any]]
    List of decision dictionaries with rationale


  #### `suggest_patterns_for_feature`

  ```python
  suggest_patterns_for_feature(self, feature_name: str, limit: int) -> List[Dict[str, Any]]
  ```

  Suggest relevant patterns for a new feature based on semantic similarity.

Part of Phase 3 Deliverable 3.2: Future TDD cycles get pattern suggestions

Args:
    feature_name: New feature being implemented
    limit: Maximum number of suggestions

Returns:
    List of relevant pattern suggestions

  **Parameters:**

  - `self`
  - `feature_name` (str): New feature being implemented
  - `limit` (int) = `5`: Maximum number of suggestions


  **Returns:** List[Dict[str, Any]]
    List of relevant pattern suggestions


  #### `fts5_search`

  ```python
  fts5_search(self, query: str, limit: int) -> List[Dict[str, Any]]
  ```

  Full-text search using FTS5 for semantic pattern matching.

Part of Phase 3 Deliverable 3.2: Pattern matching uses FTS5

Args:
    query: Search query
    limit: Maximum results

Returns:
    List of matching patterns

  **Parameters:**

  - `self`
  - `query` (str): Search query
  - `limit` (int) = `10`: Maximum results


  **Returns:** List[Dict[str, Any]]
    List of matching patterns


  #### `store_relationship`

  ```python
  store_relationship(self, relationship_id: str, file_a: str, file_b: str, relationship_type: str, strength: float, context: str) -> None
  ```

  Store code relationship in knowledge graph

Args:
    relationship_id: Unique relationship identifier
    file_a: Source file/entity
    file_b: Target file/entity
    relationship_type: Type of relationship (import, calls, etc.)
    strength: Relationship strength (0.0-1.0)
    context: Description of relationship

  **Parameters:**

  - `self`
  - `relationship_id` (str): Unique relationship identifier
  - `file_a` (str): Source file/entity
  - `file_b` (str): Target file/entity
  - `relationship_type` (str): Type of relationship (import, calls, etc.)
  - `strength` (float): Relationship strength (0.0-1.0)
  - `context` (str) = `''`: Description of relationship


  **Returns:** None


  #### `get_relationships`

  ```python
  get_relationships(self, file_a: Optional[str], file_b: Optional[str], relationship_type: Optional[str]) -> List[Dict[str, Any]]
  ```

  Get relationships matching criteria

Args:
    file_a: Filter by source file
    file_b: Filter by target file
    relationship_type: Filter by relationship type
    
Returns:
    List of matching relationships

  **Parameters:**

  - `self`
  - `file_a` (Optional[str]) = `None`: Filter by source file
  - `file_b` (Optional[str]) = `None`: Filter by target file
  - `relationship_type` (Optional[str]) = `None`: Filter by relationship type


  **Returns:** List[Dict[str, Any]]
    List of matching relationships



---
