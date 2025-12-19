# reference_tracker

CORTEX Cleanup: Reference Tracker

Tracks all file references across the codebase to enable safe reorganization.
Parses Python imports, file paths, markdown links, and config references.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms


## Table of Contents

### Classes
- [FileReference](#filereference)
- [ReferenceTracker](#referencetracker)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** ast, dataclasses, json, logging, pathlib, re, typing, yaml


## Classes

### FileReference

```python
class FileReference
```

**Decorators:** `dataclass`

Reference from one file to another


**Attributes:**

- `source_file`: str
- `target_file`: str
- `reference_type`: str
- `line_number`: int
- `line_content`: str
- `context`: str



---

### ReferenceTracker

```python
class ReferenceTracker
```

Tracks all file references across codebase.

Capabilities:
- Parse Python imports (from/import statements)
- Find file path references (Path(), open(), etc.)
- Extract markdown links
- Parse config file references
- Build dependency graph
- Generate update instructions for file moves


**Methods:**

  #### `scan`

  ```python
  scan(self, files: Dict[str, Any]) -> List[FileReference]
  ```

  Scan files for references.

Args:
    files: Dictionary of relative_path -> FileMetadata
    
Returns:
    List of all file references found

  **Parameters:**

  - `self`
  - `files` (Dict[str, Any]): Dictionary of relative_path -> FileMetadata


  **Returns:** List[FileReference]
    List of all file references found


  #### `get_dependents`

  ```python
  get_dependents(self, file_path: str) -> Set[str]
  ```

  Get all files that depend on the given file

  **Parameters:**

  - `self`
  - `file_path` (str)


  **Returns:** Set[str]


  #### `get_dependencies`

  ```python
  get_dependencies(self, file_path: str) -> Set[str]
  ```

  Get all files that the given file depends on

  **Parameters:**

  - `self`
  - `file_path` (str)


  **Returns:** Set[str]


  #### `get_update_instructions`

  ```python
  get_update_instructions(self, old_path: str, new_path: str) -> List[Dict[str, Any]]
  ```

  Generate update instructions for file move.

Args:
    old_path: Original file path (relative to project root)
    new_path: New file path (relative to project root)
    
Returns:
    List of update instructions for each reference that needs to change

  **Parameters:**

  - `self`
  - `old_path` (str): Original file path (relative to project root)
  - `new_path` (str): New file path (relative to project root)


  **Returns:** List[Dict[str, Any]]
    List of update instructions for each reference that needs to change


  #### `get_statistics`

  ```python
  get_statistics(self) -> Dict[str, Any]
  ```

  Get reference tracking statistics

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---
