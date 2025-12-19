# token_metrics

CORTEX Tier 1: Token Metrics Collector
Collect and track token usage metrics for cost monitoring and optimization analysis.

Provides real-time visibility into token consumption, cost estimation,
and optimization effectiveness.


## Table of Contents

### Classes
- [TokenMetricsCollector](#tokenmetricscollector)
- [TokenMetricsFormatter](#tokenmetricsformatter)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, json, os, pathlib, typing


## Classes

### TokenMetricsCollector

```python
class TokenMetricsCollector
```

Collect token usage metrics for dashboard and monitoring.

Key Features:
- Session token tracking
- Cost estimation ($0.000003 per token)
- Optimization rate calculation
- Database size monitoring
- Real-time metrics for dashboard


**Methods:**

  #### `record_request`

  ```python
  record_request(self, original_tokens: int, optimized_tokens: int, optimization_method: str, quality_score: Optional[float]) -> None
  ```

  Record tokens for a single request.

Args:
    original_tokens: Token count before optimization
    optimized_tokens: Token count after optimization
    optimization_method: Method used for optimization
    quality_score: Optional quality score (0.0 to 1.0)
    
Example:
    >>> collector = TokenMetricsCollector(working_memory)
    >>> collector.record_request(
    ...     original_tokens=25000,
    ...     optimized_tokens=10000,
    ...     optimization_method="ml_context_compression",
    ...     quality_score=0.95
    ... )

  **Parameters:**

  - `self`
  - `original_tokens` (int): Token count before optimization
  - `optimized_tokens` (int): Token count after optimization
  - `optimization_method` (str) = `'unknown'`: Method used for optimization
  - `quality_score` (Optional[float]) = `None`: Optional quality score (0.0 to 1.0)


  **Returns:** None


  #### `get_current_metrics`

  ```python
  get_current_metrics(self, force_refresh: bool) -> Dict[str, Any]
  ```

  Get current token metrics for dashboard.

Args:
    force_refresh: Force refresh even if cache is valid

Returns:
    Dict with comprehensive metrics
    
Example:
    >>> collector = TokenMetricsCollector(working_memory)
    >>> metrics = collector.get_current_metrics()
    >>> print(f"Session cost: ${metrics['session_cost_usd']:.4f}")

  **Parameters:**

  - `self`
  - `force_refresh` (bool) = `False`: Force refresh even if cache is valid


  **Returns:** Dict[str, Any]
    Dict with comprehensive metrics


  #### `get_session_summary`

  ```python
  get_session_summary(self) -> Dict[str, Any]
  ```

  Get session summary with detailed breakdown.

Returns:
    Dict with session summary

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict with session summary


  #### `get_request_history`

  ```python
  get_request_history(self, limit: Optional[int]) -> List[Dict[str, Any]]
  ```

  Get request history.

Args:
    limit: Optional limit on number of requests to return

Returns:
    List of request dicts

  **Parameters:**

  - `self`
  - `limit` (Optional[int]) = `None`: Optional limit on number of requests to return


  **Returns:** List[Dict[str, Any]]
    List of request dicts


  #### `export_session_data`

  ```python
  export_session_data(self, output_path: Optional[Path]) -> Path
  ```

  Export session data to JSON file.

Args:
    output_path: Optional output file path

Returns:
    Path to exported file

  **Parameters:**

  - `self`
  - `output_path` (Optional[Path]) = `None`: Optional output file path


  **Returns:** Path
    Path to exported file


  #### `reset_session`

  ```python
  reset_session(self) -> None
  ```

  Reset session metrics (start new session).

  **Parameters:**

  - `self`


  **Returns:** None



---

### TokenMetricsFormatter

```python
class TokenMetricsFormatter
```

Format token metrics for display.


**Methods:**

  #### `format_tokens`

  *Decorators:* `staticmethod`

  ```python
  format_tokens(token_count: int) -> str
  ```

  Format token count with commas.

Args:
    token_count: Number of tokens

Returns:
    Formatted string

  **Parameters:**

  - `token_count` (int): Number of tokens


  **Returns:** str
    Formatted string


  #### `format_cost`

  *Decorators:* `staticmethod`

  ```python
  format_cost(cost_usd: float) -> str
  ```

  Format cost in USD.

Args:
    cost_usd: Cost in USD

Returns:
    Formatted string

  **Parameters:**

  - `cost_usd` (float): Cost in USD


  **Returns:** str
    Formatted string


  #### `format_percentage`

  *Decorators:* `staticmethod`

  ```python
  format_percentage(percentage: float) -> str
  ```

  Format percentage.

Args:
    percentage: Percentage value

Returns:
    Formatted string

  **Parameters:**

  - `percentage` (float): Percentage value


  **Returns:** str
    Formatted string


  #### `format_filesize`

  *Decorators:* `staticmethod`

  ```python
  format_filesize(bytes_count: int) -> str
  ```

  Format file size in human-readable format.

Args:
    bytes_count: Size in bytes

Returns:
    Formatted string

  **Parameters:**

  - `bytes_count` (int): Size in bytes


  **Returns:** str
    Formatted string


  #### `format_duration`

  *Decorators:* `staticmethod`

  ```python
  format_duration(seconds: float) -> str
  ```

  Format duration in human-readable format.

Args:
    seconds: Duration in seconds

Returns:
    Formatted string

  **Parameters:**

  - `seconds` (float): Duration in seconds


  **Returns:** str
    Formatted string


  #### `format_metrics_summary`

  *Decorators:* `staticmethod`

  ```python
  format_metrics_summary(metrics: Dict[str, Any]) -> str
  ```

  Format metrics as human-readable summary.

Args:
    metrics: Metrics dict from get_current_metrics()

Returns:
    Multi-line summary string

  **Parameters:**

  - `metrics` (Dict[str, Any]): Metrics dict from get_current_metrics()


  **Returns:** str
    Multi-line summary string



---
