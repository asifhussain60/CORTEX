# virtual_environment_module

Virtual Environment Setup Module

Creates or activates Python virtual environment for CORTEX.

SOLID Principles:
- Single Responsibility: Only handles virtual environment management
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [VirtualEnvironmentModule](#virtualenvironmentmodule)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, os, pathlib, src, subprocess, sys, typing


## Classes

### VirtualEnvironmentModule

```python
class VirtualEnvironmentModule(BaseOperationModule)
```

Setup module for Python virtual environment management.

Responsibilities:
1. Check if already running in venv
2. Detect existing venv in project
3. Create new venv if needed
4. Provide activation instructions
5. Validate venv is usable


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

  Validate prerequisites for virtual environment setup.

Checks:
1. Project root exists
2. Python command available
3. Platform information available

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** Tuple[bool, List[str]]


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Execute virtual environment setup.

Steps:
1. Check if running in venv already
2. Look for existing venv
3. Create venv if needed
4. Validate venv
5. Provide activation instructions

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** OperationResult



---
