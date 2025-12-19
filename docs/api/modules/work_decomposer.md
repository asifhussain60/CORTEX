# work_decomposer

CORTEX Work Decomposer

Decomposes large work items into Features and Stories with ADO-ready output.
Each story includes title, points, description, acceptance criteria, and implementation plan.

Author: Asif Hussain
Copyright: (c) 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [WorkItemType](#workitemtype)
- [StoryPointScale](#storypointscale)
- [ADOWorkItem](#adoworkitem)
- [DecompositionResult](#decompositionresult)
- [WorkDecomposer](#workdecomposer)


## Overview

- **Classes:** 5
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, enum, math, re, typing


## Classes

### WorkItemType

```python
class WorkItemType(Enum)
```

ADO Work Item Types



---

### StoryPointScale

```python
class StoryPointScale(Enum)
```

Fibonacci story point values



---

### ADOWorkItem

```python
class ADOWorkItem
```

**Decorators:** `dataclass`

ADO-ready work item with all required fields.
Can be directly attached to ADO board.


**Attributes:**

- `title`: str
- `work_item_type`: WorkItemType
- `story_points`: int
- `description`: str
- `acceptance_criteria`: List[str]
- `implementation_plan`: str
- `technical_notes`: str
- `parent_id`: Optional[str]
- `parent_title`: Optional[str]
- `children`: List['ADOWorkItem']
- `id`: str
- `priority`: int
- `tags`: List[str]
- `area_path`: str
- `iteration_path`: str
- `complexity_score`: float
- `confidence`: str
- `estimated_hours`: float
- `dependencies`: List[str]


**Methods:**

  #### `to_ado_dict`

  ```python
  to_ado_dict(self) -> Dict[str, Any]
  ```

  Convert to ADO-compatible dictionary format.
Ready for ADO API or clipboard paste.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]


  #### `to_markdown`

  ```python
  to_markdown(self) -> str
  ```

  Format as markdown for display

  **Parameters:**

  - `self`


  **Returns:** str



---

### DecompositionResult

```python
class DecompositionResult
```

**Decorators:** `dataclass`

Result of work decomposition


**Attributes:**

- `epic`: Optional[ADOWorkItem]
- `features`: List[ADOWorkItem]
- `stories`: List[ADOWorkItem]
- `total_story_points`: int
- `total_features`: int
- `total_stories`: int
- `complexity_distribution`: Dict[str, int]
- `decomposition_notes`: List[str]
- `timestamp`: str


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert to dictionary

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]


  #### `to_markdown_report`

  ```python
  to_markdown_report(self) -> str
  ```

  Generate full markdown report of decomposition

  **Parameters:**

  - `self`


  **Returns:** str



---

### WorkDecomposer

```python
class WorkDecomposer
```

Decomposes large work items into hierarchical structure:
Epic → Features → User Stories

Each item includes ADO-ready fields for board attachment.


**Methods:**

  #### `decompose_work`

  ```python
  decompose_work(self, title: str, description: str, complexity_score: float, requirements: Optional[Dict[str, Any]], context: Optional[Dict[str, Any]]) -> DecompositionResult
  ```

  Decompose work into Features and Stories.

Args:
    title: Work item title
    description: Detailed description
    complexity_score: SWAGGER complexity score (0-100)
    requirements: Parsed requirements dict with:
        - functional_areas: List of functional areas
        - components: List of technical components
        - acceptance_criteria: List of AC items
        - dependencies: List of dependencies
    context: Additional context:
        - area_path: ADO area path
        - iteration_path: ADO iteration path
        - tags: Default tags
        - priority: Default priority

Returns:
    DecompositionResult with Epic, Features, and Stories

  **Parameters:**

  - `self`
  - `title` (str): Work item title
  - `description` (str): Detailed description
  - `complexity_score` (float): SWAGGER complexity score (0-100)
  - `requirements` (Optional[Dict[str, Any]]) = `None`: Parsed requirements dict with:
  - `context` (Optional[Dict[str, Any]]) = `None`: Additional context:


  **Returns:** DecompositionResult
    DecompositionResult with Epic, Features, and Stories


  #### `format_for_ado_board`

  ```python
  format_for_ado_board(self, result: DecompositionResult, include_hierarchy: bool) -> str
  ```

  Format decomposition result for ADO board attachment.

Args:
    result: DecompositionResult from decompose_work()
    include_hierarchy: Include parent-child relationships

Returns:
    Formatted markdown ready for ADO

  **Parameters:**

  - `self`
  - `result` (DecompositionResult): DecompositionResult from decompose_work()
  - `include_hierarchy` (bool) = `True`: Include parent-child relationships


  **Returns:** str
    Formatted markdown ready for ADO



---
