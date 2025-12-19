# cleanup_verifier

Cleanup Verifier - Post-execution verification

Verifies CORTEX functionality after cleanup execution.
Triggers automatic rollback if issues detected.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [VerificationResult](#verificationresult)
- [CleanupVerifier](#cleanupverifier)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** dataclasses, importlib, logging, pathlib, re, src, subprocess, typing


## Classes

### VerificationResult

```python
class VerificationResult
```

**Decorators:** `dataclass`

Result of post-cleanup verification


**Attributes:**

- `passed`: bool
- `message`: str
- `checks`: Dict[str, Any]
- `rollback_triggered`: bool



---

### CleanupVerifier

```python
class CleanupVerifier
```

Verify CORTEX functionality after cleanup


**Methods:**

  #### `verify_cleanup`

  ```python
  verify_cleanup(self, use_health_validator: bool) -> VerificationResult
  ```

  Run comprehensive post-cleanup verification.

Args:
    use_health_validator: Use HealthValidator for quick health check

Returns:
    VerificationResult with pass/fail and details

  **Parameters:**

  - `self`
  - `use_health_validator` (bool) = `True`: Use HealthValidator for quick health check


  **Returns:** VerificationResult
    VerificationResult with pass/fail and details



---
