# language_detector

Language Detector - Programming Language Detection

Detects programming language from file extensions and content.

Author: Asif Hussain
Version: 1.0.0


## Table of Contents

### Classes
- [LanguageDetector](#languagedetector)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** logging, pathlib, typing


## Classes

### LanguageDetector

```python
class LanguageDetector
```

Detects programming language from file characteristics.

Uses extension-based detection with fallback to content analysis.


**Attributes:**

- `EXTENSION_MAP`: Dict[str, str]


**Methods:**

  #### `detect`

  ```python
  detect(self, file_path: Path) -> str
  ```

  Detect language from file path.

Args:
    file_path: Path to file

Returns:
    Language identifier (lowercase)

  **Parameters:**

  - `self`
  - `file_path` (Path): Path to file


  **Returns:** str
    Language identifier (lowercase)



---
