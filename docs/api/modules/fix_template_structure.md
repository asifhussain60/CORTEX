# fix_template_structure

Template Cleanup Script - Move Root-Level Templates into templates: Section

This script fixes the response-templates.yaml structure by moving all incorrectly
placed root-level templates into the proper templates: section.

Author: Asif Hussain
Date: December 4, 2025


## Table of Contents


### Functions
- [fix_template_structure](#fix_template_structure)


## Overview

- **Classes:** 0
- **Functions:** 1
- **Dependencies:** pathlib, shutil, yaml


## Functions

### fix_template_structure

```python
fix_template_structure(templates_file: Path) -> dict
```

Fix template structure by moving root-level templates into templates: section.

Args:
    templates_file: Path to response-templates.yaml

Returns:
    Dict with fix statistics


**Parameters:**

- `templates_file` (Path): Path to response-templates.yaml


**Returns:** dict
  Dict with fix statistics


---
