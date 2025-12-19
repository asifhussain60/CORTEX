# real_time_collectors

CORTEX 3.0 Real-Time Data Collectors
====================================

Data collection system for feeding template variables with live metrics.
Eliminates mock data and provides real intelligence for question routing.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Feature: Quick Win #3 (Week 1) - Real-Time Data Collectors


## Table of Contents

### Classes
- [CollectorResult](#collectorresult)
- [BaseDataCollector](#basedatacollector)
- [BrainMetricsCollector](#brainmetricscollector)
- [WorkspaceHealthCollector](#workspacehealthcollector)
- [PerformanceCollector](#performancecollector)
- [TokenUsageCollector](#tokenusagecollector)
- [ConversationQualityCollector](#conversationqualitycollector)
- [DataCollectionCoordinator](#datacollectioncoordinator)

### Functions
- [main](#main)


## Overview

- **Classes:** 8
- **Functions:** 1
- **Dependencies:** abc, dataclasses, datetime, json, os, sqlite3, sys, time, typing


## Classes

### CollectorResult

```python
class CollectorResult
```

**Decorators:** `dataclass`

Standardized result from any data collector


**Attributes:**

- `collector_name`: str
- `data`: Dict[str, Any]
- `timestamp`: datetime
- `success`: bool
- `error_message`: Optional[str]
- `collection_time_ms`: float



---

### BaseDataCollector

```python
class BaseDataCollector(ABC)
```

Base class for all CORTEX data collectors


**Methods:**

  #### `collect`

  *Decorators:* `abstractmethod`

  ```python
  collect(self) -> Dict[str, Any]
  ```

  Collect data from source. Must be implemented by subclasses.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]


  #### `collect_with_cache`

  ```python
  collect_with_cache(self, force_refresh: bool) -> CollectorResult
  ```

  Collect data with caching support

  **Parameters:**

  - `self`
  - `force_refresh` (bool) = `False`


  **Returns:** CollectorResult



---

### BrainMetricsCollector

```python
class BrainMetricsCollector(BaseDataCollector)
```

Collects CORTEX brain health and performance metrics


**Methods:**

  #### `collect`

  ```python
  collect(self) -> Dict[str, Any]
  ```

  Collect brain metrics from CORTEX memory tiers

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

### WorkspaceHealthCollector

```python
class WorkspaceHealthCollector(BaseDataCollector)
```

Collects workspace code quality, build status, and health metrics


**Methods:**

  #### `collect`

  ```python
  collect(self) -> Dict[str, Any]
  ```

  Collect workspace health metrics

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

### PerformanceCollector

```python
class PerformanceCollector(BaseDataCollector)
```

Collects system performance metrics


**Methods:**

  #### `collect`

  ```python
  collect(self) -> Dict[str, Any]
  ```

  Collect performance metrics

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

### TokenUsageCollector

```python
class TokenUsageCollector(BaseDataCollector)
```

Collects token usage and template efficiency metrics (Phase 3.2).


**Methods:**

  #### `collect`

  ```python
  collect(self) -> Dict[str, Any]
  ```


---

### ConversationQualityCollector

```python
class ConversationQualityCollector(BaseDataCollector)
```

Scores conversation quality and capture recommendations (Phase 3.2).


**Methods:**

  #### `collect`

  ```python
  collect(self) -> Dict[str, Any]
  ```


---

### DataCollectionCoordinator

```python
class DataCollectionCoordinator
```

Coordinates all data collectors and provides unified interface


**Methods:**

  #### `collect_all`

  ```python
  collect_all(self, force_refresh: bool) -> Dict[str, CollectorResult]
  ```

  Collect data from all collectors

  **Parameters:**

  - `self`
  - `force_refresh` (bool) = `False`


  **Returns:** Dict[str, CollectorResult]


  #### `collect_for_template`

  ```python
  collect_for_template(self, template_name: str, force_refresh: bool) -> Dict[str, Any]
  ```

  Collect data needed for a specific template

  **Parameters:**

  - `self`
  - `template_name` (str)
  - `force_refresh` (bool) = `False`


  **Returns:** Dict[str, Any]


  #### `get_health_summary`

  ```python
  get_health_summary(self) -> Dict[str, Any]
  ```

  Get overall health summary across all collectors

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

## Functions

### main

```python
main()
```

Test the data collection system


---
