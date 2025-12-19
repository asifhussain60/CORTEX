# dashboard_validator

Dashboard Validator

Comprehensive validation of dashboard functionality including:
- Tab data completeness
- JavaScript function availability
- Data structure compatibility
- Interactive element validation
- Visualization rendering checks

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary


## Table of Contents

### Classes
- [ValidationTest](#validationtest)
- [ValidationResult](#validationresult)
- [DashboardValidator](#dashboardvalidator)

### Functions
- [validate_dashboard](#validate_dashboard)


## Overview

- **Classes:** 3
- **Functions:** 1
- **Dependencies:** dataclasses, json, logging, pathlib, re, typing


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
- `passed`: bool
- `message`: str
- `severity`: str



---

### ValidationResult

```python
class ValidationResult
```

**Decorators:** `dataclass`

Result of a validation check


**Attributes:**

- `tab_name`: str
- `passed`: bool
- `tests`: List[ValidationTest]
- `data_present`: bool


**Methods:**

  #### `issues`

  *Decorators:* `property`

  ```python
  issues(self) -> List[str]
  ```

  Get error messages

  **Parameters:**

  - `self`


  **Returns:** List[str]


  #### `warnings`

  *Decorators:* `property`

  ```python
  warnings(self) -> List[str]
  ```

  Get warning messages

  **Parameters:**

  - `self`


  **Returns:** List[str]



---

### DashboardValidator

```python
class DashboardValidator
```

Validates dashboard data for all tabs


**Methods:**

  #### `validate_all`

  ```python
  validate_all(self) -> Tuple[bool, Dict[str, Any]]
  ```

  Validate all dashboard tabs

Returns:
    Tuple of (all_passed, detailed_results)

  **Parameters:**

  - `self`


  **Returns:** Tuple[bool, Dict[str, Any]]
    Tuple of (all_passed, detailed_results)


  #### `generate_report`

  ```python
  generate_report(self) -> str
  ```

  Generate human-readable validation report

  **Parameters:**

  - `self`


  **Returns:** str



---

## Functions

### validate_dashboard

```python
validate_dashboard(output_dir: Path) -> Tuple[bool, Dict[str, Any], str]
```

Convenience function to validate dashboard

Args:
    output_dir: Directory containing dashboard files
    
Returns:
    Tuple of (all_passed, summary_dict, report_text)


**Parameters:**

- `output_dir` (Path): Directory containing dashboard files


**Returns:** Tuple[bool, Dict[str, Any], str]
  Tuple of (all_passed, summary_dict, report_text)


---
