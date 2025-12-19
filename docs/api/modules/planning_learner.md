# planning_learner

Planning Learner - Continuous improvement for routing accuracy.

Tracks routing decisions, collects feedback, and adapts complexity
scoring to improve Planning System 3.0 tier classification.

Copyright © 2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [RoutingDecision](#routingdecision)
- [PlanningLearner](#planninglearner)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, json, logging, pathlib, typing


## Classes

### RoutingDecision

```python
class RoutingDecision
```

**Decorators:** `dataclass`

Record of a routing decision for learning.


**Attributes:**

- `request`: str
- `predicted_tier`: int
- `actual_tier`: Optional[int]
- `complexity_score`: float
- `timestamp`: str
- `feedback`: Optional[str]
- `was_correct`: Optional[bool]



---

### PlanningLearner

```python
class PlanningLearner
```

Learns from routing decisions to improve accuracy.


**Methods:**

  #### `record_decision`

  ```python
  record_decision(self, request: str, tier: int, complexity: float)
  ```

  Record a routing decision for future learning.

Args:
    request: User request text
    tier: Predicted tier (1-4)
    complexity: Overall complexity score

  **Parameters:**

  - `self`
  - `request` (str): User request text
  - `tier` (int): Predicted tier (1-4)
  - `complexity` (float): Overall complexity score


  #### `provide_feedback`

  ```python
  provide_feedback(self, request: str, correct_tier: int, reason: str)
  ```

  User provides feedback on routing accuracy.

Args:
    request: Original request text
    correct_tier: Actual correct tier (1-4)
    reason: Optional explanation for correction

  **Parameters:**

  - `self`
  - `request` (str): Original request text
  - `correct_tier` (int): Actual correct tier (1-4)
  - `reason` (str) = `None`: Optional explanation for correction


  #### `get_accuracy_metrics`

  ```python
  get_accuracy_metrics(self) -> Dict[str, Any]
  ```

  Calculate current routing accuracy metrics.

Returns:
    Dictionary with accuracy metrics and breakdown

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dictionary with accuracy metrics and breakdown


  #### `get_calibration_summary`

  ```python
  get_calibration_summary(self) -> str
  ```

  Get human-readable calibration summary.

Returns:
    Formatted string with current weights

  **Parameters:**

  - `self`


  **Returns:** str
    Formatted string with current weights



---
