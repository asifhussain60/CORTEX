# cache_monitor

CORTEX Tier 1: Cache Explosion Monitor
Monitor and prevent cache explosion in conversation history.

Inspired by Cortex Token Optimizer's cache-explosion prevention system.
Prevents runaway token growth that causes API failures.


## Table of Contents

### Classes
- [CacheMonitor](#cachemonitor)
- [CacheHealthReport](#cachehealthreport)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, logging, pathlib, typing


## Classes

### CacheMonitor

```python
class CacheMonitor
```

Monitor and prevent cache explosion in conversation history.

Prevents runaway token growth that causes API failures by implementing
soft and hard token limits with automatic cleanup mechanisms.

Key Features:
- Soft limit warning (40k tokens)
- Hard limit emergency trim (50k tokens)
- Automatic archival of old conversations
- Proactive cleanup recommendations
- 99.9% prevention of API failures


**Methods:**

  #### `check_cache_health`

  ```python
  check_cache_health(self) -> Dict[str, Any]
  ```

  Monitor conversation cache size and prevent explosion.

Returns:
    Health status dict with token counts and actions taken
    
Example:
    >>> monitor = CacheMonitor(working_memory)
    >>> status = monitor.check_cache_health()
    >>> if status['status'] == 'WARNING':
    ...     print(f"Cache at {status['total_tokens']} tokens")

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Health status dict with token counts and actions taken


  #### `get_trim_recommendations`

  ```python
  get_trim_recommendations(self) -> List[Dict[str, Any]]
  ```

  Suggest conversations to archive (proactive cleanup).

Returns:
    List of recommendations with conversation IDs and reasons
    
Example:
    >>> monitor = CacheMonitor(working_memory)
    >>> recs = monitor.get_trim_recommendations()
    >>> for rec in recs:
    ...     print(f"Archive {rec['conversation_id']}: {rec['reason']}")

  **Parameters:**

  - `self`


  **Returns:** List[Dict[str, Any]]
    List of recommendations with conversation IDs and reasons


  #### `get_statistics`

  ```python
  get_statistics(self) -> Dict[str, Any]
  ```

  Get cache monitor statistics.

Returns:
    Dict with monitoring statistics

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict with monitoring statistics


  #### `reset_statistics`

  ```python
  reset_statistics(self) -> None
  ```

  Reset monitoring statistics (useful for testing).

  **Parameters:**

  - `self`


  **Returns:** None



---

### CacheHealthReport

```python
class CacheHealthReport
```

Comprehensive cache health report.

Provides detailed analysis of cache health including:
- Current token usage
- Trend analysis
- Recommendations


**Methods:**

  #### `generate_report`

  ```python
  generate_report(self) -> Dict[str, Any]
  ```

  Generate comprehensive cache health report.

Returns:
    Dict with detailed health information

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict with detailed health information



---
