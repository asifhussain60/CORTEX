# deploy_docs_preview_module

Deploy documentation preview module.

Part of the Documentation Update operation - deploys or serves documentation preview.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary


## Table of Contents

### Classes
- [DeployDocsPreviewModule](#deploydocspreviewmodule)

### Functions
- [get_github_config](#get_github_config)
- [register](#register)


## Overview

- **Classes:** 1
- **Functions:** 2
- **Dependencies:** os, pathlib, src, subprocess, typing, urllib


## Classes

### DeployDocsPreviewModule

```python
class DeployDocsPreviewModule(BaseOperationModule)
```

Deploy documentation preview.

Starts a local MkDocs server for documentation preview,
or optionally deploys to GitHub Pages (if configured).


**Methods:**

  #### `get_metadata`

  ```python
  get_metadata(self) -> OperationModuleMetadata
  ```

  Get module metadata.

  **Parameters:**

  - `self`


  **Returns:** OperationModuleMetadata


  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> OperationResult
  ```

  Execute documentation preview deployment.

Args:
    context: Operation context
    
Returns:
    OperationResult with deployment status

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Operation context


  **Returns:** OperationResult
    OperationResult with deployment status



---

## Functions

### get_github_config

```python
get_github_config()
```

Get GitHub configuration to avoid hardcoded URL patterns.


---

### register

```python
register() -> BaseOperationModule
```

Register module for discovery.


**Returns:** BaseOperationModule


---
