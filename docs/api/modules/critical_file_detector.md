# critical_file_detector

Critical File Detector for Cleanup Validation

Automatically detects files that are critical to CORTEX operation
and should never be deleted during cleanup.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [ImportInfo](#importinfo)
- [CriticalFileDetector](#criticalfiledetector)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** ast, dataclasses, logging, pathlib, typing


## Classes

### ImportInfo

```python
class ImportInfo
```

**Decorators:** `dataclass`

Information about an import statement


**Attributes:**

- `module`: str
- `file_path`: Path
- `line_number`: int



---

### CriticalFileDetector

```python
class CriticalFileDetector
```

Detect files that are critical to CORTEX operation


**Methods:**

  #### `detect_critical_files`

  ```python
  detect_critical_files(self) -> Set[Path]
  ```

  Build comprehensive list of critical files.

Returns:
    Set of Path objects for files that must not be deleted

  **Parameters:**

  - `self`


  **Returns:** Set[Path]
    Set of Path objects for files that must not be deleted


  #### `trace_imports`

  ```python
  trace_imports(self, file_path: Path, visited: Set[Path]) -> Set[Path]
  ```

  Recursively trace all imports from a Python file.

Args:
    file_path: Starting Python file
    visited: Set of already visited files (prevents cycles)

Returns:
    Set of all files in import chain

  **Parameters:**

  - `self`
  - `file_path` (Path): Starting Python file
  - `visited` (Set[Path]) = `None`: Set of already visited files (prevents cycles)


  **Returns:** Set[Path]
    Set of all files in import chain


  #### `is_critical`

  ```python
  is_critical(self, file_path: Path, critical_files: Set[Path]) -> bool
  ```

  Check if a file is critical.

Args:
    file_path: File to check
    critical_files: Pre-computed set of critical files (optional)

Returns:
    True if file is critical, False otherwise

  **Parameters:**

  - `self`
  - `file_path` (Path): File to check
  - `critical_files` (Set[Path]) = `None`: Pre-computed set of critical files (optional)


  **Returns:** bool
    True if file is critical, False otherwise


  #### `find_importers`

  ```python
  find_importers(self, file_path: Path) -> List[ImportInfo]
  ```

  Find all files that import the given file.

Args:
    file_path: File to search for

Returns:
    List of ImportInfo for files that import this file

  **Parameters:**

  - `self`
  - `file_path` (Path): File to search for


  **Returns:** List[ImportInfo]
    List of ImportInfo for files that import this file



---
