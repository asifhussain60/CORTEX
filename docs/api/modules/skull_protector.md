# skull_protector

SKULL Protection Layer - Safety, Knowledge, Validation & Learning Layer

Prevents development violations by enforcing test validation requirements.

Created: 2025-11-09
Trigger: CSS + Vision API testing failures incident


## Table of Contents

### Classes
- [SkullRuleId](#skullruleid)
- [EnforcementLevel](#enforcementlevel)
- [SkullValidation](#skullvalidation)
- [FixValidationRequest](#fixvalidationrequest)
- [SkullProtector](#skullprotector)
- [SkullProtectionError](#skullprotectionerror)

### Functions
- [enforce_skull](#enforce_skull)


## Overview

- **Classes:** 6
- **Functions:** 1
- **Dependencies:** dataclasses, enum, logging, typing


## Classes

### SkullRuleId

```python
class SkullRuleId(Enum)
```

SKULL protection rule identifiers.



---

### EnforcementLevel

```python
class EnforcementLevel(Enum)
```

Enforcement levels for SKULL rules.



---

### SkullValidation

```python
class SkullValidation
```

**Decorators:** `dataclass`

Result of SKULL validation check.


**Attributes:**

- `passed`: bool
- `rule_id`: Optional[SkullRuleId]
- `rule_name`: str
- `message`: str
- `enforcement`: EnforcementLevel
- `tests_required`: List[str]
- `tests_found`: List[str]



---

### FixValidationRequest

```python
class FixValidationRequest
```

**Decorators:** `dataclass`

Request to validate a fix against SKULL rules.


**Attributes:**

- `fix_type`: str
- `tests_run`: List[str]
- `verification`: Optional[Dict[str, Any]]
- `description`: str



---

### SkullProtector

```python
class SkullProtector
```

SKULL Protection Layer - Enforces quality standards and test requirements.

The SKULL protects the CORTEX brain from untested changes, false claims,
and quality degradation.


**Methods:**

  #### `validate_fix`

  ```python
  validate_fix(self, request: FixValidationRequest) -> SkullValidation
  ```

  Validate a fix against SKULL protection rules.

Args:
    request: Fix validation request with test info
    
Returns:
    SkullValidation result
    
Raises:
    SkullProtectionError: If BLOCKING rule violated

  **Parameters:**

  - `self`
  - `request` (FixValidationRequest): Fix validation request with test info


  **Returns:** SkullValidation
    SkullValidation result



---

### SkullProtectionError

```python
class SkullProtectionError(Exception)
```

Raised when a BLOCKING SKULL rule is violated.


**Methods:**


---

## Functions

### enforce_skull

```python
enforce_skull(request: FixValidationRequest) -> SkullValidation
```

Convenience function to enforce SKULL protection.

Args:
    request: Fix validation request
    
Returns:
    SkullValidation result
    
Raises:
    SkullProtectionError: If BLOCKING rule violated


**Parameters:**

- `request` (FixValidationRequest): Fix validation request


**Returns:** SkullValidation
  SkullValidation result


---
