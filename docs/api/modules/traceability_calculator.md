# traceability_calculator

Traceability Coverage Calculator for RA API Specifications

Calculates bidirectional traceability between legacy code, specifications,
and modern implementation.

Author: CORTEX
Version: 1.0


## Table of Contents

### Classes
- [TraceabilityCalculator](#traceabilitycalculator)

### Functions
- [main](#main)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** argparse, pathlib, re, typing


## Classes

### TraceabilityCalculator

```python
class TraceabilityCalculator
```

Calculates specification traceability coverage.


**Methods:**

  #### `count_logic_lines`

  ```python
  count_logic_lines(self) -> int
  ```

  Count lines of actual logic in legacy code (excluding comments, braces).

  **Parameters:**

  - `self`


  **Returns:** int


  #### `extract_spec_line_references`

  ```python
  extract_spec_line_references(self) -> Set[int]
  ```

  Extract all legacy line numbers referenced in specification.

  **Parameters:**

  - `self`


  **Returns:** Set[int]


  #### `extract_matrix_mappings`

  ```python
  extract_matrix_mappings(self) -> List[Dict[str, str]]
  ```

  Extract mappings from traceability matrix.

  **Parameters:**

  - `self`


  **Returns:** List[Dict[str, str]]


  #### `calculate_spec_coverage`

  ```python
  calculate_spec_coverage(self) -> Tuple[float, Dict[str, any]]
  ```

  Calculate what % of legacy code is referenced in specification.

  **Parameters:**

  - `self`


  **Returns:** Tuple[float, Dict[str, any]]


  #### `calculate_matrix_coverage`

  ```python
  calculate_matrix_coverage(self) -> Tuple[float, Dict[str, any]]
  ```

  Calculate traceability matrix completeness.

  **Parameters:**

  - `self`


  **Returns:** Tuple[float, Dict[str, any]]


  #### `validate_bidirectional_traceability`

  ```python
  validate_bidirectional_traceability(self) -> Tuple[bool, List[str]]
  ```

  Check if spec references match matrix mappings.

  **Parameters:**

  - `self`


  **Returns:** Tuple[bool, List[str]]


  #### `extract_spec_sections`

  ```python
  extract_spec_sections(self) -> Set[str]
  ```

  Extract all specification section numbers.

  **Parameters:**

  - `self`


  **Returns:** Set[str]


  #### `validate_spec_section_coverage`

  ```python
  validate_spec_section_coverage(self) -> Tuple[bool, List[str]]
  ```

  Check if all spec sections are referenced in matrix.

  **Parameters:**

  - `self`


  **Returns:** Tuple[bool, List[str]]


  #### `calculate_overall_score`

  ```python
  calculate_overall_score(self) -> float
  ```

  Calculate overall traceability quality score (0-100).

  **Parameters:**

  - `self`


  **Returns:** float


  #### `run_all_checks`

  ```python
  run_all_checks(self) -> Dict[str, any]
  ```

  Run complete traceability validation.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, any]


  #### `print_report`

  ```python
  print_report(self, results: Dict[str, any])
  ```

  Print traceability report.

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
