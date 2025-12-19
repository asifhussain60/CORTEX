# optimization_models

System Optimization Data Models

Data classes for system optimization metrics and health reporting.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms


## Table of Contents

### Classes
- [OptimizationMetrics](#optimizationmetrics)
- [SystemHealthReport](#systemhealthreport)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, typing


## Classes

### OptimizationMetrics

```python
class OptimizationMetrics
```

**Decorators:** `dataclass`

Comprehensive optimization metrics from all phases.


**Attributes:**

- `instruction_optimizations`: int
- `instruction_redundancies`: int
- `instruction_outdated_refs`: int
- `instruction_token_savings`: int
- `design_drift_resolved`: int
- `modules_synced`: int
- `status_files_consolidated`: int
- `obsolete_tests_identified`: int
- `dead_code_removed`: int
- `coverage_gaps_identified`: int
- `tier_violations_fixed`: int
- `low_confidence_patterns_pruned`: int
- `duplicate_patterns_merged`: int
- `protection_rules_validated`: bool
- `orchestrators_aligned`: int
- `commands_registered`: int
- `entry_points_synced`: int
- `tests_removed`: int
- `tests_fixed`: int
- `final_pass_rate`: float
- `skull_007_compliant`: bool
- `governance_drift_score`: float
- `governance_position_drifts`: int
- `governance_forward_refs`: int
- `governance_orphaned_rules`: int
- `total_improvements`: int
- `execution_time_seconds`: float
- `errors_encountered`: List[str]
- `warnings`: List[str]



---

### SystemHealthReport

```python
class SystemHealthReport
```

**Decorators:** `dataclass`

Comprehensive system health report.


**Attributes:**

- `timestamp`: datetime
- `overall_health`: str
- `health_score`: float
- `metrics`: OptimizationMetrics
- `recommendations`: List[str]
- `next_actions`: List[str]


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert to dictionary for JSON serialization.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---
