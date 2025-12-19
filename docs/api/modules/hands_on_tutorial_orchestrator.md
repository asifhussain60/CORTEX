# hands_on_tutorial_orchestrator

CORTEX Hands-On Tutorial Orchestrator

Interactive tutorial program that teaches users about CORTEX through
practical exercises covering planning, development, and testing.

Author: GitHub Copilot
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)


## Table of Contents

### Classes
- [TutorialProfile](#tutorialprofile)
- [ModuleStatus](#modulestatus)
- [TutorialModule](#tutorialmodule)
- [TutorialProgress](#tutorialprogress)
- [HandsOnTutorialOrchestrator](#handsontutorialorchestrator)

### Functions
- [main](#main)


## Overview

- **Classes:** 5
- **Functions:** 1
- **Dependencies:** argparse, dataclasses, datetime, enum, json, pathlib, typing


## Classes

### TutorialProfile

```python
class TutorialProfile(Enum)
```

Tutorial difficulty profiles.



---

### ModuleStatus

```python
class ModuleStatus(Enum)
```

Module completion status.



---

### TutorialModule

```python
class TutorialModule
```

**Decorators:** `dataclass`

Tutorial module definition.


**Attributes:**

- `id`: str
- `name`: str
- `duration_min`: int
- `exercises`: List[str]
- `prerequisites`: List[str]
- `status`: ModuleStatus



---

### TutorialProgress

```python
class TutorialProgress
```

**Decorators:** `dataclass`

User progress tracking.


**Attributes:**

- `session_id`: str
- `profile`: TutorialProfile
- `started_at`: datetime
- `completed_modules`: List[str]
- `current_module`: Optional[str]
- `total_time_min`: int



---

### HandsOnTutorialOrchestrator

```python
class HandsOnTutorialOrchestrator
```

Orchestrates interactive hands-on tutorial for CORTEX.

Guides users through:
1. CORTEX basics (help, context, healthcheck)
2. Planning workflow (DoR, DoD, security review)
3. TDD development (RED→GREEN→REFACTOR)
4. Testing & validation (lint, session reports)


**Methods:**

  #### `start_tutorial`

  ```python
  start_tutorial(self, profile: TutorialProfile) -> Dict[str, Any]
  ```

  Start hands-on tutorial with selected profile.

Args:
    profile: Tutorial difficulty level
    
Returns:
    Tutorial session info with first module instructions

  **Parameters:**

  - `self`
  - `profile` (TutorialProfile) = `TutorialProfile.STANDARD`: Tutorial difficulty level


  **Returns:** Dict[str, Any]
    Tutorial session info with first module instructions


  #### `next_exercise`

  ```python
  next_exercise(self, session_id: str) -> Dict[str, Any]
  ```

  Move to next exercise in tutorial.

  **Parameters:**

  - `self`
  - `session_id` (str)


  **Returns:** Dict[str, Any]


  #### `get_progress`

  ```python
  get_progress(self, session_id: str) -> Dict[str, Any]
  ```

  Get current tutorial progress.

  **Parameters:**

  - `self`
  - `session_id` (str)


  **Returns:** Dict[str, Any]



---

## Functions

### main

```python
main()
```

CLI entry point for tutorial orchestrator.


---
