# lint_utility

Lint Validation Utility

Lightweight code quality validation using built-in checks.
Replaces heavy orchestrator (461 lines) with focused utility (~250 lines).

Core Operations:
- Lint single file (Python focus)
- Lint directory
- Check violations
- Generate lint report
- List violations by severity

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [ViolationSeverity](#violationseverity)
- [Violation](#violation)
- [LintResult](#lintresult)

### Functions
- [lint_file](#lint_file)
- [lint_directory](#lint_directory)
- [check_violations](#check_violations)
- [generate_lint_report](#generate_lint_report)
- [list_violations](#list_violations)


## Overview

- **Classes:** 3
- **Functions:** 10
- **Dependencies:** dataclasses, enum, json, logging, pathlib, re, src, subprocess, time, typing


## Classes

### ViolationSeverity

```python
class ViolationSeverity(Enum)
```

Violation severity levels.



---

### Violation

```python
class Violation
```

**Decorators:** `dataclass`

Single lint violation.


**Attributes:**

- `file_path`: str
- `line`: int
- `column`: int
- `rule_id`: str
- `message`: str
- `severity`: ViolationSeverity
- `source`: str


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict
  ```


---

### LintResult

```python
class LintResult
```

**Decorators:** `dataclass`

Results from linting operation.


**Attributes:**

- `file_path`: str
- `violations`: List[Violation]
- `execution_time`: float
- `linter_used`: str


**Methods:**

  #### `critical_count`

  *Decorators:* `property`

  ```python
  critical_count(self) -> int
  ```

  #### `warning_count`

  *Decorators:* `property`

  ```python
  warning_count(self) -> int
  ```

  #### `info_count`

  *Decorators:* `property`

  ```python
  info_count(self) -> int
  ```

  #### `total_count`

  *Decorators:* `property`

  ```python
  total_count(self) -> int
  ```


---

## Functions

### lint_file

```python
lint_file(file_path: Path) -> LintResult
```

Lint single file using available linter or built-in checks.

Args:
    file_path: Path to file to lint
    
Returns:
    LintResult with violations


**Parameters:**

- `file_path` (Path): Path to file to lint


**Returns:** LintResult
  LintResult with violations


---

### lint_directory

```python
lint_directory(dir_path: Path, pattern: str) -> List[LintResult]
```

Lint all files in directory matching pattern.

Args:
    dir_path: Directory to lint
    pattern: File pattern (default: *.py)
    
Returns:
    List of LintResults


**Parameters:**

- `dir_path` (Path): Directory to lint
- `pattern` (str) = `'*.py'`: File pattern (default: *.py)


**Returns:** List[LintResult]
  List of LintResults


---

### check_violations

```python
check_violations(results: List[LintResult], severity: ViolationSeverity) -> Dict
```

Check for violations at specified severity level.

Args:
    results: List of lint results
    severity: Minimum severity to check
    
Returns:
    Dict with violation summary


**Parameters:**

- `results` (List[LintResult]): List of lint results
- `severity` (ViolationSeverity) = `ViolationSeverity.CRITICAL`: Minimum severity to check


**Returns:** Dict
  Dict with violation summary


---

### generate_lint_report

```python
generate_lint_report(results: List[LintResult], output_path: Path) -> bool
```

Generate markdown lint report.

Args:
    results: List of lint results
    output_path: Path to save report
    
Returns:
    True if successful


**Parameters:**

- `results` (List[LintResult]): List of lint results
- `output_path` (Path): Path to save report


**Returns:** bool
  True if successful


---

### list_violations

```python
list_violations(results: List[LintResult], severity: Optional[ViolationSeverity]) -> List[Violation]
```

List all violations, optionally filtered by severity.

Args:
    results: List of lint results
    severity: Filter by severity (None = all)
    
Returns:
    List of violations


**Parameters:**

- `results` (List[LintResult]): List of lint results
- `severity` (Optional[ViolationSeverity]) = `None`: Filter by severity (None = all)


**Returns:** List[Violation]
  List of violations


---
