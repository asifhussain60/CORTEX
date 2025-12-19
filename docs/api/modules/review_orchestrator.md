# review_orchestrator

Comprehensive Architectural Review Orchestrator

Performs holistic code and architecture analysis from a senior architect perspective.
Examines structure, patterns, SOLID principles, API design, security, scalability,
and maintainability.

Author: Asif Hussain
Version: 3.0.0


## Table of Contents

### Classes
- [ReviewFinding](#reviewfinding)
- [ReviewSection](#reviewsection)
- [ReviewOrchestrator](#revieworchestrator)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, json, os, pathlib, re, src, typing


## Classes

### ReviewFinding

```python
class ReviewFinding
```

**Decorators:** `dataclass`

Represents a single review finding.


**Attributes:**

- `severity`: str
- `category`: str
- `title`: str
- `description`: str
- `location`: Optional[str]
- `recommendation`: Optional[str]
- `root_cause`: Optional[str]



---

### ReviewSection

```python
class ReviewSection
```

**Decorators:** `dataclass`

Represents a section of the review.


**Attributes:**

- `name`: str
- `score`: int
- `findings`: List[ReviewFinding]
- `summary`: str
- `recommendations`: List[str]



---

### ReviewOrchestrator

```python
class ReviewOrchestrator(BaseOperationModule)
```

Comprehensive architectural and code quality review orchestrator.

Performs multi-phase analysis:
1. Architecture & Structure
2. Code Quality & Patterns
3. Security & Risk Assessment
4. Performance & Scalability
5. Maintainability & Technical Debt


**Methods:**

  #### `get_metadata`

  ```python
  get_metadata(self) -> OperationModuleMetadata
  ```

  Return module metadata.

  **Parameters:**

  - `self`


  **Returns:** OperationModuleMetadata


  #### `execute`

  *Decorators:* `with_progress`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Execute comprehensive architectural review.

Args:
    context: Operation context with optional keys:
        - 'path': Workspace path override
        - 'scope_filter': List of scope keywords (e.g., ['auth', 'api'])
        - 'request_context': User's feature request for contextual analysis
    
Returns:
    OperationResult with review findings and report path

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Operation context with optional keys:


  **Returns:** OperationResult
    OperationResult with review findings and report path



---
