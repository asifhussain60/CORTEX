# evaluate_cortex_architecture_module

Evaluate CORTEX Architecture Module - Story Refresh Operation

This module evaluates the current CORTEX architecture state by loading
CORTEX-UNIFIED-ARCHITECTURE.yaml and extracting feature inventory,
implementation status, and architecture patterns.

Author: Asif Hussain
Version: 1.0


## Table of Contents

### Classes
- [EvaluateCortexArchitectureModule](#evaluatecortexarchitecturemodule)

### Functions
- [register](#register)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** datetime, logging, pathlib, src, typing, yaml


## Classes

### EvaluateCortexArchitectureModule

```python
class EvaluateCortexArchitectureModule(BaseOperationModule)
```

Evaluate current CORTEX architecture from CORTEX-UNIFIED-ARCHITECTURE.yaml.

This module loads the unified architecture document and extracts:
- Feature inventory (all components, agents, operations, plugins)
- Implementation status (completion %, tests passing, metrics)
- Architecture patterns (SOLID, plugin system, etc.)
- Changes since last refresh (if timestamp provided)

What it does:
    1. Loads CORTEX-UNIFIED-ARCHITECTURE.yaml
    2. Extracts core components (tiers, agents, operations, plugins)
    3. Extracts implementation status (progress, tests, metrics)
    4. Extracts architecture patterns
    5. Compares with last refresh timestamp (optional)


**Methods:**

  #### `get_metadata`

  ```python
  get_metadata(self) -> OperationModuleMetadata
  ```

  Return module metadata.

  **Parameters:**

  - `self`


  **Returns:** OperationModuleMetadata


  #### `validate_prerequisites`

  ```python
  validate_prerequisites(self, context: Dict[str, Any]) -> tuple[bool, List[str]]
  ```

  Validate prerequisites.

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** tuple[bool, List[str]]


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Evaluate CORTEX architecture with mode detection.

Args:
    context: Shared context dictionary
        - Input: project_root (Path), last_refresh_timestamp (optional datetime)
          refresh_mode (optional: 'auto' | 'generate-from-scratch' | 'update-in-place')
          change_magnitude_threshold (optional: float, default 0.20)
        - Output: feature_inventory, implementation_status, architecture_patterns, 
          changes_since_last_refresh, recommended_mode, change_magnitude, mode_rationale

Returns:
    OperationResult with architecture evaluation and mode recommendation

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Shared context dictionary


  **Returns:** OperationResult
    OperationResult with architecture evaluation and mode recommendation


  #### `rollback`

  ```python
  rollback(self, context: Dict[str, Any]) -> OperationResult
  ```

  Rollback architecture evaluation (no-op).

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** OperationResult



---

## Functions

### register

```python
register() -> BaseOperationModule
```

Register module with operation system.


**Returns:** BaseOperationModule


---
