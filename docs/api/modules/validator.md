# validator

Build Validator for Sanitization

Validates that sanitized codebases build successfully and pass tests.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [BuildValidator](#buildvalidator)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** logging, os, pathlib, re, subprocess, typing


## Classes

### BuildValidator

```python
class BuildValidator
```

Validates sanitized codebases through build and test execution.


**Methods:**

  #### `detect_build_system`

  ```python
  detect_build_system(self, directory: str) -> str
  ```

  Detect build system from project files.

Args:
    directory: Project directory

Returns:
    Build system name ('dotnet', 'python', 'node', 'unknown')

  **Parameters:**

  - `self`
  - `directory` (str): Project directory


  **Returns:** str
    Build system name ('dotnet', 'python', 'node', 'unknown')


  #### `execute_build`

  ```python
  execute_build(self, directory: str, build_system: str) -> Dict[str, Any]
  ```

  Execute build for the project.

Args:
    directory: Project directory
    build_system: Detected build system

Returns:
    Dict with build results

  **Parameters:**

  - `self`
  - `directory` (str): Project directory
  - `build_system` (str): Detected build system


  **Returns:** Dict[str, Any]
    Dict with build results


  #### `run_tests`

  ```python
  run_tests(self, directory: str, build_system: str) -> Dict[str, Any]
  ```

  Run test suite for the project.

Args:
    directory: Project directory
    build_system: Detected build system

Returns:
    Dict with test results

  **Parameters:**

  - `self`
  - `directory` (str): Project directory
  - `build_system` (str): Detected build system


  **Returns:** Dict[str, Any]
    Dict with test results



---
