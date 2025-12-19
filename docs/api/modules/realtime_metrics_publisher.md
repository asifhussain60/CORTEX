# realtime_metrics_publisher

Real-Time Metrics Publisher

Extends RealTimeMetricsDashboard with WebSocket broadcasting capabilities.
Publishes metrics updates to connected WebSocket clients in real-time.

Architecture:
    RealTimeMetricsDashboard -> MetricsPublisher -> WebSocket Server -> Clients
         |                           |                    |              |
    Metrics Collection        Event-driven            Broadcasting   Dashboard UI
         |                      Observer                  |              |
    Every N seconds            Pattern              Rate limiting    Auto-update

Features:
    - WebSocket broadcasting integration
    - Event-driven observer pattern
    - Metrics aggregation and filtering
    - Operation progress tracking
    - Configurable publish intervals
    - Graceful degradation (works without WebSocket server)

Usage:
    publisher = RealtimeMetricsPublisher(
        dashboard=dashboard,
        websocket_server=server
    )
    
    # Start publishing
    await publisher.start()
    
    # Publish operation progress
    await publisher.publish_operation_progress(
        operation='sync',
        progress=50,
        status='Processing files...'
    )
    
    # Stop publishing
    await publisher.stop()

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [PublishChannel](#publishchannel)
- [OperationProgress](#operationprogress)
- [MetricsUpdate](#metricsupdate)
- [RealtimeMetricsPublisher](#realtimemetricspublisher)

### Functions
- [main](#main)


## Overview

- **Classes:** 4
- **Functions:** 1
- **Dependencies:** asyncio, dataclasses, datetime, enum, logging, modules, src, typing


## Classes

### PublishChannel

```python
class PublishChannel(Enum)
```

WebSocket publish channels.



---

### OperationProgress

```python
class OperationProgress
```

**Decorators:** `dataclass`

Operation progress data.


**Attributes:**

- `operation`: str
- `progress`: float
- `total`: Optional[int]
- `current`: Optional[int]
- `status`: str
- `timestamp`: datetime
- `metadata`: Dict[str, Any]



---

### MetricsUpdate

```python
class MetricsUpdate
```

**Decorators:** `dataclass`

Metrics update message.


**Attributes:**

- `type`: str
- `channel`: str
- `timestamp`: str
- `data`: Dict[str, Any]



---

### RealtimeMetricsPublisher

```python
class RealtimeMetricsPublisher
```

Real-time metrics publisher with WebSocket broadcasting.

Extends RealTimeMetricsDashboard to publish metrics updates
to connected WebSocket clients.

Features:
    - Event-driven metrics publishing
    - WebSocket broadcasting integration
    - Operation progress tracking
    - Channel-based subscriptions
    - Metrics aggregation
    - Graceful degradation

Attributes:
    dashboard (RealTimeMetricsDashboard): Metrics dashboard
    websocket_server (RealtimeDashboardServer): WebSocket server
    publish_interval (float): Publish interval (seconds)
    _running (bool): Publisher running state
    _publish_task (asyncio.Task): Publishing task


**Methods:**

  #### `start`

  ```python
  start(self)
  ```

  Start metrics publishing.

  **Parameters:**

  - `self`


  #### `stop`

  ```python
  stop(self)
  ```

  Stop metrics publishing.

  **Parameters:**

  - `self`


  #### `publish_operation_progress`

  ```python
  publish_operation_progress(self, operation: str, progress: float, status: str, total: Optional[int], current: Optional[int], metadata: Optional[Dict[str, Any]])
  ```

  Publish operation progress update.

Args:
    operation: Operation name (sync, optimize, deploy, etc.)
    progress: Progress percentage (0-100)
    status: Status message
    total: Total items (optional)
    current: Current item (optional)
    metadata: Additional metadata (optional)

  **Parameters:**

  - `self`
  - `operation` (str): Operation name (sync, optimize, deploy, etc.)
  - `progress` (float): Progress percentage (0-100)
  - `status` (str): Status message
  - `total` (Optional[int]) = `None`: Total items (optional)
  - `current` (Optional[int]) = `None`: Current item (optional)
  - `metadata` (Optional[Dict[str, Any]]) = `None`: Additional metadata (optional)


  #### `publish_alert`

  ```python
  publish_alert(self, severity: MetricSeverity, component: str, metric: str, value: Any, threshold: Any, message: str, action_required: bool)
  ```

  Publish alert to WebSocket clients.

Args:
    severity: Alert severity
    component: Component name
    metric: Metric name
    value: Current value
    threshold: Threshold value
    message: Alert message
    action_required: Whether action is required

  **Parameters:**

  - `self`
  - `severity` (MetricSeverity): Alert severity
  - `component` (str): Component name
  - `metric` (str): Metric name
  - `value` (Any): Current value
  - `threshold` (Any): Threshold value
  - `message` (str): Alert message
  - `action_required` (bool) = `False`: Whether action is required


  #### `publish_health_update`

  ```python
  publish_health_update(self, health_score: float, components: Dict[str, Any])
  ```

  Publish health update to WebSocket clients.

Args:
    health_score: Overall health score (0-100)
    components: Component health details

  **Parameters:**

  - `self`
  - `health_score` (float): Overall health score (0-100)
  - `components` (Dict[str, Any]): Component health details


  #### `get_active_operations`

  ```python
  get_active_operations(self) -> Dict[str, OperationProgress]
  ```

  Get all active operations.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, OperationProgress]


  #### `clear_completed_operation`

  ```python
  clear_completed_operation(self, operation: str)
  ```

  Clear completed operation from tracking.

  **Parameters:**

  - `self`
  - `operation` (str)



---

## Functions

### main

```python
main()
```

Example publisher usage.


---
