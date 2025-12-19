# scan_docstrings_module

Scan Python docstrings module for documentation generation.

Part of the Documentation Update operation - extracts docstrings from Python source files.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary


## Table of Contents

### Classes
- [DocstringInfo](#docstringinfo)
- [ScanDocstringsModule](#scandocstringsmodule)

### Functions
- [register](#register)


## Overview

- **Classes:** 2
- **Functions:** 1
- **Dependencies:** ast, dataclasses, os, pathlib, src, typing


## Classes

### DocstringInfo

```python
class DocstringInfo
```

**Decorators:** `dataclass`

Information about a docstring.


**Attributes:**

- `module_path`: str
- `object_name`: str
- `object_type`: str
- `docstring`: Optional[str]
- `line_number`: int
- `signature`: Optional[str]
- `parent_class`: Optional[str]



---

### ScanDocstringsModule

```python
class ScanDocstringsModule(BaseOperationModule)
```

Scan Python source files and extract docstrings.

Extracts docstrings from:
- Modules (file-level docstrings)
- Classes
- Functions
- Methods

Builds a structured index of all documentation strings in the codebase.


**Methods:**

  #### `get_metadata`

  ```python
  get_metadata(self) -> OperationModuleMetadata
  ```

  Get module metadata.

  **Parameters:**

  - `self`


  **Returns:** OperationModuleMetadata


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Execute docstring scanning.

Args:
    context: Operation context
    
Returns:
    OperationResult with docstring index

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Operation context


  **Returns:** OperationResult
    OperationResult with docstring index



---

## Functions

### register

```python
register() -> BaseOperationModule
```

Register module for discovery.


**Returns:** BaseOperationModule


---
