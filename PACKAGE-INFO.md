# CORTEX Package Information

**Version:** 3.3.0  
**Branch:** main  
**Build Date:** 2025-11-29 10:24:45

---

## 📊 Package Statistics

- **Files Included:** 2230
- **Directories Created:** 279
- **Files Excluded:** 3328
- **Total Size:** 90.49 MB

---

## 📦 What's Included

### Core Source Code (`src/`)
- 10 specialist agents (left brain + right brain)
- Tier 0, 1, 2, 3 architecture
- Plugin system
- Operations orchestrator
- Entry point processor

### Brain Storage (`cortex-brain/`)
- YAML configuration files
- Database schemas (SQL)
- Protection rules
- Response templates

### GitHub Copilot Integration (`.github/prompts/`)
- CORTEX.prompt.md (main entry point)
- copilot-instructions.md (baseline context)

### Documentation (`prompts/`)
- Modular documentation system
- User guides
- Technical reference
- Story narrative

### Scripts (`scripts/`)
- Automation tools
- Deployment scripts
- Utility functions

---

## 🚫 What's Excluded

- ❌ Test suite (`tests/`)
- ❌ CI/CD workflows (`.github/workflows/`)
- ❌ Documentation website (`docs/`, `site/`)
- ❌ Development tools (build scripts, profilers)
- ❌ Example code (`examples/`)
- ❌ Git commit history from main branch

---

## 🎯 Purpose

This package is designed for **end-user deployment**:

✅ Clean, minimal installation  
✅ Fast clone (no dev history)  
✅ Production-ready code only  
✅ All essential dependencies  
✅ Comprehensive setup guide  

---

## 📥 Installation

See **SETUP-CORTEX.md** for complete installation instructions.

**Quick start:**
```bash
git clone -b main --single-branch https://github.com/asifhussain60/CORTEX.git
cd CORTEX
pip install -r requirements.txt
cp cortex.config.template.json cortex.config.json
# Edit cortex.config.json with your paths
```

---

**Copyright © 2024-2025 Asif Hussain. All rights reserved.**
