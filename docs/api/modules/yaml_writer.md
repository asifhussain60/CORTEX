# yaml_writer

YAML Writer & Validator (Phase 5)
Safely appends lessons to lessons-learned.yaml with validation and rollback.

Features:
- Schema validation for lesson structure
- Atomic writes with backup/rollback
- Auto-generated lesson IDs (git-learning-NNN)
- YAML formatting preservation
- File integrity verification

7-Step Safety Protocol:
1. Create backup
2. Validate schema
3. Generate unique ID
4. Atomic write
5. Verify integrity
6. Cleanup backup
7. Log operation

Author: Asif Hussain
License: Source-Available


## Table of Contents

### Classes
- [SchemaValidationError](#schemavalidationerror)
- [YAMLWriter](#yamlwriter)

### Functions
- [generate_lesson_id](#generate_lesson_id)


## Overview

- **Classes:** 2
- **Functions:** 1
- **Dependencies:** contextlib, datetime, logging, pathlib, shutil, src, typing, yaml


## Classes

### SchemaValidationError

```python
class SchemaValidationError(Exception)
```

Raised when lesson schema validation fails.



---

### YAMLWriter

```python
class YAMLWriter
```

Safe YAML writer for lessons-learned.yaml.

Provides atomic writes with backup/rollback, schema validation,
and automatic ID generation.


**Methods:**

  #### `append_lesson`

  ```python
  append_lesson(self, lesson: CapturedLesson) -> str
  ```

  Append captured lesson to YAML file.

Follows 7-step safety protocol with backup/rollback.

Args:
    lesson: CapturedLesson to append
    
Returns:
    Generated lesson ID
    
Raises:
    SchemaValidationError: If lesson fails validation
    IOError: If file operations fail

  **Parameters:**

  - `self`
  - `lesson` (CapturedLesson): CapturedLesson to append


  **Returns:** str
    Generated lesson ID



---

## Functions

### generate_lesson_id

```python
generate_lesson_id(existing_ids: List[str]) -> str
```

Generate next sequential lesson ID.

Format: 'git-learning-NNN' where NNN is zero-padded 3-digit number.

Args:
    existing_ids: List of existing lesson IDs
    
Returns:
    Next available lesson ID


**Parameters:**

- `existing_ids` (List[str]): List of existing lesson IDs


**Returns:** str
  Next available lesson ID


---
