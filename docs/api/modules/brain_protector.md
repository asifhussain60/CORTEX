# brain_protector

CORTEX Brain Protector - Architectural Integrity Guardian

Implements 6 protection layers to prevent degradation of CORTEX intelligence:
1. Instinct Immutability - Tier 0 governance rules cannot be bypassed
2. Tier Boundary Protection - Data stored in correct tier
3. SOLID Compliance - No God Objects, proper separation
4. Hemisphere Specialization - Strategic vs tactical separation
5. Knowledge Quality - Pattern validation and confidence thresholds
6. Commit Integrity - Brain state files excluded from commits

Phase 3 Task 3.2: Brain Protector Automation
Duration: 2-3 hours
Date: November 6, 2025

Updated: November 8, 2025 - YAML-based configuration
Now loads rules from cortex-brain/brain-protection-rules.yaml


## Table of Contents

### Classes
- [Severity](#severity)
- [ProtectionLayer](#protectionlayer)
- [Violation](#violation)
- [ModificationRequest](#modificationrequest)
- [ProtectionResult](#protectionresult)
- [Challenge](#challenge)
- [BrainProtector](#brainprotector)


## Overview

- **Classes:** 7
- **Functions:** 0
- **Dependencies:** dataclasses, datetime, enum, json, pathlib, src, typing, yaml


## Classes

### Severity

```python
class Severity(Enum)
```

Protection violation severity levels.



---

### ProtectionLayer

```python
class ProtectionLayer(Enum)
```

6 protection layers.



---

### Violation

```python
class Violation
```

**Decorators:** `dataclass`

A single protection violation.


**Attributes:**

- `layer`: ProtectionLayer
- `rule`: str
- `severity`: Severity
- `description`: str
- `evidence`: Optional[str]
- `file_path`: Optional[str]



---

### ModificationRequest

```python
class ModificationRequest
```

**Decorators:** `dataclass`

Request to modify CORTEX system.


**Attributes:**

- `intent`: str
- `description`: str
- `files`: List[str]
- `justification`: Optional[str]
- `user`: str
- `metadata`: Optional[Dict[str, Any]]



---

### ProtectionResult

```python
class ProtectionResult
```

**Decorators:** `dataclass`

Result of protection analysis.


**Attributes:**

- `severity`: Severity
- `violations`: List[Violation]
- `decision`: str
- `message`: str
- `alternatives`: List[str]
- `override_required`: bool



---

### Challenge

```python
class Challenge
```

**Decorators:** `dataclass`

Protection challenge presented to user.


**Attributes:**

- `timestamp`: str
- `request`: ModificationRequest
- `result`: ProtectionResult
- `challenge_text`: str
- `options`: List[str]



---

### BrainProtector

```python
class BrainProtector
```

Automates architectural protection challenges.

Implements 6 protection layers from brain-protection-rules.yaml:
1. Instinct Immutability - Cannot disable TDD, skip DoD/DoR
2. Tier Boundary Protection - Application paths not in Tier 0
3. SOLID Compliance - No God Objects, no mode switches
4. Hemisphere Specialization - RIGHT plans, LEFT executes
5. Knowledge Quality - Min 3 occurrences, max 0.50 single-event confidence
6. Commit Integrity - Brain state files excluded from commits


**Methods:**

  #### `analyze_request`

  ```python
  analyze_request(self, request: ModificationRequest) -> ProtectionResult
  ```

  Analyze modification request against all protection layers.

Args:
    request: Modification request to analyze

Returns:
    ProtectionResult with severity and violations

  **Parameters:**

  - `self`
  - `request` (ModificationRequest): Modification request to analyze


  **Returns:** ProtectionResult
    ProtectionResult with severity and violations


  #### `generate_challenge`

  ```python
  generate_challenge(self, violations: List[Violation]) -> Challenge
  ```

  Generate challenge with threat description, risks, and alternatives.

Args:
    violations: List of violations detected

Returns:
    Challenge object with formatted text and options

  **Parameters:**

  - `self`
  - `violations` (List[Violation]): List of violations detected


  **Returns:** Challenge
    Challenge object with formatted text and options


  #### `log_event`

  ```python
  log_event(self, challenge: Challenge, user_decision: str, override_justification: Optional[str])
  ```

  Log protection event to corpus callosum.

Args:
    challenge: Protection challenge
    user_decision: User's decision (accept/different/override)
    override_justification: Justification if user overrode

  **Parameters:**

  - `self`
  - `challenge` (Challenge): Protection challenge
  - `user_decision` (str): User's decision (accept/different/override)
  - `override_justification` (Optional[str]) = `None`: Justification if user overrode



---
