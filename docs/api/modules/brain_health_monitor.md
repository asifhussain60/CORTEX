# brain_health_monitor

Brain Health Monitor

Monitors health and performance of all 3 brain tiers, detects corruption,
generates health reports, and provides CLI dashboard.

Responsibilities:
- Check overall brain health status (healthy/degraded/critical)
- Monitor tier-specific metrics (database size, record counts, FTS5 status)
- Detect database corruption
- Generate human-readable health reports
- Display CLI health dashboard
- Measure query performance

Usage:
    >>> from src.tier0.brain_health_monitor import BrainHealthMonitor
    >>> monitor = BrainHealthMonitor(brain_path="/path/to/cortex-brain")
    >>> health = monitor.check_health()
    >>> print(f"Status: {health['status']}")
    >>> monitor.display_dashboard()

Author: Asif Hussain
Phase: 7.3 - Brain Initialization System


## Table of Contents

### Classes
- [BrainHealthMonitor](#brainhealthmonitor)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, json, pathlib, sqlite3, time, typing


## Classes

### BrainHealthMonitor

```python
class BrainHealthMonitor
```

Monitors brain health across all 3 tiers.

Provides health checks, corruption detection, reporting,
and performance monitoring.


**Methods:**

  #### `check_health`

  ```python
  check_health(self) -> Dict[str, Any]
  ```

  Check overall brain health.

Aggregates health from all 3 tiers and determines overall status.

Returns:
    Dict with status (healthy/degraded/critical) and tier details

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict with status (healthy/degraded/critical) and tier details


  #### `check_tier1`

  ```python
  check_tier1(self) -> Dict[str, Any]
  ```

  Check Tier 1 (Working Memory) health.

Returns:
    Dict with database status, version, counts, and size

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict with database status, version, counts, and size


  #### `check_tier2`

  ```python
  check_tier2(self) -> Dict[str, Any]
  ```

  Check Tier 2 (Knowledge Graph) health.

Returns:
    Dict with database status, pattern/relationship counts, FTS5 status

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict with database status, pattern/relationship counts, FTS5 status


  #### `check_tier3`

  ```python
  check_tier3(self) -> Dict[str, Any]
  ```

  Check Tier 3 (Development Context) health.

Returns:
    Dict with database status, metrics count, git activity tracking

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict with database status, metrics count, git activity tracking


  #### `generate_report`

  ```python
  generate_report(self) -> str
  ```

  Generate human-readable health report.

Returns:
    Markdown-formatted health report

  **Parameters:**

  - `self`


  **Returns:** str
    Markdown-formatted health report


  #### `display_dashboard`

  ```python
  display_dashboard(self)
  ```

  Display CLI health dashboard.

Prints colored dashboard to stdout.

  **Parameters:**

  - `self`


  #### `get_performance_metrics`

  ```python
  get_performance_metrics(self) -> Dict[str, float]
  ```

  Get query performance metrics.

Measures average query time for each tier.

Returns:
    Dict with average query times in milliseconds

  **Parameters:**

  - `self`


  **Returns:** Dict[str, float]
    Dict with average query times in milliseconds



---
