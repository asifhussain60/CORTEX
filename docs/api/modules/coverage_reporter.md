# coverage_reporter

CORTEX Test Coverage Reporter

Advanced coverage reporting with tier-specific analysis:
- Overall project coverage
- Tier-specific coverage (tier0, tier1, tier2, tier3)
- Plugin coverage
- HTML report generation
- Coverage threshold validation

Part of Test Execution Infrastructure
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Created: 2025-11-11


## Table of Contents

### Classes
- [CoverageStatus](#coveragestatus)
- [CoverageMetrics](#coveragemetrics)
- [CoverageReport](#coveragereport)
- [CoverageReporter](#coveragereporter)

### Functions
- [run_coverage_analysis](#run_coverage_analysis)


## Overview

- **Classes:** 4
- **Functions:** 1
- **Dependencies:** argparse, dataclasses, enum, json, pathlib, re, src, subprocess, sys, typing


## Classes

### CoverageStatus

```python
class CoverageStatus(Enum)
```

Coverage status levels.



---

### CoverageMetrics

```python
class CoverageMetrics
```

**Decorators:** `dataclass`

Coverage metrics for a component.


**Attributes:**

- `component`: str
- `statements`: int
- `covered`: int
- `missing`: int
- `excluded`: int
- `percentage`: float
- `status`: CoverageStatus



---

### CoverageReport

```python
class CoverageReport
```

**Decorators:** `dataclass`

Complete coverage report.


**Attributes:**

- `overall`: CoverageMetrics
- `by_tier`: Dict[str, CoverageMetrics]
- `by_plugin`: Dict[str, CoverageMetrics]
- `by_file`: Dict[str, CoverageMetrics]
- `html_report_path`: Optional[Path]
- `json_data`: Optional[Dict]
- `threshold_passed`: bool
- `threshold_value`: float



---

### CoverageReporter

```python
class CoverageReporter
```

Generates and analyzes test coverage reports.

Features:
- Runs pytest with coverage
- Generates HTML reports
- Tier-specific analysis
- Threshold validation
- Trend tracking


**Methods:**

  #### `run_coverage`

  ```python
  run_coverage(self, test_pattern: Optional[str], show_missing: bool) -> CoverageReport
  ```

  Run tests with coverage analysis.

Args:
    test_pattern: Optional pytest pattern to filter tests
    show_missing: Whether to show missing lines

Returns:
    CoverageReport with results

  **Parameters:**

  - `self`
  - `test_pattern` (Optional[str]) = `None`: Optional pytest pattern to filter tests
  - `show_missing` (bool) = `True`: Whether to show missing lines


  **Returns:** CoverageReport
    CoverageReport with results


  #### `generate_markdown_report`

  ```python
  generate_markdown_report(self, report: CoverageReport) -> str
  ```

  Generate markdown-formatted coverage report.

  **Parameters:**

  - `self`
  - `report` (CoverageReport)


  **Returns:** str



---

## Functions

### run_coverage_analysis

```python
run_coverage_analysis(test_pattern: Optional[str], threshold: float) -> bool
```

Convenience function to run coverage analysis.

Args:
    test_pattern: Optional pytest pattern to filter tests
    threshold: Minimum acceptable coverage percentage

Returns:
    True if threshold passed


**Parameters:**

- `test_pattern` (Optional[str]) = `None`: Optional pytest pattern to filter tests
- `threshold` (float) = `80.0`: Minimum acceptable coverage percentage


**Returns:** bool
  True if threshold passed


---
