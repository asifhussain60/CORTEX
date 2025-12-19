# real_time_metrics_dashboard

CORTEX 3.0 Phase 2 - Real-Time Metrics Dashboard
===============================================

Real-time metrics dashboard integrating Phase 1 data collectors with Phase 2 brain optimization.
Provides unified monitoring, health scoring, and performance analytics.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Phase: Phase 2 - Data Collection Integration (Task 3)
Integration: Phase 1 Data Collectors + Phase 2 Brain Optimization


## Table of Contents

### Classes
- [DashboardStatus](#dashboardstatus)
- [MetricSeverity](#metricseverity)
- [DashboardAlert](#dashboardalert)
- [UnifiedMetricsSnapshot](#unifiedmetricssnapshot)
- [RealTimeMetricsDashboard](#realtimemetricsdashboard)

### Functions
- [create_real_time_dashboard](#create_real_time_dashboard)
- [get_dashboard_summary](#get_dashboard_summary)


## Overview

- **Classes:** 5
- **Functions:** 2
- **Dependencies:** dataclasses, datetime, enum, json, logging, pathlib, sqlite3, src, threading, time, typing


## Classes

### DashboardStatus

```python
class DashboardStatus(Enum)
```

Dashboard status levels



---

### MetricSeverity

```python
class MetricSeverity(Enum)
```

Metric severity levels



---

### DashboardAlert

```python
class DashboardAlert
```

**Decorators:** `dataclass`

Dashboard alert data structure


**Attributes:**

- `timestamp`: datetime
- `severity`: MetricSeverity
- `component`: str
- `metric`: str
- `value`: Union[float, int, str]
- `threshold`: Union[float, int, str]
- `message`: str
- `action_required`: bool



---

### UnifiedMetricsSnapshot

```python
class UnifiedMetricsSnapshot
```

**Decorators:** `dataclass`

Unified snapshot of all CORTEX metrics


**Attributes:**

- `timestamp`: datetime
- `collectors_active`: int
- `collectors_total`: int
- `collection_success_rate`: float
- `avg_collection_time_ms`: float
- `brain_health_score`: float
- `tier1_performance_ms`: float
- `tier2_performance_ms`: float
- `tier3_performance_ms`: float
- `cache_hit_rate`: float
- `cache_memory_mb`: float
- `memory_usage_mb`: float
- `memory_pressure`: str
- `templates_used_24h`: int
- `avg_template_response_time_ms`: float
- `template_success_rate`: float
- `tokens_used_24h`: int
- `token_optimization_rate`: float
- `estimated_cost_24h`: float
- `workspace_health_score`: float
- `files_monitored`: int
- `build_status`: str
- `test_coverage`: float
- `active_alerts`: List[DashboardAlert]



---

### RealTimeMetricsDashboard

```python
class RealTimeMetricsDashboard
```

Real-time metrics dashboard for CORTEX 3.0.

Integrates Phase 1 data collectors with Phase 2 brain optimization
to provide unified monitoring, alerting, and performance analytics.

Features:
- Unified metrics collection from all components
- Real-time health monitoring with alerting
- Performance trend analysis
- Optimization recommendations
- Historical data storage


**Methods:**

  #### `start_monitoring`

  ```python
  start_monitoring(self)
  ```

  Start real-time monitoring.

  **Parameters:**

  - `self`


  #### `stop_monitoring`

  ```python
  stop_monitoring(self)
  ```

  Stop real-time monitoring.

  **Parameters:**

  - `self`


  #### `get_current_dashboard_state`

  ```python
  get_current_dashboard_state(self) -> Dict[str, Any]
  ```

  Get current dashboard state and latest metrics.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]


  #### `get_unified_metrics_snapshot`

  ```python
  get_unified_metrics_snapshot(self) -> Optional[UnifiedMetricsSnapshot]
  ```

  Collect unified metrics snapshot from all systems.

  **Parameters:**

  - `self`


  **Returns:** Optional[UnifiedMetricsSnapshot]



---

## Functions

### create_real_time_dashboard

```python
create_real_time_dashboard(brain_path: str, workspace_path: str, config: Dict[str, Any]) -> RealTimeMetricsDashboard
```

Create and start real-time metrics dashboard.

Args:
    brain_path: Path to CORTEX brain directory
    workspace_path: Path to workspace
    config: Dashboard configuration
    
Returns:
    Initialized and running RealTimeMetricsDashboard


**Parameters:**

- `brain_path` (str) = `None`: Path to CORTEX brain directory
- `workspace_path` (str) = `None`: Path to workspace
- `config` (Dict[str, Any]) = `None`: Dashboard configuration


**Returns:** RealTimeMetricsDashboard
  Initialized and running RealTimeMetricsDashboard


---

### get_dashboard_summary

```python
get_dashboard_summary(dashboard: RealTimeMetricsDashboard) -> Dict[str, Any]
```

Get comprehensive dashboard summary.

Args:
    dashboard: Dashboard instance
    
Returns:
    Dashboard summary with all key metrics


**Parameters:**

- `dashboard` (RealTimeMetricsDashboard): Dashboard instance


**Returns:** Dict[str, Any]
  Dashboard summary with all key metrics


---
