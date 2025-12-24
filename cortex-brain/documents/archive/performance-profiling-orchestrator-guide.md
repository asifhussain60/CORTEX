# Performance Profiling Orchestrator Guide

## Overview
The Performance Profiling Orchestrator provides execution profiling, bottleneck detection, and performance regression analysis for CORTEX operations.

## Key Features
- **Execution Profiling**: Profile function execution with timing statistics
- **Bottleneck Detection**: Identify performance hotspots  
- **Regression Analysis**: Detect performance degradation over time

## Usage

### Basic Profiling
```python
from src.operations.utilities import PerformanceProfilingOrchestrator

orchestrator = PerformanceProfilingOrchestrator()

# Profile a function
result = orchestrator.profile_execution(my_function, args=(arg1,), runs=10)
print(f"Avg time: {result.avg_execution_time:.3f}s")
```

### Bottleneck Detection
```python
profile_data = {
    'function_a': {'time': 0.5, 'calls': 10},
    'function_b': {'time': 1.2, 'calls': 3}
}

bottlenecks = orchestrator.identify_bottlenecks(profile_data, threshold=0.1)
for hotspot in bottlenecks.hotspots:
    print(f"{hotspot['function']}: {hotspot['time']:.3f}s")
```

### Regression Detection
```python
baseline = {'function_a': 0.5}
current = {'function_a': 0.8}

regression = orchestrator.detect_regression(baseline, current, threshold=0.10)
if regression.has_regression:
    print(f"Degraded functions: {regression.degraded_functions}")
```

## API Reference
- `profile_execution(func, args=(), kwargs=None, runs=1)` - Profile function execution
- `identify_bottlenecks(profile_data, threshold=0.0)` - Detect performance bottlenecks
- `detect_regression(baseline, current, threshold=0.10)` - Identify performance regressions
