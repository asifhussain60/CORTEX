# bloat_detector

File Bloat Detector for CORTEX

Detects and reports files exceeding size thresholds to prevent bloat.
Part of Phase 8: File Bloat Prevention System.

Thresholds:
- YAML files: 2000 lines / 100KB
- Python files: 1000 lines / 50KB
- Markdown files: 1500 lines / 75KB
- JSON files: 500 lines / 25KB

Usage:
    python -m src.operations.modules.quality.bloat_detector
    python -m src.operations.modules.quality.bloat_detector --refactor

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0


## Table of Contents

### Classes
- [FileType](#filetype)
- [BloatThreshold](#bloatthreshold)
- [BloatReport](#bloatreport)
- [BloatDetector](#bloatdetector)

### Functions
- [main](#main)


## Overview

- **Classes:** 4
- **Functions:** 1
- **Dependencies:** argparse, dataclasses, enum, json, logging, pathlib, subprocess, typing


## Classes

### FileType

```python
class FileType(Enum)
```

Supported file types for bloat detection.



---

### BloatThreshold

```python
class BloatThreshold
```

**Decorators:** `dataclass`

Threshold configuration for file type.


**Attributes:**

- `file_type`: FileType
- `max_lines`: int
- `max_kb`: int



---

### BloatReport

```python
class BloatReport
```

**Decorators:** `dataclass`

Report for a bloated file.


**Attributes:**

- `file_path`: Path
- `file_type`: FileType
- `lines`: int
- `kb`: float
- `threshold_lines`: int
- `threshold_kb`: int
- `lines_over`: int
- `kb_over`: float
- `severity`: str
- `suggestions`: List[str]



---

### BloatDetector

```python
class BloatDetector
```

Detects and reports file bloat across CORTEX.

Features:
- Configurable thresholds by file type
- Refactoring suggestions
- Git staging area scanning
- Severity classification


**Methods:**

  #### `scan_codebase`

  ```python
  scan_codebase(self) -> List[BloatReport]
  ```

  Scan entire codebase for bloated files.

Returns:
    List of bloat reports for files exceeding thresholds

  **Parameters:**

  - `self`


  **Returns:** List[BloatReport]
    List of bloat reports for files exceeding thresholds


  #### `scan_staged_files`

  ```python
  scan_staged_files(self) -> List[BloatReport]
  ```

  Scan git staged files for bloat (for pre-commit hook).

Returns:
    List of bloat reports for staged files exceeding thresholds

  **Parameters:**

  - `self`


  **Returns:** List[BloatReport]
    List of bloat reports for staged files exceeding thresholds


  #### `generate_report`

  ```python
  generate_report(self, bloated_files: List[BloatReport]) -> str
  ```

  Generate human-readable bloat report.

Args:
    bloated_files: List of bloat reports

Returns:
    Formatted report string

  **Parameters:**

  - `self`
  - `bloated_files` (List[BloatReport]): List of bloat reports


  **Returns:** str
    Formatted report string



---

## Functions

### main

```python
main()
```

CLI entry point for bloat detector.


---
