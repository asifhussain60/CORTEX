# application_metrics

Application Metrics Collector

Collects project size, technology stack, complexity, and dependency metrics.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [ApplicationMetricsCollector](#applicationmetricscollector)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** logging, pathlib, subprocess, typing


## Classes

### ApplicationMetricsCollector

```python
class ApplicationMetricsCollector
```

Collect application-level metrics.


**Methods:**

  #### `collect`

  ```python
  collect(self, project_root: Path) -> Dict[str, Any]
  ```

  Collect application metrics.

Metrics:
    - Total files and LOC
    - Technology stack
    - Test coverage percentage
    - Code complexity
    - Dependency analysis

  **Parameters:**

  - `self`
  - `project_root` (Path)


  **Returns:** Dict[str, Any]



---
