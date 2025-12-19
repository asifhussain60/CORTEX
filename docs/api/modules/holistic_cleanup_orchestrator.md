# holistic_cleanup_orchestrator

Holistic Cleanup Orchestrator for CORTEX 3.2

Performs comprehensive repository analysis and cleanup with:
- Recursive directory scanning
- Production-ready file naming validation
- Redundancy detection and elimination
- Detailed reporting before execution
- Safe execution with backup/rollback

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions) - See LICENSE


## Table of Contents

### Classes
- [FileInfo](#fileinfo)
- [CleanupManifest](#cleanupmanifest)
- [FileCategorizationEngine](#filecategorizationengine)
- [ProductionReadinessValidator](#productionreadinessvalidator)
- [HolisticRepositoryScanner](#holisticrepositoryscanner)
- [CleanupManifestGenerator](#cleanupmanifestgenerator)
- [HolisticCleanupOrchestrator](#holisticcleanuporchestrator)


## Overview

- **Classes:** 7
- **Functions:** 0
- **Dependencies:** cleanup_test_harness, cleanup_validator, cleanup_verifier, collections, dataclasses, datetime, hashlib, json, logging, markdown_consolidation_engine, pathlib, re, shutil, src, subprocess, typing


## Classes

### FileInfo

```python
class FileInfo
```

**Decorators:** `dataclass`

Information about a file


**Attributes:**

- `path`: str
- `name`: str
- `size`: int
- `modified`: datetime
- `categories`: List[str]
- `production_ready`: bool
- `violations`: List[Dict[str, str]]
- `recommended_name`: Optional[str]



---

### CleanupManifest

```python
class CleanupManifest
```

**Decorators:** `dataclass`

Comprehensive cleanup manifest


**Attributes:**

- `generated_at`: datetime
- `repository`: str
- `overview`: Dict[str, Any]
- `categories`: Dict[str, Any]
- `recommendations`: List[Dict[str, Any]]
- `proposed_actions`: List[Dict[str, Any]]


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict[str, Any]
  ```


---

### FileCategorizationEngine

```python
class FileCategorizationEngine
```

Categorize files by type, purpose, and status


**Methods:**

  #### `categorize_file`

  ```python
  categorize_file(self, file_path: Path) -> FileInfo
  ```

  Categorize a single file

  **Parameters:**

  - `self`
  - `file_path` (Path)


  **Returns:** FileInfo



---

### ProductionReadinessValidator

```python
class ProductionReadinessValidator
```

Validate files meet production naming standards


**Methods:**

  #### `validate_file`

  ```python
  validate_file(self, file_path: Path) -> FileInfo
  ```

  Check if file meets production standards

  **Parameters:**

  - `self`
  - `file_path` (Path)


  **Returns:** FileInfo



---

### HolisticRepositoryScanner

```python
class HolisticRepositoryScanner
```

Recursively scan entire repository


**Methods:**

  #### `scan_repository`

  ```python
  scan_repository(self) -> Dict[str, Any]
  ```

  Perform holistic scan

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]



---

### CleanupManifestGenerator

```python
class CleanupManifestGenerator
```

Generate comprehensive cleanup manifest


**Methods:**

  #### `generate_manifest`

  ```python
  generate_manifest(self, scan_results: Dict[str, Any]) -> CleanupManifest
  ```

  Create detailed cleanup manifest

  **Parameters:**

  - `self`
  - `scan_results` (Dict[str, Any])


  **Returns:** CleanupManifest



---

### HolisticCleanupOrchestrator

```python
class HolisticCleanupOrchestrator(BaseOperationModule)
```

Holistic cleanup orchestrator with:
- Recursive repository scanning
- Production-ready validation
- Detailed manifest generation
- Safe execution with backup/rollback


**Methods:**

  #### `get_metadata`

  ```python
  get_metadata(self) -> OperationModuleMetadata
  ```

  Module metadata

  **Parameters:**

  - `self`


  **Returns:** OperationModuleMetadata


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Execute holistic cleanup

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** OperationResult


  #### `execute_markdown_consolidation`

  ```python
  execute_markdown_consolidation(self, documents_root: Optional[Path], dry_run: bool) -> OperationResult
  ```

  Execute markdown file consolidation.

Args:
    documents_root: Root directory for documents (default: cortex-brain/documents)
    dry_run: If True, only preview changes
    
Returns:
    OperationResult with consolidation report

  **Parameters:**

  - `self`
  - `documents_root` (Optional[Path]) = `None`: Root directory for documents (default: cortex-brain/documents)
  - `dry_run` (bool) = `True`: If True, only preview changes


  **Returns:** OperationResult
    OperationResult with consolidation report



---
