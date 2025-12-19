# commit

<<<<<<< Updated upstream
Commit Entry Point

Simple CLI wrapper for fast CommitUtility.
Follows standard CORTEX operations pattern.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary


## Table of Contents


### Functions
- [run_commit](#run_commit)
- [main](#main)
- [run_commit](#run_commit)
- [main](#main)


## Overview

- **Classes:** 0
- **Functions:** 4
- **Dependencies:** argparse, operations, pathlib, src, sys


## Functions

### run_commit

```python
run_commit(**kwargs)
```

Run commit operation using fast utility.

Returns:
    Dict with success, message, and commit results


**Parameters:**

- `**kwargs`


---

### main

```python
main()
```

CLI entry point.


---

### run_commit

```python
run_commit(project_root: Path, auto_add_untracked: bool, rebase: bool, commit_message: str) -> Dict[str, Any]
```

Execute git commit and sync workflow.

Performs intelligent git synchronization with stash-pull-merge-push pattern:
1. Pre-flight validation (branch check, untracked files)
2. Handle untracked files (interactive or auto-add)
3. Stash local changes (preserves uncommitted work)
4. Pull from origin (merge or rebase)
5. Apply stash (intelligent conflict resolution for split-machine work)
6. Create safety checkpoint (rollback capability)
7. Push to origin (sync complete)

Args:
    project_root: Project root directory (default: current working directory)
    auto_add_untracked: Automatically add untracked files (default: False)
    rebase: Use rebase instead of merge when pulling (default: False)
    commit_message: Commit message for uncommitted changes (optional)

Returns:
    Dict with:
        - success (bool): True if workflow completed successfully
        - message (str): Summary message
        - checkpoint_created (bool): Whether safety checkpoint was created
        - checkpoint_id (str): Checkpoint ID for rollback
        - steps_completed (List[str]): List of completed workflow steps
        - duration_seconds (float): Total workflow duration
        - stash_applied (bool): Whether stash was applied
        - conflicts_resolved (int): Number of conflicts auto-resolved

Examples:
    # Standard sync (interactive untracked file handling)
    result = run_commit()
    
    # Auto-add untracked files
    result = run_commit(auto_add_untracked=True)
    
    # Use rebase instead of merge
    result = run_commit(rebase=True)
    
    # Custom commit message
    result = run_commit(commit_message="feat: Add commit CLI wrapper")


**Parameters:**

- `project_root` (Path) = `None`: Project root directory (default: current working directory)
- `auto_add_untracked` (bool) = `False`: Automatically add untracked files (default: False)
- `rebase` (bool) = `False`: Use rebase instead of merge when pulling (default: False)
- `commit_message` (str) = `None`: Commit message for uncommitted changes (optional)


**Returns:** Dict[str, Any]
  Dict with: - success (bool): True if workflow completed successfully - message (str): Summary message - checkpoint_created (bool): Whether safety checkpoint was created - checkpoint_id (str): Checkpoint ID for rollback - steps_completed (List[str]): List of completed workflow steps - duration_seconds (float): Total workflow duration - stash_applied (bool): Whether stash was applied - conflicts_resolved (int): Number of conflicts auto-resolved


---

### main

```python
main()
```

CLI entry point for direct execution.


---
