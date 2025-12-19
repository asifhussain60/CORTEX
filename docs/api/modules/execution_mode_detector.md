# execution_mode_detector

Execution Mode Detector

Detects whether user request is for autonomous, interactive, or continuation execution.

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Version: 1.0.0


## Table of Contents

### Classes
- [ExecutionModeDetector](#executionmodedetector)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** re, typing


## Classes

### ExecutionModeDetector

```python
class ExecutionModeDetector
```

Detects if user request is for autonomous execution.


**Methods:**

  #### `detect`

  ```python
  detect(self, user_message: str) -> ExecutionMode
  ```

  Detects execution mode from user message.

Args:
    user_message: The user's request text

Returns:
    ExecutionMode: 'autonomous', 'interactive', or 'continuation'

  **Parameters:**

  - `self`
  - `user_message` (str): The user's request text


  **Returns:** ExecutionMode
    ExecutionMode: 'autonomous', 'interactive', or 'continuation'


  #### `is_autonomous_mode`

  ```python
  is_autonomous_mode(self, user_message: str) -> bool
  ```

  Convenience method to check if mode is autonomous.

Args:
    user_message: The user's request text

Returns:
    bool: True if autonomous mode detected

  **Parameters:**

  - `self`
  - `user_message` (str): The user's request text


  **Returns:** bool
    bool: True if autonomous mode detected


  #### `is_continuation_mode`

  ```python
  is_continuation_mode(self, user_message: str) -> bool
  ```

  Convenience method to check if mode is continuation.

Args:
    user_message: The user's request text

Returns:
    bool: True if continuation mode detected

  **Parameters:**

  - `self`
  - `user_message` (str): The user's request text


  **Returns:** bool
    bool: True if continuation mode detected


  #### `should_auto_progress`

  ```python
  should_auto_progress(self, user_message: str) -> bool
  ```

  Determines if execution should auto-progress without user confirmation.

Args:
    user_message: The user's request text

Returns:
    bool: True if autonomous or continuation mode detected

  **Parameters:**

  - `self`
  - `user_message` (str): The user's request text


  **Returns:** bool
    bool: True if autonomous or continuation mode detected



---
