# performance_profiling_orchestrator

Performance Profiling Orchestrator.

Provides execution profiling, bottleneck detection, and regression analysis.


## Table of Contents

### Classes
- [ProfileResult](#profileresult)
- [BottleneckReport](#bottleneckreport)
- [RegressionReport](#regressionreport)
- [PerformanceProfilingOrchestrator](#performanceprofilingorchestrator)


## Overview

- **Classes:** 4
- **Functions:** 0
- **Dependencies:** cProfile, dataclasses, functools, io, pstats, time, typing


## Classes

### ProfileResult

```python
class ProfileResult
```

**Decorators:** `dataclass`

Result of a profiling execution.


**Attributes:**

- `function_name`: str
- `execution_time`: float
- `call_count`: int
- `return_value`: Any
- `runs`: int
- `avg_execution_time`: float
- `min_execution_time`: float
- `max_execution_time`: float


**Methods:**


---

### BottleneckReport

```python
class BottleneckReport
```

**Decorators:** `dataclass`

Report of identified performance bottlenecks.


**Attributes:**

- `hotspots`: List[Dict[str, Any]]
- `recommendations`: List[str]
- `total_time`: float



---

### RegressionReport

```python
class RegressionReport
```

**Decorators:** `dataclass`

Report of performance regression analysis.


**Attributes:**

- `has_regression`: bool
- `degraded_functions`: List[str]
- `percentage_change`: Dict[str, float]
- `threshold`: float



---

### PerformanceProfilingOrchestrator

```python
class PerformanceProfilingOrchestrator
```

Orchestrator for performance profiling and analysis.

Features:
- Execution profiling with cProfile
- Bottleneck identification
- Regression detection
- Performance comparison


**Methods:**

  #### `profile_execution`

  ```python
  profile_execution(self, func: Callable, args: Tuple, kwargs: Optional[Dict], runs: int) -> ProfileResult
  ```

  Profile function execution.

Args:
    func: Function to profile
    args: Positional arguments
    kwargs: Keyword arguments
    runs: Number of runs for averaging
    
Returns:
    ProfileResult with timing data

  **Parameters:**

  - `self`
  - `func` (Callable): Function to profile
  - `args` (Tuple) = `()`: Positional arguments
  - `kwargs` (Optional[Dict]) = `None`: Keyword arguments
  - `runs` (int) = `1`: Number of runs for averaging


  **Returns:** ProfileResult
    ProfileResult with timing data


  #### `generate_profile_data`

  ```python
  generate_profile_data(self, result: ProfileResult) -> Dict[str, Dict[str, Any]]
  ```

  Generate profile data dictionary from ProfileResult.

Args:
    result: ProfileResult instance
    
Returns:
    Dictionary with profile data

  **Parameters:**

  - `self`
  - `result` (ProfileResult): ProfileResult instance


  **Returns:** Dict[str, Dict[str, Any]]
    Dictionary with profile data


  #### `identify_bottlenecks`

  ```python
  identify_bottlenecks(self, profile_data: Dict[str, Dict[str, Any]], threshold: float) -> BottleneckReport
  ```

  Identify performance bottlenecks.

Args:
    profile_data: Dictionary of function profiling data
    threshold: Minimum time threshold for bottlenecks
    
Returns:
    BottleneckReport with hotspots and recommendations

  **Parameters:**

  - `self`
  - `profile_data` (Dict[str, Dict[str, Any]]): Dictionary of function profiling data
  - `threshold` (float) = `0.0`: Minimum time threshold for bottlenecks


  **Returns:** BottleneckReport
    BottleneckReport with hotspots and recommendations


  #### `detect_regression`

  ```python
  detect_regression(self, baseline: Dict[str, float], current: Dict[str, float], threshold: float) -> RegressionReport
  ```

  Detect performance regressions.

Args:
    baseline: Baseline performance metrics (function -> time)
    current: Current performance metrics (function -> time)
    threshold: Regression threshold (0.10 = 10% slower)
    
Returns:
    RegressionReport with regression details

  **Parameters:**

  - `self`
  - `baseline` (Dict[str, float]): Baseline performance metrics (function -> time)
  - `current` (Dict[str, float]): Current performance metrics (function -> time)
  - `threshold` (float) = `0.1`: Regression threshold (0.10 = 10% slower)


  **Returns:** RegressionReport
    RegressionReport with regression details



---
