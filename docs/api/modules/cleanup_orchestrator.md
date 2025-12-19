# cleanup_orchestrator

Cleanup Orchestrator for CORTEX 3.0 - Enhanced Edition

Comprehensive workspace cleanup orchestrator with advanced capabilities:
- Recursive file scanning and categorization
- Smart deletion with safety validation
- File reorganization with automatic reference updates
- Document consolidation
- Script/test organization
- Git recovery capability
- Comprehensive reporting

NEW CAPABILITIES (v3.0):
- Deep recursive scanning from repo root
- Intelligent file categorization (type, purpose, age)
- Reference tracking across Python imports, paths, markdown links
- Automatic import/path/link updates when files move
- Smart deletion rules with risk assessment
- Post-cleanup verification with git recovery
- Comprehensive audit trail and reporting

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms


## Table of Contents

### Classes
- [CleanupOrchestrator](#cleanuporchestrator)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** collections, datetime, hashlib, json, logging, pathlib, re, remove_obsolete_tests_module, shutil, src, subprocess, typing


## Classes

### CleanupOrchestrator

```python
class CleanupOrchestrator(BaseOperationModule)
```

Orchestrates comprehensive workspace cleanup with:
- Backup file management (GitHub archival before deletion)
- Root folder organization
- File reorganization to correct locations
- MD file consolidation (removes duplicates)
- Bloat detection for entry points/orchestrators
- Automatic optimization trigger after cleanup


**Methods:**

  #### `get_metadata`

  ```python
  get_metadata(self) -> OperationModuleMetadata
  ```

  Module metadata.

  **Parameters:**

  - `self`


  **Returns:** OperationModuleMetadata


  #### `check_prerequisites`

  ```python
  check_prerequisites(self, context: Dict[str, Any]) -> Dict[str, Any]
  ```

  Check if cleanup can run

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** Dict[str, Any]


  #### `execute_enhanced`

  ```python
  execute_enhanced(self, context: Dict[str, Any]) -> OperationResult
  ```

  Execute ENHANCED comprehensive cleanup workflow (v3.0).

NEW WORKFLOW:
1. Deep recursive scanning and categorization
2. Reference tracking (imports, paths, links)
3. Smart deletion with risk assessment
4. File reorganization with auto-reference updates
5. Document consolidation
6. Script/test organization
7. Final verification with git recovery
8. Comprehensive reporting

Args:
    context: Execution context with options
    
Returns:
    OperationResult with comprehensive cleanup data

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Execution context with options


  **Returns:** OperationResult
    OperationResult with comprehensive cleanup data


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Execute comprehensive cleanup workflow

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** OperationResult



---
