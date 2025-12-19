# tier_validator

CORTEX Tier Validator - Validates Brain Tier Integrity

Ensures data is stored in the correct tier and validates tier boundaries:
- Tier 0: Immutable governance rules (brain-protection-rules.yaml)
- Tier 1: Conversation history and working memory (SQLite)
- Tier 2: Knowledge graph and learned patterns (YAML)
- Tier 3: Development context and project health (YAML)

Part of Brain Protection Layer
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Created: 2025-11-11


## Table of Contents

### Classes
- [TierLevel](#tierlevel)
- [ValidationSeverity](#validationseverity)
- [TierViolation](#tierviolation)
- [TierValidationResult](#tiervalidationresult)
- [TierValidator](#tiervalidator)

### Functions
- [validate_brain_tiers](#validate_brain_tiers)


## Overview

- **Classes:** 5
- **Functions:** 1
- **Dependencies:** dataclasses, enum, json, pathlib, sqlite3, src, sys, typing, yaml


## Classes

### TierLevel

```python
class TierLevel(Enum)
```

CORTEX tier levels.



---

### ValidationSeverity

```python
class ValidationSeverity(Enum)
```

Validation result severity levels.



---

### TierViolation

```python
class TierViolation
```

**Decorators:** `dataclass`

A tier boundary violation.


**Attributes:**

- `tier`: TierLevel
- `violation_type`: str
- `severity`: ValidationSeverity
- `message`: str
- `affected_file`: Optional[str]
- `suggestion`: Optional[str]



---

### TierValidationResult

```python
class TierValidationResult
```

**Decorators:** `dataclass`

Result of tier validation.


**Attributes:**

- `passed`: bool
- `tier`: TierLevel
- `violations`: List[TierViolation]
- `warnings`: List[TierViolation]
- `metadata`: Dict[str, Any]



---

### TierValidator

```python
class TierValidator
```

Validates CORTEX brain tier integrity.

Ensures:
1. Tier 0 contains only immutable governance rules
2. Tier 1 contains only conversation data
3. Tier 2 contains only aggregated patterns
4. Tier 3 contains only development context
5. No cross-tier data leakage


**Methods:**

  #### `validate_all_tiers`

  ```python
  validate_all_tiers(self) -> Dict[TierLevel, TierValidationResult]
  ```

  Validate all tiers for integrity.

Returns:
    Dictionary mapping tier to validation result

  **Parameters:**

  - `self`


  **Returns:** Dict[TierLevel, TierValidationResult]
    Dictionary mapping tier to validation result


  #### `validate_tier`

  ```python
  validate_tier(self, tier: TierLevel) -> TierValidationResult
  ```

  Validate a specific tier.

Args:
    tier: Tier to validate

Returns:
    TierValidationResult with violations and warnings

  **Parameters:**

  - `self`
  - `tier` (TierLevel): Tier to validate


  **Returns:** TierValidationResult
    TierValidationResult with violations and warnings


  #### `generate_report`

  ```python
  generate_report(self, results: Dict[TierLevel, TierValidationResult]) -> str
  ```

  Generate human-readable validation report.

Args:
    results: Validation results for all tiers

Returns:
    Formatted report string

  **Parameters:**

  - `self`
  - `results` (Dict[TierLevel, TierValidationResult]): Validation results for all tiers


  **Returns:** str
    Formatted report string



---

## Functions

### validate_brain_tiers

```python
validate_brain_tiers() -> bool
```

Convenience function to validate all brain tiers.

Returns:
    True if all tiers passed validation


**Returns:** bool
  True if all tiers passed validation


---
