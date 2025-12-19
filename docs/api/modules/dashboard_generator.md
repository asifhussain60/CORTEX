# dashboard_generator

Dashboard Generator (Legacy)

Generates self-contained HTML dashboards by embedding JSON data
into the report-dashboard-template.html (for orchestrator reports).
NOT used by admin dashboard.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary


## Table of Contents

### Classes
- [DashboardGenerator](#dashboardgenerator)

### Functions
- [generate_dashboard_html](#generate_dashboard_html)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** datetime, json, logging, pathlib, typing


## Classes

### DashboardGenerator

```python
class DashboardGenerator
```

Generates self-contained HTML dashboards


**Methods:**

  #### `generate`

  ```python
  generate(self, output_path: Path, title: str, project_info: Dict[str, Any], quality_data: Dict[str, Any], security_data: Dict[str, Any], architecture_data: Dict[str, Any], techstack_data: Dict[str, Any], recommendations_data: list, uml_diagram: str) -> Path
  ```

  Generate self-contained dashboard HTML

Args:
    output_path: Path to save dashboard.html
    title: Dashboard title
    project_info: Project metadata
    quality_data: Code quality analysis
    security_data: Security scan results
    architecture_data: Architecture graph
    techstack_data: Tech stack analysis
    recommendations_data: Recommendations list
    uml_diagram: UML diagram SVG/image data
    
Returns:
    Path to generated dashboard

  **Parameters:**

  - `self`
  - `output_path` (Path): Path to save dashboard.html
  - `title` (str): Dashboard title
  - `project_info` (Dict[str, Any]): Project metadata
  - `quality_data` (Dict[str, Any]): Code quality analysis
  - `security_data` (Dict[str, Any]): Security scan results
  - `architecture_data` (Dict[str, Any]): Architecture graph
  - `techstack_data` (Dict[str, Any]): Tech stack analysis
  - `recommendations_data` (list): Recommendations list
  - `uml_diagram` (str) = `''`: UML diagram SVG/image data


  **Returns:** Path
    Path to generated dashboard



---

## Functions

### generate_dashboard_html

```python
generate_dashboard_html(template_path: Path, output_path: Path, title: str, project_info: Dict[str, Any], quality_data: Dict[str, Any], security_data: Dict[str, Any], architecture_data: Dict[str, Any], techstack_data: Dict[str, Any], recommendations_data: list, uml_diagram: str) -> Path
```

Convenience function to generate dashboard

Args:
    template_path: Path to template HTML
    output_path: Path to save dashboard
    title: Dashboard title
    project_info: Project metadata
    quality_data: Quality analysis
    security_data: Security scan
    architecture_data: Architecture graph
    techstack_data: Tech stack
    recommendations_data: Recommendations
    uml_diagram: UML diagram data
    
Returns:
    Path to generated dashboard


**Parameters:**

- `template_path` (Path): Path to template HTML
- `output_path` (Path): Path to save dashboard
- `title` (str): Dashboard title
- `project_info` (Dict[str, Any]): Project metadata
- `quality_data` (Dict[str, Any]): Quality analysis
- `security_data` (Dict[str, Any]): Security scan
- `architecture_data` (Dict[str, Any]): Architecture graph
- `techstack_data` (Dict[str, Any]): Tech stack
- `recommendations_data` (list): Recommendations
- `uml_diagram` (str) = `''`: UML diagram data


**Returns:** Path
  Path to generated dashboard


---
