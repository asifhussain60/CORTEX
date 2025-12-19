# doc_archive_cleaner

Document Archive Cleaner for CORTEX

Handles cleanup of old archived documentation files.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms


## Table of Contents

### Classes
- [DocumentArchiveCleaner](#documentarchivecleaner)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, logging, pathlib, typing


## Classes

### DocumentArchiveCleaner

```python
class DocumentArchiveCleaner
```

Cleans up old archived documentation files.

Removes archived duplicate documents older than 30 days from:
- cortex-brain/documents/archive/
- docs/archive/consolidated/


**Methods:**

  #### `cleanup`

  ```python
  cleanup(self, dry_run: bool) -> None
  ```

  Clean up old archived documentation files.

Args:
    dry_run: If True, only preview without deleting

  **Parameters:**

  - `self`
  - `dry_run` (bool): If True, only preview without deleting


  **Returns:** None



---
