# Update Documentation Operation

**Auto-generated:** 2025-11-15 03:35:42

---

## Overview

CORTEX Documentation Generator - Monolithic Script

Single-script implementation for documentation update operation.
Auto-generates docs from code/YAML, validates links, updates MkDocs structure.

Design Philosophy (CORTEX 3.0):
- Monolithic-then-modular: Ship working MVP first
- User value over perfect architecture
- Refactor only when complexity warrants (>500 lines)

Features:
- API reference extraction from docstrings
- Operation documentation auto-generation
- Link validation system
- MkDocs navigation updates
- YAML-based configuration

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0 (CORTEX 3.0 Phase 1.1 Week 2)

## Usage

```python
from src.operations.update_documentation import DocGenerationResult

operation = DocGenerationResult()
result = operation.execute()
```

## Methods

### `to_dict(self)`

Convert to dictionary.
