# hardcoded_data_cleaner_module

Hardcoded Data Cleaner Module

Aggressively scans for and eliminates:
- Hardcoded file paths (absolute paths, Windows/Unix specific paths)
- Mock data masquerading as real data
- Fallback mechanisms that return fake values
- Test fixtures with hardcoded values
- Placeholder data in production code
- Default values that should be configuration-driven

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0


## Table of Contents

### Classes
- [HardcodedViolation](#hardcodedviolation)
- [HardcodedDataMetrics](#hardcodeddatametrics)
- [HardcodedDataCleanerModule](#hardcodeddatacleanermodule)

### Functions
- [register](#register)


## Overview

- **Classes:** 3
- **Functions:** 1
- **Dependencies:** ast, dataclasses, logging, pathlib, re, src, typing


## Classes

### HardcodedViolation

```python
class HardcodedViolation
```

**Decorators:** `dataclass`

Represents a single hardcoded data violation.


**Attributes:**

- `file_path`: Path
- `line_number`: int
- `violation_type`: str
- `severity`: str
- `code_snippet`: str
- `suggested_fix`: str
- `context`: str



---

### HardcodedDataMetrics

```python
class HardcodedDataMetrics
```

**Decorators:** `dataclass`

Metrics for hardcoded data detection.


**Attributes:**

- `files_scanned`: int
- `violations_found`: int
- `critical_violations`: int
- `high_violations`: int
- `medium_violations`: int
- `low_violations`: int
- `violations_by_type`: Dict[str, int]
- `violations`: List[HardcodedViolation]
- `clean_files`: int



---

### HardcodedDataCleanerModule

```python
class HardcodedDataCleanerModule(BaseOperationModule)
```

Aggressively detects hardcoded paths, mock data, and fallback mechanisms.

Detection Rules:

1. HARDCODED PATHS (CRITICAL):
   - Absolute paths: C:\Users\..., /home/user/..., D:\PROJECTS\...
   - Platform-specific paths without Path() wrapper
   - Hardcoded directory separators (\, /) instead of Path.joinpath

2. MOCK DATA (HIGH):
   - unittest.mock imports in non-test files
   - @patch, @MagicMock in production code
   - Functions returning hardcoded dicts/lists without data source
   - Fake/dummy/stub data in production code

3. FALLBACK VALUES (HIGH):
   - try/except returning hardcoded values on failure
   - .get() with hardcoded defaults that mask missing config
   - if/else chains with hardcoded fallbacks
   - Default values that should come from config/environment

4. TEST FIXTURES (MEDIUM):
   - Hardcoded test data inside test functions
   - No use of @pytest.fixture for shared test data
   - Inline dictionaries/lists with test values

5. PLACEHOLDER DATA (MEDIUM):
   - TODO/FIXME comments with temporary hardcoded values
   - Obvious placeholder strings ('test', 'example', 'dummy', 'fake')
   - Hardcoded URLs, API keys, database connections

Usage:
    cleaner = HardcodedDataCleanerModule()
    result = cleaner.execute(context={
        'project_root': Path('/path/to/project'),
        'scan_paths': [Path('src'), Path('tests')],
        'exclude_patterns': ['__pycache__', '.git'],
        'fail_on_critical': True
    })


**Methods:**

  #### `get_metadata`

  ```python
  get_metadata(self) -> OperationModuleMetadata
  ```

  Module metadata.

  **Parameters:**

  - `self`


  **Returns:** OperationModuleMetadata


  #### `validate_prerequisites`

  ```python
  validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]
  ```

  Validate prerequisites.

Args:
    context: Shared execution context (must contain 'project_root')

Returns:
    Tuple of (is_valid, issues_list)

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Shared execution context (must contain 'project_root')


  **Returns:** tuple[bool, List[str]]
    Tuple of (is_valid, issues_list)


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Execute hardcoded data detection.

Args:
    context: Shared execution context with keys:
        - project_root: Root path to scan (REQUIRED)
        - scan_paths: List of paths to scan (default: ['src', 'tests'])
        - exclude_patterns: Patterns to exclude (default: ['__pycache__', '.git'])
        - fail_on_critical: Fail if critical violations found (default: True)
        - fix_automatically: Attempt to fix violations (default: False)

Returns:
    OperationResult with detected violations

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Shared execution context with keys:


  **Returns:** OperationResult
    OperationResult with detected violations


  #### `rollback`

  ```python
  rollback(self, context: Dict[str, Any]) -> bool
  ```

  Rollback changes (no changes made during scan).

Args:
    context: Shared execution context

Returns:
    Always True (nothing to rollback)

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Shared execution context


  **Returns:** bool
    Always True (nothing to rollback)



---

## Functions

### register

```python
register() -> BaseOperationModule
```

Register module with operation factory.


**Returns:** BaseOperationModule


---
