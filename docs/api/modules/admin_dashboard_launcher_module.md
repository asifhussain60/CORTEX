# admin_dashboard_launcher_module

Admin Dashboard Launcher Module

Purpose: Launch enhanced CORTEX dashboard with repository selector dropdown.
         ADMIN ONLY - not included in production builds.

📖 COMPLETE DOCUMENTATION: cortex-brain/documents/implementation-guides/dashboard-operation-guide.md
   Read this guide for:
   - Launch commands and options
   - Data structure and file locations
   - Server configuration details
   - Troubleshooting common issues

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)

SECURITY: This module is admin-only and blocked from production by:
- deployment_tier: admin in cortex-operations.yaml
- Listed in publish-config.yaml admin_operations exclusion
- Validation gate in deployment pipeline


## Table of Contents

### Classes
- [AdminDashboardLauncherModule](#admindashboardlaunchermodule)

### Functions
- [execute](#execute)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** json, logging, os, pathlib, src, subprocess, sys, time, typing


## Classes

### AdminDashboardLauncherModule

```python
class AdminDashboardLauncherModule
```

Launch CORTEX dashboard with repository selector.

Admin Features:
- Lists all available dashboard data directories
- Provides dropdown selector UI
- Remembers last selected repository
- Auto-detects new repositories


**Methods:**

  #### `execute`

  ```python
  execute(self, context: Dict[str, Any]) -> Dict[str, Any]
  ```

  Execute admin dashboard launch.

Args:
    context: Execution context with options

Returns:
    Result dictionary

  **Parameters:**

  - `self`
  - `context` (Dict[str, Any]): Execution context with options


  **Returns:** Dict[str, Any]
    Result dictionary



---

## Functions

### execute

```python
execute(context: Dict[str, Any]) -> Dict[str, Any]
```

Module entry point.

Args:
    context: Execution context

Returns:
    Result dictionary


**Parameters:**

- `context` (Dict[str, Any]): Execution context


**Returns:** Dict[str, Any]
  Result dictionary


---
