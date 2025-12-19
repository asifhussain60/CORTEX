# tutorial_validator

Tutorial Exercise Validation

Validates that tutorial exercises complete successfully and produce expected outputs.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [TutorialValidator](#tutorialvalidator)

### Functions
- [validate_ado_exercise](#validate_ado_exercise)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** logging, pathlib, re, typing


## Classes

### TutorialValidator

```python
class TutorialValidator
```

Validates tutorial exercise completion.


**Methods:**

  #### `validate_ado_planning_exercise`

  ```python
  validate_ado_planning_exercise(self, work_item_id: str) -> Dict[str, Any]
  ```

  Validate ADO planning exercise completion.

Args:
    work_item_id: Work item ID to validate
    
Returns:
    Validation results

  **Parameters:**

  - `self`
  - `work_item_id` (str): Work item ID to validate


  **Returns:** Dict[str, Any]
    Validation results


  #### `validate_all_exercises`

  ```python
  validate_all_exercises(self, session_id: str) -> Dict[str, Any]
  ```

  Validate all exercises for a tutorial session.

Args:
    session_id: Tutorial session ID
    
Returns:
    Comprehensive validation results

  **Parameters:**

  - `self`
  - `session_id` (str): Tutorial session ID


  **Returns:** Dict[str, Any]
    Comprehensive validation results


  #### `generate_validation_report`

  ```python
  generate_validation_report(self, validation_results: Dict[str, Any]) -> str
  ```

  Generate human-readable validation report.

Args:
    validation_results: Results from validate_ado_planning_exercise
    
Returns:
    Formatted report

  **Parameters:**

  - `self`
  - `validation_results` (Dict[str, Any]): Results from validate_ado_planning_exercise


  **Returns:** str
    Formatted report



---

## Functions

### validate_ado_exercise

```python
validate_ado_exercise(cortex_root: Path, work_item_id: str) -> Dict[str, Any]
```

Quick validation function for ADO planning exercise.


**Parameters:**

- `cortex_root` (Path)
- `work_item_id` (str)


**Returns:** Dict[str, Any]


---
