# project_validation_module

Project Validation Setup Module

Validates CORTEX project structure and required files.

SOLID Principles:
- Single Responsibility: Only handles project structure validation
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [ProjectValidationModule](#projectvalidationmodule)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, os, pathlib, src, typing


## Classes

### ProjectValidationModule

```python
class ProjectValidationModule(BaseOperationModule)
```

Setup module for project structure validation.

Responsibilities:
1. Validate CORTEX project root directory
2. Check for required directories (cortex-brain/, src/, tests/, prompts/)
3. Verify essential configuration files
4. Ensure minimum project structure exists


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

  Validate prerequisites for project validation.

Minimal requirements:
1. Current working directory exists
2. Can read filesystem

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** Tuple[bool, List[str]]


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Execute project structure validation.

Steps:
1. Determine project root (from context or discover)
2. Validate required directories exist
3. Check for required files (warnings only)
4. Verify brain structure
5. Update context with project paths

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** OperationResult



---
