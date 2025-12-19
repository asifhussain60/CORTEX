# file_discovery_engine

File Discovery Engine - Recursive Directory Traversal

Discovers files in a codebase with metadata collection, exclusion filtering,
and language detection.

Author: Asif Hussain
Version: 1.0.0


## Table of Contents

### Classes
- [FileDiscoveryEngine](#filediscoveryengine)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, exclusion_engine, fnmatch, hashlib, language_detector, logging, models, pathlib, typing


## Classes

### FileDiscoveryEngine

```python
class FileDiscoveryEngine
```

Discovers and catalogs files in a directory tree.

Features:
- Recursive directory traversal
- Exclusion pattern filtering
- Language detection
- Metadata collection (size, hash, lines, encoding)
- Progress tracking


**Methods:**

  #### `discover`

  ```python
  discover(self, scope: DiscoveryScope) -> FileInventory
  ```

  Discover files within scope.

Args:
    scope: Discovery scope defining root path and patterns

Returns:
    FileInventory with discovered files and statistics

Raises:
    ValueError: If scope is invalid

  **Parameters:**

  - `self`
  - `scope` (DiscoveryScope): Discovery scope defining root path and patterns


  **Returns:** FileInventory
    FileInventory with discovered files and statistics



---
