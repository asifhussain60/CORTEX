# git_recovery_manifest

Git Recovery Manifest Generator for CORTEX Cleanup

Creates comprehensive manifests of deleted files with git commit hashes
and file content snapshots for easy recovery.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [GitRecoveryManifest](#gitrecoverymanifest)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, hashlib, json, logging, pathlib, subprocess, typing


## Classes

### GitRecoveryManifest

```python
class GitRecoveryManifest
```

Generates comprehensive manifests for git recovery of deleted files.

Capabilities:
- Captures git commit hash for each deleted file
- Records file content hash (SHA256)
- Stores file metadata (size, mtime, path)
- Generates recovery commands
- Enables bulk or selective recovery


**Methods:**

  #### `create_deletion_manifest`

  ```python
  create_deletion_manifest(self, files_to_delete: List[Path], operation_type: str, dry_run: bool) -> Path
  ```

  Create comprehensive deletion manifest with git recovery info.

Args:
    files_to_delete: List of file paths to be deleted
    operation_type: Type of cleanup operation
    dry_run: If True, creates manifest but doesn't verify git hashes
    
Returns:
    Path to created manifest file

  **Parameters:**

  - `self`
  - `files_to_delete` (List[Path]): List of file paths to be deleted
  - `operation_type` (str) = `'cleanup'`: Type of cleanup operation
  - `dry_run` (bool) = `False`: If True, creates manifest but doesn't verify git hashes


  **Returns:** Path
    Path to created manifest file


  #### `create_reorganization_manifest`

  ```python
  create_reorganization_manifest(self, file_moves: List[Tuple[Path, Path]], dry_run: bool) -> Path
  ```

  Create manifest for file reorganization (moves).

Args:
    file_moves: List of (old_path, new_path) tuples
    dry_run: If True, creates manifest but doesn't verify git hashes
    
Returns:
    Path to created manifest file

  **Parameters:**

  - `self`
  - `file_moves` (List[Tuple[Path, Path]]): List of (old_path, new_path) tuples
  - `dry_run` (bool) = `False`: If True, creates manifest but doesn't verify git hashes


  **Returns:** Path
    Path to created manifest file


  #### `load_manifest`

  ```python
  load_manifest(self, manifest_path: Path) -> Dict[str, Any]
  ```

  Load existing manifest

  **Parameters:**

  - `self`
  - `manifest_path` (Path)


  **Returns:** Dict[str, Any]


  #### `recover_from_manifest`

  ```python
  recover_from_manifest(self, manifest_path: Path, file_paths: Optional[List[str]], dry_run: bool) -> Dict[str, Any]
  ```

  Recover files from a manifest.

Args:
    manifest_path: Path to deletion manifest
    file_paths: Specific files to recover (None = all)
    dry_run: If True, only show what would be recovered
    
Returns:
    Dict with recovery stats

  **Parameters:**

  - `self`
  - `manifest_path` (Path): Path to deletion manifest
  - `file_paths` (Optional[List[str]]) = `None`: Specific files to recover (None = all)
  - `dry_run` (bool) = `True`: If True, only show what would be recovered


  **Returns:** Dict[str, Any]
    Dict with recovery stats



---
