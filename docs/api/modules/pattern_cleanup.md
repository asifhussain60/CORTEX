# pattern_cleanup

CORTEX Tier 2: Pattern Cleanup System
Automated maintenance for knowledge graph patterns.

Features:
- Confidence decay for unused patterns
- Pattern consolidation (merge similar patterns)
- Scope-aware protection (never touch generic/CORTEX-core)
- Stale pattern detection and removal


## Table of Contents

### Classes
- [CleanupStats](#cleanupstats)
- [PatternCleanup](#patterncleanup)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, json, knowledge_graph, logging, pathlib, sqlite3, typing


## Classes

### CleanupStats

```python
class CleanupStats
```

**Decorators:** `dataclass`

Statistics from cleanup operations.


**Attributes:**

- `decayed_count`: int
- `deleted_count`: int
- `consolidated_count`: int
- `errors`: List[str]


**Methods:**


---

### PatternCleanup

```python
class PatternCleanup
```

Pattern Cleanup System for automated knowledge graph maintenance.

Key Principles:
- NEVER modify scope='cortex' patterns (CORTEX core protection)
- NEVER modify patterns in CORTEX-core namespace
- Only affect application-specific patterns
- Respect confidence thresholds
- Log all cleanup actions for audit trail


**Methods:**

  #### `apply_automatic_decay`

  ```python
  apply_automatic_decay(self, protect_generic: bool) -> CleanupStats
  ```

      Apply confidence decay to application patterns only.
    
    Rules:
- Generic patterns (scope='cortex') NEVER decay
    - CORTEX-core namespace patterns NEVER decay
    - Application patterns decay 1% per day after 30 days
    - Patterns below 0.3 confidence are deleted
    - Pinned patterns are protected
    
    Args:
        protect_generic: If True, skip all scope='cortex' patterns (default: True)
    
    Returns:
        CleanupStats with decayed and deleted counts
    

  **Parameters:**

  - `self`
  - `protect_generic` (bool) = `True`: If True, skip all scope='cortex' patterns (default: True)


  **Returns:** CleanupStats
    CleanupStats with decayed and deleted counts


  #### `consolidate_similar_patterns`

  ```python
  consolidate_similar_patterns(self, namespace: Optional[str], dry_run: bool) -> CleanupStats
  ```

  Merge similar patterns to reduce duplication.

Rules:
- Only consolidate patterns with same scope and overlapping namespaces
- Never consolidate generic patterns (they're immutable)
- Preserve highest confidence and most recent evidence
- Combine access counts
- Keep all tags

Args:
    namespace: Limit consolidation to specific namespace (optional)
    dry_run: If True, report what would be consolidated without changes

Returns:
    CleanupStats with consolidated count

  **Parameters:**

  - `self`
  - `namespace` (Optional[str]) = `None`: Limit consolidation to specific namespace (optional)
  - `dry_run` (bool) = `False`: If True, report what would be consolidated without changes


  **Returns:** CleanupStats
    CleanupStats with consolidated count


  #### `remove_stale_patterns`

  ```python
  remove_stale_patterns(self, stale_days: int, protect_generic: bool) -> CleanupStats
  ```

  Remove patterns not accessed in a long time.

Args:
    stale_days: Days of inactivity to consider stale (default: 90)
    protect_generic: Never remove generic patterns (default: True)

Returns:
    CleanupStats with deleted count

  **Parameters:**

  - `self`
  - `stale_days` (int) = `90`: Days of inactivity to consider stale (default: 90)
  - `protect_generic` (bool) = `True`: Never remove generic patterns (default: True)


  **Returns:** CleanupStats
    CleanupStats with deleted count


  #### `optimize_database`

  ```python
  optimize_database(self) -> bool
  ```

  Optimize database performance.

- Run VACUUM to reclaim space
- Rebuild FTS5 index
- Analyze query performance

Returns:
    True if successful, False otherwise

  **Parameters:**

  - `self`


  **Returns:** bool
    True if successful, False otherwise


  #### `get_cleanup_recommendations`

  ```python
  get_cleanup_recommendations(self) -> Dict[str, Any]
  ```

  Analyze patterns and recommend cleanup actions.

Returns:
    Dict with recommendations for decay, consolidation, deletion

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict with recommendations for decay, consolidation, deletion



---
