# code_quality_analyzer

Code Quality Analyzer

Analyzes code quality metrics using CORTEX admin optimizer.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0


## Table of Contents

### Classes
- [CodeQualityAnalyzer](#codequalityanalyzer)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** json, logging, pathlib, subprocess, typing


## Classes

### CodeQualityAnalyzer

```python
class CodeQualityAnalyzer
```

Analyzes code quality metrics using CORTEX admin optimizer.

Runs the comprehensive CORTEX optimizer tool which provides:
- Token usage analysis (prompt efficiency, YAML optimization)
- YAML validation (brain file integrity, schema compliance)
- Plugin health checks (metadata completeness, registration)
- Database optimization (SQLite performance, indexes)


**Methods:**

  #### `analyze`

  ```python
  analyze(self) -> Dict[str, Any]
  ```

  Run code quality analysis.

Returns:
    Dict with insights, issues, and stats

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict with insights, issues, and stats



---
