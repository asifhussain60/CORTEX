# lesson_capture

Interactive Lesson Capture System (Phase 3)
Guides users through structured prompts to capture high-quality lessons from git commits.

Author: Asif Hussain
License: Source-Available


## Table of Contents

### Classes
- [ValidationError](#validationerror)
- [CapturedLesson](#capturedlesson)
- [LessonCapture](#lessoncapture)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** dataclasses, logging, pathlib, re, src, typing, yaml


## Classes

### ValidationError

```python
class ValidationError(Exception)
```

Raised when lesson validation fails.



---

### CapturedLesson

```python
class CapturedLesson
```

**Decorators:** `dataclass`

Structured lesson captured from user input.


**Attributes:**

- `problem`: str
- `root_cause`: str
- `solution`: str
- `prevention_rules`: List[str]
- `time_cost`: str
- `commit_hash`: str
- `confidence`: float


**Methods:**


---

### LessonCapture

```python
class LessonCapture
```

Interactive system for capturing structured lessons from git commits.


**Methods:**

  #### `capture_lesson`

  ```python
  capture_lesson(self, candidate: Candidate) -> Optional[CapturedLesson]
  ```

  Interactively capture a lesson from a commit candidate.

Args:
    candidate: Commit candidate to capture lesson from
    
Returns:
    CapturedLesson if successful, None if skipped

  **Parameters:**

  - `self`
  - `candidate` (Candidate): Commit candidate to capture lesson from


  **Returns:** Optional[CapturedLesson]
    CapturedLesson if successful, None if skipped



---
