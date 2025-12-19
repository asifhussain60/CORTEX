# velocity_metrics

Velocity Metrics Collector

Collects sprint velocity, cycle time, and estimate accuracy metrics.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [VelocityMetricsCollector](#velocitymetricscollector)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** logging, pathlib, sqlite3, typing


## Classes

### VelocityMetricsCollector

```python
class VelocityMetricsCollector
```

Collect development velocity metrics.


**Methods:**

  #### `collect`

  ```python
  collect(self, project_root: Path) -> Dict[str, Any]
  ```

  Collect velocity metrics.

Metrics:
    - Story points per sprint
    - Average cycle time
    - Estimate accuracy percentage
    - Lead time for changes
    - Throughput trends

  **Parameters:**

  - `self`
  - `project_root` (Path)


  **Returns:** Dict[str, Any]



---
