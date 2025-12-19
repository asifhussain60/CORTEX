# knowledge_graph_auto_updater

Knowledge Graph Auto-Updater - Automated knowledge graph maintenance.

Extracts patterns from execution context and safely updates knowledge-graph.yaml
with file locking, backup/rollback, and concurrent access protection.


## Table of Contents

### Classes
- [UpdateResult](#updateresult)
- [PatternExtractor](#patternextractor)
- [KnowledgeGraphAutoUpdater](#knowledgegraphautoupdater)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, fcntl, logging, pathlib, time, typing, yaml


## Classes

### UpdateResult

```python
class UpdateResult
```

**Decorators:** `dataclass`

Result of knowledge graph update operation.


**Attributes:**

- `success`: bool
- `patterns_added`: int
- `duplicates_skipped`: int
- `backup_path`: Optional[Path]
- `error_message`: Optional[str]



---

### PatternExtractor

```python
class PatternExtractor
```

Extracts reusable patterns from execution context.


**Methods:**

  #### `extract_from_context`

  *Decorators:* `staticmethod`

  ```python
  extract_from_context(context: Dict[str, Any]) -> List[Dict[str, Any]]
  ```

  Extract 3-5 patterns from execution context.

Args:
    context: Execution context with metrics
    
Returns:
    List of pattern dictionaries

  **Parameters:**

  - `context` (Dict[str, Any]): Execution context with metrics


  **Returns:** List[Dict[str, Any]]
    List of pattern dictionaries



---

### KnowledgeGraphAutoUpdater

```python
class KnowledgeGraphAutoUpdater
```

Automatically updates knowledge-graph.yaml with new patterns.

Features:
- File locking (fcntl) for concurrent access safety
- Automatic backup before modification
- Rollback on failure
- Pattern deduplication
- Extracts 3-5 patterns per run


**Methods:**

  #### `acquire_lock`

  ```python
  acquire_lock(self) -> bool
  ```

  Acquire exclusive lock on knowledge graph file.

Returns:
    True if lock acquired, False otherwise

  **Parameters:**

  - `self`


  **Returns:** bool
    True if lock acquired, False otherwise


  #### `release_lock`

  ```python
  release_lock(self) -> bool
  ```

  Release lock on knowledge graph file.

Returns:
    True if lock released successfully

  **Parameters:**

  - `self`


  **Returns:** bool
    True if lock released successfully


  #### `create_backup`

  ```python
  create_backup(self) -> Optional[Path]
  ```

  Create backup of current knowledge graph.

Returns:
    Path to backup file or None on failure

  **Parameters:**

  - `self`


  **Returns:** Optional[Path]
    Path to backup file or None on failure


  #### `restore_from_backup`

  ```python
  restore_from_backup(self, backup_path: Path) -> bool
  ```

  Restore knowledge graph from backup.

Args:
    backup_path: Path to backup file
    
Returns:
    True if restore successful

  **Parameters:**

  - `self`
  - `backup_path` (Path): Path to backup file


  **Returns:** bool
    True if restore successful


  #### `extract_patterns`

  ```python
  extract_patterns(self, context: Dict[str, Any]) -> List[Dict[str, Any]]
  ```

  Extract patterns from execution context.

Args:
    context: Execution context with metrics
    
Returns:
    List of 3-5 pattern dictionaries

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Execution context with metrics


  **Returns:** List[Dict[str, Any]]
    List of 3-5 pattern dictionaries


  #### `update_knowledge_graph`

  ```python
  update_knowledge_graph(self, context: Dict[str, Any]) -> UpdateResult
  ```

  Update knowledge graph with patterns from execution context.

Workflow:
1. Acquire lock
2. Create backup
3. Load current graph
4. Extract and add new patterns (deduplicate)
5. Write updated graph
6. Release lock
7. Rollback on failure

Args:
    context: Execution context with execution metrics
    
Returns:
    UpdateResult with success status and metrics

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Execution context with execution metrics


  **Returns:** UpdateResult
    UpdateResult with success status and metrics



---
