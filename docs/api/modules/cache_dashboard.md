# cache_dashboard

Cache Performance Dashboard
Display cache statistics, effectiveness metrics, and recommendations

Shows:
- Hit rates by operation (align, deploy, optimize, cleanup)
- Cache size and entry age distribution
- Performance impact (time saved)
- Recommendations for optimization

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [CacheMetrics](#cachemetrics)
- [CacheDashboard](#cachedashboard)

### Functions
- [main](#main)


## Overview

- **Classes:** 2
- **Functions:** 1
- **Dependencies:** argparse, dataclasses, datetime, logging, pathlib, rich, sqlite3, src, typing


## Classes

### CacheMetrics

```python
class CacheMetrics
```

**Decorators:** `dataclass`

Cache metrics for an operation.


**Attributes:**

- `operation`: str
- `total_entries`: int
- `hits`: int
- `misses`: int
- `hit_rate`: float
- `avg_entry_age_hours`: float
- `oldest_entry_days`: float
- `cache_size_mb`: float
- `estimated_time_saved_seconds`: float



---

### CacheDashboard

```python
class CacheDashboard
```

Cache performance dashboard with Rich visualization.

Provides comprehensive view of:
- Cache effectiveness (hit rates)
- Cache health (size, age, staleness)
- Performance impact (time saved)
- Optimization recommendations


**Methods:**

  #### `show_dashboard`

  ```python
  show_dashboard(self, detailed: bool)
  ```

  Display cache performance dashboard.

Args:
    detailed: Show detailed per-key statistics

  **Parameters:**

  - `self`
  - `detailed` (bool) = `False`: Show detailed per-key statistics



---

## Functions

### main

```python
main()
```

CLI entry point for cache dashboard.


---
