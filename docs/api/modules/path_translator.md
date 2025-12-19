# path_translator

Path translation utilities for cross-machine compatibility.

Handles conversion between Windows and Unix path formats.


## Table of Contents

### Classes
- [PathTranslator](#pathtranslator)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** pathlib, typing


## Classes

### PathTranslator

```python
class PathTranslator
```

Utility for translating paths between Windows and Unix formats.


**Methods:**

  #### `is_windows_absolute`

  *Decorators:* `staticmethod`

  ```python
  is_windows_absolute(path: str) -> bool
  ```

  Check if path is Windows absolute (C:\ format).

  **Parameters:**

  - `path` (str)


  **Returns:** bool


  #### `is_unix_absolute`

  *Decorators:* `staticmethod`

  ```python
  is_unix_absolute(path: str) -> bool
  ```

  Check if path is Unix absolute (/ format).

  **Parameters:**

  - `path` (str)


  **Returns:** bool


  #### `is_unc_path`

  *Decorators:* `staticmethod`

  ```python
  is_unc_path(path: str) -> bool
  ```

  Check if path is UNC network path (\\server\share).

  **Parameters:**

  - `path` (str)


  **Returns:** bool


  #### `translate`

  *Decorators:* `staticmethod`

  ```python
  translate(path: str, target_os: str) -> str
  ```

  Translate path between Windows and Unix formats.

Args:
    path: Path to translate
    target_os: Target OS ("Windows" or "Unix")
    
Returns:
    Translated path

  **Parameters:**

  - `path` (str): Path to translate
  - `target_os` (str): Target OS ("Windows" or "Unix")


  **Returns:** str
    Translated path



---
