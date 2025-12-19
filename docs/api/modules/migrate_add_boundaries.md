# migrate_add_boundaries

CORTEX Tier 2: Schema Migration - Add Namespace/Scope Boundaries

This migration adds the knowledge boundary system to enforce impenetrable
separation between CORTEX core intelligence (generic) and application-specific
knowledge (KSESSIONS, NOOR, etc.).

Changes:
1. Add `scope` column: 'generic' (CORTEX) vs 'application' (apps)
2. Add `namespaces` column: JSON array supporting multi-app patterns
3. Create indexes for performance
4. Classify existing patterns based on content/source
5. Create rollback backup before migration

Usage:
    python CORTEX/src/tier2/migrate_add_boundaries.py [--dry-run] [--db-path PATH]

Args:
    --dry-run: Show what would be done without making changes
    --db-path: Path to database (default: cortex-brain/tier2/knowledge_graph.db)


## Table of Contents

### Classes
- [BoundaryMigration](#boundarymigration)

### Functions
- [main](#main)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** argparse, datetime, json, pathlib, shutil, sqlite3, traceback, typing


## Classes

### BoundaryMigration

```python
class BoundaryMigration
```

Handles schema migration for namespace/scope boundaries.


**Methods:**

  #### `create_backup`

  ```python
  create_backup(self) -> Path
  ```

  Create backup of database before migration.

Returns:
    Path to backup file

  **Parameters:**

  - `self`


  **Returns:** Path
    Path to backup file


  #### `classify_pattern`

  ```python
  classify_pattern(self, pattern_id: str, title: str, content: str, source: str) -> Tuple[str, List[str]]
  ```

  Classify pattern as generic or application-specific.

Rules:
1. Source from simulations/ → application, namespace from path
2. Contains application paths → application, extract namespace
3. Generic workflow/governance keywords → generic, CORTEX-core
4. Protection/tier patterns → generic, CORTEX-core
5. Default: generic if uncertain

Args:
    pattern_id: Pattern identifier
    title: Pattern title
    content: Pattern content
    source: Pattern source

Returns:
    Tuple of (scope, namespaces)
    - scope: 'generic' or 'application'
    - namespaces: List of namespace strings

  **Parameters:**

  - `self`
  - `pattern_id` (str): Pattern identifier
  - `title` (str): Pattern title
  - `content` (str): Pattern content
  - `source` (str): Pattern source


  **Returns:** Tuple[str, List[str]]
    Tuple of (scope, namespaces) - scope: 'generic' or 'application' - namespaces: List of namespace strings


  #### `get_existing_patterns`

  ```python
  get_existing_patterns(self) -> List[Dict[str, Any]]
  ```

  Retrieve all existing patterns for classification.

Returns:
    List of pattern dicts with id, title, content, source

  **Parameters:**

  - `self`


  **Returns:** List[Dict[str, Any]]
    List of pattern dicts with id, title, content, source


  #### `execute_migration`

  ```python
  execute_migration(self) -> Dict[str, Any]
  ```

  Execute the migration.

Returns:
    Migration statistics

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Migration statistics


  #### `print_summary`

  ```python
  print_summary(self, stats: Dict[str, Any])
  ```

  Print migration summary.

  **Parameters:**

  - `self`
  - `stats` (Dict[str, Any])



---

## Functions

### main

```python
main()
```

Main migration entry point.


---
