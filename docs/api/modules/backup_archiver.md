# backup_archiver

Backup Archiver for CORTEX Cleanup

Handles archiving backup files to GitHub before deletion.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms


## Table of Contents

### Classes
- [BackupArchiver](#backuparchiver)


## Overview

- **Classes:** 1
- **Functions:** 0
- **Dependencies:** datetime, json, logging, pathlib, shutil, subprocess, typing


## Classes

### BackupArchiver

```python
class BackupArchiver
```

Archives backup files to GitHub before deletion.

Creates a .backup-archive directory, copies backups, creates manifest,
and commits/pushes to GitHub for safety.


**Methods:**

  #### `archive_to_github`

  ```python
  archive_to_github(self, backup_files: List[Path]) -> Dict[str, Any]
  ```

  Archive backup files to GitHub before deletion.

Args:
    backup_files: List of backup file paths to archive

Returns:
    Dict with success status, commit SHA, and archived file count

  **Parameters:**

  - `self`
  - `backup_files` (List[Path]): List of backup file paths to archive


  **Returns:** Dict[str, Any]
    Dict with success status, commit SHA, and archived file count



---
