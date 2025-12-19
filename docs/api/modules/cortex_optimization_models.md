# cortex_optimization_models

Optimization Metrics Models

Data models for CORTEX optimization orchestrator.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0


## Table of Contents

### Classes
- [OptimizationMetrics](#optimizationmetrics)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, typing


## Classes

### OptimizationMetrics

```python
class OptimizationMetrics
```

**Decorators:** `dataclass`

Metrics collected during optimization execution.


**Attributes:**

- `optimization_id`: str
- `timestamp`: datetime
- `tests_run`: int
- `tests_passed`: int
- `tests_failed`: int
- `issues_identified`: int
- `optimizations_applied`: int
- `optimizations_succeeded`: int
- `optimizations_failed`: int
- `doc_deduplication_count`: int
- `git_commits`: List[str]
- `duration_seconds`: float
- `improvements`: Dict[str, Any]
- `errors`: List[str]



---
