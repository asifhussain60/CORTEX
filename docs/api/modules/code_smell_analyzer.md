# code_smell_analyzer

Code Smell Analyzer - Identify common anti-patterns and technical debt.

Detects code quality issues that increase maintenance burden and
reduce code readability.

Copyright © 2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [CodeSmell](#codesmell)
- [CodeSmellAnalyzer](#codesmellanalyzer)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** ast, dataclasses, logging, pathlib, typing


## Classes

### CodeSmell

```python
class CodeSmell
```

**Decorators:** `dataclass`

Individual code smell detection.


**Attributes:**

- `smell_type`: str
- `file_path`: str
- `line_number`: int
- `description`: str
- `severity`: str
- `recommendation`: str



---

### CodeSmellAnalyzer

```python
class CodeSmellAnalyzer
```

Detect code smells and anti-patterns.


**Methods:**

  #### `analyze`

  ```python
  analyze(self, target_path: Path) -> Dict[str, Any]
  ```

  Analyze code for smells and anti-patterns.

Args:
    target_path: Directory or file to analyze
    
Returns:
    Code smell analysis with recommendations

  **Parameters:**

  - `self`
  - `target_path` (Path): Directory or file to analyze


  **Returns:** Dict[str, Any]
    Code smell analysis with recommendations



---
