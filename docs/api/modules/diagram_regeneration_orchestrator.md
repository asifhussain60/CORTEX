# diagram_regeneration_orchestrator

CORTEX Diagram Regeneration Orchestrator

Handles regeneration of all CORTEX diagram documentation with D3.js dashboard integration.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [DiagramStatus](#diagramstatus)
- [DiagramRegenerationReport](#diagramregenerationreport)
- [DiagramRegenerationOrchestrator](#diagramregenerationorchestrator)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, logging, pathlib, src, typing


## Classes

### DiagramStatus

```python
class DiagramStatus
```

**Decorators:** `dataclass`

Status of a single diagram


**Attributes:**

- `id`: str
- `name`: str
- `title`: str
- `has_prompt`: bool
- `has_narrative`: bool
- `has_mermaid`: bool
- `has_image`: bool
- `last_modified`: Optional[datetime]


**Methods:**

  #### `completion_percentage`

  *Decorators:* `property`

  ```python
  completion_percentage(self) -> int
  ```

  Calculate completion percentage

  **Parameters:**

  - `self`


  **Returns:** int


  #### `status`

  *Decorators:* `property`

  ```python
  status(self) -> str
  ```

  Get status label

  **Parameters:**

  - `self`


  **Returns:** str



---

### DiagramRegenerationReport

```python
class DiagramRegenerationReport
```

**Decorators:** `dataclass`

Report from diagram regeneration operation


**Attributes:**

- `timestamp`: datetime
- `diagrams`: List[DiagramStatus]
- `total_diagrams`: int
- `complete_diagrams`: int
- `incomplete_diagrams`: int
- `regenerated_count`: int
- `failed_count`: int
- `duration_seconds`: float


**Methods:**

  #### `overall_completion`

  *Decorators:* `property`

  ```python
  overall_completion(self) -> float
  ```

  Calculate overall completion percentage

  **Parameters:**

  - `self`


  **Returns:** float



---

### DiagramRegenerationOrchestrator

```python
class DiagramRegenerationOrchestrator
```

Orchestrates diagram regeneration with D3.js dashboard generation


**Methods:**

  #### `execute`

  ```python
  execute(self) -> DiagramRegenerationReport
  ```

  Execute diagram regeneration and generate dashboard

  **Parameters:**

  - `self`


  **Returns:** DiagramRegenerationReport



---
