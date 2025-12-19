# idea_organizer

CORTEX 3.0 - Feature 1: IDEA Capture System - Organization Module

Purpose: Smart organization system for captured ideas with categorization,
         tagging, priority management, and intelligent clustering.

Core Components:
- IdeaOrganizer: Main organization engine
- CategoryManager: Auto-categorization by project/component/type
- TagSystem: Flexible tagging with hierarchical relationships
- PriorityEngine: Dynamic priority scoring and management
- ClusteringEngine: Related idea detection and grouping

Performance Requirements:
- Organization processing: <50ms per idea
- Search queries: <100ms for 10,000+ ideas
- Batch processing: 1000+ ideas/second
- Memory efficient: <10MB for 100,000 ideas

Architecture Pattern:
- Event-driven: React to idea capture events
- Pluggable: Extensible categorization rules
- Cached: Intelligent caching for fast retrieval
- Async: Non-blocking background processing

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms


## Table of Contents

### Classes
- [IdeaCategory](#ideacategory)
- [IdeaTag](#ideatag)
- [IdeaCluster](#ideacluster)
- [CategoryManager](#categorymanager)
- [TagSystem](#tagsystem)
- [PriorityEngine](#priorityengine)
- [ClusteringEngine](#clusteringengine)
- [IdeaOrganizer](#ideaorganizer)

### Functions
- [create_idea_organizer](#create_idea_organizer)


## Overview

- **Classes:** 8
- **Functions:** 1
- **Dependencies:** collections, concurrent, dataclasses, datetime, hashlib, idea_queue, json, logging, pathlib, re, sqlite3, threading, time, typing


## Classes

### IdeaCategory

```python
class IdeaCategory
```

**Decorators:** `dataclass`

Represents a category classification for an idea.


**Attributes:**

- `name`: str
- `confidence`: float
- `source`: str
- `created_at`: datetime


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  #### `from_dict`

  *Decorators:* `classmethod`

  ```python
  from_dict(cls, data: Dict[str, Any]) -> 'IdeaCategory'
  ```


---

### IdeaTag

```python
class IdeaTag
```

**Decorators:** `dataclass`

Represents a tag applied to an idea.


**Attributes:**

- `name`: str
- `category`: Optional[str]
- `confidence`: float
- `source`: str
- `parent_tag`: Optional[str]
- `created_at`: datetime


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  #### `from_dict`

  *Decorators:* `classmethod`

  ```python
  from_dict(cls, data: Dict[str, Any]) -> 'IdeaTag'
  ```


---

### IdeaCluster

```python
class IdeaCluster
```

**Decorators:** `dataclass`

Represents a cluster of related ideas.


**Attributes:**

- `cluster_id`: str
- `ideas`: List[str]
- `similarity_threshold`: float
- `cluster_center`: Optional[str]
- `tags`: List[str]
- `created_at`: datetime
- `updated_at`: datetime


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  #### `from_dict`

  *Decorators:* `classmethod`

  ```python
  from_dict(cls, data: Dict[str, Any]) -> 'IdeaCluster'
  ```


---

### CategoryManager

```python
class CategoryManager
```

Manages automatic categorization of ideas.


**Methods:**

  #### `categorize_idea`

  ```python
  categorize_idea(self, idea: IdeaCapture) -> List[IdeaCategory]
  ```

  Categorize an idea using built-in rules.

  **Parameters:**

  - `self`
  - `idea` (IdeaCapture)


  **Returns:** List[IdeaCategory]


  #### `detect_component`

  ```python
  detect_component(self, idea: IdeaCapture) -> Optional[str]
  ```

  Detect the component/module this idea relates to.

  **Parameters:**

  - `self`
  - `idea` (IdeaCapture)


  **Returns:** Optional[str]



---

### TagSystem

```python
class TagSystem
```

Manages flexible tagging system with hierarchical relationships.


**Methods:**

  #### `add_tag`

  ```python
  add_tag(self, idea_id: str, tag: IdeaTag) -> bool
  ```

  Add a tag to an idea.

  **Parameters:**

  - `self`
  - `idea_id` (str)
  - `tag` (IdeaTag)


  **Returns:** bool


  #### `get_tags`

  ```python
  get_tags(self, idea_id: str) -> List[IdeaTag]
  ```

  Get all tags for an idea.

  **Parameters:**

  - `self`
  - `idea_id` (str)


  **Returns:** List[IdeaTag]


  #### `auto_tag_idea`

  ```python
  auto_tag_idea(self, idea: IdeaCapture) -> List[IdeaTag]
  ```

  Automatically generate tags for an idea.

  **Parameters:**

  - `self`
  - `idea` (IdeaCapture)


  **Returns:** List[IdeaTag]



---

### PriorityEngine

```python
class PriorityEngine
```

Dynamic priority scoring and management.


**Methods:**

  #### `calculate_priority_score`

  ```python
  calculate_priority_score(self, idea: IdeaCapture) -> float
  ```

  Calculate dynamic priority score (0.0 to 1.0).

  **Parameters:**

  - `self`
  - `idea` (IdeaCapture)


  **Returns:** float


  #### `get_priority_label`

  ```python
  get_priority_label(self, score: float) -> str
  ```

  Convert priority score to human-readable label.

  **Parameters:**

  - `self`
  - `score` (float)


  **Returns:** str



---

### ClusteringEngine

```python
class ClusteringEngine
```

Engine for detecting and clustering related ideas.


**Methods:**

  #### `calculate_similarity`

  ```python
  calculate_similarity(self, idea1: IdeaCapture, idea2: IdeaCapture) -> float
  ```

  Calculate similarity between two ideas.

  **Parameters:**

  - `self`
  - `idea1` (IdeaCapture)
  - `idea2` (IdeaCapture)


  **Returns:** float


  #### `find_clusters`

  ```python
  find_clusters(self, ideas: List[IdeaCapture]) -> List[IdeaCluster]
  ```

  Find clusters of related ideas.

  **Parameters:**

  - `self`
  - `ideas` (List[IdeaCapture])


  **Returns:** List[IdeaCluster]



---

### IdeaOrganizer

```python
class IdeaOrganizer
```

Main organization engine that coordinates all organization components.


**Methods:**

  #### `organize_idea`

  ```python
  organize_idea(self, idea: IdeaCapture, async_processing: bool) -> Dict[str, Any]
  ```

  Organize a newly captured idea.

  **Parameters:**

  - `self`
  - `idea` (IdeaCapture)
  - `async_processing` (bool) = `True`


  **Returns:** Dict[str, Any]


  #### `batch_organize_ideas`

  ```python
  batch_organize_ideas(self, ideas: List[IdeaCapture]) -> Dict[str, Any]
  ```

  Organize multiple ideas in batch for efficiency.

  **Parameters:**

  - `self`
  - `ideas` (List[IdeaCapture])


  **Returns:** Dict[str, Any]


  #### `get_organization_stats`

  ```python
  get_organization_stats(self) -> Dict[str, Any]
  ```

  Get organization processing statistics.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]


  #### `shutdown`

  ```python
  shutdown(self)
  ```

  Shutdown the organizer and cleanup resources.

  **Parameters:**

  - `self`



---

## Functions

### create_idea_organizer

```python
create_idea_organizer(db_path: str, enable_clustering: bool) -> IdeaOrganizer
```

Factory function to create an IdeaOrganizer instance.


**Parameters:**

- `db_path` (str)
- `enable_clustering` (bool) = `True`


**Returns:** IdeaOrganizer


---
