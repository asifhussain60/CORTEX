# healthcheck_utility

Minimal Health Check Utility - Fast & Reliable

Lightweight healthcheck for CORTEX system monitoring without complex dependencies.

Design Goals:
    - Execute in <3 seconds
    - Clear pass/fail reporting
    - No complex dependencies
    - User-facing operation
    - Actionable error messages

Health Checks (8 Core):
    1. System resources (CPU, memory, disk)
    2. Brain tier structure (tier0-3)
    3. Database health (working_memory, knowledge_graph, development_context)
    4. Response templates loaded
    5. Protection rules valid
    6. Core modules present (orchestrators/agents)
    7. Configuration valid (cortex.config.json)
    8. Brain integrity (basic validation)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
Status: PRODUCTION


## Table of Contents

### Classes
- [HealthCheckResult](#healthcheckresult)
- [HealthReport](#healthreport)
- [HealthCheckUtility](#healthcheckutility)

### Functions
- [safe_print](#safe_print)
- [run_healthcheck_utility](#run_healthcheck_utility)


## Overview

- **Classes:** 3
- **Functions:** 2
- **Dependencies:** dataclasses, datetime, json, logging, pathlib, psutil, sqlite3, src, sys, typing, yaml


## Classes

### HealthCheckResult

```python
class HealthCheckResult
```

**Decorators:** `dataclass`

Result of a single health check.


**Attributes:**

- `check_name`: str
- `passed`: bool
- `message`: str
- `details`: str
- `severity`: str
- `metrics`: Dict[str, Any]


**Methods:**


---

### HealthReport

```python
class HealthReport
```

**Decorators:** `dataclass`

Complete system health report.


**Attributes:**

- `timestamp`: datetime
- `checks`: List[HealthCheckResult]
- `execution_time`: float


**Methods:**

  #### `passed_count`

  *Decorators:* `property`

  ```python
  passed_count(self) -> int
  ```

  Count of passed checks.

  **Parameters:**

  - `self`


  **Returns:** int


  #### `total_count`

  *Decorators:* `property`

  ```python
  total_count(self) -> int
  ```

  Total checks executed.

  **Parameters:**

  - `self`


  **Returns:** int


  #### `is_healthy`

  *Decorators:* `property`

  ```python
  is_healthy(self) -> bool
  ```

  Overall health status.

  **Parameters:**

  - `self`


  **Returns:** bool


  #### `status_text`

  *Decorators:* `property`

  ```python
  status_text(self) -> str
  ```

  Human-readable status.

  **Parameters:**

  - `self`


  **Returns:** str


  #### `format_console`

  ```python
  format_console(self) -> str
  ```

  Format report for console output.

  **Parameters:**

  - `self`


  **Returns:** str



---

### HealthCheckUtility

```python
class HealthCheckUtility
```

Fast system health validator.

Usage:
    utility = HealthCheckUtility()
    report = utility.run_healthcheck()
    print(report.format_console())


**Methods:**

  #### `validate_system_resources`

  ```python
  validate_system_resources(self) -> HealthCheckResult
  ```

  Check system resources (CPU, memory, disk).

Returns:
    HealthCheckResult with resource metrics

  **Parameters:**

  - `self`


  **Returns:** HealthCheckResult
    HealthCheckResult with resource metrics


  #### `validate_brain_structure`

  ```python
  validate_brain_structure(self) -> HealthCheckResult
  ```

  Check brain tier structure (tier0-3).

Returns:
    HealthCheckResult for brain architecture

  **Parameters:**

  - `self`


  **Returns:** HealthCheckResult
    HealthCheckResult for brain architecture


  #### `validate_database`

  ```python
  validate_database(self, db_name: str, tier: int, display_name: str) -> HealthCheckResult
  ```

  Check database health.

Args:
    db_name: Database filename
    tier: Tier number (1, 2, 3)
    display_name: Human-readable name

Returns:
    HealthCheckResult for database

  **Parameters:**

  - `self`
  - `db_name` (str): Database filename
  - `tier` (int): Tier number (1, 2, 3)
  - `display_name` (str): Human-readable name


  **Returns:** HealthCheckResult
    HealthCheckResult for database


  #### `validate_protection_rules`

  ```python
  validate_protection_rules(self) -> HealthCheckResult
  ```

  Check brain protection rules.

Returns:
    HealthCheckResult for protection rules

  **Parameters:**

  - `self`


  **Returns:** HealthCheckResult
    HealthCheckResult for protection rules


  #### `validate_response_templates`

  ```python
  validate_response_templates(self) -> HealthCheckResult
  ```

  Check response templates.

Returns:
    HealthCheckResult for templates

  **Parameters:**

  - `self`


  **Returns:** HealthCheckResult
    HealthCheckResult for templates


  #### `validate_core_modules`

  ```python
  validate_core_modules(self) -> HealthCheckResult
  ```

  Check core modules present (orchestrators/agents).

Returns:
    HealthCheckResult for modules

  **Parameters:**

  - `self`


  **Returns:** HealthCheckResult
    HealthCheckResult for modules


  #### `validate_configuration`

  ```python
  validate_configuration(self) -> HealthCheckResult
  ```

  Check cortex.config.json validity.

Returns:
    HealthCheckResult for configuration

  **Parameters:**

  - `self`


  **Returns:** HealthCheckResult
    HealthCheckResult for configuration


  #### `run_healthcheck`

  ```python
  run_healthcheck(self) -> HealthReport
  ```

  Execute all health checks and generate report.

  **Parameters:**

  - `self`


  **Returns:** HealthReport



---

## Functions

### safe_print

```python
safe_print(message: str) -> None
```

Print with Unicode fallback for Windows console encoding issues.


**Parameters:**

- `message` (str)


**Returns:** None


---

### run_healthcheck_utility

```python
run_healthcheck_utility() -> Dict[str, Any]
```

Entry point for health check utility - callable from orchestrators or CLI.

Returns:
    Dict with 'success', 'message', 'report_text', 'report_data'


**Returns:** Dict[str, Any]
  Dict with 'success', 'message', 'report_text', 'report_data'


---
