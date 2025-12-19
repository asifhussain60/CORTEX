# intent_router_auto_fixer

Intent Router Auto-Fixer for CORTEX Align v2.0

Automatically adds missing operations to the intent router with appropriate triggers.
Analyzes operation files to extract natural language triggers and adds them to the
routing configuration.

Author: Asif Hussain
Date: December 3, 2025
Version: 1.0.0


## Table of Contents

### Classes
- [IntentRouterFix](#intentrouterfix)
- [IntentRouterAutoFixer](#intentrouterautofixer)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** dataclasses, logging, pathlib, re, typing, yaml


## Classes

### IntentRouterFix

```python
class IntentRouterFix
```

**Decorators:** `dataclass`

Result of adding operation to intent router.


**Attributes:**

- `success`: bool
- `operation_name`: str
- `triggers`: List[str]
- `error_message`: str



---

### IntentRouterAutoFixer

```python
class IntentRouterAutoFixer
```

Automatically adds missing operations to intent router.


**Methods:**

  #### `extract_triggers_from_operation`

  ```python
  extract_triggers_from_operation(self, operation_name: str) -> List[str]
  ```

  Extract natural language triggers for an operation.

Args:
    operation_name: Name of the operation (e.g., 'align', 'tdd')

Returns:
    List of natural language trigger phrases

  **Parameters:**

  - `self`
  - `operation_name` (str): Name of the operation (e.g., 'align', 'tdd')


  **Returns:** List[str]
    List of natural language trigger phrases


  #### `add_to_intent_router`

  ```python
  add_to_intent_router(self, operation_name: str, triggers: Optional[List[str]], dry_run: bool) -> IntentRouterFix
  ```

  Add operation to intent router configuration.

Args:
    operation_name: Name of the operation to add
    triggers: Optional list of trigger phrases (auto-extracted if None)
    dry_run: If True, don't modify files

Returns:
    IntentRouterFix result

  **Parameters:**

  - `self`
  - `operation_name` (str): Name of the operation to add
  - `triggers` (Optional[List[str]]) = `None`: Optional list of trigger phrases (auto-extracted if None)
  - `dry_run` (bool) = `False`: If True, don't modify files


  **Returns:** IntentRouterFix
    IntentRouterFix result


  #### `fix_missing_operations`

  ```python
  fix_missing_operations(self, missing_operations: List[str], dry_run: bool) -> List[IntentRouterFix]
  ```

  Fix multiple missing operations at once.

Args:
    missing_operations: List of operation names to add
    dry_run: If True, don't modify files

Returns:
    List of IntentRouterFix results

  **Parameters:**

  - `self`
  - `missing_operations` (List[str]): List of operation names to add
  - `dry_run` (bool) = `False`: If True, don't modify files


  **Returns:** List[IntentRouterFix]
    List of IntentRouterFix results



---
