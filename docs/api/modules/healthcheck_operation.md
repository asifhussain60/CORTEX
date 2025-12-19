# healthcheck_operation

CORTEX Healthcheck Operation Module

Provides comprehensive system health monitoring and diagnostics.
Reports on brain health, database performance, cache status, and system metrics.

Features:
- Brain tier health checks (Tier 0-3)
- Database performance metrics
- Cache hit rates and optimization
- Memory usage and patterns
- Operation success rates
- System recommendations

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [HealthCheckOperation](#healthcheckoperation)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** base_operation_module, datetime, json, logging, pathlib, sqlite3, src, typing


## Classes

### HealthCheckOperation

```python
class HealthCheckOperation(BaseOperationModule)
```

Health check operation for CORTEX system.

Features:
- Brain tier health (working memory, knowledge graph, dev context)
- Database performance metrics
- Cache optimization status
- System resource usage
- Error rate monitoring
- Performance recommendations

Usage:
    User says: "healthcheck" or "system health" or "check cortex health"
    CORTEX routes to this module


**Methods:**

  #### `get_metadata`

  ```python
  get_metadata(self) -> OperationModuleMetadata
  ```

  Return operation metadata.

  **Parameters:**

  - `self`


  **Returns:** OperationModuleMetadata


  #### `validate`

  ```python
  validate(self) -> OperationResult
  ```

  Validate healthcheck operation can run.

Returns:
    OperationResult with validation status

  **Parameters:**

  - `self`


  **Returns:** OperationResult
    OperationResult with validation status


  #### `execute`

  *Decorators:* `with_progress`

  ```python
  execute(self, context: Optional[Dict[str, Any]]) -> OperationResult
  ```

  Execute health check operation with progress monitoring.

Args:
    context: Optional execution context
    
Returns:
    OperationResult with health metrics

  **Parameters:**

  - `self`
  - `context` (Optional[Dict[str, Any]]) = `None`: Optional execution context


  **Returns:** OperationResult
    OperationResult with health metrics


  #### `rollback`

  ```python
  rollback(self) -> OperationResult
  ```

  Rollback not applicable for health checks.

Returns:
    OperationResult indicating rollback not needed

  **Parameters:**

  - `self`


  **Returns:** OperationResult
    OperationResult indicating rollback not needed



---
