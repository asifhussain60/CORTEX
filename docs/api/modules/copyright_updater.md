# copyright_updater

Bulk Copyright Updater Utility

Reusable utility for bulk operations on markdown files:
- Add CORTEX copyright headers
- Update existing headers
- Scan and report missing headers
- Dry run mode for safety

Author: Asif Hussain
Date: December 15, 2025


## Table of Contents

### Classes
- [BulkCopyrightUpdater](#bulkcopyrightupdater)
- [PlanningDocumentRealigner](#planningdocumentrealigner)

### Functions
- [main](#main)


## Overview

- **Classes:** 2
- **Functions:** 1
- **Dependencies:** argparse, datetime, json, logging, pathlib, re, shutil, typing


## Classes

### BulkCopyrightUpdater

```python
class BulkCopyrightUpdater
```

Reusable utility for bulk copyright header operations.

Features:
- Add copyright headers to markdown files
- Update existing headers (preserve custom titles)
- Recursive directory scanning
- Dry run mode (report only, no changes)
- Backup before modifications
- Protected file patterns (skip certain files)
- Custom copyright format support


**Methods:**

  #### `execute`

  ```python
  execute(self, file_pattern: str) -> Dict[str, Any]
  ```

  Execute bulk copyright update operation.

Args:
    file_pattern: Glob pattern for files to process (default: **/*.md)

Returns:
    Dictionary with operation results and statistics

  **Parameters:**

  - `self`
  - `file_pattern` (str) = `'**/*.md'`: Glob pattern for files to process (default: **/*.md)


  **Returns:** Dict[str, Any]
    Dictionary with operation results and statistics


  #### `scan_missing_headers`

  ```python
  scan_missing_headers(self, file_pattern: str) -> List[Path]
  ```

  Scan for files missing copyright headers (read-only operation).

Args:
    file_pattern: Glob pattern for files to scan

Returns:
    List of file paths missing copyright headers

  **Parameters:**

  - `self`
  - `file_pattern` (str) = `'**/*.md'`: Glob pattern for files to scan


  **Returns:** List[Path]
    List of file paths missing copyright headers



---

### PlanningDocumentRealigner

```python
class PlanningDocumentRealigner
```

Specialized realigner for planning documents.

Combines copyright header updates with folder organization enforcement.


**Methods:**

  #### `realign_all`

  ```python
  realign_all(self) -> Dict[str, Any]
  ```

  Execute comprehensive realignment:
1. Add copyright headers to all planning documents
2. Move files to proper folders (temp-plans/, active/, completed/)
3. Create universal subfolders (context/, reports/, artifacts/, tracking/)
4. Generate realignment report

Returns:
    Dictionary with realignment results

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dictionary with realignment results



---

## Functions

### main

```python
main()
```

CLI interface for bulk copyright updater.


---
