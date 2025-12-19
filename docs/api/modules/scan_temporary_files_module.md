# scan_temporary_files_module

Scan Temporary Files Module

Identifies temporary files for cleanup in CORTEX workspace.

SOLID Principles:
- Single Responsibility: Only handles temporary file scanning
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [ScanTemporaryFilesModule](#scantemporaryfilesmodule)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, os, pathlib, src, typing


## Classes

### ScanTemporaryFilesModule

```python
class ScanTemporaryFilesModule(BaseOperationModule)
```

Cleanup module for scanning temporary files.

Responsibilities:
1. Scan for temporary files (*.tmp, *.cache, etc.)
2. Identify build artifacts
3. Find Python cache directories
4. Locate old log files
5. Track file locations and sizes


**Methods:**

  #### `get_metadata`

  ```python
  get_metadata(self) -> OperationModuleMetadata
  ```

  Return module metadata.

  **Parameters:**

  - `self`


  **Returns:** OperationModuleMetadata


  #### `validate_prerequisites`

  ```python
  validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]
  ```

  Validate prerequisites for scanning.

Checks:
1. Project root exists

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** Tuple[bool, List[str]]


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Execute temporary file scanning.

Steps:
1. Scan for temporary files by extension
2. Find Python cache directories
3. Identify old log files
4. Calculate total size
5. Store scan results in context

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** OperationResult



---
