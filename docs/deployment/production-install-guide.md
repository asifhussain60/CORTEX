# CORTEX Production Installation Guide

**Version:** 3.2.0  
**Last Updated:** December 16, 2025  
**Author:** Asif Hussain

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Configuration](#configuration)
4. [Verification](#verification)
5. [CLI Commands](#cli-commands)
6. [Troubleshooting](#troubleshooting)
7. [Uninstallation](#uninstallation)

---

## Prerequisites

### System Requirements

- **Python:** 3.9+ (tested on 3.9, 3.10, 3.11, 3.12, 3.13)
- **Operating System:** Windows, macOS, Linux
- **Disk Space:** ~100 MB for package + dependencies
- **Memory:** 512 MB minimum (2 GB recommended)

### Required Tools

```bash
# Check Python version
python --version  # Should be 3.9 or higher

# Upgrade pip (recommended)
python -m pip install --upgrade pip

# Install build tools (optional, for development)
pip install build twine
```

---

## Installation Methods

### Method 1: From Source (Development)

**Use this method for active development or contributing to CORTEX.**

```bash
# 1. Clone repository
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX

# 2. Install in editable mode
pip install -e .

# 3. Verify installation
cortex "version"
```

**Benefits:**
- Changes to source code immediately available
- No reinstall needed during development
- Full access to git history and branches

### Method 2: From Wheel Distribution

**Use this method for production deployments or testing packaged version.**

```bash
# 1. Build wheel (if not already built)
python -m build

# 2. Install from wheel
pip install dist/cortex_ai-3.2.0-py3-none-any.whl

# 3. Verify installation
cortex "version"
```

**Benefits:**
- Clean installation without source files
- Faster installation (pre-built)
- Suitable for deployment pipelines

### Method 3: From PyPI (Future)

**This method will be available after PyPI publication.**

```bash
# Install from PyPI
pip install cortex-ai

# Verify installation
cortex "version"
```

---

## Configuration

### 1. Configuration File Setup

CORTEX uses `cortex.config.json` for machine-specific paths. The package includes a template.

```bash
# Copy template to create your config
cp cortex.config.template.json cortex.config.json

# Edit with your paths (use absolute paths)
# Required paths:
# - cortex_root: Path to CORTEX repository
# - cortex_brain: Path to cortex-brain directory
# - user_repos: Paths to your project repositories
```

**Example Configuration:**

```json
{
    "version": "3.2.0",
    "paths": {
        "cortex_root": "D:/PROJECTS/CORTEX",
        "cortex_brain": "D:/PROJECTS/CORTEX/cortex-brain",
        "user_repos": {
            "noorcanvas": "D:/PROJECTS/NOOR CANVAS",
            "ksessions": "D:/PROJECTS/KSESSIONS"
        }
    },
    "settings": {
        "log_level": "INFO",
        "enable_caching": true
    }
}
```

### 2. Environment Variables (Optional)

```bash
# Set CORTEX_ROOT for package-aware resource resolution
export CORTEX_ROOT=/path/to/CORTEX

# Set log level
export CORTEX_LOG_LEVEL=DEBUG
```

### 3. First-Time Setup

After installation, initialize the brain storage:

```bash
# This creates necessary directories and databases
cortex "help"
```

---

## Verification

### Basic Verification

```bash
# Test 1: Check version
cortex "version"
# Expected: CORTEX v3.2.0

# Test 2: Test planning command (simple request)
cortex-plan "test implementation"
# Expected: "Simple request, no planning needed"

# Test 3: Test planning command (complex request)
cortex-plan "comprehensive authentication system analysis"
# Expected: Plan created with TEMP-PLAN-YYYYMMDD_HHMMSS-* format
```

### Advanced Verification

```bash
# Test 4: Check imports
python -c "from src.entry_point.planning_gate import PlanningGate; print('✓ Imports working')"

# Test 5: Check resource loading
python -c "from src.config import get_config; print('✓ Config system working')"

# Test 6: Check CLI entry points
which cortex cortex-plan cortex-approve cortex-reject
# Expected: All 4 commands found in your Python environment
```

### Integration Test Suite

For comprehensive validation, run the integration tests:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run integration tests
pytest tests/integration/test_production_install.py -v

# Expected results:
# - 6/9 core tests passing (CLI commands, config, planning)
# - 3 pre-existing issues (YAML syntax, Unicode encoding)
```

---

## CLI Commands

### Primary Commands

#### `cortex`
**Purpose:** Main CORTEX entry point for interactive commands

```bash
# Get version
cortex "version"

# Get help
cortex "help"

# Execute operations (examples)
cortex "system maintenance"
cortex "sanitize codebase"
cortex "align"
```

#### `cortex-plan`
**Purpose:** Create execution plans for complex requests

```bash
# Syntax
cortex-plan "<request description>"

# Examples
cortex-plan "implement authentication system"
cortex-plan "add user management module"
cortex-plan "refactor database layer"

# Behavior:
# - Tier 1-2 (simple): No plan created, direct execution suggested
# - Tier 3+ (complex): Creates temporary plan in cortex-brain/documents/planning/features/temp-plans/
```

#### `cortex-approve`
**Purpose:** Approve a temporary plan for execution

```bash
# Syntax
cortex-approve <plan-id>

# Example
cortex-approve TEMP-PLAN-20251216_165118-authentication-system

# Behavior:
# - Validates plan exists
# - Marks plan as approved
# - Initiates execution (placeholder - full implementation in Plan B)
```

#### `cortex-reject`
**Purpose:** Reject and delete a temporary plan

```bash
# Syntax
cortex-reject <plan-id>

# Example
cortex-reject TEMP-PLAN-20251216_165118-authentication-system

# Behavior:
# - Validates plan exists
# - Deletes plan folder and all contents
# - Confirms deletion
```

---

## Troubleshooting

### Issue 1: `ModuleNotFoundError: No module named 'src'`

**Cause:** Package not installed or not in editable mode

**Solution:**
```bash
# From CORTEX repository root
pip install -e .

# OR reinstall
pip uninstall cortex-ai
pip install -e .
```

### Issue 2: `FileNotFoundError: [Errno 2] No such file or directory: 'cortex.config.json'`

**Cause:** Configuration file missing

**Solution:**
```bash
# Copy template
cp cortex.config.template.json cortex.config.json

# Edit with your paths
# Ensure cortex_root points to CORTEX installation directory
```

### Issue 3: `command not found: cortex`

**Cause:** Entry points not registered or wrong Python environment

**Solution:**
```bash
# Check which Python
which python
pip --version

# Reinstall package
pip uninstall cortex-ai
pip install -e .

# Verify entry points
pip show -f cortex-ai | grep -A 10 "Entry-points"
```

### Issue 4: `UnicodeEncodeError` when running CLI commands

**Cause:** Terminal doesn't support Unicode/emojis (Windows CMD)

**Solution:**
```bash
# Use PowerShell or Windows Terminal instead of CMD
# OR set environment variable
set PYTHONIOENCODING=utf-8

# For PowerShell
$env:PYTHONIOENCODING="utf-8"
```

### Issue 5: `IndentationError` or `SyntaxError` after installation

**Cause:** Python version mismatch or corrupted installation

**Solution:**
```bash
# Check Python version
python --version  # Must be 3.9+

# Clean reinstall
pip uninstall cortex-ai
pip cache purge
pip install -e .
```

### Issue 6: `ImportError: cannot import name 'PlanningGate'`

**Cause:** Circular import or missing dependencies

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check for circular imports
python -c "import src.entry_point.planning_gate"
```

### Issue 7: YAML syntax error in `response-templates.yaml`

**Status:** Pre-existing issue, does not block CLI functionality

**Workaround:** CLI planning commands (`cortex-plan`, `cortex-approve`, `cortex-reject`) work correctly. Main `cortex` command may show warnings but functional.

---

## Uninstallation

### Complete Uninstall

```bash
# 1. Uninstall package
pip uninstall cortex-ai

# 2. Remove configuration (optional)
rm cortex.config.json

# 3. Clean pip cache (optional)
pip cache purge

# 4. Remove virtual environment (if used)
deactivate
rm -rf .venv
```

### Partial Uninstall (Keep Configuration)

```bash
# Just uninstall package
pip uninstall cortex-ai

# Configuration remains for reinstall
```

### Remove Development Installation

```bash
# If installed with pip install -e .
pip uninstall cortex-ai

# Remove source directory (optional)
cd ..
rm -rf CORTEX
```

---

## Platform-Specific Notes

### Windows

- Use **PowerShell** or **Windows Terminal** (not CMD) for best Unicode support
- Paths use backslashes: `D:\PROJECTS\CORTEX`
- Git Bash also works well

### macOS

- No special considerations
- Ensure Python 3.9+ from Homebrew or python.org
- `which python3` should point to correct version

### Linux

- No special considerations
- Use package manager's Python or pyenv
- Ensure `pip` matches `python` version

---

## Next Steps

After successful installation:

1. **Configure:** Edit `cortex.config.json` with your paths
2. **Verify:** Run `cortex "version"` and basic CLI tests
3. **Learn:** Review `cortex "help"` for available operations
4. **Execute:** Start using `cortex-plan` for complex tasks

For development contributions, see `CONTRIBUTING.md`.

For API documentation, see `docs/api/`.

---

## Support

- **GitHub Issues:** https://github.com/asifhussain60/CORTEX/issues
- **Documentation:** `docs/` directory in repository
- **Author:** Asif Hussain

---

**Installation Guide Version:** 1.0.0  
**Compatible with CORTEX:** 3.2.0+
