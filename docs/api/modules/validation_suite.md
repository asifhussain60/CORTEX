# validation_suite

Complete Validation Suite for RA API Specifications

Runs all validation checks in sequence and provides comprehensive report.

Author: CORTEX
Version: 1.0


## Table of Contents

### Classes
- [ValidationSuite](#validationsuite)

### Functions
- [main](#main)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** argparse, pathlib, subprocess, sys, typing


## Classes

### ValidationSuite

```python
class ValidationSuite
```

Orchestrates complete specification validation.


**Methods:**

  #### `validate_prerequisites`

  ```python
  validate_prerequisites(self) -> bool
  ```

  Check if required files exist.

  **Parameters:**

  - `self`


  **Returns:** bool


  #### `run_ast_validation`

  ```python
  run_ast_validation(self) -> Dict[str, any]
  ```

  Run AST completeness checker.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, any]


  #### `run_data_flow_validation`

  ```python
  run_data_flow_validation(self) -> Dict[str, any]
  ```

  Run data flow validator.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, any]


  #### `run_traceability_validation`

  ```python
  run_traceability_validation(self) -> Dict[str, any]
  ```

  Run traceability calculator.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, any]


  #### `run_layer_mapping_validation`

  ```python
  run_layer_mapping_validation(self) -> Dict[str, any]
  ```

  Run project reference validator on layer mapping.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, any]


  #### `print_final_report`

  ```python
  print_final_report(self)
  ```

  Print comprehensive validation report.

  **Parameters:**

  - `self`


  #### `run_all`

  ```python
  run_all(self, legacy_file: Path) -> bool
  ```

  Run complete validation suite.

  **Parameters:**

  - `self`
  - `legacy_file` (Path)


  **Returns:** bool



---

## Functions

### main

```python
main()
```

---
