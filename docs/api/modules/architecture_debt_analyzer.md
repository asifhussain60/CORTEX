# architecture_debt_analyzer

Architectural Debt Analyzer - Layer violations and circular dependencies.

Detects architectural anti-patterns that increase maintenance cost
and reduce code modularity.

Copyright © 2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [ArchitectureViolation](#architectureviolation)
- [ArchitectureDebtAnalyzer](#architecturedebtanalyzer)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** dataclasses, logging, pathlib, typing


## Classes

### ArchitectureViolation

```python
class ArchitectureViolation
```

**Decorators:** `dataclass`

Architectural rule violation.


**Attributes:**

- `violation_type`: str
- `severity`: str
- `description`: str
- `affected_modules`: List[str]
- `recommendation`: str



---

### ArchitectureDebtAnalyzer

```python
class ArchitectureDebtAnalyzer
```

Analyze architectural quality and identify debt.


**Methods:**

  #### `analyze`

  ```python
  analyze(self) -> Dict[str, Any]
  ```

  Analyze codebase architecture for violations and debt.

Returns:
    Architecture analysis with violations and recommendations

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Architecture analysis with violations and recommendations



---
