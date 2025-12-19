# legacy_kds_cleaner

Legacy Cleanup Handlers for CORTEX

Handles cleanup of legacy KDS (Key Data Streams) files and directories
from pre-CORTEX 2.0 era.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms


## Table of Contents

### Classes
- [LegacyKDSCleaner](#legacykdscleaner)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** logging, pathlib, shutil, typing


## Classes

### LegacyKDSCleaner

```python
class LegacyKDSCleaner
```

Cleans up legacy KDS prompt files and directories.

Removes old Key Data Streams (KDS) prompts and folders that are no longer
needed after CORTEX 2.0 deployment. Only keeps CORTEX.prompt.md and
copilot-instructions.md in .github/prompts/.


**Methods:**

  #### `cleanup`

  ```python
  cleanup(self, dry_run: bool) -> int
  ```

  Clean up legacy KDS files and directories.

Legacy files removed:
- Old prompt files: ask.prompt.md, continue.prompt.md, task.prompt.md, etc.
- Old subdirectories: comm/, knowledge/, ops/, quality/, shared/, util/
- Old root directories: _Portable, instructions, key-data-streams, learning, prompts.keys

Args:
    dry_run: If True, only simulate cleanup without actual deletions

Returns:
    int: Number of legacy files/directories removed

  **Parameters:**

  - `self`
  - `dry_run` (bool): If True, only simulate cleanup without actual deletions


  **Returns:** int
    int: Number of legacy files/directories removed



---
