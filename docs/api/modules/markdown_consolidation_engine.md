# markdown_consolidation_engine

Markdown Consolidation Engine - Intelligent consolidation of markdown files

This module provides fast, intelligent consolidation of markdown files with:
- Hash-based duplicate detection (SHA256)
- Time-series consolidation (multi-phase reports → single file)
- Topic clustering (related content → single file)
- Archive management (30-day retention)
- Cross-reference updates (maintain link integrity)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Version: 3.2.1


## Table of Contents

### Classes
- [MarkdownFile](#markdownfile)
- [ConsolidationRule](#consolidationrule)
- [ConsolidationReport](#consolidationreport)
- [MarkdownConsolidationEngine](#markdownconsolidationengine)


## Overview

- **Classes:** 4
- **Functions:** 0
- **Dependencies:** collections, dataclasses, datetime, hashlib, logging, pathlib, re, shutil, typing


## Classes

### MarkdownFile

```python
class MarkdownFile
```

**Decorators:** `dataclass`

Metadata about a markdown file


**Attributes:**

- `path`: Path
- `title`: str
- `size`: int
- `modified`: datetime
- `content_hash`: str
- `category`: str
- `keywords`: Set[str]
- `date_in_name`: Optional[datetime]


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict
  ```

  Convert to dictionary

  **Parameters:**

  - `self`


  **Returns:** Dict



---

### ConsolidationRule

```python
class ConsolidationRule
```

**Decorators:** `dataclass`

Rule for consolidating files


**Attributes:**

- `name`: str
- `pattern`: str
- `action`: str
- `target_filename`: Optional[str]
- `file_paths`: List[Path]
- `estimated_reduction`: int


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict
  ```

  Convert to dictionary

  **Parameters:**

  - `self`


  **Returns:** Dict



---

### ConsolidationReport

```python
class ConsolidationReport
```

**Decorators:** `dataclass`

Report of consolidation results


**Attributes:**

- `generated_at`: datetime
- `rules_applied`: List[ConsolidationRule]
- `files_before`: int
- `files_after`: int
- `size_before_mb`: float
- `size_after_mb`: float
- `execution_time`: float
- `archived_files`: List[Path]
- `errors`: List[str]


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict
  ```

  Convert to dictionary

  **Parameters:**

  - `self`


  **Returns:** Dict



---

### MarkdownConsolidationEngine

```python
class MarkdownConsolidationEngine
```

Fast, intelligent markdown file consolidation engine.

Capabilities:
- Discovery: Scan and extract metadata (<10 seconds for 664 files)
- Deduplication: Hash-based duplicate detection (SHA256)
- Time-series: Consolidate multi-phase reports (70% reduction)
- Topic clustering: Merge related content (50% reduction)
- Archive management: 30-day retention before deletion

Performance:
- Discovery: <10s (664 files)
- Analysis: <15s (hash comparison, clustering)
- Consolidation: <60s (file I/O)
- Total: <2 minutes for full operation

Expected Results:
- Reports: 302 → ~50 files (83% reduction)
- Analysis: 80 → ~30 files (62% reduction)
- Overall: 664 → ~250 files (62% reduction)


**Methods:**

  #### `discover_files`

  ```python
  discover_files(self) -> Dict[str, MarkdownFile]
  ```

  Discover and extract metadata from markdown files.

Returns:
    Dictionary of file path → MarkdownFile metadata
    
Performance: <10 seconds for 664 files

  **Parameters:**

  - `self`


  **Returns:** Dict[str, MarkdownFile]
    Dictionary of file path → MarkdownFile metadata Performance: <10 seconds for 664 files


  #### `analyze_consolidation_opportunities`

  ```python
  analyze_consolidation_opportunities(self) -> List[ConsolidationRule]
  ```

  Analyze files and generate consolidation recommendations.

Returns:
    List of consolidation rules to apply
    
Performance: <15 seconds (hash comparison, clustering)

  **Parameters:**

  - `self`


  **Returns:** List[ConsolidationRule]
    List of consolidation rules to apply Performance: <15 seconds (hash comparison, clustering)


  #### `execute_consolidation`

  ```python
  execute_consolidation(self, rules: Optional[List[ConsolidationRule]], dry_run: bool) -> ConsolidationReport
  ```

  Execute consolidation rules.

Args:
    rules: Rules to apply (uses self.consolidation_rules if None)
    dry_run: If True, only preview changes without executing
    
Returns:
    ConsolidationReport with results
    
Performance: <60 seconds for 664 files

  **Parameters:**

  - `self`
  - `rules` (Optional[List[ConsolidationRule]]) = `None`: Rules to apply (uses self.consolidation_rules if None)
  - `dry_run` (bool) = `True`: If True, only preview changes without executing


  **Returns:** ConsolidationReport
    ConsolidationReport with results Performance: <60 seconds for 664 files


  #### `cleanup_old_archives`

  ```python
  cleanup_old_archives(self) -> int
  ```

  Remove archived files older than retention period.

Returns:
    Number of files deleted

  **Parameters:**

  - `self`


  **Returns:** int
    Number of files deleted



---
