# regeneration_tracker

CORTEX Regeneration Tracker

Intelligent change detection system for document/image/diagram regeneration.
Only regenerates files when source content or dependencies actually change.

Features:
- SHA256 content hashing for accurate change detection
- Dependency tracking (templates, configs affect outputs)
- Manifest persistence (survives git operations)
- Statistics tracking (time saved, files skipped)
- Force regeneration override

Usage:
    tracker = RegenerationTracker()
    
    # Check if file needs regeneration
    if tracker.should_regenerate("output.md", ["source.yaml", "template.j2"]):
        regenerate_file()
        tracker.mark_regenerated("output.md", ["source.yaml", "template.j2"])
    
    # Force regeneration
    tracker.force_regenerate_all()

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0


## Table of Contents

### Classes
- [RegenerationTracker](#regenerationtracker)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, hashlib, pathlib, src, time, typing, yaml


## Classes

### RegenerationTracker

```python
class RegenerationTracker
```

Tracks content changes to enable intelligent incremental regeneration.


**Methods:**

  #### `compute_file_hash`

  ```python
  compute_file_hash(self, file_path: Path) -> str
  ```

  Compute SHA256 hash of file content.

Args:
    file_path: Path to file (relative to CORTEX root or absolute)

Returns:
    SHA256 hash as hex string

  **Parameters:**

  - `self`
  - `file_path` (Path): Path to file (relative to CORTEX root or absolute)


  **Returns:** str
    SHA256 hash as hex string


  #### `compute_combined_hash`

  ```python
  compute_combined_hash(self, file_paths: List[Path]) -> str
  ```

  Compute combined hash of multiple files (for dependencies).

Args:
    file_paths: List of file paths

Returns:
    SHA256 hash of concatenated file hashes

  **Parameters:**

  - `self`
  - `file_paths` (List[Path]): List of file paths


  **Returns:** str
    SHA256 hash of concatenated file hashes


  #### `should_regenerate`

  ```python
  should_regenerate(self, output_file: str, source_dependencies: List[str], category: str) -> Tuple[bool, str]
  ```

  Check if output file needs regeneration.

Args:
    output_file: Path to output file (relative to CORTEX root)
    source_dependencies: List of source files that generate this output
    category: Type of file ('documents', 'images', 'diagrams')

Returns:
    Tuple of (should_regenerate: bool, reason: str)

  **Parameters:**

  - `self`
  - `output_file` (str): Path to output file (relative to CORTEX root)
  - `source_dependencies` (List[str]): List of source files that generate this output
  - `category` (str) = `'documents'`: Type of file ('documents', 'images', 'diagrams')


  **Returns:** Tuple[bool, str]
    Tuple of (should_regenerate: bool, reason: str)


  #### `mark_regenerated`

  ```python
  mark_regenerated(self, output_file: str, source_dependencies: List[str], category: str, additional_metadata: Optional[Dict])
  ```

  Mark file as regenerated and update manifest.

Args:
    output_file: Path to output file (relative to CORTEX root)
    source_dependencies: List of source files used to generate output
    category: Type of file ('documents', 'images', 'diagrams')
    additional_metadata: Optional extra data to store (e.g., generation params)

  **Parameters:**

  - `self`
  - `output_file` (str): Path to output file (relative to CORTEX root)
  - `source_dependencies` (List[str]): List of source files used to generate output
  - `category` (str) = `'documents'`: Type of file ('documents', 'images', 'diagrams')
  - `additional_metadata` (Optional[Dict]) = `None`: Optional extra data to store (e.g., generation params)


  #### `mark_full_regeneration`

  ```python
  mark_full_regeneration(self)
  ```

  Mark that a full regeneration occurred.

  **Parameters:**

  - `self`


  #### `finalize`

  ```python
  finalize(self) -> Dict
  ```

  Finalize tracking session and save manifest.

Returns:
    Summary statistics

  **Parameters:**

  - `self`


  **Returns:** Dict
    Summary statistics


  #### `get_statistics`

  ```python
  get_statistics(self) -> Dict
  ```

  Get regeneration statistics.

  **Parameters:**

  - `self`


  **Returns:** Dict


  #### `clear_manifest`

  ```python
  clear_manifest(self)
  ```

  Clear all tracking data (for force regeneration).

  **Parameters:**

  - `self`


  #### `get_tracked_files`

  ```python
  get_tracked_files(self, category: Optional[str]) -> List[str]
  ```

  Get list of tracked files.

Args:
    category: Optional category filter ('documents', 'images', 'diagrams')

Returns:
    List of tracked file paths

  **Parameters:**

  - `self`
  - `category` (Optional[str]) = `None`: Optional category filter ('documents', 'images', 'diagrams')


  **Returns:** List[str]
    List of tracked file paths


  #### `print_summary`

  ```python
  print_summary(self)
  ```

  Print tracking summary.

  **Parameters:**

  - `self`



---
