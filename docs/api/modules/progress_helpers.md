# progress_helpers

Progress Helpers

Helper functions for calculating and displaying phase progress.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0


## Table of Contents

### Classes
- [PhaseProgressCalculator](#phaseprogresscalculator)
- [ProgressBarGenerator](#progressbargenerator)
- [SyncContextGenerator](#synccontextgenerator)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** re, src, typing


## Classes

### PhaseProgressCalculator

```python
class PhaseProgressCalculator
```

Calculates phase completion percentages from status document content.


**Methods:**

  #### `calculate`

  ```python
  calculate(self, content: str) -> tuple[Dict[str, int], List[str]]
  ```

  Calculate phase completion percentages AND execution order by parsing Current Focus.

Returns:
    Tuple of (phase_progress_dict, execution_order_list)
    - phase_progress_dict: Maps phase names to completion percentages (0-100)
    - execution_order_list: List of phase names in user-specified execution order

  **Parameters:**

  - `self`
  - `content` (str)


  **Returns:** tuple[Dict[str, int], List[str]]
    Tuple of (phase_progress_dict, execution_order_list) - phase_progress_dict: Maps phase names to completion percentages (0-100) - execution_order_list: List of phase names in user-specified execution order



---

### ProgressBarGenerator

```python
class ProgressBarGenerator
```

Generates visual ASCII progress bars.


**Methods:**

  #### `generate`

  ```python
  generate(self, percentage: int, width: int) -> str
  ```

  Generate visual progress bar with █ (complete) and ░ (remaining).

Args:
    percentage: Completion percentage (0-100)
    width: Total width of progress bar in characters
    
Returns:
    Progress bar string like "[████████████████████░░░░░░░░]"

  **Parameters:**

  - `self`
  - `percentage` (int): Completion percentage (0-100)
  - `width` (int) = `32`: Total width of progress bar in characters


  **Returns:** str
    Progress bar string like "[████████████████████░░░░░░░░]"



---

### SyncContextGenerator

```python
class SyncContextGenerator
```

Generates contextual suffix for sync timestamp.


**Methods:**

  #### `generate`

  ```python
  generate(self, updates: List[str], impl_state: ImplementationState, transformations: Dict[str, Any]) -> str
  ```

  Add contextual suffix to sync timestamp based on what changed.

Analyzes the updates and transformations to generate a meaningful
description like "(design_sync + deployment updates)" instead of
just generic "(design_sync)".

Args:
    updates: Recent updates list
    impl_state: Implementation state
    transformations: Transformations applied
    
Returns:
    Contextual suffix string

  **Parameters:**

  - `self`
  - `updates` (List[str]): Recent updates list
  - `impl_state` (ImplementationState): Implementation state
  - `transformations` (Dict[str, Any]): Transformations applied


  **Returns:** str
    Contextual suffix string



---
