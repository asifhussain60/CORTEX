# tdd_cycle_logger

TDD Cycle Logger - Capture patterns from TDD workflow cycles

Logs patterns from:
- RED phase: Test-first development (failing tests)
- GREEN phase: Minimal implementation (passing tests)
- REFACTOR phase: Code cleanup (tests still passing)

Integrates with Phase 3 TDD workflow for automatic pattern learning.

Author: Asif Hussain


## Table of Contents

### Classes
- [TDDCycleLogger](#tddcyclelogger)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, hashlib, json, pathlib, typing


## Classes

### TDDCycleLogger

```python
class TDDCycleLogger
```

Log and link TDD cycle patterns for learning


**Methods:**

  #### `log_red_phase`

  ```python
  log_red_phase(self, test_file: str, test_name: str, test_content: str, intent: str) -> str
  ```

  Log RED phase pattern (test-first)

Args:
    test_file: Path to test file
    test_name: Name of test function/method
    test_content: Test code content
    intent: Purpose of the test
    
Returns:
    Pattern ID

  **Parameters:**

  - `self`
  - `test_file` (str): Path to test file
  - `test_name` (str): Name of test function/method
  - `test_content` (str): Test code content
  - `intent` (str): Purpose of the test


  **Returns:** str
    Pattern ID


  #### `log_green_phase`

  ```python
  log_green_phase(self, impl_file: str, impl_content: str, test_file: str, test_passed: bool) -> str
  ```

  Log GREEN phase pattern (implementation)

Args:
    impl_file: Path to implementation file
    impl_content: Implementation code
    test_file: Related test file
    test_passed: Whether test passed after implementation
    
Returns:
    Pattern ID

  **Parameters:**

  - `self`
  - `impl_file` (str): Path to implementation file
  - `impl_content` (str): Implementation code
  - `test_file` (str): Related test file
  - `test_passed` (bool): Whether test passed after implementation


  **Returns:** str
    Pattern ID


  #### `log_refactor_phase`

  ```python
  log_refactor_phase(self, file_path: str, before_code: str, after_code: str, refactor_type: str, tests_still_passing: bool) -> str
  ```

  Log REFACTOR phase pattern (code cleanup)

Args:
    file_path: Path to refactored file
    before_code: Code before refactoring
    after_code: Code after refactoring
    refactor_type: Type of refactoring (extract_method, rename, etc.)
    tests_still_passing: Whether tests still pass after refactor
    
Returns:
    Pattern ID

  **Parameters:**

  - `self`
  - `file_path` (str): Path to refactored file
  - `before_code` (str): Code before refactoring
  - `after_code` (str): Code after refactoring
  - `refactor_type` (str): Type of refactoring (extract_method, rename, etc.)
  - `tests_still_passing` (bool): Whether tests still pass after refactor


  **Returns:** str
    Pattern ID


  #### `link_cycle`

  ```python
  link_cycle(self, red_pattern_id: str, green_pattern_id: str, refactor_pattern_id: Optional[str], refactor_id: Optional[str]) -> str
  ```

  Link RED→GREEN→REFACTOR patterns into complete TDD cycle

Args:
    red_pattern_id: RED phase pattern ID
    green_pattern_id: GREEN phase pattern ID
    refactor_pattern_id: Optional REFACTOR phase pattern ID
    refactor_id: Alias for refactor_pattern_id (backward compatibility)
    
Returns:
    Cycle pattern ID

  **Parameters:**

  - `self`
  - `red_pattern_id` (str): RED phase pattern ID
  - `green_pattern_id` (str): GREEN phase pattern ID
  - `refactor_pattern_id` (Optional[str]) = `None`: Optional REFACTOR phase pattern ID
  - `refactor_id` (Optional[str]) = `None`: Alias for refactor_pattern_id (backward compatibility)


  **Returns:** str
    Cycle pattern ID



---
