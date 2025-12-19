# remove_obsolete_tests_module

Remove Obsolete Tests Module

Detects and removes test files calling non-existent APIs (methods removed during refactoring).
This prevents false test failures from outdated tests testing old implementations.

Detection Strategy:
1. Parse test files for method calls (._method_name patterns)
2. Check if those methods exist in current implementation
3. Mark tests as obsolete if calling removed private methods
4. Remove obsolete test files (with Git tracking)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [RemoveObsoleteTestsModule](#removeobsoletetestsmodule)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** ast, importlib, logging, pathlib, re, src, typing


## Classes

### RemoveObsoleteTestsModule

```python
class RemoveObsoleteTestsModule(BaseOperationModule)
```

Detects and removes tests calling non-existent implementation methods.


**Methods:**

  #### `get_metadata`

  ```python
  get_metadata(self) -> OperationModuleMetadata
  ```

  #### `execute`

  ```python
  execute(self, context: Dict) -> OperationResult
  ```

  Find and remove obsolete test files.

Args:
    context: Must contain 'dry_run' boolean
    
Returns:
    OperationResult with removed_tests list

  **Parameters:**

  - `self`
  - `context` (Dict): Must contain 'dry_run' boolean


  **Returns:** OperationResult
    OperationResult with removed_tests list



---
