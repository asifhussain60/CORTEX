# timeframe_estimator

TIMEFRAME Entry Point Module

Purpose: Time Investment Mapping & Effort Forecasting for Resource Allocation, Management & Execution
Author: Asif Hussain
Version: 1.0

Converts SWAGGER scope/complexity data into time estimates:
- Story point calculation (Fibonacci scale)
- Hours estimation (developer effort)
- Team capacity calculation (multi-developer)
- Sprint allocation (timeline generation)

Natural Language Triggers:
- "timeframe", "estimate", "time estimate", "how long", "duration"
- "story points", "sprint estimate", "team size", "velocity"


## Table of Contents

### Classes
- [ParallelTrack](#paralleltrack)
- [TimeEstimate](#timeestimate)
- [TimeframeEstimator](#timeframeestimator)

### Functions
- [quick_estimate](#quick_estimate)


## Overview

- **Classes:** 3
- **Functions:** 1
- **Dependencies:** collections, dataclasses, datetime, math, typing


## Classes

### ParallelTrack

```python
class ParallelTrack
```

**Decorators:** `dataclass`

Represents a parallel work track


**Attributes:**

- `track_id`: int
- `name`: str
- `developers`: List[int]
- `tasks`: List[str]
- `hours`: float
- `dependencies`: List[int]
- `start_sprint`: float
- `end_sprint`: float



---

### TimeEstimate

```python
class TimeEstimate
```

**Decorators:** `dataclass`

Enhanced time estimation result with parallel work analysis


**Attributes:**

- `story_points`: int
- `hours_single`: float
- `hours_team`: float
- `days_single`: float
- `days_team`: float
- `sprints`: float
- `team_size`: int
- `confidence`: str
- `assumptions`: List[str]
- `breakdown`: Dict[str, float]
- `parallel_tracks`: List[ParallelTrack]
- `max_parallel_tracks`: int
- `critical_path_hours`: float
- `explanation`: str
- `complexity_factors`: Dict[str, float]
- `sprint_allocation`: List[Dict[str, any]]



---

### TimeframeEstimator

```python
class TimeframeEstimator
```

TIMEFRAME Entry Point Module

Converts SWAGGER complexity scores (0-100) into actionable time estimates.
Uses industry-standard formulas with configurable multipliers.


**Methods:**

  #### `estimate_timeframe`

  ```python
  estimate_timeframe(self, complexity: float, scope: Optional[Dict], team_size: int, velocity: Optional[float]) -> TimeEstimate
  ```

  Generate complete time estimate from SWAGGER complexity score with parallel work analysis

Args:
    complexity: SWAGGER complexity score (0-100)
    scope: Optional SWAGGER scope dict (for detailed breakdown)
    team_size: Number of developers on team (default: 1)
    velocity: Optional team velocity (story points per sprint)

Returns:
    Enhanced TimeEstimate with parallel tracks, explanations, sprint allocation

  **Parameters:**

  - `self`
  - `complexity` (float): SWAGGER complexity score (0-100)
  - `scope` (Optional[Dict]) = `None`: Optional SWAGGER scope dict (for detailed breakdown)
  - `team_size` (int) = `DEFAULT_TEAM_SIZE`: Number of developers on team (default: 1)
  - `velocity` (Optional[float]) = `None`: Optional team velocity (story points per sprint)


  **Returns:** TimeEstimate
    Enhanced TimeEstimate with parallel tracks, explanations, sprint allocation


  #### `generate_timeline_comparison`

  ```python
  generate_timeline_comparison(self, estimate: 'TimeEstimate', hourly_rate: float) -> Dict[str, any]
  ```

  Generate visual timeline comparison: Single Developer vs Max Parallel Team

Args:
    estimate: TimeEstimate object with parallel track analysis
    hourly_rate: Hourly rate for cost projections (default: $75)

Returns:
    Dict containing ASCII timeline, HTML timeline, and comparison metrics

  **Parameters:**

  - `self`
  - `estimate` ('TimeEstimate'): TimeEstimate object with parallel track analysis
  - `hourly_rate` (float) = `75.0`: Hourly rate for cost projections (default: $75)


  **Returns:** Dict[str, any]
    Dict containing ASCII timeline, HTML timeline, and comparison metrics


  #### `generate_what_if_scenarios`

  ```python
  generate_what_if_scenarios(self, complexity: float, scope: Optional[Dict], team_sizes: List[int], hourly_rate: float) -> Dict[str, any]
  ```

  Generate what-if scenarios for different team configurations

Args:
    complexity: SWAGGER complexity score
    scope: Optional SWAGGER scope
    team_sizes: List of team sizes to compare (default: [1, 2, 3, 5])
    hourly_rate: Hourly rate for cost calculations

Returns:
    Comparison of scenarios with recommendations

  **Parameters:**

  - `self`
  - `complexity` (float): SWAGGER complexity score
  - `scope` (Optional[Dict]) = `None`: Optional SWAGGER scope
  - `team_sizes` (List[int]) = `None`: List of team sizes to compare (default: [1, 2, 3, 5])
  - `hourly_rate` (float) = `75.0`: Hourly rate for cost calculations


  **Returns:** Dict[str, any]
    Comparison of scenarios with recommendations


  #### `format_professional_report`

  ```python
  format_professional_report(self, estimate: 'TimeEstimate', include_timeline: bool, include_cost: bool, hourly_rate: float) -> str
  ```

  Generate comprehensive professional report with all visualizations

Args:
    estimate: TimeEstimate object
    include_timeline: Include visual timeline comparison
    include_cost: Include cost projections
    hourly_rate: Hourly rate for cost calculations

Returns:
    Formatted markdown report

  **Parameters:**

  - `self`
  - `estimate` ('TimeEstimate'): TimeEstimate object
  - `include_timeline` (bool) = `True`: Include visual timeline comparison
  - `include_cost` (bool) = `True`: Include cost projections
  - `hourly_rate` (float) = `75.0`: Hourly rate for cost calculations


  **Returns:** str
    Formatted markdown report


  #### `estimate_three_point`

  ```python
  estimate_three_point(self, complexity: float, scope: Optional[Dict], team_size: int) -> Dict[str, TimeEstimate]
  ```

  Generate PERT three-point estimate (Best/Likely/Worst)

Formula:
- Best case: complexity * 0.75
- Most likely: complexity (as-is)
- Worst case: complexity * 1.50

Args:
    complexity: SWAGGER complexity score
    scope: Optional SWAGGER scope dict
    team_size: Number of developers

Returns:
    Dict with 'best', 'likely', 'worst' TimeEstimate objects

  **Parameters:**

  - `self`
  - `complexity` (float): SWAGGER complexity score
  - `scope` (Optional[Dict]) = `None`: Optional SWAGGER scope dict
  - `team_size` (int) = `DEFAULT_TEAM_SIZE`: Number of developers


  **Returns:** Dict[str, TimeEstimate]
    Dict with 'best', 'likely', 'worst' TimeEstimate objects


  #### `format_estimate_report`

  ```python
  format_estimate_report(self, estimate: TimeEstimate, include_breakdown: bool) -> str
  ```

  Format time estimate as human-readable report

Args:
    estimate: TimeEstimate object
    include_breakdown: Include effort breakdown section

Returns:
    Formatted markdown string

  **Parameters:**

  - `self`
  - `estimate` (TimeEstimate): TimeEstimate object
  - `include_breakdown` (bool) = `True`: Include effort breakdown section


  **Returns:** str
    Formatted markdown string



---

## Functions

### quick_estimate

```python
quick_estimate(complexity: float, team_size: int) -> str
```

Quick one-line estimate for chat responses

Args:
    complexity: SWAGGER complexity score (0-100)
    team_size: Number of developers

Returns:
    One-line summary string


**Parameters:**

- `complexity` (float): SWAGGER complexity score (0-100)
- `team_size` (int) = `1`: Number of developers


**Returns:** str
  One-line summary string


---
