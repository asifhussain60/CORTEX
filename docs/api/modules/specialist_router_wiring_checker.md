# specialist_router_wiring_checker

Specialist Router Wiring Checker for CORTEX Align v2.0

Detects and fixes unwired specialist intent routers (TDD, Strategic, etc.)
that exist but aren't integrated into the main request flow.

Problem:
- Specialist routers exist (TDDIntentRouter, etc) but aren't called
- Main IntentRouter in cortex_agents/intent_router.py doesn't delegate to them
- Result: Features like auto-TDD activation don't work

Solution:
- Detect all specialist router classes
- Check if main IntentRouter imports and uses them
- Auto-generate wiring code to integrate them
- Validate integration after fix

Author: Asif Hussain
Date: December 4, 2025
Version: 1.0.0


## Table of Contents

### Classes
- [SpecialistRouter](#specialistrouter)
- [WiringIssue](#wiringissue)
- [SpecialistRouterWiringChecker](#specialistrouterwiringchecker)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** ast, dataclasses, logging, pathlib, re, traceback, typing


## Classes

### SpecialistRouter

```python
class SpecialistRouter
```

**Decorators:** `dataclass`

Metadata about a specialist intent router.


**Attributes:**

- `name`: str
- `file_path`: Path
- `module_path`: str
- `purpose`: str
- `intents_handled`: List[str]
- `is_wired`: bool



---

### WiringIssue

```python
class WiringIssue
```

**Decorators:** `dataclass`

An unwired router that needs integration.


**Attributes:**

- `router`: SpecialistRouter
- `severity`: str
- `impact`: str
- `fix_description`: str



---

### SpecialistRouterWiringChecker

```python
class SpecialistRouterWiringChecker
```

Detects and fixes unwired specialist routers.


**Methods:**

  #### `check_wiring`

  ```python
  check_wiring(self) -> Dict[str, Any]
  ```

  Check if all specialist routers are properly wired.

Returns:
    Dict with:
        - passed (bool): True if all routers wired
        - specialist_routers (list): All specialist routers found
        - wired_routers (list): Routers properly integrated
        - unwired_routers (list): Routers NOT integrated
        - issues (list): WiringIssue objects for unwired routers

  **Parameters:**

  - `self`


  **Returns:** Dict[str, Any]
    Dict with: - passed (bool): True if all routers wired - specialist_routers (list): All specialist routers found - wired_routers (list): Routers properly integrated - unwired_routers (list): Routers NOT integrated - issues (list): WiringIssue objects for unwired routers


  #### `fix_wiring`

  ```python
  fix_wiring(self, dry_run: bool) -> Dict[str, Any]
  ```

  Auto-fix unwired specialist routers.

Args:
    dry_run: If True, don't modify files, just report what would change

Returns:
    Dict with:
        - success (bool): True if all fixes applied
        - fixes_applied (list): Fixes that were applied
        - fixes_skipped (list): Fixes that couldn't be applied
        - errors (list): Errors encountered

  **Parameters:**

  - `self`
  - `dry_run` (bool) = `False`: If True, don't modify files, just report what would change


  **Returns:** Dict[str, Any]
    Dict with: - success (bool): True if all fixes applied - fixes_applied (list): Fixes that were applied - fixes_skipped (list): Fixes that couldn't be applied - errors (list): Errors encountered



---
