# tdd_mastery

TDD Mastery Collector

Collects test coverage, test-first adherence, and test execution metrics.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [TDDMasteryCollector](#tddmasterycollector)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** logging, pathlib, typing


## Classes

### TDDMasteryCollector

```python
class TDDMasteryCollector
```

Collect TDD mastery metrics.


**Methods:**

  #### `collect`

  ```python
  collect(self, project_root: Path) -> Dict[str, Any]
  ```

  Collect TDD mastery metrics.

Metrics:
    - Test-first adherence percentage
    - Red-Green-Refactor cycle compliance
    - First-run test success rate
    - Test coverage trends
    - Test execution speed

  **Parameters:**

  - `self`
  - `project_root` (Path)


  **Returns:** Dict[str, Any]



---
