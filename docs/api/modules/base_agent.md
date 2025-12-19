# base_agent

Base Agent Module

Provides the base class for all CORTEX agents with common functionality.


## Table of Contents

### Classes
- [AgentMetrics](#agentmetrics)
- [BaseAgent](#baseagent)
- [MetricsCollector](#metricscollector)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** abc, asyncio, dataclasses, datetime, logging, time, typing


## Classes

### AgentMetrics

```python
class AgentMetrics
```

**Decorators:** `dataclass`

Metrics for agent performance tracking


**Attributes:**

- `execution_count`: int
- `total_execution_time`: float
- `last_execution_time`: Optional[datetime]
- `success_count`: int
- `error_count`: int
- `errors`: list


**Methods:**

  #### `average_execution_time`

  *Decorators:* `property`

  ```python
  average_execution_time(self) -> float
  ```

  Calculate average execution time

  **Parameters:**

  - `self`


  **Returns:** float


  #### `success_rate`

  *Decorators:* `property`

  ```python
  success_rate(self) -> float
  ```

  Calculate success rate percentage

  **Parameters:**

  - `self`


  **Returns:** float



---

### BaseAgent

```python
class BaseAgent(ABC)
```

Base class for all CORTEX agents.

Provides common functionality including:
- Logging configuration
- Metrics tracking  
- Error handling
- Execution timing
- Health monitoring


**Methods:**

  #### `execute_with_metrics`

  ```python
  execute_with_metrics(self, operation_name: str, operation_func, *args, **kwargs)
  ```

  Execute an operation with automatic metrics tracking.

Args:
    operation_name: Name of the operation for logging
    operation_func: Function to execute
    *args, **kwargs: Arguments to pass to function
    
Returns:
    Result of operation function

  **Parameters:**

  - `self`
  - `operation_name` (str): Name of the operation for logging
  - `operation_func`: Function to execute
  - `*args`
  - `**kwargs`


  #### `get_health_status`

  ```python
  get_health_status(self) -> Dict[str, Any]
  ```

  Get agent health status.

Returns:
    Dictionary with health information

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dictionary with health information


  #### `process`

  *Decorators:* `abstractmethod`

  ```python
  process(self, *args, **kwargs)
  ```

  Main processing method to be implemented by subclasses.

This is the primary entry point for agent operations.

  **Parameters:**

  - `self`
  - `*args`
  - `**kwargs`



---

### MetricsCollector

```python
class MetricsCollector
```

Collects and aggregates metrics from multiple agents


**Methods:**

  #### `register_agent`

  ```python
  register_agent(self, agent: BaseAgent)
  ```

  Register an agent for metrics collection

  **Parameters:**

  - `self`
  - `agent` (BaseAgent)


  #### `get_aggregate_metrics`

  ```python
  get_aggregate_metrics(self) -> Dict[str, Any]
  ```

  Get aggregated metrics from all registered agents

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---
