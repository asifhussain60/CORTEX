# personal_knowledge_archive

CORTEX Knowledge Archive - Personal Cross-Project Learning System

Your personal archive of proven solutions across all projects.

This module manages your knowledge archive - a persistent memory of:
- Successful patterns you've used
- Mistakes you've learned from (anti-patterns)
- PR decisions and their outcomes
- Solutions that worked (and didn't work)

Think of it as "collaborating with Future You" - capture knowledge once,
reuse it forever across all your projects.


## Table of Contents

### Classes
- [ArchivedPattern](#archivedpattern)
- [ArchivedAntiPattern](#archivedantipattern)
- [CortexKnowledgeArchive](#cortexknowledgearchive)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, json, pathlib, sqlite3, typing


## Classes

### ArchivedPattern

```python
class ArchivedPattern
```

**Decorators:** `dataclass`

Represents a proven pattern from your past work


**Attributes:**

- `pattern_id`: str
- `pattern_type`: str
- `title`: str
- `description`: str
- `confidence`: float
- `usage_count`: int
- `success_count`: int
- `failure_count`: int
- `scope`: str
- `project_name`: str
- `archived_date`: str
- `pr_references`: List[str]
- `conversation_links`: List[str]
- `keywords`: str
- `created_at`: str
- `last_used`: str


**Methods:**


---

### ArchivedAntiPattern

```python
class ArchivedAntiPattern
```

**Decorators:** `dataclass`

Represents a mistake you've learned from (what NOT to do)


**Attributes:**

- `antipattern_id`: str
- `antipattern_type`: str
- `title`: str
- `description`: str
- `why_it_failed`: str
- `confidence`: float
- `times_encountered`: int
- `project_name`: str
- `learned_date`: str
- `pr_references`: List[str]
- `similar_patterns`: List[str]
- `created_at`: str


**Methods:**


---

### CortexKnowledgeArchive

```python
class CortexKnowledgeArchive
```

Your Personal Knowledge Archive - Learn Once, Use Forever

Features:
- Archive successful patterns from your projects
- Remember mistakes you've made (anti-patterns)
- Search across all your past work
- Track what worked and what didn't
- Cross-project pattern reuse

Benefits:
- Never rediscover the same solution twice
- Avoid repeating past mistakes
- Build your personal "second brain"
- Accelerate future work with proven patterns


**Methods:**

  #### `add_pattern`

  ```python
  add_pattern(self, pattern: ArchivedPattern) -> bool
  ```

  Archive a successful pattern for future reference

  **Parameters:**

  - `self`
  - `pattern` (ArchivedPattern)


  **Returns:** bool


  #### `add_antipattern`

  ```python
  add_antipattern(self, antipattern: ArchivedAntiPattern) -> bool
  ```

  Archive a mistake you've learned from

  **Parameters:**

  - `self`
  - `antipattern` (ArchivedAntiPattern)


  **Returns:** bool


  #### `search_patterns`

  ```python
  search_patterns(self, query: str, pattern_type: Optional[str], limit: int) -> List[ArchivedPattern]
  ```

  Search your archived patterns using full-text search.
Returns patterns sorted by relevance and confidence.

  **Parameters:**

  - `self`
  - `query` (str)
  - `pattern_type` (Optional[str]) = `None`
  - `limit` (int) = `10`


  **Returns:** List[ArchivedPattern]


  #### `get_pattern`

  ```python
  get_pattern(self, pattern_id: str) -> Optional[ArchivedPattern]
  ```

  Get a specific archived pattern by ID

  **Parameters:**

  - `self`
  - `pattern_id` (str)


  **Returns:** Optional[ArchivedPattern]


  #### `increment_pattern_usage`

  ```python
  increment_pattern_usage(self, pattern_id: str, success: bool) -> bool
  ```

  Track when you reuse a pattern (and whether it worked)

  **Parameters:**

  - `self`
  - `pattern_id` (str)
  - `success` (bool) = `True`


  **Returns:** bool


  #### `get_archive_statistics`

  ```python
  get_archive_statistics(self) -> Dict[str, Any]
  ```

  Get statistics about your knowledge archive

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]


  #### `add_project`

  ```python
  add_project(self, project_id: str, project_name: str) -> bool
  ```

  Register a project in your archive

  **Parameters:**

  - `self`
  - `project_id` (str)
  - `project_name` (str)


  **Returns:** bool


  #### `update_project_stats`

  ```python
  update_project_stats(self, project_id: str) -> bool
  ```

  Update project statistics

  **Parameters:**

  - `self`
  - `project_id` (str)


  **Returns:** bool



---
