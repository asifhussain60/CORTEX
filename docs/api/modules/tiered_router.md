# tiered_router

Tiered Router for CORTEX Planning System 3.0

This module implements LLM-based operation classification into 4 tiers:
- Tier 1: Instant (<2s) - CLI operations, status checks
- Tier 2: Lightweight (<10s) - Single file changes
- Tier 3: Documented (10-60min) - Feature additions
- Tier 4: Complex (>1h) - Architecture changes

Author: Asif Hussain
Version: 3.0.0
Phase: 01 of CORTEX Evolution v3.9


## Table of Contents

### Classes
- [OperationTier](#operationtier)
- [RoutingDecision](#routingdecision)
- [RoutingFeedback](#routingfeedback)
- [RegexFallback](#regexfallback)
- [RoutingTelemetry](#routingtelemetry)
- [TieredRouter](#tieredrouter)


## Overview

- **Classes:** 6
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, enum, hashlib, json, logging, re, time, typing


## Classes

### OperationTier

```python
class OperationTier(Enum)
```

Operation complexity tiers.



---

### RoutingDecision

```python
class RoutingDecision
```

**Decorators:** `dataclass`

Result of routing classification.


**Attributes:**

- `tier`: int
- `confidence`: float
- `reasoning`: str
- `execution_method`: str
- `estimated_time`: str
- `requires_planning`: bool
- `timestamp`: datetime
- `cache_hit`: bool



---

### RoutingFeedback

```python
class RoutingFeedback
```

**Decorators:** `dataclass`

User feedback on routing accuracy.


**Attributes:**

- `operation`: str
- `expected_tier`: int
- `actual_tier`: int
- `timestamp`: datetime



---

### RegexFallback

```python
class RegexFallback
```

Regex-based fallback classifier when LLM unavailable.


**Methods:**

  #### `classify`

  ```python
  classify(self, operation: str) -> int
  ```

  Classify operation using regex patterns.

  **Parameters:**

  - `self`
  - `operation` (str)


  **Returns:** int



---

### RoutingTelemetry

```python
class RoutingTelemetry
```

Track routing accuracy and performance.


**Methods:**

  #### `record_decision`

  ```python
  record_decision(self, decision: RoutingDecision)
  ```

  Record routing decision.

  **Parameters:**

  - `self`
  - `decision` (RoutingDecision)


  #### `record_feedback`

  ```python
  record_feedback(self, operation: str, expected_tier: int, actual_tier: int)
  ```

  Record user feedback on routing accuracy.

  **Parameters:**

  - `self`
  - `operation` (str)
  - `expected_tier` (int)
  - `actual_tier` (int)


  #### `calculate_accuracy`

  ```python
  calculate_accuracy(self, last_n: int) -> float
  ```

  Calculate routing accuracy over last N operations.

  **Parameters:**

  - `self`
  - `last_n` (int) = `100`


  **Returns:** float


  #### `get_metrics`

  ```python
  get_metrics(self) -> Dict[str, Any]
  ```

  Get telemetry metrics.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

### TieredRouter

```python
class TieredRouter
```

LLM-based router for 4-tier operation classification.


**Methods:**

  #### `route`

  ```python
  route(self, operation: str, context: Dict[str, Any]) -> RoutingDecision
  ```

  Route operation to appropriate tier (1-4).

Args:
    operation: Operation name/description
    context: Optional context dictionary
    
Returns:
    RoutingDecision with tier, confidence, reasoning

  **Parameters:**

  - `self`
  - `operation` (str): Operation name/description
  - `context` (Dict[str, Any]) = `None`: Optional context dictionary


  **Returns:** RoutingDecision
    RoutingDecision with tier, confidence, reasoning


  #### `get_telemetry`

  ```python
  get_telemetry(self) -> Dict[str, Any]
  ```

  Get routing telemetry metrics.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]


  #### `provide_feedback`

  ```python
  provide_feedback(self, operation: str, expected_tier: int, actual_tier: int)
  ```

  Provide feedback on routing accuracy for learning.

  **Parameters:**

  - `self`
  - `operation` (str)
  - `expected_tier` (int)
  - `actual_tier` (int)



---
