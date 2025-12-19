# deduplication_analyzer

Deduplication Analyzer - AST-powered semantic duplicate detection.

Identifies functionally similar code blocks that could be refactored
into shared utilities or modules.

Copyright © 2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [DuplicateGroup](#duplicategroup)
- [DeduplicationAnalyzer](#deduplicationanalyzer)


## Overview

- **Classes:** 2
- **Functions:** 0
- **Dependencies:** dataclasses, logging, pathlib, typing


## Classes

### DuplicateGroup

```python
class DuplicateGroup
```

**Decorators:** `dataclass`

Group of semantically similar code blocks.


**Attributes:**

- `similarity_score`: float
- `locations`: List[Dict[str, Any]]
- `lines_count`: int
- `recommendation`: str



---

### DeduplicationAnalyzer

```python
class DeduplicationAnalyzer
```

Detect semantic code duplicates using AST analysis.


**Methods:**

  #### `analyze`

  ```python
  analyze(self, target_path: Path) -> Dict[str, Any]
  ```

  Analyze codebase for semantic duplicates.

Args:
    target_path: Specific directory/file or None for full project
    
Returns:
    Analysis results with duplicate groups and recommendations

  **Parameters:**

  - `self`
  - `target_path` (Path) = `None`: Specific directory/file or None for full project


  **Returns:** Dict[str, Any]
    Analysis results with duplicate groups and recommendations



---
