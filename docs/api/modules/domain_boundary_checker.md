# domain_boundary_checker

Domain Boundary Checker - Validates Clean Architecture layer boundaries

Purpose:
    Detect violations of Clean Architecture principles:
    - Entity exposure (domain entities in API responses)
    - Layer dependency violations (Domain → Infrastructure, etc.)
    - Cross-domain entity exposure
    - Project reference violations

Usage:
    python scripts/architecture/domain_boundary_checker.py --project RA.Api.Host
    python scripts/architecture/domain_boundary_checker.py --solution Platform.Classic.sln
    python scripts/architecture/domain_boundary_checker.py --file Controllers/FundingInvoiceController.cs

Author: Asif Hussain (CORTEX)
Version: 1.0


## Table of Contents

### Classes
- [ViolationType](#violationtype)
- [Violation](#violation)
- [DomainBoundaryChecker](#domainboundarychecker)

### Functions
- [main](#main)


## Overview

- **Classes:** 3
- **Functions:** 1
- **Dependencies:** argparse, dataclasses, enum, os, pathlib, re, typing


## Classes

### ViolationType

```python
class ViolationType(Enum)
```

Types of boundary violations



---

### Violation

```python
class Violation
```

**Decorators:** `dataclass`

Represents a single boundary violation


**Attributes:**

- `violation_type`: ViolationType
- `file_path`: str
- `line_number`: int
- `description`: str
- `severity`: str
- `suggestion`: str



---

### DomainBoundaryChecker

```python
class DomainBoundaryChecker
```

Checks for Clean Architecture boundary violations


**Methods:**

  #### `check_file`

  ```python
  check_file(self, file_path: Path) -> List[Violation]
  ```

  Check a single C# file for violations

  **Parameters:**

  - `self`
  - `file_path` (Path)


  **Returns:** List[Violation]


  #### `check_project`

  ```python
  check_project(self, project_path: Path) -> List[Violation]
  ```

  Check all C# files in a project

  **Parameters:**

  - `self`
  - `project_path` (Path)


  **Returns:** List[Violation]


  #### `check_solution`

  ```python
  check_solution(self, solution_path: Path) -> List[Violation]
  ```

  Check all projects in a solution

  **Parameters:**

  - `self`
  - `solution_path` (Path)


  **Returns:** List[Violation]


  #### `generate_report`

  ```python
  generate_report(self) -> str
  ```

  Generate a human-readable report of violations

  **Parameters:**

  - `self`


  **Returns:** str



---

## Functions

### main

```python
main()
```

---
