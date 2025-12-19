# orchestration_metrics_collector

Orchestration Metrics Collector - Silent background metrics for orchestrator engagement.

**Purpose:** Enable visibility into which orchestrators handle requests and their execution efficiency.
**Performance:** <5ms overhead per metric collection
**Storage:** logs/orchestration-metrics/{YYYY-MM-DD}/events.jsonl (git-ignored)
**Retention:** 30 days auto-archival

**Usage:**
    from src.operations.utilities.orchestration_metrics_collector import with_orchestration_metrics

    @with_orchestration_metrics
    async def my_orchestrator_handler(request):
        # Your orchestrator logic
        return response

**Author:** Asif Hussain
**Feature:** Orchestrator Enhancement Plan v2.0 - Feature 10


## Table of Contents

### Classes
- [OrchestrationMetricsCollector](#orchestrationmetricscollector)

### Functions
- [with_orchestration_metrics](#with_orchestration_metrics)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** datetime, functools, json, logging, pathlib, shutil, time, typing, uuid


## Classes

### OrchestrationMetricsCollector

```python
class OrchestrationMetricsCollector
```

Silent background collector for orchestrator engagement metrics.

**Responsibilities:**
1. Log engagement_start events with event_id, orchestrator_name, timestamp
2. Log engagement_complete events with matching event_id, duration, outcome
3. Auto-create daily folders: logs/orchestration-metrics/{YYYY-MM-DD}/
4. Write JSONL events (one JSON object per line)
5. Performance: <5ms per operation
6. Report generation: 7-day aggregation with statistics
7. Retention policy: Archive data older than 30 days


**Methods:**

  #### `log_engagement_start`

  ```python
  log_engagement_start(self, orchestrator_name: str, operation_type: str, event_id: Optional[str], metadata: Optional[Dict[str, Any]]) -> str
  ```

  Log orchestrator engagement start event.

Args:
    orchestrator_name: Name of orchestrator (e.g., "PlanningOrchestrator")
    operation_type: Type of operation (e.g., "plan_generation", "test_execution")
    event_id: Optional event ID (auto-generated UUID if not provided)
    metadata: Optional metadata dictionary

Returns:
    event_id for matching with engagement_complete

  **Parameters:**

  - `self`
  - `orchestrator_name` (str): Name of orchestrator (e.g., "PlanningOrchestrator")
  - `operation_type` (str): Type of operation (e.g., "plan_generation", "test_execution")
  - `event_id` (Optional[str]) = `None`: Optional event ID (auto-generated UUID if not provided)
  - `metadata` (Optional[Dict[str, Any]]) = `None`: Optional metadata dictionary


  **Returns:** str
    event_id for matching with engagement_complete


  #### `log_engagement_complete`

  ```python
  log_engagement_complete(self, event_id: str, status: str, result_summary: Optional[str], error_message: Optional[str], duration_ms: Optional[float], metadata: Optional[Dict[str, Any]]) -> bool
  ```

  Log orchestrator engagement completion event.

Args:
    event_id: Event ID from log_engagement_start (for matching)
    status: "success" or "error"
    result_summary: Optional summary of result
    error_message: Optional error message if status="error"
    duration_ms: Optional execution duration in milliseconds (calculated if not provided)
    metadata: Optional metadata dictionary

Returns:
    True if logged successfully

  **Parameters:**

  - `self`
  - `event_id` (str): Event ID from log_engagement_start (for matching)
  - `status` (str) = `'success'`: "success" or "error"
  - `result_summary` (Optional[str]) = `None`: Optional summary of result
  - `error_message` (Optional[str]) = `None`: Optional error message if status="error"
  - `duration_ms` (Optional[float]) = `None`: Optional execution duration in milliseconds (calculated if not provided)
  - `metadata` (Optional[Dict[str, Any]]) = `None`: Optional metadata dictionary


  **Returns:** bool
    True if logged successfully


  #### `generate_report`

  ```python
  generate_report(self, days: int) -> Dict[str, Any]
  ```

  Generate aggregated metrics report for last N days.

Args:
    days: Number of days to include in report (default: 7)

Returns:
    Dictionary with aggregate statistics:
    - total_engagements: Total count
    - by_orchestrator: {orchestrator_name: {count, avg_duration_ms, success_rate}}
    - by_day: {YYYY-MM-DD: count}
    - avg_duration_ms: Overall average
    - success_rate: Overall success percentage

  **Parameters:**

  - `self`
  - `days` (int) = `7`: Number of days to include in report (default: 7)


  **Returns:** Dict[str, Any]
    Dictionary with aggregate statistics: - total_engagements: Total count - by_orchestrator: {orchestrator_name: {count, avg_duration_ms, success_rate}} - by_day: {YYYY-MM-DD: count} - avg_duration_ms: Overall average - success_rate: Overall success percentage


  #### `apply_retention_policy`

  ```python
  apply_retention_policy(self, days: int) -> int
  ```

  Archive metrics data older than specified days.

Args:
    days: Number of days to retain (default: 30)

Returns:
    Number of folders archived

  **Parameters:**

  - `self`
  - `days` (int) = `30`: Number of days to retain (default: 30)


  **Returns:** int
    Number of folders archived



---

## Functions

### with_orchestration_metrics

```python
with_orchestration_metrics(orchestrator_name: str)
```

Decorator for automatic orchestrator metrics collection.

Usage:
    @with_orchestration_metrics("MyOrchestrator")
    def my_orchestrator(request):
        return response

Features:
- Auto-logs engagement_start before function execution
- Auto-logs engagement_complete after function execution
- Tracks duration and status (success/error)
- <5ms overhead per call

Args:
    orchestrator_name: Name of orchestrator for metrics tracking


**Parameters:**

- `orchestrator_name` (str): Name of orchestrator for metrics tracking


---
