# ast_completeness_checker

AST Completeness Checker for RA API Specifications

Validates that all public methods, business rules, and logic paths from legacy code
are documented in the generated business specification.

Author: CORTEX
Version: 1.0


## Table of Contents

### Classes
- [ASTCompletenessChecker](#astcompletenesschecker)

### Functions
- [main](#main)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** argparse, pathlib, re, typing


## Classes

### ASTCompletenessChecker

```python
class ASTCompletenessChecker
```

Validates specification completeness against legacy C# code.


**Methods:**

  #### `extract_public_methods`

  ```python
  extract_public_methods(self) -> List[Dict[str, any]]
  ```

  Extract all public method signatures from legacy code.

  **Parameters:**

  - `self`


  **Returns:** List[Dict[str, any]]


  #### `extract_if_statements`

  ```python
  extract_if_statements(self) -> List[Dict[str, any]]
  ```

  Extract all if/else branches representing business rules.

  **Parameters:**

  - `self`


  **Returns:** List[Dict[str, any]]


  #### `extract_validation_rules`

  ```python
  extract_validation_rules(self) -> List[Dict[str, any]]
  ```

  Extract validation logic (throw, return error, etc.).

  **Parameters:**

  - `self`


  **Returns:** List[Dict[str, any]]


  #### `extract_database_operations`

  ```python
  extract_database_operations(self) -> List[Dict[str, any]]
  ```

  Extract database queries and operations.

  **Parameters:**

  - `self`


  **Returns:** List[Dict[str, any]]


  #### `extract_external_service_calls`

  ```python
  extract_external_service_calls(self) -> List[Dict[str, any]]
  ```

  Extract calls to external services/APIs.

  **Parameters:**

  - `self`


  **Returns:** List[Dict[str, any]]


  #### `extract_spec_operations`

  ```python
  extract_spec_operations(self) -> Set[str]
  ```

  Extract documented operations from specification.

  **Parameters:**

  - `self`


  **Returns:** Set[str]


  #### `extract_spec_business_rules`

  ```python
  extract_spec_business_rules(self) -> List[str]
  ```

  Extract documented business rules from specification.

  **Parameters:**

  - `self`


  **Returns:** List[str]


  #### `extract_spec_line_references`

  ```python
  extract_spec_line_references(self) -> Set[int]
  ```

  Extract all legacy line numbers referenced in specification.

  **Parameters:**

  - `self`


  **Returns:** Set[int]


  #### `validate_method_coverage`

  ```python
  validate_method_coverage(self) -> Tuple[bool, List[str]]
  ```

  Check if all public methods are documented.

  **Parameters:**

  - `self`


  **Returns:** Tuple[bool, List[str]]


  #### `validate_business_rule_coverage`

  ```python
  validate_business_rule_coverage(self) -> Tuple[bool, List[str]]
  ```

  Check if all if/else branches are documented as rules.

  **Parameters:**

  - `self`


  **Returns:** Tuple[bool, List[str]]


  #### `validate_validation_coverage`

  ```python
  validate_validation_coverage(self) -> Tuple[bool, List[str]]
  ```

  Check if all validation rules are documented.

  **Parameters:**

  - `self`


  **Returns:** Tuple[bool, List[str]]


  #### `validate_database_operations_coverage`

  ```python
  validate_database_operations_coverage(self) -> Tuple[bool, List[str]]
  ```

  Check if database operations are documented.

  **Parameters:**

  - `self`


  **Returns:** Tuple[bool, List[str]]


  #### `run_all_checks`

  ```python
  run_all_checks(self) -> Dict[str, any]
  ```

  Run complete validation suite.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, any]


  #### `print_report`

  ```python
  print_report(self, results: Dict[str, any])
  ```

  Print validation report.

  **Parameters:**

  - `self`
  - `results` (Dict[str, any])



---

## Functions

### main

```python
main()
```

---
