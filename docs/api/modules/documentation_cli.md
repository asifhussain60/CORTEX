# documentation_cli

CORTEX 3.0 - EPM Documentation CLI (Feature 4 - Phase 4.4)
==========================================================

Command-line interface for EPM documentation generation
with configuration support and batch processing.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Feature: Feature 4 - Phase 4.4 (Week 3)
Effort: 8 hours (CLI interface)
Dependencies: Phases 4.1, 4.2, 4.3 - ALL COMPLETED


## Table of Contents

### Classes
- [EPMDocumentationCLI](#epmdocumentationcli)

### Functions
- [main](#main)


## Overview

- **Classes:** 1
- **Functions:** 1
- **Dependencies:** argparse, datetime, documentation_generator, json, os, pathlib, sys, template_engine, traceback, typing, yaml


## Classes

### EPMDocumentationCLI

```python
class EPMDocumentationCLI
```

Command-line interface for EPM documentation generation.

Features:
- Project analysis and documentation generation
- Multiple output formats and templates
- Batch processing of multiple projects
- Configuration file support
- Progress reporting and logging


**Methods:**

  #### `run`

  ```python
  run(self, args: Optional[List[str]]) -> int
  ```

  Run the CLI with provided arguments.

Args:
    args: Command line arguments (defaults to sys.argv)
    
Returns:
    Exit code (0 for success, non-zero for error)

  **Parameters:**

  - `self`
  - `args` (Optional[List[str]]) = `None`: Command line arguments (defaults to sys.argv)


  **Returns:** int
    Exit code (0 for success, non-zero for error)



---

## Functions

### main

```python
main()
```

Main entry point for CLI


---
