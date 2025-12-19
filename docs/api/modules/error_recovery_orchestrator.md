# error_recovery_orchestrator

Error Recovery Orchestrator

Provides sophisticated error recovery mechanisms with:
- Exponential backoff retry with jitter
- Circuit breaker pattern for failing services
- Fallback strategy chains
- Error classification and pattern recognition
- Recovery statistics and telemetry

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 3.0.0
Feature: Orchestrator Enhancement Plan v2.0 - Feature 17


## Table of Contents

### Classes
- [ErrorRecoveryOrchestrator](#errorrecoveryorchestrator)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** asyncio, collections, datetime, random, time, typing


## Classes

### ErrorRecoveryOrchestrator

```python
class ErrorRecoveryOrchestrator
```

Orchestrates error recovery across operations with retry policies,
circuit breakers, and fallback strategies


**Methods:**

  #### `calculate_backoff`

  ```python
  calculate_backoff(self, attempt: int) -> float
  ```

  Calculate exponential backoff delay

Args:
    attempt: Current attempt number (0-indexed)

Returns:
    Delay in seconds with optional jitter

  **Parameters:**

  - `self`
  - `attempt` (int): Current attempt number (0-indexed)


  **Returns:** float
    Delay in seconds with optional jitter


  #### `retry_with_backoff`

  ```python
  retry_with_backoff(self, operation: Callable, max_attempts: Optional[int], operation_name: Optional[str]) -> Any
  ```

  Retry operation with exponential backoff

Args:
    operation: Async or sync function to retry
    max_attempts: Override default max attempts
    operation_name: Name for tracking statistics

Returns:
    Result of successful operation

Raises:
    Last exception if all attempts fail

  **Parameters:**

  - `self`
  - `operation` (Callable): Async or sync function to retry
  - `max_attempts` (Optional[int]) = `None`: Override default max attempts
  - `operation_name` (Optional[str]) = `None`: Name for tracking statistics


  **Returns:** Any
    Result of successful operation


  #### `record_failure`

  ```python
  record_failure(self, operation_name: str) -> None
  ```

  Record operation failure for circuit breaker

Args:
    operation_name: Name of the operation

  **Parameters:**

  - `self`
  - `operation_name` (str): Name of the operation


  **Returns:** None


  #### `record_success`

  ```python
  record_success(self, operation_name: str) -> None
  ```

  Record operation success for circuit breaker

Args:
    operation_name: Name of the operation

  **Parameters:**

  - `self`
  - `operation_name` (str): Name of the operation


  **Returns:** None


  #### `is_circuit_open`

  ```python
  is_circuit_open(self, operation_name: str) -> bool
  ```

  Check if circuit breaker is open for operation

Args:
    operation_name: Name of the operation

Returns:
    True if circuit is open (blocking requests)

  **Parameters:**

  - `self`
  - `operation_name` (str): Name of the operation


  **Returns:** bool
    True if circuit is open (blocking requests)


  #### `execute_with_fallback`

  ```python
  execute_with_fallback(self, strategies: List[Callable], operation_name: Optional[str]) -> Any
  ```

  Execute with fallback strategy chain

Args:
    strategies: List of async functions to try in order
    operation_name: Name for tracking

Returns:
    Result from first successful strategy

Raises:
    Last exception if all strategies fail

  **Parameters:**

  - `self`
  - `strategies` (List[Callable]): List of async functions to try in order
  - `operation_name` (Optional[str]) = `None`: Name for tracking


  **Returns:** Any
    Result from first successful strategy


  #### `classify_error`

  ```python
  classify_error(self, error: Exception) -> str
  ```

  Classify error as transient or permanent

Args:
    error: Exception instance

Returns:
    "transient" or "permanent"

  **Parameters:**

  - `self`
  - `error` (Exception): Exception instance


  **Returns:** str
    "transient" or "permanent"


  #### `is_retryable`

  ```python
  is_retryable(self, error: Exception) -> bool
  ```

  Check if error should be retried

Args:
    error: Exception instance

Returns:
    True if error is retryable

  **Parameters:**

  - `self`
  - `error` (Exception): Exception instance


  **Returns:** bool
    True if error is retryable


  #### `track_recovery_attempt`

  ```python
  track_recovery_attempt(self, operation: str, attempt: int, success: bool, error_type: Optional[str]) -> None
  ```

  Track recovery attempt statistics

Args:
    operation: Operation name
    attempt: Attempt number
    success: Whether attempt succeeded
    error_type: Type of error if failed

  **Parameters:**

  - `self`
  - `operation` (str): Operation name
  - `attempt` (int): Attempt number
  - `success` (bool): Whether attempt succeeded
  - `error_type` (Optional[str]): Type of error if failed


  **Returns:** None


  #### `get_recovery_stats`

  ```python
  get_recovery_stats(self, operation: str) -> Optional[Dict]
  ```

  Get recovery statistics for operation

Args:
    operation: Operation name

Returns:
    Statistics dictionary or None if no data

  **Parameters:**

  - `self`
  - `operation` (str): Operation name


  **Returns:** Optional[Dict]
    Statistics dictionary or None if no data


  #### `get_global_stats`

  ```python
  get_global_stats(self) -> Dict
  ```

  Get global recovery statistics

Returns:
    Aggregated statistics across all operations

  **Parameters:**

  - `self`


  **Returns:** Dict
    Aggregated statistics across all operations


  #### `reset_circuit`

  ```python
  reset_circuit(self, operation_name: str) -> None
  ```

  Manually reset circuit breaker

Args:
    operation_name: Name of operation to reset

  **Parameters:**

  - `self`
  - `operation_name` (str): Name of operation to reset


  **Returns:** None


  #### `reset_all_circuits`

  ```python
  reset_all_circuits(self) -> None
  ```

  Reset all circuit breakers

  **Parameters:**

  - `self`


  **Returns:** None


  #### `get_circuit_state`

  ```python
  get_circuit_state(self, operation_name: str) -> str
  ```

  Get current circuit breaker state

Args:
    operation_name: Name of operation

Returns:
    "closed", "open", or "half-open"

  **Parameters:**

  - `self`
  - `operation_name` (str): Name of operation


  **Returns:** str
    "closed", "open", or "half-open"



---
