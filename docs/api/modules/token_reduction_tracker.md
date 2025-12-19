# token_reduction_tracker

Token Reduction Tracker for CORTEX Planning

Tracks token baselines and reductions across all planning operations.
Provides consistent metrics across all orchestrators.

Author: Asif Hussain
Version: 1.0.0


## Table of Contents

### Classes
- [TokenBaseline](#tokenbaseline)
- [PhaseReduction](#phasereduction)
- [TokenReductionTracker](#tokenreductiontracker)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, json, logging, pathlib, typing


## Classes

### TokenBaseline

```python
class TokenBaseline
```

**Decorators:** `dataclass`

Token baseline for a plan.


**Attributes:**

- `plan_id`: str
- `tokens`: int
- `files`: int
- `measurement_date`: datetime


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  #### `from_dict`

  *Decorators:* `classmethod`

  ```python
  from_dict(cls, data: Dict[str, Any]) -> 'TokenBaseline'
  ```


---

### PhaseReduction

```python
class PhaseReduction
```

**Decorators:** `dataclass`

Token reduction for a single phase.


**Attributes:**

- `phase_number`: int
- `tokens_saved`: int
- `files_modified`: List[str]
- `recorded_at`: datetime


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  #### `from_dict`

  *Decorators:* `classmethod`

  ```python
  from_dict(cls, data: Dict[str, Any]) -> 'PhaseReduction'
  ```


---

### TokenReductionTracker

```python
class TokenReductionTracker
```

Unified token tracking across all plans.

Stores baselines, tracks reductions, calculates percentages.


**Methods:**

  #### `establish_baseline`

  ```python
  establish_baseline(self, plan_id: str, token_count: int, file_count: int, measurement_date: datetime)
  ```

  Record baseline for a plan.

Args:
    plan_id: Plan identifier
    token_count: Total tokens at baseline
    file_count: Total files at baseline
    measurement_date: When measurement was taken

  **Parameters:**

  - `self`
  - `plan_id` (str): Plan identifier
  - `token_count` (int): Total tokens at baseline
  - `file_count` (int): Total files at baseline
  - `measurement_date` (datetime): When measurement was taken


  #### `record_reduction`

  ```python
  record_reduction(self, plan_id: str, phase_number: int, tokens_saved: int, files_modified: List[str])
  ```

  Record token reduction for a phase.

Args:
    plan_id: Plan identifier
    phase_number: Phase number
    tokens_saved: Tokens saved in this phase
    files_modified: Files modified in this phase

  **Parameters:**

  - `self`
  - `plan_id` (str): Plan identifier
  - `phase_number` (int): Phase number
  - `tokens_saved` (int): Tokens saved in this phase
  - `files_modified` (List[str]): Files modified in this phase


  #### `get_plan_metrics`

  ```python
  get_plan_metrics(self, plan_id: str) -> Dict
  ```

  Get all metrics for a plan.

Args:
    plan_id: Plan identifier

Returns:
    Dictionary with baseline, reductions, totals

  **Parameters:**

  - `self`
  - `plan_id` (str): Plan identifier


  **Returns:** Dict
    Dictionary with baseline, reductions, totals


  #### `calculate_percentage`

  ```python
  calculate_percentage(self, baseline: int, current: int) -> float
  ```

  Calculate reduction percentage.

Args:
    baseline: Baseline token count
    current: Current token count

Returns:
    Percentage reduction (0-100)

  **Parameters:**

  - `self`
  - `baseline` (int): Baseline token count
  - `current` (int): Current token count


  **Returns:** float
    Percentage reduction (0-100)


  #### `format_tokens`

  ```python
  format_tokens(self, tokens: int, include_label: bool) -> str
  ```

  Format tokens with K/M suffix and optional label.

Args:
    tokens: Token count
    include_label: If True, append " saved" to clarify meaning

Returns:
    Formatted string (e.g., "6.7M saved", "150K saved", "500")

  **Parameters:**

  - `self`
  - `tokens` (int): Token count
  - `include_label` (bool) = `False`: If True, append " saved" to clarify meaning


  **Returns:** str
    Formatted string (e.g., "6.7M saved", "150K saved", "500")



---
