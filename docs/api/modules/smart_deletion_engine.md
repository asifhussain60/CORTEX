# smart_deletion_engine

CORTEX Cleanup: Smart Deletion Engine

Intelligently identifies and safely deletes obsolete files using rules and analysis.
Generates deletion manifest for review and rollback capability.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms


## Table of Contents

### Classes
- [DeletionReason](#deletionreason)
- [DeletionRisk](#deletionrisk)
- [DeletionCandidate](#deletioncandidate)
- [SmartDeletionEngine](#smartdeletionengine)


## Overview

- **Classes:** 4
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, enum, file_scanner, json, logging, pathlib, typing


## Classes

### DeletionReason

```python
class DeletionReason(Enum)
```

Reason for file deletion



---

### DeletionRisk

```python
class DeletionRisk(Enum)
```

Risk level of deletion



---

### DeletionCandidate

```python
class DeletionCandidate
```

**Decorators:** `dataclass`

File candidate for deletion


**Attributes:**

- `metadata`: FileMetadata
- `reason`: DeletionReason
- `risk`: DeletionRisk
- `confidence`: float
- `evidence`: List[str]
- `related_files`: List[str]


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

### SmartDeletionEngine

```python
class SmartDeletionEngine
```

Intelligent file deletion engine.

Capabilities:
- Rule-based deletion identification
- Safety validation (protected files, dependencies)
- Risk assessment
- Manifest generation for review
- Safe deletion with rollback capability


**Methods:**

  #### `analyze`

  ```python
  analyze(self, files: Dict[str, FileMetadata], dependency_graph: Dict[str, Set[str]]) -> List[DeletionCandidate]
  ```

  Analyze files and identify deletion candidates.

Args:
    files: Dictionary of relative_path -> FileMetadata
    dependency_graph: Dictionary of file -> files that depend on it
    
Returns:
    List of deletion candidates

  **Parameters:**

  - `self`
  - `files` (Dict[str, FileMetadata]): Dictionary of relative_path -> FileMetadata
  - `dependency_graph` (Dict[str, Set[str]]): Dictionary of file -> files that depend on it


  **Returns:** List[DeletionCandidate]
    List of deletion candidates


  #### `generate_manifest`

  ```python
  generate_manifest(self, output_path: Optional[Path]) -> Path
  ```

  Generate deletion manifest for review.

Args:
    output_path: Optional custom output path
    
Returns:
    Path to generated manifest

  **Parameters:**

  - `self`
  - `output_path` (Optional[Path]) = `None`: Optional custom output path


  **Returns:** Path
    Path to generated manifest


  #### `execute_deletions`

  ```python
  execute_deletions(self, dry_run: bool, risk_filter: Optional[Set[DeletionRisk]]) -> Dict[str, Any]
  ```

  Execute file deletions.

Args:
    dry_run: If True, only simulate deletions
    risk_filter: Optional set of risk levels to delete (defaults to safe auto-delete)
    
Returns:
    Dictionary with deletion results

  **Parameters:**

  - `self`
  - `dry_run` (bool) = `True`: If True, only simulate deletions
  - `risk_filter` (Optional[Set[DeletionRisk]]) = `None`: Optional set of risk levels to delete (defaults to safe auto-delete)


  **Returns:** Dict[str, Any]
    Dictionary with deletion results


  #### `get_candidates_by_risk`

  ```python
  get_candidates_by_risk(self, risk: DeletionRisk) -> List[DeletionCandidate]
  ```

  Get all candidates with specific risk level

  **Parameters:**

  - `self`
  - `risk` (DeletionRisk)


  **Returns:** List[DeletionCandidate]


  #### `get_candidates_by_reason`

  ```python
  get_candidates_by_reason(self, reason: DeletionReason) -> List[DeletionCandidate]
  ```

  Get all candidates with specific deletion reason

  **Parameters:**

  - `self`
  - `reason` (DeletionReason)


  **Returns:** List[DeletionCandidate]


  #### `get_statistics`

  ```python
  get_statistics(self) -> Dict[str, Any]
  ```

  Get deletion statistics

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---
