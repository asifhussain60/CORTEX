# file_reorganization_engine

CORTEX Cleanup: File Reorganization Engine

Reorganizes files into proper structure and automatically updates all references.
Tracks moves and updates imports, paths, and links across the codebase.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms


## Table of Contents

### Classes
- [ReorganizationRule](#reorganizationrule)
- [FileMove](#filemove)
- [FileReorganizationEngine](#filereorganizationengine)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, file_scanner, json, logging, pathlib, re, reference_tracker, shutil, typing


## Classes

### ReorganizationRule

```python
class ReorganizationRule
```

**Decorators:** `dataclass`

Rule for reorganizing files


**Attributes:**

- `name`: str
- `description`: str
- `source_pattern`: str
- `destination_template`: str
- `category_filter`: Optional[FileCategory]
- `purpose_filter`: Optional[FilePurpose]
- `priority`: int



---

### FileMove

```python
class FileMove
```

**Decorators:** `dataclass`

Record of a file move operation


**Attributes:**

- `old_path`: str
- `new_path`: str
- `reason`: str
- `timestamp`: datetime
- `references_updated`: List[str]


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

### FileReorganizationEngine

```python
class FileReorganizationEngine
```

File reorganization engine with automatic reference updating.

Capabilities:
- Rule-based file reorganization
- Automatic Python import updates
- File path reference updates
- Markdown link updates
- Config file reference updates
- Move tracking and rollback capability


**Methods:**

  #### `add_rule`

  ```python
  add_rule(self, rule: ReorganizationRule) -> None
  ```

  Add custom reorganization rule

  **Parameters:**

  - `self`
  - `rule` (ReorganizationRule)


  **Returns:** None


  #### `analyze_reorganization`

  ```python
  analyze_reorganization(self, files: Dict[str, FileMetadata]) -> Dict[str, str]
  ```

  Analyze files and determine reorganization plan.

Args:
    files: Dictionary of relative_path -> FileMetadata
    
Returns:
    Dictionary of old_path -> new_path for all moves

  **Parameters:**

  - `self`
  - `files` (Dict[str, FileMetadata]): Dictionary of relative_path -> FileMetadata


  **Returns:** Dict[str, str]
    Dictionary of old_path -> new_path for all moves


  #### `execute_reorganization`

  ```python
  execute_reorganization(self, reorganization_plan: Dict[str, str], dry_run: bool) -> Dict[str, Any]
  ```

  Execute file reorganization with reference updates.

Args:
    reorganization_plan: Dictionary of old_path -> new_path
    dry_run: If True, only simulate moves
    
Returns:
    Dictionary with reorganization results

  **Parameters:**

  - `self`
  - `reorganization_plan` (Dict[str, str]): Dictionary of old_path -> new_path
  - `dry_run` (bool) = `True`: If True, only simulate moves


  **Returns:** Dict[str, Any]
    Dictionary with reorganization results


  #### `generate_move_manifest`

  ```python
  generate_move_manifest(self, output_path: Optional[Path]) -> Path
  ```

  Generate manifest of all file moves

  **Parameters:**

  - `self`
  - `output_path` (Optional[Path]) = `None`


  **Returns:** Path


  #### `get_statistics`

  ```python
  get_statistics(self) -> Dict[str, Any]
  ```

  Get reorganization statistics

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---
