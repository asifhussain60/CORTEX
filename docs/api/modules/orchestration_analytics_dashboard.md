# orchestration_analytics_dashboard

Orchestration Analytics Dashboard - Visualization and reporting for orchestrator metrics.

**Purpose:** Provide real-time and static visualizations of orchestrator engagement patterns
**Features:**
- 7-day and 30-day metrics aggregation
- Side-by-side orchestrator comparison
- Performance trends (line charts)
- Success rate visualization (pie charts)
- HTML report generation with embedded charts
- Flask server on port 5000 for live dashboard

**CLI Command:** cortex dashboard launch
**Reports Output:** cortex-brain/documents/reports/
**Data Source:** logs/orchestration-metrics/{YYYY-MM-DD}/*.json

**Author:** Asif Hussain
**Feature:** Orchestrator Enhancement Plan v2.0 - Feature 15


## Table of Contents

### Classes
- [OrchestrationAnalyticsDashboard](#orchestrationanalyticsdashboard)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** collections, datetime, flask, json, logging, matplotlib, pathlib, typing


## Classes

### OrchestrationAnalyticsDashboard

```python
class OrchestrationAnalyticsDashboard
```

Analytics dashboard for orchestrator engagement metrics.

**Responsibilities:**
1. Aggregate metrics from OrchestrationMetricsCollector logs
2. Generate performance trends (line charts)
3. Calculate success rates (pie charts)
4. Create HTML reports with embedded visualizations
5. Serve live dashboard via Flask on port 5000
6. Support 7-day and 30-day reporting windows


**Methods:**

  #### `aggregate_metrics`

  ```python
  aggregate_metrics(self, days: int) -> Dict[str, Any]
  ```

  Aggregate metrics from last N days.

Args:
    days: Number of days to aggregate (default: 7)

Returns:
    Dictionary with:
    - total_engagements: Total count
    - by_orchestrator: {orchestrator_name: {count, avg_duration_ms, success_rate}}
    - by_day: {YYYY-MM-DD: count}
    - avg_duration_ms: Overall average
    - success_rate: Overall success percentage

  **Parameters:**

  - `self`
  - `days` (int) = `7`: Number of days to aggregate (default: 7)


  **Returns:** Dict[str, Any]
    Dictionary with: - total_engagements: Total count - by_orchestrator: {orchestrator_name: {count, avg_duration_ms, success_rate}} - by_day: {YYYY-MM-DD: count} - avg_duration_ms: Overall average - success_rate: Overall success percentage


  #### `compare_orchestrators`

  ```python
  compare_orchestrators(self, days: int, sort_by: str) -> List[Dict[str, Any]]
  ```

  Compare statistics across multiple orchestrators.

Args:
    days: Number of days to analyze (default: 7)
    sort_by: Sort key ("engagement_count", "avg_duration", "success_rate")

Returns:
    List of orchestrator statistics sorted by specified key

  **Parameters:**

  - `self`
  - `days` (int) = `7`: Number of days to analyze (default: 7)
  - `sort_by` (str) = `'engagement_count'`: Sort key ("engagement_count", "avg_duration", "success_rate")


  **Returns:** List[Dict[str, Any]]
    List of orchestrator statistics sorted by specified key


  #### `generate_performance_trend`

  ```python
  generate_performance_trend(self, days: int, orchestrator_filter: Optional[str]) -> Dict[str, Any]
  ```

  Generate performance trend data for line charts.

Args:
    days: Number of days to analyze
    orchestrator_filter: Optional orchestrator name to filter by

Returns:
    Dictionary with dates and durations for charting:
    - dates: List of datetime objects
    - durations: List of average durations per day
    - by_orchestrator: {orch_name: {dates: [...], durations: [...]}}

  **Parameters:**

  - `self`
  - `days` (int) = `7`: Number of days to analyze
  - `orchestrator_filter` (Optional[str]) = `None`: Optional orchestrator name to filter by


  **Returns:** Dict[str, Any]
    Dictionary with dates and durations for charting: - dates: List of datetime objects - durations: List of average durations per day - by_orchestrator: {orch_name: {dates: [...], durations: [...]}}


  #### `generate_duration_chart`

  ```python
  generate_duration_chart(self, trend_data: Dict[str, Any]) -> Optional[Path]
  ```

  Generate duration line chart visualization.

Args:
    trend_data: Trend data from generate_performance_trend()

Returns:
    Path to generated chart image (PNG)

  **Parameters:**

  - `self`
  - `trend_data` (Dict[str, Any]): Trend data from generate_performance_trend()


  **Returns:** Optional[Path]
    Path to generated chart image (PNG)


  #### `calculate_success_metrics`

  ```python
  calculate_success_metrics(self, days: int) -> Dict[str, Any]
  ```

  Calculate success/failure/skip metrics for pie charts.

Args:
    days: Number of days to analyze

Returns:
    Dictionary with success_count, error_count, skip_count, success_rate

  **Parameters:**

  - `self`
  - `days` (int) = `7`: Number of days to analyze


  **Returns:** Dict[str, Any]
    Dictionary with success_count, error_count, skip_count, success_rate


  #### `generate_success_pie_chart`

  ```python
  generate_success_pie_chart(self, success_metrics: Dict[str, Any]) -> Optional[Path]
  ```

  Generate success rate pie chart.

Args:
    success_metrics: Metrics from calculate_success_metrics()

Returns:
    Path to generated chart image (PNG)

  **Parameters:**

  - `self`
  - `success_metrics` (Dict[str, Any]): Metrics from calculate_success_metrics()


  **Returns:** Optional[Path]
    Path to generated chart image (PNG)


  #### `calculate_success_metrics_by_orchestrator`

  ```python
  calculate_success_metrics_by_orchestrator(self, days: int) -> List[Dict[str, Any]]
  ```

  Calculate success rate for each orchestrator separately.

Args:
    days: Number of days to analyze

Returns:
    List of {orchestrator_name, success_count, error_count, success_rate}

  **Parameters:**

  - `self`
  - `days` (int) = `7`: Number of days to analyze


  **Returns:** List[Dict[str, Any]]
    List of {orchestrator_name, success_count, error_count, success_rate}


  #### `generate_html_report`

  ```python
  generate_html_report(self, days: int) -> Path
  ```

  Generate static HTML report with embedded charts.

Args:
    days: Number of days to include in report

Returns:
    Path to generated HTML report

  **Parameters:**

  - `self`
  - `days` (int) = `7`: Number of days to include in report


  **Returns:** Path
    Path to generated HTML report


  #### `create_flask_app`

  ```python
  create_flask_app(self)
  ```

  Create Flask application for live dashboard.

Returns:
    Flask app instance with configured routes

  **Parameters:**

  - `self`


  #### `start_server`

  ```python
  start_server(self, host: str, port: Optional[int])
  ```

  Start Flask server for live dashboard.

Args:
    host: Server host (default: localhost)
    port: Server port (default: self.port or 5000)

  **Parameters:**

  - `self`
  - `host` (str) = `'127.0.0.1'`: Server host (default: localhost)
  - `port` (Optional[int]) = `None`: Server port (default: self.port or 5000)



---
