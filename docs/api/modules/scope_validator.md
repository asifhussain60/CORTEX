# scope_validator

CORTEX Scope Validator

Purpose: Validate scope boundaries and identify missing elements for clarification
Target: Confidence threshold validation + gap detection + clarification questions
Status: TDD GREEN Phase - Implementation to pass RED tests

Component of: SWAGGER Entry Point Module (Phase 3.3)


## Table of Contents

### Classes
- [ValidationSeverity](#validationseverity)
- [ValidationRule](#validationrule)
- [ValidationResult](#validationresult)
- [ScopeValidator](#scopevalidator)


## Overview

- **Classes:** 4
- **Functions:** 0
- **Dependencies:** dataclasses, enum, logging, src, typing


## Classes

### ValidationSeverity

```python
class ValidationSeverity(Enum)
```

Severity levels for validation issues



---

### ValidationRule

```python
class ValidationRule
```

**Decorators:** `dataclass`

Single validation rule


**Attributes:**

- `name`: str
- `severity`: ValidationSeverity
- `message`: str
- `passed`: bool



---

### ValidationResult

```python
class ValidationResult
```

**Decorators:** `dataclass`

Result of scope validation


**Attributes:**

- `is_valid`: bool
- `requires_clarification`: bool
- `confidence_score`: float
- `validation_errors`: List[str]
- `warnings`: List[str]
- `missing_elements`: List[str]
- `rules_evaluated`: List[ValidationRule]



---

### ScopeValidator

```python
class ScopeValidator
```

Validate scope boundaries and generate clarification questions

Key Innovation: Smart validation that distinguishes between:
- Missing critical elements (tables, files) → clarification required
- Optional elements (services) → no clarification needed
- Over-limit scope → prioritization required


**Methods:**

  #### `validate_scope`

  ```python
  validate_scope(self, boundary: ScopeBoundary) -> ValidationResult
  ```

  Validate scope boundary against quality rules

Args:
    boundary: Scope boundary from inference engine
    
Returns:
    ValidationResult with errors, warnings, and missing elements

  **Parameters:**

  - `self`
  - `boundary` (ScopeBoundary): Scope boundary from inference engine


  **Returns:** ValidationResult
    ValidationResult with errors, warnings, and missing elements


  #### `generate_clarification_questions`

  ```python
  generate_clarification_questions(self, validation_result: ValidationResult, boundary: ScopeBoundary) -> List[str]
  ```

  Generate targeted clarification questions based on validation gaps

Args:
    validation_result: Result from validate_scope()
    boundary: Original scope boundary
    
Returns:
    List of clarification questions (empty if no clarification needed)

  **Parameters:**

  - `self`
  - `validation_result` (ValidationResult): Result from validate_scope()
  - `boundary` (ScopeBoundary): Original scope boundary


  **Returns:** List[str]
    List of clarification questions (empty if no clarification needed)



---
