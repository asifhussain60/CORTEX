# project_reference_validator

Project Reference Validator - Validates .csproj references match Clean Architecture rules

Purpose:
    Ensure project references follow Clean Architecture dependency rules:
    - Domain has NO references
    - Use Case references Domain ONLY
    - Internal Infrastructure references Domain ONLY
    - External Infrastructure references Use Case + (optional) Domain
    - Presentation references Domain + Use Case (code), ALL (DI setup allowed)

Usage:
    python scripts/architecture/project_reference_validator.py --solution Platform.Classic.sln
    python scripts/architecture/project_reference_validator.py --project RA.DomainCore/RA.DomainCore.csproj
    python scripts/architecture/project_reference_validator.py --domain RA

Author: Asif Hussain (CORTEX)
Version: 1.0


## Table of Contents

### Classes
- [LayerType](#layertype)
- [ProjectReference](#projectreference)
- [ReferenceViolation](#referenceviolation)
- [ProjectReferenceValidator](#projectreferencevalidator)

### Functions
- [main](#main)


## Overview

- **Classes:** 4
- **Functions:** 1
- **Dependencies:** argparse, dataclasses, enum, pathlib, typing, xml


## Classes

### LayerType

```python
class LayerType(Enum)
```

Clean Architecture layer types



---

### ProjectReference

```python
class ProjectReference
```

**Decorators:** `dataclass`

Represents a project reference


**Attributes:**

- `from_project`: str
- `to_project`: str
- `from_layer`: LayerType
- `to_layer`: LayerType



---

### ReferenceViolation

```python
class ReferenceViolation
```

**Decorators:** `dataclass`

Represents an invalid project reference


**Attributes:**

- `from_project`: str
- `to_project`: str
- `from_layer`: LayerType
- `to_layer`: LayerType
- `reason`: str
- `severity`: str



---

### ProjectReferenceValidator

```python
class ProjectReferenceValidator
```

Validates project references against Clean Architecture rules


**Methods:**

  #### `validate_project`

  ```python
  validate_project(self, csproj_path: Path) -> List[ReferenceViolation]
  ```

  Validate references in a single project

  **Parameters:**

  - `self`
  - `csproj_path` (Path)


  **Returns:** List[ReferenceViolation]


  #### `validate_solution`

  ```python
  validate_solution(self, solution_path: Path, domain_filter: str) -> List[ReferenceViolation]
  ```

  Validate all projects in a solution

  **Parameters:**

  - `self`
  - `solution_path` (Path)
  - `domain_filter` (str) = `None`


  **Returns:** List[ReferenceViolation]


  #### `generate_report`

  ```python
  generate_report(self) -> str
  ```

  Generate human-readable validation report

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
