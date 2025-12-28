# CORTEX Toolkit - Quick Reference Guide

**Version:** 1.0.0  
**Last Updated:** December 27, 2025

---

## ⚡ Quick Commands

### Discovery
```bash
# List all tools
python cortex-toolkit/shared/toolkit_registry.py list

# Get tool info
python cortex-toolkit/shared/toolkit_registry.py info align

# List categories
python cortex-toolkit/shared/toolkit_registry.py categories
```

### Brain Operations
```bash
# System alignment
python cortex-toolkit/cli/wrappers/align_wrapper.py --check-only

# Health check
python cortex-toolkit/cli/wrappers/healthcheck_wrapper.py

# Optimize
python cortex-toolkit/cli/wrappers/optimize_wrapper.py

# Cleanup
python cortex-toolkit/cli/wrappers/cleanup_wrapper.py
```

### System Operations
```bash
# Code review
python cortex-toolkit/cli/wrappers/review_wrapper.py

# Deploy
python cortex-toolkit/cli/wrappers/deploy_wrapper.py

# Sanitize
python cortex-toolkit/cli/wrappers/sanitize_wrapper.py [directory]
```

---

## 📂 File Locations

| Category | Path | Count |
|----------|------|-------|
| Brain Operations | `core/brain/` | 4 |
| System Operations | `core/operations/` | 3 |
| Planning | `core/planning/` | 3 |
| Analytics | `analytics/` | 7 |
| Documentation | `documentation/` | 3 |
| Testing | `testing/` | 3 |
| Migration | `migration/` | 2 |
| Maintenance | `maintenance/` | 3 |
| Generators | `core/generators/` | 5 |
| CLI Wrappers | `cli/wrappers/` | 20 |
| Shared Libraries | `shared/` | 4 |

**Total:** 55 Python scripts

---

## 🔧 Common Tasks

### Add New Tool

1. Create script in appropriate category folder
2. Add entry to `toolkit-manifest.yaml`
3. (Optional) Create CLI wrapper
4. Test with registry

### Fix Import Issues

Use relative imports in toolkit files:
```python
# ✅ CORRECT
from .base_wrapper import BaseCLIWrapper

# ❌ WRONG
from scripts.cli_wrappers.base_wrapper import BaseCLIWrapper
from cortex_toolkit.cli.wrappers.base_wrapper import BaseCLIWrapper
```

### Cross-Repository Usage

```bash
# Set CORTEX_TOOLKIT_ROOT environment variable
export CORTEX_TOOLKIT_ROOT=~/PROJECTS/CORTEX/cortex-toolkit

# Invoke from any repository
python $CORTEX_TOOLKIT_ROOT/shared/toolkit_registry.py invoke healthcheck
```

---

## 📊 Tool Summary

**55 Total Tools Across 10 Categories:**

- **Brain Operations (4):** align, healthcheck, optimize, cleanup
- **System Operations (3):** review, deploy, sanitize
- **Planning (3):** plan, ado, planning-file-manager
- **Analytics (7):** profiling, metrics collection, visualization
- **Documentation (3):** code docs, quick reference, prompt regeneration
- **Testing (3):** performance tests, deployment validation, mock verification
- **Migration (2):** schema migration, version detection
- **Maintenance (3):** temp cleanup, duplicate detection, master cleanup
- **Generators (5):** OpenAPI, schemas, narratives
- **CLI Wrappers (20):** Unified wrapper infrastructure

---

## 🔗 Links

- **Main Docs:** [README.md](./README.md)
- **Tool Inventory:** [TOOLS-INVENTORY.md](/cortex-toolkit/TOOLS-INVENTORY.md)
- **Folder Structure:** [FOLDER-STRUCTURE.md](/cortex-toolkit/FOLDER-STRUCTURE.md)
- **CORTEX Prompt:** [CORTEX.prompt.md](/.github/prompts/CORTEX.prompt.md)

---

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX
