# git_history_scanner

Git History Scanner

Scans git history for specified timeframe and extracts commit metadata.
Used by learning library update orchestrator to identify learning-worthy commits.

Features:
- Configurable timeframe (default 24 hours)
- Extracts: sha, message, author, timestamp, files, line counts
- Handles non-git directories gracefully
- Reuses subprocess pattern from GitMetricsCollector

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [CommitMetadata](#commitmetadata)
- [GitHistoryScanner](#githistoryscanner)

### Functions
- [scan_commits](#scan_commits)


## Overview

- **Classes:** 2
- **Functions:** 1
- **Dependencies:** dataclasses, datetime, logging, pathlib, subprocess, typing


## Classes

### CommitMetadata

```python
class CommitMetadata
```

**Decorators:** `dataclass`

Metadata extracted from git commit.

Attributes:
    sha: Commit hash (short or full)
    message: Commit message (first line)
    author: Commit author name
    timestamp: Commit timestamp
    files_changed: List of modified file paths
    lines_added: Total lines added across all files
    lines_deleted: Total lines deleted across all files
    net_change: lines_added - lines_deleted


**Attributes:**

- `sha`: str
- `message`: str
- `author`: str
- `timestamp`: datetime
- `files_changed`: List[str]
- `lines_added`: int
- `lines_deleted`: int
- `net_change`: int



---

### GitHistoryScanner

```python
class GitHistoryScanner
```

Scans git repository history and extracts commit metadata.

Uses subprocess to call git log with --numstat for line counts.
Follows pattern from src/tier3/metrics/git_metrics.py.

Example:
    scanner = GitHistoryScanner(repo_path=Path.cwd())
    commits = scanner.scan_commits(since_hours=24)
    
    for commit in commits:
        print(f"{commit.sha}: {commit.lines_added} lines added")


**Methods:**

  #### `scan_commits`

  ```python
  scan_commits(self, since_hours: int, use_cache: bool) -> List[CommitMetadata]
  ```

  Scan git commits within specified timeframe.

Args:
    since_hours: Number of hours to look back (default: 24)
    use_cache: Whether to use cached results (default: True)
    
Returns:
    List of CommitMetadata objects, newest first

  **Parameters:**

  - `self`
  - `since_hours` (int) = `24`: Number of hours to look back (default: 24)
  - `use_cache` (bool) = `True`: Whether to use cached results (default: True)


  **Returns:** List[CommitMetadata]
    List of CommitMetadata objects, newest first



---

## Functions

### scan_commits

```python
scan_commits(repo_path: Optional[Path], since_hours: int) -> List[CommitMetadata]
```

Convenience function to scan git commits.

Args:
    repo_path: Path to git repository (default: current directory)
    since_hours: Number of hours to look back (default: 24)
    
Returns:
    List of CommitMetadata objects


**Parameters:**

- `repo_path` (Optional[Path]) = `None`: Path to git repository (default: current directory)
- `since_hours` (int) = `24`: Number of hours to look back (default: 24)


**Returns:** List[CommitMetadata]
  List of CommitMetadata objects


---
