---
title: Installation Guide
description: Complete installation instructions for CORTEX 3.0
author: 
generated: true
version: ""
last_updated: 
---

# CORTEX 3.0 Installation Guide

**Purpose:** Complete installation and setup instructions for CORTEX 3.0  
**Audience:** New users, system administrators  
**Version:**   
**Last Updated:** 

---

## Quick Install

### Prerequisites

CORTEX 3.0 requires:

- **Python:**  or higher
- **pip:** Latest version
- **Git:** For repository cloning (optional)
- **Operating System:** Windows, macOS, or Linux

### Installation Steps

1. **Clone or Download CORTEX**

```bash
# Option 1: Clone from repository
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX

# Option 2: Download ZIP and extract
```

2. **Install Python Dependencies**

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
python -c "import yaml, pytest; print('Dependencies OK')"
```

3. **Configure Environment**

```bash
# Copy example configuration
cp cortex.config.example.json cortex.config.json

# Edit configuration with your settings
# (See Configuration Guide for details)
```

4. **Initialize CORTEX Brain**

```bash
# Run setup script
python scripts/setup/init_brain.py

# Verify brain structure
python scripts/verify_installation.py
```

5. **Verify Installation**

```bash
# Run quick verification
python -c "from src.core import cortex_init; print('CORTEX Ready!')"

# Run test suite (optional but recommended)
pytest tests/ -v
```

---

## Platform-Specific Instructions

### Windows Installation

**Using PowerShell:**

```powershell
# Clone repository
git clone https://github.com/asifhussain60/CORTEX.git
Set-Location CORTEX

# Install dependencies
pip install -r requirements.txt

# Initialize brain
python scripts\setup\init_brain.py

# Verify
python scripts\verify_installation.py
```

**Common Issues:**
- **Path issues:** Use absolute paths in `cortex.config.json`
- **Permission errors:** Run PowerShell as Administrator
- **Python not found:** Add Python to PATH environment variable

### macOS Installation

**Using Terminal:**

```bash
# Clone repository
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX

# Install dependencies
pip3 install -r requirements.txt

# Initialize brain
python3 scripts/setup/init_brain.py

# Verify
python3 scripts/verify_installation.py
```

**Common Issues:**
- **SSL certificate errors:** Install certificates: `/Applications/Python\ 3.x/Install\ Certificates.command`
- **Permission denied:** Use `sudo` for system-wide installation
- **Python version:** Ensure Python 3.9+ is default

### Linux Installation

**Using bash:**

```bash
# Clone repository
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX

# Install dependencies
pip3 install -r requirements.txt

# Initialize brain
python3 scripts/setup/init_brain.py

# Verify
python3 scripts/verify_installation.py
```

**Common Issues:**
- **Package conflicts:** Use virtual environment: `python3 -m venv venv && source venv/bin/activate`
- **Permission errors:** Install in user space: `pip3 install --user -r requirements.txt`
- **Missing system packages:** Install build tools: `sudo apt-get install build-essential python3-dev`

---

## Configuration

### Required Configuration

Edit `cortex.config.json` with your settings:

```json
{
  "version": "",
  "name": "CORTEX",
  "description": "Memory and context system for GitHub Copilot",
  
  "paths": {
    "root": "/absolute/path/to/CORTEX",
    "brain": "/absolute/path/to/CORTEX/cortex-brain",
    "docs": "/absolute/path/to/CORTEX/docs"
  },
  
  "python": {
    "version": "3.9.6+",
    "executable": "python3"
  }
}
```

### Optional Configuration

**VS Code Extension:**
- Install from `cortex-extension/`
- See VS Code Extension Guide for details

**GitHub Integration:**
- Configure GitHub token in `.env`
- See Configuration Guide for OAuth setup

**Documentation Generation:**
- Configure MkDocs: `mkdocs.yml`
- See Admin Guide for documentation workflow

---

## Verification

### Test Your Installation

```bash
# Run verification script
python scripts/verify_installation.py
```

**Expected Output:**
```
✅ Python version: 3.9.6
✅ Required packages: All installed
✅ CORTEX brain: Initialized
✅ Configuration: Valid
✅ File permissions: OK

Installation Status: READY
```

### Run Test Suite

```bash
# Run all tests
pytest tests/ -v

# Run specific tier tests
pytest tests/tier0/ -v  # Brain protection
pytest tests/tier1/ -v  # Working memory
pytest tests/tier2/ -v  # Knowledge graph
pytest tests/tier3/ -v  # Context intelligence
```

---

## Troubleshooting

### Common Installation Issues

**Issue: "Module not found" errors**
```bash
# Solution: Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

**Issue: "Permission denied" when creating brain directories**
```bash
# Solution: Check directory permissions
chmod -R 755 cortex-brain/
```

**Issue: "YAML parsing error" in configuration**
```bash
# Solution: Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('cortex.config.json'))"
```

**Issue: "Import error: No module named 'src'"**
```bash
# Solution: Add CORTEX to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/CORTEX"
```

---

## Next Steps

After successful installation:

1. **Read Quick Start Guide:** Learn basic CORTEX usage
2. **Configure Settings:** Customize `cortex.config.json`
3. **Run First Operation:** Try `python -m src.entry_point.main help`
4. **Read Architecture Guide:** Understand CORTEX structure

---

## Getting Help

- **Documentation:** See [Quick Start Guide](quick-start.md)
- **Configuration:** See [Configuration Guide](configuration.md)
- **Troubleshooting:** See [Troubleshooting Guide](../guides/troubleshooting.md)
- **GitHub Issues:** [Report problems](https://github.com/asifhussain60/CORTEX/issues)

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file  
**Version:**   
**Generated:** 