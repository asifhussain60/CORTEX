# Environment Setup Operation

**Operation ID:** `environment_setup`  
**Natural Language:** "setup", "configure", "initialize environment"  
**Version:** 1.0.0 (CORTEX 3.0 Phase 1.1)  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.

---

## Overview

The Environment Setup operation configures your development environment for CORTEX 3.0. It handles platform detection, dependency installation, virtual environment creation, and brain database initialization.

**What it does:**
- ✅ Detects your platform (Windows/Mac/Linux)
- ✅ Validates Python 3.9+ installation
- ✅ Validates Git installation
- ✅ Creates virtual environment (.venv)
- ✅ Installs Python dependencies from requirements.txt
- ✅ Initializes brain databases (Tier 1-3)
- ✅ Validates final setup

**Time to complete:** 2-5 minutes (depending on internet speed)

---

## Requirements

### Essential
- **Python:** 3.9 or higher
- **Git:** Any recent version
- **Internet:** For pip package downloads

### Optional
- **VS Code:** For enhanced development experience

---

## Usage

### Natural Language (Recommended)

Simply tell CORTEX to set up your environment:

```
"setup my environment"
"configure cortex"
"initialize development environment"
```

### Command Line

Run the operation directly:

```powershell
# Windows PowerShell
python src/operations/setup.py

# Standard profile (default)
python src/operations/setup.py --profile standard

# Minimal profile (validation only)
python src/operations/setup.py --profile minimal

# Full profile (everything)
python src/operations/setup.py --profile full
```

### Python API

Use programmatically:

```python
from src.operations.setup import setup_environment
from pathlib import Path

# Auto-detect project root
result = setup_environment(profile='standard')

# Specify project root
result = setup_environment(
    profile='standard',
    project_root=Path('d:/PROJECTS/CORTEX')
)

# Check result
if result['success']:
    print(f"Setup complete on {result['platform']}")
    print(f"Python: {result['python_version']}")
    print(f"Dependencies: {result['dependencies_installed']}")
else:
    print(f"Setup failed: {result.get('error')}")
```

---

## Profiles

### Minimal (`minimal`)

**What it does:**
- Platform detection
- Python version validation
- Git validation

**Use when:**
- Checking environment status
- Verifying prerequisites
- Quick validation

**Time:** ~10 seconds

---

### Standard (`standard`) - DEFAULT

**What it does:**
- Everything in Minimal, plus:
- Creates virtual environment
- Installs dependencies
- Initializes brain databases

**Use when:**
- First-time setup
- Setting up new machine
- Resetting environment

**Time:** 2-5 minutes

---

### Full (`full`)

**What it does:**
- Everything in Standard, plus:
- Validates VS Code installation
- Creates additional development files
- Runs comprehensive validation

**Use when:**
- Complete development setup
- Contributing to CORTEX
- Ensuring full compatibility

**Time:** 5-10 minutes

---

## Output Example

