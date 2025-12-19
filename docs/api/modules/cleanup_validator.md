# cleanup_validator

Cleanup Validator - Pre-execution validation

Validates proposed cleanup actions to ensure CORTEX functionality
is not compromised.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [ValidationError](#validationerror)
- [ValidationResult](#validationresult)
- [CleanupValidator](#cleanupvalidator)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** critical_file_detector, dataclasses, importlib, logging, pathlib, subprocess, time, typing


## Classes

### ValidationError

```python
class ValidationError
```

**Decorators:** `dataclass`

Represents a validation error


**Attributes:**

- `severity`: str
- `category`: str
- `message`: str
- `file`: Path
- `details`: Dict[str, Any]



---

### ValidationResult

```python
class ValidationResult
```

**Decorators:** `dataclass`

Result of validation checks


**Attributes:**

- `passed`: bool
- `errors`: List[ValidationError]
- `warnings`: List[ValidationError]
- `validation_time`: float


**Methods:**

  #### `critical_errors`

  *Decorators:* `property`

  ```python
  critical_errors(self) -> List[ValidationError]
  ```

  Get only critical errors

  **Parameters:**

  - `self`


  **Returns:** List[ValidationError]


  #### `has_critical_errors`

  *Decorators:* `property`

  ```python
  has_critical_errors(self) -> bool
  ```

  Check if any critical errors

  **Parameters:**

  - `self`


  **Returns:** bool



---

### CleanupValidator

```python
class CleanupValidator
```

Validate cleanup operations before execution


**Methods:**

  #### `validate_proposed_cleanup`

  ```python
  validate_proposed_cleanup(self, manifest: Dict[str, Any]) -> ValidationResult
  ```

  Validate entire cleanup manifest.

Args:
    manifest: Cleanup manifest with proposed_actions

Returns:
    ValidationResult with pass/fail and details

  **Parameters:**

  - `self`
  - `manifest` (Dict[str, Any]): Cleanup manifest with proposed_actions


  **Returns:** ValidationResult
    ValidationResult with pass/fail and details



---
