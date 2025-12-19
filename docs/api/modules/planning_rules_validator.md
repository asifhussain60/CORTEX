# planning_rules_validator

CORTEX Planning Rules Validator

Validates planning artifacts against the enhanced DoR framework and Development Executor rules.
Integrates with optimize and healthcheck operations to enforce planning quality.

This validator:
1. Checks DoR compliance (ambiguity detection, self-audit completion)
2. Validates TDD tier assignments (simple/medium/complex)
3. Enforces clean code gates (unused code, complexity thresholds)
4. Validates security review completion (OWASP checklist)
5. Generates actionable recommendations for improvement

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0


## Table of Contents

### Classes
- [ValidationIssue](#validationissue)
- [PlanningValidationReport](#planningvalidationreport)
- [PlanningRulesValidator](#planningrulesvalidator)

### Functions
- [validate_planning_rules](#validate_planning_rules)


## Overview

- **Classes:** 3
- **Functions:** 1
- **Dependencies:** dataclasses, logging, pathlib, re, typing, yaml


## Classes

### ValidationIssue

```python
class ValidationIssue
```

**Decorators:** `dataclass`

Represents a planning validation issue.


**Attributes:**

- `severity`: str
- `category`: str
- `message`: str
- `file_path`: Optional[Path]
- `line_number`: Optional[int]
- `suggestion`: Optional[str]



---

### PlanningValidationReport

```python
class PlanningValidationReport
```

**Decorators:** `dataclass`

Results of planning rules validation.


**Attributes:**

- `total_plans`: int
- `plans_validated`: int
- `blocking_issues`: List[ValidationIssue]
- `warnings`: List[ValidationIssue]
- `info`: List[ValidationIssue]
- `compliant_plans`: List[Path]
- `non_compliant_plans`: List[Path]


**Methods:**

  #### `has_blocking_issues`

  *Decorators:* `property`

  ```python
  has_blocking_issues(self) -> bool
  ```

  Check if any blocking issues exist.

  **Parameters:**

  - `self`


  **Returns:** bool


  #### `compliance_rate`

  *Decorators:* `property`

  ```python
  compliance_rate(self) -> float
  ```

  Calculate compliance rate.

  **Parameters:**

  - `self`


  **Returns:** float



---

### PlanningRulesValidator

```python
class PlanningRulesValidator
```

Validates planning artifacts against enhanced DoR and Development Executor rules.

Usage:
    validator = PlanningRulesValidator(project_root=Path('/path/to/cortex'))
    report = validator.validate_all_plans()
    
    if report.has_blocking_issues:
        for issue in report.blocking_issues:
            print(f"BLOCKING: {issue.message}")


**Methods:**

  #### `validate_all_plans`

  ```python
  validate_all_plans(self) -> PlanningValidationReport
  ```

  Validate all planning documents in the workspace.

Returns:
    PlanningValidationReport with validation results

  **Parameters:**

  - `self`


  **Returns:** PlanningValidationReport
    PlanningValidationReport with validation results


  #### `generate_recommendations`

  ```python
  generate_recommendations(self, report: PlanningValidationReport) -> List[str]
  ```

  Generate actionable recommendations based on validation report.

Args:
    report: Validation report
    
Returns:
    List of recommendation strings

  **Parameters:**

  - `self`
  - `report` (PlanningValidationReport): Validation report


  **Returns:** List[str]
    List of recommendation strings



---

## Functions

### validate_planning_rules

```python
validate_planning_rules(project_root: Path) -> PlanningValidationReport
```

Convenience function to validate planning rules.

Args:
    project_root: Path to CORTEX project root
    
Returns:
    PlanningValidationReport


**Parameters:**

- `project_root` (Path): Path to CORTEX project root


**Returns:** PlanningValidationReport
  PlanningValidationReport


---
