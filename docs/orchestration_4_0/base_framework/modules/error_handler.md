# error_handler

Error Handler for CORTEX 4.0 Orchestrators

Provides standardized error handling, recovery strategies, and logging.


## Table of Contents

### Classes
- [ErrorSeverity](#errorseverity)
- [RecoveryStrategy](#recoverystrategy)
- [OrchestratorError](#orchestratorerror)
- [ErrorHandler](#errorhandler)


## Overview

- **Classes:** 4
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, enum, logging, traceback, typing


## Classes

### ErrorSeverity

```python
class ErrorSeverity(Enum)
```

Error severity levels



---

### RecoveryStrategy

```python
class RecoveryStrategy(Enum)
```

Error recovery strategies



---

### OrchestratorError

```python
class OrchestratorError
```

**Decorators:** `dataclass`

Structured error information for orchestrators.

Attributes:
    phase: Phase where error occurred
    severity: Error severity level
    message: Human-readable error message
    exception: Original exception (if any)
    traceback: Stack trace
    recovery_strategy: Recommended recovery action
    context: Additional context data
    timestamp: When error occurred


**Attributes:**

- `phase`: str
- `severity`: ErrorSeverity
- `message`: str
- `exception`: Optional[Exception]
- `traceback`: Optional[str]
- `recovery_strategy`: RecoveryStrategy
- `context`: Optional[Dict[str, Any]]
- `timestamp`: datetime


**Methods:**


---

### ErrorHandler

```python
class ErrorHandler
```

Centralized error handling for orchestrators.

Features:
- Structured error capture
- Recovery strategy recommendation
- Error history tracking
- Retry logic with exponential backoff
- User-friendly error messages


**Methods:**

  #### `handle_error`

  ```python
  handle_error(self, phase: str, exception: Exception, severity: ErrorSeverity, recovery_strategy: Optional[RecoveryStrategy], context: Optional[Dict[str, Any]]) -> OrchestratorError
  ```

  Handle an error that occurred during orchestration.

Args:
    phase: Phase where error occurred
    exception: The exception that was raised
    severity: Error severity level
    recovery_strategy: Recommended recovery action (auto-determined if not provided)
    context: Additional context data
    
Returns:
    OrchestratorError object with full error details

  **Parameters:**

  - `self`
  - `phase` (str): Phase where error occurred
  - `exception` (Exception): The exception that was raised
  - `severity` (ErrorSeverity) = `ErrorSeverity.ERROR`: Error severity level
  - `recovery_strategy` (Optional[RecoveryStrategy]) = `None`: Recommended recovery action (auto-determined if not provided)
  - `context` (Optional[Dict[str, Any]]) = `None`: Additional context data


  **Returns:** OrchestratorError
    OrchestratorError object with full error details


  #### `can_retry`

  ```python
  can_retry(self, phase: str) -> bool
  ```

  Check if phase can be retried.

Args:
    phase: Phase name to check
    
Returns:
    True if retry attempts remain

  **Parameters:**

  - `self`
  - `phase` (str): Phase name to check


  **Returns:** bool
    True if retry attempts remain


  #### `record_retry`

  ```python
  record_retry(self, phase: str) -> int
  ```

  Record a retry attempt for a phase.

Args:
    phase: Phase name
    
Returns:
    Current retry count

  **Parameters:**

  - `self`
  - `phase` (str): Phase name


  **Returns:** int
    Current retry count


  #### `reset_retries`

  ```python
  reset_retries(self, phase: str) -> None
  ```

  Reset retry counter for a phase

  **Parameters:**

  - `self`
  - `phase` (str)


  **Returns:** None


  #### `get_error_summary`

  ```python
  get_error_summary(self) -> Dict[str, Any]
  ```

  Get summary of all errors.

Returns:
    Dictionary with error statistics

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dictionary with error statistics


  #### `has_critical_errors`

  ```python
  has_critical_errors(self) -> bool
  ```

  Check if any critical errors occurred

  **Parameters:**

  - `self`


  **Returns:** bool


  #### `clear_errors`

  ```python
  clear_errors(self) -> None
  ```

  Clear all error history

  **Parameters:**

  - `self`


  **Returns:** None



---
