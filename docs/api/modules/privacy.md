# privacy

Privacy Sanitization Engine

Removes sensitive data from feedback reports based on privacy level.

Privacy Levels:
- full: Remove all potentially sensitive data (paths, usernames, etc.)
- medium: Remove obvious sensitive data (passwords, keys, emails)
- minimal: Remove only critical secrets (passwords, API keys)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [PrivacySanitizer](#privacysanitizer)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** hashlib, logging, pathlib, re, typing


## Classes

### PrivacySanitizer

```python
class PrivacySanitizer
```

Sanitize feedback reports for privacy protection.


**Methods:**

  #### `sanitize`

  ```python
  sanitize(self, data: Dict[str, Any]) -> Dict[str, Any]
  ```

  Sanitize feedback report based on privacy level.

Args:
    data: Feedback report dictionary

Returns:
    Sanitized feedback report

  **Parameters:**

  - `self`
  - `data` (Dict[str, Any]): Feedback report dictionary


  **Returns:** Dict[str, Any]
    Sanitized feedback report


  #### `redact_file_paths`

  ```python
  redact_file_paths(self, text: str) -> str
  ```

  Redact file paths from text.

  **Parameters:**

  - `self`
  - `text` (str)


  **Returns:** str


  #### `anonymize_user_identifier`

  ```python
  anonymize_user_identifier(self, user_id: str) -> str
  ```

  Convert user identifier to non-reversible hash.

  **Parameters:**

  - `self`
  - `user_id` (str)


  **Returns:** str



---
