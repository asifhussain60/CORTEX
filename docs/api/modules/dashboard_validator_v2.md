# dashboard_validator_v2

Dashboard Validator V2 - Comprehensive Functionality Testing

Tests all dashboard features:
- Tab loading and visibility
- Data structure validation
- JavaScript function presence
- Interactive elements (filters, search, pagination)
- Visualization components (charts, graphs, diagrams)
- Export functionality
- Data binding and rendering

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary


## Table of Contents

### Classes
- [ValidationTest](#validationtest)
- [TabValidation](#tabvalidation)
- [DashboardValidator](#dashboardvalidator)

### Functions
- [validate_dashboard](#validate_dashboard)


## Overview

- **Classes:** 3
- **Functions:** 1
- **Dependencies:** dataclasses, datetime, json, logging, pathlib, re, typing


## Classes

### ValidationTest

```python
class ValidationTest
```

**Decorators:** `dataclass`

Individual validation test result


**Attributes:**

- `test_name`: str
- `category`: str
- `tab`: str
- `passed`: bool
- `message`: str
- `severity`: str
- `details`: str



---

### TabValidation

```python
class TabValidation
```

**Decorators:** `dataclass`

Validation results for a single tab


**Attributes:**

- `tab_name`: str
- `tests`: List[ValidationTest]


**Methods:**

  #### `passed`

  *Decorators:* `property`

  ```python
  passed(self) -> bool
  ```

  All critical tests passed

  **Parameters:**

  - `self`


  **Returns:** bool


  #### `errors`

  *Decorators:* `property`

  ```python
  errors(self) -> List[ValidationTest]
  ```

  #### `warnings`

  *Decorators:* `property`

  ```python
  warnings(self) -> List[ValidationTest]
  ```

  #### `passed_count`

  *Decorators:* `property`

  ```python
  passed_count(self) -> int
  ```


---

### DashboardValidator

```python
class DashboardValidator
```

Comprehensive dashboard validator


**Methods:**

  #### `validate_all`

  ```python
  validate_all(self) -> Tuple[bool, Dict[str, Any]]
  ```

  Run comprehensive validation of all dashboard functionality

Returns:
    Tuple of (all_passed, detailed_report)

  **Parameters:**

  - `self`


  **Returns:** Tuple[bool, Dict[str, Any]]
    Tuple of (all_passed, detailed_report)


  #### `print_report`

  ```python
  print_report(self)
  ```

  Print human-readable validation report

  **Parameters:**

  - `self`



---

## Functions

### validate_dashboard

```python
validate_dashboard(output_dir: Path, dashboard_path: Optional[Path]) -> Tuple[bool, Dict[str, Any]]
```

Convenience function to validate dashboard

Args:
    output_dir: Directory containing data files
    dashboard_path: Optional path to dashboard.html (defaults to output_dir/dashboard.html)

Returns:
    Tuple of (success, report_dict)


**Parameters:**

- `output_dir` (Path): Directory containing data files
- `dashboard_path` (Optional[Path]) = `None`: Optional path to dashboard.html (defaults to output_dir/dashboard.html)


**Returns:** Tuple[bool, Dict[str, Any]]
  Tuple of (success, report_dict)


---
