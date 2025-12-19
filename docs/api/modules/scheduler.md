# scheduler

CORTEX 3.0 - Data Collection Scheduler (Phase 3.1)

Lightweight scheduler for triggering data collectors at a fixed interval.
Test-friendly design using a tick() method to avoid sleep in unit tests.


## Table of Contents

### Classes
- [SchedulerStats](#schedulerstats)
- [DataCollectionScheduler](#datacollectionscheduler)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** __future__, dataclasses, time, typing


## Classes

### SchedulerStats

```python
class SchedulerStats
```

**Decorators:** `dataclass`

**Attributes:**

- `runs`: int
- `last_run_ms`: float



---

### DataCollectionScheduler

```python
class DataCollectionScheduler
```

Simple, test-friendly scheduler that triggers coordinator collections.

Usage:
  sched = DataCollectionScheduler(coordinator, interval_seconds=60)
  # In production you might call run_forever(); in tests, call tick().


**Methods:**

  #### `tick`

  ```python
  tick(self, force_refresh: bool)
  ```

  Trigger one run if interval elapsed since last run (or always if first run).

  **Parameters:**

  - `self`
  - `force_refresh` (bool) = `False`


  #### `run_forever`

  ```python
  run_forever(self, force_refresh: bool)
  ```

  Naive loop runner (useful for manual runs).

  **Parameters:**

  - `self`
  - `force_refresh` (bool) = `False`



---
