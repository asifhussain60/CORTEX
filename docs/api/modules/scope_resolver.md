# scope_resolver

Scope Resolver - Determine Discovery Scope

Resolves user input into a concrete DiscoveryScope with validated paths
and exclusion patterns.

Author: Asif Hussain
Version: 1.0.0


## Table of Contents

### Classes
- [ScopeResolver](#scoperesolver)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** logging, models, pathlib, typing


## Classes

### ScopeResolver

```python
class ScopeResolver
```

Resolves discovery scope from user input.

Handles:
- Path resolution (relative to absolute)
- Scope validation
- Default pattern application
- Estimated file count calculation


**Methods:**

  #### `resolve`

  ```python
  resolve(self, scope_input: str | Path | Dict[str, Any], depth: str) -> DiscoveryScope
  ```

  Resolve scope from user input.

Args:
    scope_input: Scope specification (path, "project", or dict)
    depth: Discovery depth ("quick", "moderate", "full")

Returns:
    Resolved DiscoveryScope object

Raises:
    ValueError: If scope cannot be resolved

  **Parameters:**

  - `self`
  - `scope_input` (str | Path | Dict[str, Any]): Scope specification (path, "project", or dict)
  - `depth` (str) = `'moderate'`: Discovery depth ("quick", "moderate", "full")


  **Returns:** DiscoveryScope
    Resolved DiscoveryScope object


  #### `validate_scope`

  ```python
  validate_scope(self, scope: DiscoveryScope) -> bool
  ```

  Validate that scope is viable.

Args:
    scope: DiscoveryScope to validate

Returns:
    True if valid

Raises:
    ValueError: If scope is invalid

  **Parameters:**

  - `self`
  - `scope` (DiscoveryScope): DiscoveryScope to validate


  **Returns:** bool
    True if valid


  #### `estimate_file_count`

  ```python
  estimate_file_count(self, scope: DiscoveryScope) -> int
  ```

  Estimate number of files in scope.

Args:
    scope: DiscoveryScope to estimate

Returns:
    Estimated file count

  **Parameters:**

  - `self`
  - `scope` (DiscoveryScope): DiscoveryScope to estimate


  **Returns:** int
    Estimated file count



---
