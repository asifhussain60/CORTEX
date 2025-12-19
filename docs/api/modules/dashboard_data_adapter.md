# dashboard_data_adapter

Dashboard Data Adapter

Transforms CORTEX analyzer outputs into D3.js dashboard JSON format.
Replaces mock data files with real-time analysis results during application onboarding.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [DashboardMetadata](#dashboardmetadata)
- [QualityIssue](#qualityissue)
- [SecurityVulnerability](#securityvulnerability)
- [PerformanceMetric](#performancemetric)
- [DashboardDataAdapter](#dashboarddataadapter)


## Overview

- **Classes:** 5
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, json, logging, pathlib, typing


## Classes

### DashboardMetadata

```python
class DashboardMetadata
```

**Decorators:** `dataclass`

Project metadata for dashboard.


**Attributes:**

- `project_name`: str
- `version`: str
- `analysis_timestamp`: str
- `scenario`: str
- `total_files`: int
- `total_lines`: int
- `languages`: List[str]



---

### QualityIssue

```python
class QualityIssue
```

**Decorators:** `dataclass`

Quality issue for dashboard.


**Attributes:**

- `type`: str
- `severity`: str
- `file`: str
- `line`: int
- `description`: str
- `suggestion`: str



---

### SecurityVulnerability

```python
class SecurityVulnerability
```

**Decorators:** `dataclass`

Security vulnerability for dashboard.


**Attributes:**

- `type`: str
- `severity`: str
- `cve`: Optional[str]
- `description`: str
- `file`: str
- `line`: int
- `remediation`: str
- `owasp_category`: Optional[str]



---

### PerformanceMetric

```python
class PerformanceMetric
```

**Decorators:** `dataclass`

Performance metric for dashboard.


**Attributes:**

- `metric_name`: str
- `current_value`: float
- `benchmark_value`: float
- `unit`: str
- `trend`: str
- `recommendation`: str



---

### DashboardDataAdapter

```python
class DashboardDataAdapter
```

Transforms CORTEX analyzer outputs into D3.js dashboard format.

Replaces mock data files with real analysis results:
- CodeQualityAnalyzer → mock-quality.json
- SecurityScanner → mock-security.json
- PerformanceMetrics → mock-performance.json


**Methods:**

  #### `transform_metadata`

  ```python
  transform_metadata(self, project_info: Dict[str, Any]) -> Dict[str, Any]
  ```

  Transform project info to dashboard metadata format.

Args:
    project_info: {
        'name': str,
        'version': str,
        'files': int,
        'lines': int,
        'languages': List[str]
    }

Returns:
    Dashboard-compatible metadata dict

  **Parameters:**

  - `self`
  - `project_info` (Dict[str, Any]): {


  **Returns:** Dict[str, Any]
    Dashboard-compatible metadata dict


  #### `transform_quality_data`

  ```python
  transform_quality_data(self, quality_issues: List[Any], quality_score: float) -> Dict[str, Any]
  ```

  Transform CodeQualityAnalyzer output to dashboard quality format.

Args:
    quality_issues: List[CodeQualityIssue] from analyzer
    quality_score: Overall score 0-100

Returns:
    Dashboard-compatible quality dict

  **Parameters:**

  - `self`
  - `quality_issues` (List[Any]): List[CodeQualityIssue] from analyzer
  - `quality_score` (float): Overall score 0-100


  **Returns:** Dict[str, Any]
    Dashboard-compatible quality dict


  #### `transform_security_data`

  ```python
  transform_security_data(self, vulnerabilities: List[Any]) -> Dict[str, Any]
  ```

  Transform SecurityScanner output to dashboard security format.

Args:
    vulnerabilities: List[SecurityFinding] from scanner

Returns:
    Dashboard-compatible security dict

  **Parameters:**

  - `self`
  - `vulnerabilities` (List[Any]): List[SecurityFinding] from scanner


  **Returns:** Dict[str, Any]
    Dashboard-compatible security dict


  #### `transform_performance_data`

  ```python
  transform_performance_data(self, metrics: List[Any]) -> Dict[str, Any]
  ```

  Transform PerformanceMetrics to dashboard performance format.

Args:
    metrics: List[PerformanceMetric] from telemetry

Returns:
    Dashboard-compatible performance dict

  **Parameters:**

  - `self`
  - `metrics` (List[Any]): List[PerformanceMetric] from telemetry


  **Returns:** Dict[str, Any]
    Dashboard-compatible performance dict


  #### `save_dashboard_data`

  ```python
  save_dashboard_data(self, metadata: Dict[str, Any], quality: Dict[str, Any], security: Dict[str, Any], performance: Dict[str, Any], architecture: Optional[Dict[str, Any]]) -> None
  ```

  Save all dashboard data files (replaces mock data).

Args:
    metadata: Transformed metadata
    quality: Transformed quality data
    security: Transformed security data
    performance: Transformed performance data
    architecture: Architecture graph data (nodes/edges for D3.js)

  **Parameters:**

  - `self`
  - `metadata` (Dict[str, Any]): Transformed metadata
  - `quality` (Dict[str, Any]): Transformed quality data
  - `security` (Dict[str, Any]): Transformed security data
  - `performance` (Dict[str, Any]): Transformed performance data
  - `architecture` (Optional[Dict[str, Any]]) = `None`: Architecture graph data (nodes/edges for D3.js)


  **Returns:** None


  #### `generate_full_dashboard_data`

  ```python
  generate_full_dashboard_data(self, project_info: Dict[str, Any], quality_issues: List[Any], quality_score: float, vulnerabilities: List[Any], metrics: List[Any], architecture_graph: Optional[Dict[str, Any]]) -> None
  ```

  Generate complete dashboard data from CORTEX analyzers.

This is the main entry point called during application onboarding.

Args:
    project_info: Project metadata
    quality_issues: From CodeQualityAnalyzer
    quality_score: Overall quality score 0-100
    vulnerabilities: From SecurityScanner
    metrics: From PerformanceMetrics
    architecture_graph: From ArchitectureGraphBuilder (nodes/edges)

  **Parameters:**

  - `self`
  - `project_info` (Dict[str, Any]): Project metadata
  - `quality_issues` (List[Any]): From CodeQualityAnalyzer
  - `quality_score` (float): Overall quality score 0-100
  - `vulnerabilities` (List[Any]): From SecurityScanner
  - `metrics` (List[Any]): From PerformanceMetrics
  - `architecture_graph` (Optional[Dict[str, Any]]) = `None`: From ArchitectureGraphBuilder (nodes/edges)


  **Returns:** None



---
