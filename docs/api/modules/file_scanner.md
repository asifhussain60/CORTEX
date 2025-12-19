# file_scanner

CORTEX Cleanup: Comprehensive File Scanner

Recursively scans repository to categorize all files by type, purpose, age, and usage.
Builds file inventory for intelligent cleanup decisions.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms


## Table of Contents

### Classes
- [FileCategory](#filecategory)
- [FilePurpose](#filepurpose)
- [FileMetadata](#filemetadata)
- [FileScanner](#filescanner)


## Overview

- **Classes:** 4
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, enum, fnmatch, hashlib, logging, mimetypes, pathlib, typing


## Classes

### FileCategory

```python
class FileCategory(Enum)
```

File category classification



---

### FilePurpose

```python
class FilePurpose(Enum)
```

File purpose classification



---

### FileMetadata

```python
class FileMetadata
```

**Decorators:** `dataclass`

Complete file metadata


**Attributes:**

- `path`: Path
- `relative_path`: str
- `category`: FileCategory
- `purpose`: FilePurpose
- `size_bytes`: int
- `created_time`: datetime
- `modified_time`: datetime
- `accessed_time`: datetime
- `mime_type`: str
- `extension`: str
- `is_binary`: bool
- `line_count`: Optional[int]
- `content_hash`: Optional[str]
- `is_protected`: bool
- `is_duplicate`: bool
- `is_obsolete`: bool
- `dependencies`: List[str]
- `dependents`: List[str]
- `action`: Optional[str]
- `reason`: Optional[str]
- `destination`: Optional[str]


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```

  Convert to dictionary

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

### FileScanner

```python
class FileScanner
```

Comprehensive file scanner for cleanup orchestrator.

Capabilities:
- Recursive scanning from repository root
- File categorization by type and purpose
- Metadata extraction and analysis
- Duplicate detection via content hashing
- Protection validation
- Relationship mapping (dependencies/dependents)


**Methods:**

  #### `scan`

  ```python
  scan(self, path: Optional[Path]) -> Dict[str, FileMetadata]
  ```

  Recursively scan directory and categorize all files.

Args:
    path: Starting path (defaults to project_root)
    
Returns:
    Dictionary of relative_path -> FileMetadata

  **Parameters:**

  - `self`
  - `path` (Optional[Path]) = `None`: Starting path (defaults to project_root)


  **Returns:** Dict[str, FileMetadata]
    Dictionary of relative_path -> FileMetadata


  #### `get_files_by_category`

  ```python
  get_files_by_category(self, category: FileCategory) -> List[FileMetadata]
  ```

  Get all files in a category

  **Parameters:**

  - `self`
  - `category` (FileCategory)


  **Returns:** List[FileMetadata]


  #### `get_files_by_purpose`

  ```python
  get_files_by_purpose(self, purpose: FilePurpose) -> List[FileMetadata]
  ```

  Get all files with a purpose

  **Parameters:**

  - `self`
  - `purpose` (FilePurpose)


  **Returns:** List[FileMetadata]


  #### `get_statistics`

  ```python
  get_statistics(self) -> Dict[str, Any]
  ```

  Get scanning statistics

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---
