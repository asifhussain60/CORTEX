# optimize_tokens

CORTEX Token Optimization CLI

On-demand bulk token optimization for governance files to prevent
GitHub Copilot premature conversation summarization.

Commands:
    optimize tokens quick          - Quick wins only (~1 hour, 35% reduction)
    optimize tokens full           - Complete optimization (~3-4 hours, 75% reduction)
    optimize tokens auto           - Intelligent optimization (auto-detects best strategy)
    optimize tokens validate       - Check current token usage vs budgets
    optimize tokens rollback       - Undo last optimization
    optimize tokens status         - Show optimization history

Features:
    - Automatic backups before optimization
    - YAML syntax validation after changes
    - Progress reporting with ETA
    - Rollback capability
    - Dry-run mode for safety
    - Detailed before/after reports

Usage:
    # Quick optimization (high-impact only)
    python3 -m src.operations.optimize_tokens quick
    
    # Full optimization to reach 17K token target
    python3 -m src.operations.optimize_tokens full
    
    # Let CORTEX decide best approach
    python3 -m src.operations.optimize_tokens auto
    
    # Check current status
    python3 -m src.operations.optimize_tokens status

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0.0
Status: PRODUCTION
Created: 2025-12-01


## Table of Contents

### Classes
- [OptimizationResult](#optimizationresult)
- [TokenOptimizer](#tokenoptimizer)

### Functions
- [safe_print](#safe_print)
- [main](#main)


## Overview

- **Classes:** 2
- **Functions:** 2
- **Dependencies:** dataclasses, datetime, json, os, pathlib, shutil, src, subprocess, sys, time, typing, yaml


## Classes

### OptimizationResult

```python
class OptimizationResult
```

**Decorators:** `dataclass`

Result of a token optimization operation.


**Attributes:**

- `timestamp`: datetime
- `strategy`: str
- `success`: bool
- `before_tokens`: int
- `after_tokens`: int
- `tokens_saved`: int
- `reduction_percent`: float
- `files_modified`: List[str]
- `files_created`: List[str]
- `execution_time`: float
- `error_message`: Optional[str]
- `backup_path`: Optional[str]



---

### TokenOptimizer

```python
class TokenOptimizer
```

Bulk token optimization engine for CORTEX governance files.


**Methods:**

  #### `create_backup`

  ```python
  create_backup(self, label: str) -> Path
  ```

  Create backup of all governance files.

Args:
    label: Descriptive label for this backup
    
Returns:
    Path to backup directory

  **Parameters:**

  - `self`
  - `label` (str): Descriptive label for this backup


  **Returns:** Path
    Path to backup directory


  #### `restore_backup`

  ```python
  restore_backup(self, backup_path: Path) -> bool
  ```

  Restore files from backup.

Args:
    backup_path: Path to backup directory
    
Returns:
    True if successful

  **Parameters:**

  - `self`
  - `backup_path` (Path): Path to backup directory


  **Returns:** bool
    True if successful


  #### `validate_yaml_syntax`

  ```python
  validate_yaml_syntax(self, yaml_path: Path) -> Tuple[bool, Optional[str]]
  ```

  Validate YAML file syntax.

Args:
    yaml_path: Path to YAML file
    
Returns:
    Tuple of (is_valid, error_message)

  **Parameters:**

  - `self`
  - `yaml_path` (Path): Path to YAML file


  **Returns:** Tuple[bool, Optional[str]]
    Tuple of (is_valid, error_message)


  #### `get_current_tokens`

  ```python
  get_current_tokens(self) -> Dict[str, int]
  ```

  Get current token usage for all governance files.

Returns:
    Dictionary mapping file names to token counts

  **Parameters:**

  - `self`


  **Returns:** Dict[str, int]
    Dictionary mapping file names to token counts


  #### `optimize_quick`

  ```python
  optimize_quick(self) -> OptimizationResult
  ```

  Quick optimization - high-impact changes only.

Strategy:
    1. Extract 10 largest remaining templates from brain-protection-rules.yaml
    2. Implement YAML anchors in response-templates.yaml
    3. Move 3 largest sections from CORTEX.prompt.md to guides

Expected: ~35% total reduction, ~1 hour execution

  **Parameters:**

  - `self`


  **Returns:** OptimizationResult


  #### `optimize_full`

  ```python
  optimize_full(self) -> OptimizationResult
  ```

  Full optimization - reach 17K token target.

Strategy:
    1. Extract ALL remaining templates from brain-protection-rules.yaml
    2. Implement comprehensive YAML anchors
    3. Template inheritance for response-templates.yaml
    4. Module-based architecture for CORTEX.prompt.md

Expected: ~75% total reduction, ~3-4 hours execution

  **Parameters:**

  - `self`


  **Returns:** OptimizationResult


  #### `optimize_auto`

  ```python
  optimize_auto(self) -> OptimizationResult
  ```

  Intelligent optimization - auto-detect best strategy.

Logic:
    - If >50% over budget: Run full optimization
    - If 20-50% over budget: Run quick optimization
    - If <20% over budget: Skip, recommend monitoring

  **Parameters:**

  - `self`


  **Returns:** OptimizationResult


  #### `show_status`

  ```python
  show_status(self) -> None
  ```

  Show current token usage and optimization history.

  **Parameters:**

  - `self`


  **Returns:** None


  #### `rollback_last`

  ```python
  rollback_last(self) -> bool
  ```

  Rollback the most recent optimization.

  **Parameters:**

  - `self`


  **Returns:** bool



---

## Functions

### safe_print

```python
safe_print(message: str) -> None
```

Print with Unicode fallback for Windows console encoding issues.


**Parameters:**

- `message` (str)


**Returns:** None


---

### main

```python
main()
```

CLI entry point.


---
