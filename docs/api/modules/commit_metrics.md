# commit_metrics

Commit Metrics Collector

Collects build success, deployment frequency, and rollback rate metrics.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [CommitMetricsCollector](#commitmetricscollector)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** logging, pathlib, subprocess, typing


## Classes

### CommitMetricsCollector

```python
class CommitMetricsCollector
```

Collect commit-related metrics.


**Methods:**

  #### `collect`

  ```python
  collect(self, project_root: Path) -> Dict[str, Any]
  ```

  Collect commit metrics.

Metrics:
    - Build success rate
    - Deployment frequency
    - Rollback rate
    - Mean time to recovery (MTTR)
    - Failed build patterns

  **Parameters:**

  - `self`
  - `project_root` (Path)


  **Returns:** Dict[str, Any]



---
