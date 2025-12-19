# tooling_detection_module

Tooling Detection Module

Detects installed tooling on target machine (Python, Git, Node.js, pip, etc.)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [ToolingDetector](#toolingdetector)

### Functions
- [execute](#execute)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** logging, pathlib, platform, re, shutil, sqlite3, subprocess, typing


## Classes

### ToolingDetector

```python
class ToolingDetector
```

Detect installed development tooling.


**Methods:**

  #### `detect_all`

  ```python
  detect_all(self) -> Dict[str, Dict]
  ```

  Detect all required tooling.

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Dict]


  #### `detect_python`

  ```python
  detect_python(self) -> Dict
  ```

  Detect Python installation.

  **Parameters:**

  - `self`


  **Returns:** Dict


  #### `detect_pip`

  ```python
  detect_pip(self) -> Dict
  ```

  Detect pip installation.

  **Parameters:**

  - `self`


  **Returns:** Dict


  #### `detect_git`

  ```python
  detect_git(self) -> Dict
  ```

  Detect Git installation.

  **Parameters:**

  - `self`


  **Returns:** Dict


  #### `detect_node`

  ```python
  detect_node(self) -> Dict
  ```

  Detect Node.js installation.

  **Parameters:**

  - `self`


  **Returns:** Dict


  #### `detect_npm`

  ```python
  detect_npm(self) -> Dict
  ```

  Detect npm installation.

  **Parameters:**

  - `self`


  **Returns:** Dict


  #### `detect_sqlite`

  ```python
  detect_sqlite(self) -> Dict
  ```

  Detect SQLite installation.

  **Parameters:**

  - `self`


  **Returns:** Dict


  #### `detect_package_manager`

  ```python
  detect_package_manager(self) -> Dict
  ```

  Detect system package manager for automated installation.

  **Parameters:**

  - `self`


  **Returns:** Dict


  #### `get_missing_required`

  ```python
  get_missing_required(self) -> list
  ```

  Get list of missing required tools.

  **Parameters:**

  - `self`


  **Returns:** list


  #### `print_report`

  ```python
  print_report(self)
  ```

  Print detection report.

  **Parameters:**

  - `self`



---

## Functions

### execute

```python
execute(context: Dict) -> Dict
```

Execute tooling detection.


**Parameters:**

- `context` (Dict) = `None`


**Returns:** Dict


---
