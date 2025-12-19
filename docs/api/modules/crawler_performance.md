# crawler_performance

Crawler Performance Collector

Collects discovery statistics, cache efficiency, and error patterns.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [CrawlerPerformanceCollector](#crawlerperformancecollector)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, logging, pathlib, sqlite3, typing


## Classes

### CrawlerPerformanceCollector

```python
class CrawlerPerformanceCollector
```

Collect crawler performance metrics.


**Methods:**

  #### `collect`

  ```python
  collect(self, project_root: Path) -> Dict[str, Any]
  ```

  Collect crawler performance metrics.

Metrics:
    - Discovery runs count and success rate
    - Average execution duration
    - Elements discovered and cached
    - Cache hit rate
    - Error patterns and retry stats

  **Parameters:**

  - `self`
  - `project_root` (Path)


  **Returns:** Dict[str, Any]



---
