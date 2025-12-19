# doc_deduplicator

Documentation Deduplicator

Handles documentation deduplication using DocumentGovernance.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0


## Table of Contents

### Classes
- [DocumentDeduplicator](#documentdeduplicator)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** logging, pathlib, src, typing


## Classes

### DocumentDeduplicator

```python
class DocumentDeduplicator
```

Deduplicates documentation using DocumentGovernance.

This class:
1. Instantiates DocumentGovernance
2. Scans all markdown files in cortex-brain/documents/
3. Finds duplicates using 3 algorithms (exact, title, keyword)
4. Applies consolidation suggestions (keeps older, archives newer)
5. Logs consolidation actions
6. Updates metrics with deduplicated count


**Methods:**

  #### `deduplicate`

  ```python
  deduplicate(self, metrics: OptimizationMetrics) -> Dict[str, Any]
  ```

  Scan and deduplicate documentation.

Args:
    metrics: Metrics collector

Returns:
    Dict with success status, consolidated count, and details

  **Parameters:**

  - `self`
  - `metrics` (OptimizationMetrics): Metrics collector


  **Returns:** Dict[str, Any]
    Dict with success status, consolidated count, and details



---
