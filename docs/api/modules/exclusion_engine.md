# exclusion_engine

Exclusion Engine - Pattern-Based File Filtering

Applies exclusion patterns from .gitignore, .cortexignore, and custom rules
to filter discovered files.

Author: Asif Hussain
Version: 1.0.0


## Table of Contents

### Classes
- [ExclusionEngine](#exclusionengine)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** fnmatch, logging, pathlib, typing


## Classes

### ExclusionEngine

```python
class ExclusionEngine
```

Applies exclusion patterns to file paths.

Supports:
- .gitignore syntax
- .cortexignore custom patterns
- Glob patterns
- Directory exclusions


**Methods:**

  #### `should_exclude`

  ```python
  should_exclude(self, path: Path, relative_path: Path) -> bool
  ```

  Check if path should be excluded.

Args:
    path: Absolute path to check
    relative_path: Path relative to project root

Returns:
    True if path should be excluded

  **Parameters:**

  - `self`
  - `path` (Path): Absolute path to check
  - `relative_path` (Path): Path relative to project root


  **Returns:** bool
    True if path should be excluded


  #### `add_pattern`

  ```python
  add_pattern(self, pattern: str) -> None
  ```

  Add custom exclusion pattern.

Args:
    pattern: Glob pattern or directory name

  **Parameters:**

  - `self`
  - `pattern` (str): Glob pattern or directory name


  **Returns:** None


  #### `add_patterns`

  ```python
  add_patterns(self, patterns: List[str]) -> None
  ```

  Add multiple exclusion patterns.

Args:
    patterns: List of patterns to add

  **Parameters:**

  - `self`
  - `patterns` (List[str]): List of patterns to add


  **Returns:** None


  #### `get_patterns`

  ```python
  get_patterns(self) -> List[str]
  ```

  Get all current exclusion patterns.

Returns:
    List of exclusion patterns

  **Parameters:**

  - `self`


  **Returns:** List[str]
    List of exclusion patterns



---