```
🔧 CORTEX Environment Setup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Profile: standard
Project: d:\PROJECTS\CORTEX

Step 1/8: Platform Detection
  Platform: Windows
  ✅ Detected successfully

Step 2/8: Python Validation
  Version: 3.11.5
  ✅ Meets requirement (3.9+)

Step 3/8: Git Validation
  Version: 2.42.0
  ✅ Git installed

Step 4/8: VS Code Check
  ⚠️  VS Code not found (optional)

Step 5/8: Virtual Environment
  Creating .venv...
  ✅ Virtual environment created

Step 6/8: Dependencies
  Installing from requirements.txt...
  ✅ Installed 12 packages

Step 7/8: Brain Databases
  Initializing Tier 1 (conversations)...
  Initializing Tier 2 (knowledge-graph)...
  Initializing Tier 3 (context-intelligence)...
  ✅ Brain databases initialized

Step 8/8: Final Validation
  Virtual environment: ✅
  Dependencies: ✅
  Brain databases: ✅

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Environment setup complete!

Next Steps:
  1. Activate virtual environment:
     Windows: .venv\Scripts\activate
     Mac/Linux: source .venv/bin/activate
  
  2. Verify installation:
     python -c "import src.cortex; print('CORTEX ready!')"
  
  3. Start using CORTEX:
     Tell Copilot what you need!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Troubleshooting

### "Python version too old"

**Problem:** Python 3.8 or earlier detected  
**Solution:** Install Python 3.9 or higher from [python.org](https://www.python.org/downloads/)

### "Git not found"

**Problem:** Git is not installed or not in PATH  
**Solution:** 
- Install Git from [git-scm.com](https://git-scm.com/)
- Windows: Ensure "Add to PATH" is checked during installation

### "Permission denied creating virtual environment"

**Problem:** Insufficient permissions  
**Solution:**
- Windows: Run PowerShell as Administrator
- Mac/Linux: Check directory permissions with `ls -la`

### "Dependency installation failed"

**Problem:** pip can't download packages  
**Solution:**
- Check internet connection
- Try: `python -m pip install --upgrade pip`
- Try: `pip install -r requirements.txt` manually

### "Brain database creation failed"

**Problem:** SQLite error or disk space  
**Solution:**
- Check available disk space (need ~100MB)
- Ensure `cortex-brain/` directory is writable
- Try deleting `cortex-brain/` and re-running setup

---

## What Gets Created

After successful setup:

```
CORTEX/
├── .venv/                          # Virtual environment
│   ├── Scripts/                    # Windows executables
│   ├── bin/                        # Unix executables
│   └── Lib/                        # Python packages
│
├── cortex-brain/                   # Brain storage
│   ├── tier1/
│   │   └── conversations.db        # Short-term memory
│   ├── tier2/
│   │   └── knowledge-graph.db      # Long-term memory
│   └── tier3/
│       └── context-intelligence.db # Development context
│
└── requirements.txt                # Dependency manifest
```

**Virtual Environment Size:** ~100-200MB  
**Brain Databases:** ~1-5MB (grows with usage)

---

## Platform-Specific Notes

### Windows

- **Shell:** PowerShell or Command Prompt
- **Activate venv:** `.venv\Scripts\activate`
- **Python command:** `python`

### macOS

- **Shell:** zsh or bash
- **Activate venv:** `source .venv/bin/activate`
- **Python command:** `python3`

### Linux

- **Shell:** bash
- **Activate venv:** `source .venv/bin/activate`
- **Python command:** `python3`

---

## Advanced Usage

### Custom Project Root

```python
from pathlib import Path
from src.operations.setup import setup_environment

# Setup in different directory
result = setup_environment(
    profile='standard',
    project_root=Path('/path/to/my/cortex')
)
```

### Skip Virtual Environment

If you prefer global Python installation:

```python
result = setup_environment(profile='minimal')
# Only validates, doesn't create venv
```

### Retry Failed Steps

If setup partially fails:

```python
# Re-run setup (it skips completed steps)
result = setup_environment(profile='standard')
# Will skip: platform detection, Python/Git validation
# Will retry: venv creation, dependencies, brain databases
```

---

## Integration with CORTEX Operations

The setup operation integrates with CORTEX's universal operations system:

```python
from src.operations import execute_operation

# Execute via operations system
result = execute_operation('environment_setup', profile='standard')

# Or use natural language
result = execute_operation('setup my environment')
```

---

## Security Notes

- ✅ **No credentials stored** - Setup doesn't collect or store any sensitive data
- ✅ **Local-only** - All operations happen on your machine
- ✅ **Safe defaults** - Uses standard Python venv and pip
- ✅ **Validated sources** - Dependencies from PyPI only

---

## Performance

**Typical execution times:**

| Step | Time |
|------|------|
| Platform detection | <1s |
| Python/Git validation | <1s |
| Virtual environment creation | 5-10s |
| Dependency installation | 60-120s |
| Brain database initialization | 1-2s |
| **Total (standard profile)** | **~2-3 minutes** |

**Network usage:**
- ~50-100MB download (Python packages)
- One-time setup cost

---

## Support

**Issues?**

1. Check troubleshooting section above
2. Verify requirements (Python 3.9+, Git)
3. Run with `--profile minimal` to isolate issue
4. Check `logs/setup.log` for detailed errors

**Need help?**

- Natural language: "help with setup"
- Documentation: This file
- Source code: `src/operations/setup.py`

---

**Last Updated:** 2025-11-14  
**Phase:** 1.1 Week 3 (Simplified Operations)  
**Status:** ✅ Production Ready

---

*This operation is part of CORTEX 3.0 - The cognitive framework for GitHub Copilot.*
