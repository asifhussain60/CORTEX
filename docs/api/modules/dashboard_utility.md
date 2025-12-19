# dashboard_utility

Dashboard Utility

Lightweight D3.js dashboard generation for CORTEX system health and metrics.

Core Operations:
- generate_dashboard: Create complete HTML dashboard with all charts
- render_health_chart: Generate health trend visualization config
- render_heatmap: Generate integration heatmap config
- render_coverage: Generate test coverage gauge config
- render_radar: Generate code quality radar config
- export_dashboard: Export dashboard to file

Version: 3.0.0 (Migrated from DashboardGenerator orchestrator)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents


### Functions
- [generate_dashboard](#generate_dashboard)
- [render_health_chart](#render_health_chart)
- [render_heatmap](#render_heatmap)
- [render_coverage](#render_coverage)
- [render_radar](#render_radar)
- [export_dashboard](#export_dashboard)


## Overview

- **Classes:** 0
- **Functions:** 11
- **Dependencies:** datetime, jinja2, json, logging, pathlib, src, time, typing


## Functions

### generate_dashboard

```python
generate_dashboard(output_filename: Optional[str], days: int, include_charts: Optional[List[str]]) -> Dict[str, Any]
```

Generate complete interactive HTML dashboard

Args:
    output_filename: Custom filename (default: dashboard-{timestamp}.html)
    days: Number of days of historical data to include
    include_charts: List of chart types (None = all: health_trend, integration_heatmap, coverage_gauge, quality_radar)
    
Returns:
    Dict with keys: success, file_path, message, charts_generated
    
Example:
    >>> result = generate_dashboard(days=30)
    >>> print(result["file_path"])
    "/path/to/dashboard-20251202-120000.html"


**Parameters:**

- `output_filename` (Optional[str]) = `None`: Custom filename (default: dashboard-{timestamp}.html)
- `days` (int) = `30`: Number of days of historical data to include
- `include_charts` (Optional[List[str]]) = `None`: List of chart types (None = all: health_trend, integration_heatmap, coverage_gauge, quality_radar)


**Returns:** Dict[str, Any]
  Dict with keys: success, file_path, message, charts_generated


---

### render_health_chart

```python
render_health_chart(health_data: List[Dict]) -> Dict
```

Generate health trend chart configuration

Args:
    health_data: List of health snapshot dicts
    
Returns:
    D3.js chart configuration dict
    
Example:
    >>> config = render_health_chart(snapshots)
    >>> print(config["title"])
    "System Health Trend"


**Parameters:**

- `health_data` (List[Dict]): List of health snapshot dicts


**Returns:** Dict
  D3.js chart configuration dict


---

### render_heatmap

```python
render_heatmap(health_data: List[Dict]) -> Dict
```

Generate integration heatmap configuration

Args:
    health_data: List of health snapshot dicts
    
Returns:
    D3.js heatmap configuration dict
    
Example:
    >>> config = render_heatmap(snapshots)
    >>> print(config["type"])
    "heatmap"


**Parameters:**

- `health_data` (List[Dict]): List of health snapshot dicts


**Returns:** Dict
  D3.js heatmap configuration dict


---

### render_coverage

```python
render_coverage(test_results: List[Dict]) -> Dict
```

Generate test coverage gauge configuration

Args:
    test_results: List of test result dicts
    
Returns:
    D3.js gauge configuration dict
    
Example:
    >>> config = render_coverage(results)
    >>> print(config["value"])
    85.5


**Parameters:**

- `test_results` (List[Dict]): List of test result dicts


**Returns:** Dict
  D3.js gauge configuration dict


---

### render_radar

```python
render_radar(code_metrics: List[Dict]) -> Dict
```

Generate code quality radar chart configuration

Args:
    code_metrics: List of code metric dicts
    
Returns:
    D3.js radar chart configuration dict
    
Example:
    >>> config = render_radar(metrics)
    >>> print(config["dimensions"])
    ["complexity", "maintainability", "coverage", ...]


**Parameters:**

- `code_metrics` (List[Dict]): List of code metric dicts


**Returns:** Dict
  D3.js radar chart configuration dict


---

### export_dashboard

```python
export_dashboard(html_path: str, format: str) -> Dict[str, Any]
```

Export dashboard to PNG/SVG/PDF

Args:
    html_path: Path to HTML dashboard file
    format: Export format ('png', 'svg', 'pdf')
    
Returns:
    Dict with keys: success, file_path, message
    
Example:
    >>> result = export_dashboard("/path/to/dashboard.html", "png")
    >>> print(result["success"])
    False  # Not yet implemented


**Parameters:**

- `html_path` (str): Path to HTML dashboard file
- `format` (str) = `'png'`: Export format ('png', 'svg', 'pdf')


**Returns:** Dict[str, Any]
  Dict with keys: success, file_path, message


---
