# CORTEX Admin Tools

**Purpose:** Administrative utilities for CORTEX maintenance and optimization  
**Audience:** CORTEX administrators only  
**Packaging:** ❌ NOT included in deployments  
**Location:** `scripts/admin/` (isolated from production code)

---

## Overview

This directory contains admin-only tools for analyzing, optimizing, and maintaining the CORTEX codebase. These tools are intended for development and maintenance use only and are **never packaged** for deployment.

---

## Tools

### 🔍 CORTEX Optimizer (`cortex_optimizer.py`)

**Purpose:** Comprehensive CORTEX-specific codebase analysis

**Features:**
- **Token Usage Analysis** - Prompt file efficiency, YAML token usage
- **YAML Validation** - Brain file schema compliance, required fields
- **Plugin Health Checks** - Metadata completeness, registration validation
- **Database Optimization** - SQLite performance, indexes, fragmentation

**Usage:**
```bash
# Run full analysis
python scripts/admin/cortex_optimizer.py analyze

# Generate JSON report
python scripts/admin/cortex_optimizer.py analyze --report json

# Via CORTEX operations (natural language)
# Just say: "optimize codebase" or "check code health"
# CORTEX will automatically run this tool!

# Future commands (coming soon)
python scripts/admin/cortex_optimizer.py refactor --dry-run
python scripts/admin/cortex_optimizer.py profile --module tier1
python scripts/admin/cortex_optimizer.py cleanup --interactive
```

**Output Example:**
```
🔍 CORTEX Codebase Optimization Analysis
============================================================

✅ Token Usage: 87/100
⚠️ YAML Validation: 95/100
✅ Plugin Health: 75/100
✅ Database Optimization: 92/100

🎯 Overall Optimization Score: 87/100
```

**When to Use:**
- Weekly health checks
- Pre-release validation
- After major refactoring
- Quarterly cleanup reviews

**Documentation:** `docs/admin/optimization-guide.md`

---

## Standard Tools Integration

The CORTEX Optimizer complements standard Python tools:

| Tool | Purpose | Command |
|------|---------|---------|
| **radon** | Complexity metrics | `radon cc src/ --min B` |
| **pylint** | Code quality | `pylint src/` |
| **vulture** | Dead code detection | `vulture src/ --min-confidence 80` |
| **black** | Code formatting | `black src/` (via pre-commit) |
| **mypy** | Type checking | `mypy src/` |

**Pre-commit Integration:** `.pre-commit-config.yaml` runs these automatically

---

## Why Separate from Production?

**Admin tools are NOT packaged because:**

1. **No Runtime Value** - Only useful during development/maintenance
2. **Reduce Package Size** - Keep deployments lean (production code only)
3. **Security** - Admin tools may expose internal implementation details
4. **Dependencies** - May require dev-only packages (radon, pylint, vulture)
5. **Clear Separation** - Maintains distinction between runtime vs. admin utilities

**Packaging Exclusion:**
- `setup.py` excludes `scripts/admin/`
- `pyproject.toml` excludes via `packages` configuration
- `.gitignore` does NOT exclude (needed for development)

---

## Adding New Admin Tools

**Guidelines:**

1. **Create in `scripts/admin/`** - Keep all admin tools centralized
2. **Add executable header:**
   ```python
   #!/usr/bin/env python3
   """
   Tool Name - Brief description
   ADMIN TOOL - NOT packaged for deployment
   """
   ```
3. **Update this README** - Document new tool purpose and usage
4. **Add to pre-commit** (optional) - If tool should run on commits
5. **Write docs** - Add comprehensive guide to `docs/admin/`

**Template:**
```python
#!/usr/bin/env python3
"""
CORTEX [Tool Name]
==================
ADMIN TOOL - NOT packaged for deployment

Purpose: Brief description
Usage: python scripts/admin/tool_name.py [args]
"""

import sys
from pathlib import Path

# Add CORTEX root to path
CORTEX_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(CORTEX_ROOT))

def main():
    """Main entry point."""
    pass

if __name__ == "__main__":
    main()
```

---

## Cleanup Pattern

**Admin completion reports** (like `ADMIN-OPTIMIZATION-TOOLKIT-COMPLETE.md`) are:
- ✅ Tracked in `cleanup-detection-patterns.yaml`
- ⏰ Auto-cleanup after 30 days
- 📁 Stored in `cortex-brain/` (temporary informational docs)

**Rationale:** Completion reports are historical snapshots, not operational data. After 30 days, the information is captured in:
- Git commit history
- CORTEX knowledge graph (if learned)
- Production documentation (`docs/admin/`)

---

## Quick Reference

```bash
# Weekly health check
python scripts/admin/cortex_optimizer.py analyze

# Pre-release validation
pre-commit run --all-files
python scripts/admin/cortex_optimizer.py analyze --report json

# Quarterly cleanup
radon cc src/ --min B
pylint src/ --output-format=json > pylint-report.json
vulture src/ --min-confidence 60
```

**Target Metrics:**
- Overall optimization score: >85
- Plugin health: 100%
- YAML validation: 100%
- Complexity: No E/F ratings

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary  
**Last Updated:** 2025-11-13
