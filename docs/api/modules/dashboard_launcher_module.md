# dashboard_launcher_module

Dashboard Launcher Module

Module wrapper for dashboard launcher orchestrator. Part of CORTEX operations system.

Triggered by: "load dashboard", "launch dashboard", "open dashboard"

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [DashboardLauncherModule](#dashboardlaunchermodule)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** pathlib, src, typing


## Classes

### DashboardLauncherModule

```python
class DashboardLauncherModule(BaseOperationModule)
```

Launch CORTEX dashboard with HTTP server.

Features:
- Auto-detect cortex-brain/dashboards/ui/ directory
- Launch HTTP server on available port (8080-8089)
- Auto-open browser to dashboard
- Background server process
- CORS support


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

  Execute dashboard launch.

Args:
    context: Operation context with optional keys:
        - port: int (default: 8080)
        - auto_open: bool (default: True)
        - source: str (default: "mock")
        - cortex_root: Path (auto-detected if not provided)

Returns:
    OperationResult with launch status and server details

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Operation context with optional keys:


  **Returns:** OperationResult
    OperationResult with launch status and server details



---
