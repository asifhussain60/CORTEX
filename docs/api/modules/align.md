# align

CORTEX Align v2.0 Command - Entry Point Wrapper

Enhanced system alignment with intelligent maintenance capabilities:
- Feature registration validation
- Auto-discovery and registration
- Intent router coverage check
- Response template validation
- Documentation alignment
- Obsolete code detection
- Module import health check
- CORTEX.prompt.md optimization validation

Usage:
    # From command line
    python3 -m src.operations.align                          # Full system alignment v2.0
    python3 -m src.operations.align --auto-fix               # Auto-fix issues
    python3 -m src.operations.align --dry-run                # Preview changes
    python3 -m src.operations.align governance-tokens        # Token budget validation
    
    # From Python code
    from src.operations.align import run_align
    result = run_align()

Subcommands:
    (none)              - Run CORTEX Align v2.0 holistic system check (default)
    governance-tokens   - Validate governance file token budgets

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 3.0
Status: PRODUCTION (Enhanced - CORTEX v3.9 Compatible)


## Table of Contents


### Functions
- [run_align](#run_align)
- [run_governance_tokens](#run_governance_tokens)
- [main](#main)


## Overview

- **Classes:** 0
- **Functions:** 3
- **Dependencies:** argparse, pathlib, src, sys, typing


## Functions

### run_align

```python
run_align(auto_fix: bool, dry_run: bool, force_full: bool, quick_mode: bool) -> Dict[str, Any]
```

Execute CORTEX Align v3.2 - Holistic system alignment with incremental support.

This is the MOST CRUCIAL validation step. When user says '/CORTEX align',
this function runs comprehensive checks to ensure CORTEX is fully operational.

Features (v3.2):
- Incremental validation (only check changed features)
- File change detection via SHA256 checksums
- Auto-discovery and wiring validation for new features
- Admin vs User context detection
- Performance metrics tracking
- Feature registration validation (all operations in cortex-operations.yaml)
- Intent router coverage check (all operations have triggers)
- Response template validation (all operations have templates)
- Documentation alignment (docs match implementation)
- Obsolete code detection and cleanup
- Module import health check
- CORTEX.prompt.md optimization validation

Args:
    auto_fix: Automatically fix issues without prompting (default: False)
    dry_run: Preview changes without applying (default: False)
    force_full: Force full scan even if incremental is possible (default: False)
    quick_mode: Infrastructure checks only, skip feature validation (default: False)

Returns:
    Dict with:
        - success (bool): True if system is healthy
        - checks (dict): Results from all checks
        - fixes_applied (list): List of fixes applied
        - warnings (list): Warnings found
        - errors (list): Errors found
        - report_path (str): Path to detailed report
        - performance (dict): Performance metrics


**Parameters:**

- `auto_fix` (bool) = `False`: Automatically fix issues without prompting (default: False)
- `dry_run` (bool) = `False`: Preview changes without applying (default: False)
- `force_full` (bool) = `False`: Force full scan even if incremental is possible (default: False)
- `quick_mode` (bool) = `False`: Infrastructure checks only, skip feature validation (default: False)


**Returns:** Dict[str, Any]
  Dict with: - success (bool): True if system is healthy - checks (dict): Results from all checks - fixes_applied (list): List of fixes applied - warnings (list): Warnings found - errors (list): Errors found - report_path (str): Path to detailed report - performance (dict): Performance metrics


---

### run_governance_tokens

```python
run_governance_tokens(command: str) -> Dict[str, Any]
```

Execute governance token budget validation.

Validates that CORTEX governance files stay within token budgets
to prevent GitHub Copilot premature summarization.

Args:
    command: Subcommand ('validate', 'report', 'analyze', 'optimize')

Returns:
    Dict with:
        - success (bool): True if all files within budget
        - message (str): Summary message
        - report_text (str): Full console output
        - report_data (dict): Structured validation data


**Parameters:**

- `command` (str) = `'validate'`: Subcommand ('validate', 'report', 'analyze', 'optimize')


**Returns:** Dict[str, Any]
  Dict with: - success (bool): True if all files within budget - message (str): Summary message - report_text (str): Full console output - report_data (dict): Structured validation data


---

### main

```python
main()
```

CLI entry point for direct execution.


---
