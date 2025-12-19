# vision_api_module

Vision API Setup Module

Activates GitHub Copilot Vision API for screenshot analysis in CORTEX.

SOLID Principles:
- Single Responsibility: Only handles Vision API activation
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [VisionAPIModule](#visionapimodule)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** PIL, datetime, json, pathlib, src, typing


## Classes

### VisionAPIModule

```python
class VisionAPIModule(BaseOperationModule)
```

Setup module for activating Vision API.

Responsibilities:
1. Verify cortex.config.json exists
2. Enable vision_api.enabled flag
3. Configure default settings if not present
4. Verify Pillow/PIL is installed (optional, for preprocessing)
5. Update context for downstream modules

Configuration (from YAML):
    config_file: Path to cortex.config.json
    config_path: JSON path to enable (e.g., "vision_api.enabled")
    max_tokens_per_image: Token budget per image
    cache_results: Whether to cache analysis results
    requires_copilot: Whether GitHub Copilot is required


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
  validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]
  ```

  Validate prerequisites for Vision API activation.

Checks:
1. Project root exists in context
2. cortex.config.json exists
3. Config file is valid JSON

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** Tuple[bool, List[str]]


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Execute Vision API activation.

Steps:
1. Load cortex.config.json
2. Enable vision_api.enabled = true
3. Set default configuration if missing
4. Save updated config
5. Update context

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** OperationResult


  #### `rollback`

  ```python
  rollback(self, context: Dict[str, Any]) -> bool
  ```

  Rollback Vision API activation.

Disables vision_api.enabled in config.

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** bool


  #### `should_run`

  ```python
  should_run(self, context: Dict[str, Any]) -> bool
  ```

  Determine if Vision API setup should run.

Runs if:
- User explicitly requested full setup
- User included 'vision' in setup request

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any])


  **Returns:** bool



---
