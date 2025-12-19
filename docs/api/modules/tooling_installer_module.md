# tooling_installer_module

Tooling Installer Module

Automatically installs missing development tooling (Python, Git, SQLite, etc.)
Note: Node.js installation removed after migration to Python-only architecture

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [ToolingInstaller](#toolinginstaller)
- [VisionAPIInstaller](#visionapiinstaller)

### Functions
- [get_download_urls](#get_download_urls)
- [execute](#execute)


## Overview

- **Classes:** 2
- **Functions:** 2
- **Dependencies:** logging, os, pathlib, platform, shutil, subprocess, typing, urllib


## Classes

### ToolingInstaller

```python
class ToolingInstaller
```

Automated tooling installation.


**Methods:**

  #### `install_python`

  ```python
  install_python(self) -> Tuple[bool, str]
  ```

  Install Python.

  **Parameters:**

  - `self`


  **Returns:** Tuple[bool, str]


  #### `install_git`

  ```python
  install_git(self) -> Tuple[bool, str]
  ```

  Install Git.

  **Parameters:**

  - `self`


  **Returns:** Tuple[bool, str]


  #### `install_node`

  ```python
  install_node(self) -> Tuple[bool, str]
  ```

  Deprecated: Node.js installation removed after migration to Python-only.
Returns success=False to indicate Node.js is not supported.

  **Parameters:**

  - `self`


  **Returns:** Tuple[bool, str]


  #### `install_sqlite`

  ```python
  install_sqlite(self) -> Tuple[bool, str]
  ```

  Install SQLite.

  **Parameters:**

  - `self`


  **Returns:** Tuple[bool, str]


  #### `install_pip_packages`

  ```python
  install_pip_packages(self, requirements_file: Path) -> Tuple[bool, str]
  ```

  Install Python packages from requirements.txt.

  **Parameters:**

  - `self`
  - `requirements_file` (Path)


  **Returns:** Tuple[bool, str]


  #### `install_missing_tools`

  ```python
  install_missing_tools(self, missing: list) -> Dict
  ```

  Install all missing tools.

  **Parameters:**

  - `self`
  - `missing` (list)


  **Returns:** Dict


  #### `print_install_report`

  ```python
  print_install_report(self, results: Dict)
  ```

  Print installation report.

  **Parameters:**

  - `self`
  - `results` (Dict)



---

### VisionAPIInstaller

```python
class VisionAPIInstaller
```

Install Vision API dependencies.


**Methods:**

  #### `install`

  ```python
  install(self, cortex_root: Path) -> Tuple[bool, str]
  ```

  Install Vision API dependencies.

  **Parameters:**

  - `self`
  - `cortex_root` (Path)


  **Returns:** Tuple[bool, str]


  #### `configure_credentials`

  ```python
  configure_credentials(self, api_key: str) -> Tuple[bool, str]
  ```

  Configure Vision API credentials.

  **Parameters:**

  - `self`
  - `api_key` (str) = `None`


  **Returns:** Tuple[bool, str]



---

## Functions

### get_download_urls

```python
get_download_urls()
```

Get tool download URLs with proper URL construction.


---

### execute

```python
execute(context: Dict) -> Dict
```

Execute tooling installation.


**Parameters:**

- `context` (Dict) = `None`


**Returns:** Dict


---
