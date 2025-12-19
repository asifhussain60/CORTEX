# data_flow_validator

Data Flow Validator for RA API Specifications

Compares documented data flow diagrams against actual execution traces
to ensure accuracy of sequence diagrams.

Author: CORTEX
Version: 1.0


## Table of Contents

### Classes
- [DataFlowValidator](#dataflowvalidator)

### Functions
- [main](#main)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** argparse, pathlib, re, typing


## Classes

### DataFlowValidator

```python
class DataFlowValidator
```

Validates data flow diagrams against execution traces.


**Methods:**

  #### `parse_mermaid_sequence`

  ```python
  parse_mermaid_sequence(self) -> List[Dict[str, str]]
  ```

  Extract sequence diagram steps from Mermaid.

  **Parameters:**

  - `self`


  **Returns:** List[Dict[str, str]]


  #### `extract_documented_paths`

  ```python
  extract_documented_paths(self) -> Set[str]
  ```

  Extract all execution paths from diagram.

  **Parameters:**

  - `self`


  **Returns:** Set[str]


  #### `parse_trace_log`

  ```python
  parse_trace_log(self) -> List[Dict[str, str]]
  ```

  Parse execution trace log (if available).

  **Parameters:**

  - `self`


  **Returns:** List[Dict[str, str]]


  #### `extract_components`

  ```python
  extract_components(self) -> Set[str]
  ```

  Extract all components mentioned in diagram.

  **Parameters:**

  - `self`


  **Returns:** Set[str]


  #### `extract_alt_paths`

  ```python
  extract_alt_paths(self) -> List[Dict[str, any]]
  ```

  Extract alternative paths (error handling, conditionals).

  **Parameters:**

  - `self`


  **Returns:** List[Dict[str, any]]


  #### `validate_diagram_syntax`

  ```python
  validate_diagram_syntax(self) -> Tuple[bool, List[str]]
  ```

  Validate Mermaid syntax is correct.

  **Parameters:**

  - `self`


  **Returns:** Tuple[bool, List[str]]


  #### `validate_completeness`

  ```python
  validate_completeness(self) -> Tuple[bool, List[str]]
  ```

  Check if diagram includes all necessary components.

  **Parameters:**

  - `self`


  **Returns:** Tuple[bool, List[str]]


  #### `validate_against_trace`

  ```python
  validate_against_trace(self) -> Tuple[bool, List[str]]
  ```

  Validate diagram against execution trace (if available).

  **Parameters:**

  - `self`


  **Returns:** Tuple[bool, List[str]]


  #### `calculate_coverage_score`

  ```python
  calculate_coverage_score(self) -> float
  ```

  Calculate overall diagram quality score (0-100).

  **Parameters:**

  - `self`


  **Returns:** float


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
