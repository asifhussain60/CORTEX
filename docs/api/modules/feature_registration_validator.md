# feature_registration_validator

Feature Registration Validator for CORTEX Align Orchestrator v2.0

This module validates that all operations and modules are properly registered
in cortex-operations.yaml. Part of the Intelligent Maintenance System.

Author: Asif Hussain
Date: December 3, 2025
Version: 1.0.0


## Table of Contents

### Classes
- [ValidationResult](#validationresult)
- [FeatureRegistrationValidator](#featureregistrationvalidator)

### Functions
- [main](#main)


## Overview

- **Classes:** 2
- **Functions:** 1
- **Dependencies:** dataclasses, logging, pathlib, sys, typing, yaml


## Classes

### ValidationResult

```python
class ValidationResult
```

**Decorators:** `dataclass`

Results from feature registration validation.


**Attributes:**

- `passed`: bool
- `unregistered_operations`: List[str]
- `unregistered_modules`: List[Dict[str, str]]
- `registered_operations`: List[str]
- `registered_modules`: List[str]
- `total_operations_found`: int
- `total_modules_found`: int
- `total_registered_operations`: int
- `total_registered_modules`: int
- `severity`: str
- `message`: str


**Methods:**

  #### `unregistered_count`

  *Decorators:* `property`

  ```python
  unregistered_count(self) -> int
  ```

  Total count of unregistered items.

  **Parameters:**

  - `self`


  **Returns:** int


  #### `registration_percentage`

  *Decorators:* `property`

  ```python
  registration_percentage(self) -> float
  ```

  Percentage of items properly registered.

  **Parameters:**

  - `self`


  **Returns:** float



---

### FeatureRegistrationValidator

```python
class FeatureRegistrationValidator
```

Validates feature registration integrity across CORTEX.


**Methods:**

  #### `scan_operations_directory`

  ```python
  scan_operations_directory(self) -> List[str]
  ```

  Scan multiple directories for executable operations with smart filtering.

Scans:
- src/operations/*.py - User-facing commands
- src/orchestrators/*.py - Complex workflows  
- src/workflows/*.py - Multi-stage workflows (top-level only)
- src/cortex_agents/*.py - AI agents (top-level only)

Returns:
    List of operation names (file stems without .py extension)

  **Parameters:**

  - `self`


  **Returns:** List[str]
    List of operation names (file stems without .py extension)


  #### `scan_operation_modules`

  ```python
  scan_operation_modules(self) -> List[Dict[str, str]]
  ```

  Scan src/operations/modules/*/ for utility modules.

Returns:
    List of dicts with 'category', 'module', and 'path' keys

  **Parameters:**

  - `self`


  **Returns:** List[Dict[str, str]]
    List of dicts with 'category', 'module', and 'path' keys


  #### `load_registered_operations`

  ```python
  load_registered_operations(self) -> Dict[str, Any]
  ```

  Load registered operations from cortex-operations.yaml.

Returns:
    Dictionary of operations from YAML

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dictionary of operations from YAML


  #### `is_module_registered`

  ```python
  is_module_registered(self, module_info: Dict[str, str], registered_ops: Dict[str, Any]) -> bool
  ```

  Check if a module is registered under any operation.

Args:
    module_info: Dict with 'category', 'module', 'path'
    registered_ops: Registered operations from YAML

Returns:
    True if module is registered, False otherwise

  **Parameters:**

  - `self`
  - `module_info` (Dict[str, str]): Dict with 'category', 'module', 'path'
  - `registered_ops` (Dict[str, Any]): Registered operations from YAML


  **Returns:** bool
    True if module is registered, False otherwise


  #### `identify_unregistered`

  ```python
  identify_unregistered(self) -> Dict[str, Any]
  ```

  Find operations and modules that exist but aren't registered.

Returns:
    Dict with 'operations' and 'modules' lists of unregistered items

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict with 'operations' and 'modules' lists of unregistered items


  #### `validate`

  ```python
  validate(self) -> ValidationResult
  ```

  Execute validation and return comprehensive results.

Returns:
    ValidationResult with all validation data

  **Parameters:**

  - `self`


  **Returns:** ValidationResult
    ValidationResult with all validation data


  #### `generate_report`

  ```python
  generate_report(self, result: ValidationResult) -> str
  ```

  Generate a formatted report from validation results.

Args:
    result: ValidationResult to format

Returns:
    Formatted markdown report

  **Parameters:**

  - `self`
  - `result` (ValidationResult): ValidationResult to format


  **Returns:** str
    Formatted markdown report



---

## Functions

### main

```python
main()
```

CLI entry point for standalone validation.


---
