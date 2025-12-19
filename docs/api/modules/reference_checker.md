# reference_checker

Reference Checker for CORTEX Cleanup Operations

Checks and updates references when files are reorganized or consolidated.
Handles Python imports, file paths, markdown links, and config references.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [ReferenceChecker](#referencechecker)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** logging, pathlib, re, typing


## Classes

### ReferenceChecker

```python
class ReferenceChecker
```

Checks and updates file references after reorganization.

Handles:
- Python imports (from X import Y)
- File paths (Path("..."), os.path.join(...))
- Markdown links ([text](path))
- Config references (in YAML, JSON)


**Methods:**

  #### `scan_references`

  ```python
  scan_references(self, old_path: str) -> List[Tuple[Path, int, str, str]]
  ```

  Scan for references to a file that will be moved/deleted.

Args:
    old_path: Relative path of file being moved/deleted
    
Returns:
    List of (file_path, line_number, line_content, reference_type)

  **Parameters:**

  - `self`
  - `old_path` (str): Relative path of file being moved/deleted


  **Returns:** List[Tuple[Path, int, str, str]]
    List of (file_path, line_number, line_content, reference_type)


  #### `update_references`

  ```python
  update_references(self, old_path: str, new_path: str, references: List[Tuple[Path, int, str, str]], dry_run: bool) -> Dict[str, int]
  ```

  Update references after file reorganization.

Args:
    old_path: Old relative path
    new_path: New relative path
    references: List from scan_references()
    dry_run: If True, only simulate updates
    
Returns:
    Dict with update counts by type

  **Parameters:**

  - `self`
  - `old_path` (str): Old relative path
  - `new_path` (str): New relative path
  - `references` (List[Tuple[Path, int, str, str]]): List from scan_references()
  - `dry_run` (bool) = `True`: If True, only simulate updates


  **Returns:** Dict[str, int]
    Dict with update counts by type


  #### `generate_reference_report`

  ```python
  generate_reference_report(self, old_path: str, references: List[Tuple[Path, int, str, str]]) -> str
  ```

  Generate a report of all references found

  **Parameters:**

  - `self`
  - `old_path` (str)
  - `references` (List[Tuple[Path, int, str, str]])


  **Returns:** str



---
