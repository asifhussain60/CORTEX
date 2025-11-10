# Environment Setup

**Operation:** `environment_setup`  
**Category:** Environment  
**Status:** ✅ Ready

## Overview

Configure CORTEX development environment on Mac/Windows/Linux with automatic platform detection, dependency installation, and brain system initialization.

## Natural Language Triggers

- "setup"
- "setup environment"
- "configure"
- "configure cortex"
- "initialize environment"
- "get started"

## Setup Modules

The setup operation consists of 11 modules:

1. **project_validation** - Verify CORTEX project structure
2. **platform_detection** - Auto-detect OS (Mac/Windows/Linux)
3. **git_sync** - Sync with git repository
4. **virtual_environment** - Create/activate Python venv
5. **python_dependencies** - Install requirements.txt
6. **vision_api** - Configure vision capabilities (optional)
7. **conversation_tracking** - Enable conversation memory
8. **brain_initialization** - Initialize 4-tier brain system
9. **brain_tests** - Validate brain system (22 tests)
10. **tooling_verification** - Verify pytest, mkdocs, etc.
11. **setup_completion** - Final validation and report

## Profiles

### Minimal Profile ⚡
Core functionality only - fastest setup.

**Duration:** ~2-3 minutes  
**Modules:** project_validation, platform_detection, virtual_environment, python_dependencies, brain_initialization, setup_completion

```bash
# Use when
"minimal setup"
"quick start"
"just get it working"
```

### Standard Profile ⭐ Recommended
Recommended for most users - includes testing.

**Duration:** ~4-5 minutes  
**Modules:** All except conversation_tracking and tooling_verification

```bash
# Use when
"setup"
"configure cortex"
```

### Full Profile 🚀
Everything enabled - complete installation.

**Duration:** ~6-8 minutes  
**Modules:** All 11 modules

```bash
# Use when
"full setup"
"complete installation"
"setup everything"
```

## Platform-Specific Behavior

### macOS
- Uses Python 3.11+ (Homebrew or system)
- Virtual environment: `venv/`
- Package manager: pip
- Shell: zsh (default)

### Windows
- Uses Python 3.11+ (Microsoft Store or python.org)
- Virtual environment: `venv\`
- Package manager: pip
- Shell: PowerShell or cmd

### Linux
- Uses Python 3.11+ (apt/dnf/pacman)
- Virtual environment: `venv/`
- Package manager: pip
- Shell: bash (default)

## Prerequisites

### All Platforms
- Python 3.11 or higher
- Git 2.0 or higher
- Internet connection (for pip packages)

### Optional (Full Profile)
- OpenAI API key (for vision API)
- MkDocs (for documentation generation)

## Examples

### First-Time Setup

```bash
# Via entry point
/CORTEX setup

# Natural language
"setup cortex"
"configure environment"
"get started"
```

### Minimal Setup (CI/CD)

```bash
# Via entry point with profile
/CORTEX setup minimal

# Natural language
"minimal setup"
"quick start setup"
```

### Full Setup (Development)

```bash
# Via entry point
/CORTEX setup full

# Natural language
"full setup"
"complete installation"
```

## Expected Output

```
🧠 CORTEX Environment Setup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Module 1/11: Project Validation
   └─ CORTEX structure verified

✅ Module 2/11: Platform Detection  
   └─ Detected: macOS (arm64)

✅ Module 3/11: Git Sync
   └─ Branch: CORTEX-2.0 (up to date)

✅ Module 4/11: Virtual Environment
   └─ Created: venv/ (Python 3.11.6)

✅ Module 5/11: Python Dependencies
   └─ Installed: 47 packages from requirements.txt

✅ Module 6/11: Vision API
   └─ Configured: OpenAI GPT-4 Vision

✅ Module 7/11: Conversation Tracking
   └─ Initialized: cortex-brain/conversation-history.db

✅ Module 8/11: Brain Initialization
   └─ Brain system ready (4 tiers initialized)

✅ Module 9/11: Brain Tests
   └─ Passed: 22/22 brain protection tests

✅ Module 10/11: Tooling Verification
   └─ pytest ✓  mkdocs ✓  git ✓

✅ Module 11/11: Setup Completion
   └─ CORTEX ready for use!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Setup complete in 4m 32s
```

## Success Criteria

✅ Python 3.11+ detected and available  
✅ Virtual environment created and activated  
✅ All dependencies installed (47 packages)  
✅ Brain system initialized (4 tiers)  
✅ Brain protection tests passing (22/22)  
✅ Configuration files validated  
✅ Git repository synced (if enabled)

## Troubleshooting

### Python Not Found
```bash
# macOS
brew install python@3.11

# Windows  
# Install from python.org or Microsoft Store

# Linux (Ubuntu/Debian)
sudo apt install python3.11 python3.11-venv
```

### Permission Errors
```bash
# macOS/Linux
chmod +x run-cortex.sh
./run-cortex.sh setup

# Windows (PowerShell as Admin)
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Import Errors After Setup
```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Verify installation
pip list | grep pytest
python -c "import src.tier0.brain_protector; print('OK')"
```

### Brain Tests Failing
```bash
# Run tests manually to see details
pytest tests/tier0/test_brain_protector.py -v

# Check brain-protection-rules.yaml integrity
python -c "import yaml; yaml.safe_load(open('cortex-brain/brain-protection-rules.yaml'))"
```

## Configuration

Setup can be customized via `cortex.config.json`:

```json
{
  "environment": {
    "auto_detect_platform": true,
    "python_version": "3.11",
    "use_venv": true,
    "venv_path": "venv"
  },
  "brain": {
    "initialize_on_setup": true,
    "run_tests_on_init": true,
    "enable_conversation_tracking": true
  },
  "optional_features": {
    "vision_api": false,
    "documentation_generation": false
  }
}
```

## Related Documentation

- [Configuration Guide](../getting-started/configuration.md)
- [Platform Switch Plugin](../plugins/platform-switch.md)
- [Brain System Guide](../guides/brain-system.md)
- [Troubleshooting](../guides/troubleshooting.md)

## Module Details

### Module: project_validation
Validates CORTEX directory structure and required files.

**Checks:**
- `src/` directory exists
- `cortex-brain/` directory exists  
- `cortex.config.json` exists
- `requirements.txt` exists

**Output:** ✅ CORTEX structure verified or ❌ Missing files list

### Module: platform_detection
Auto-detects operating system and architecture.

**Detection:**
- OS: macOS, Windows, Linux
- Architecture: x86_64, arm64, aarch64
- Shell: zsh, bash, PowerShell, cmd

**Output:** Platform details with recommendations

### Module: brain_initialization
Initializes the 4-tier brain system.

**Tiers Initialized:**
- Tier 0: Governance (brain-protection-rules.yaml)
- Tier 1: Working Memory (conversation-history.db)
- Tier 2: Knowledge Graph (knowledge-graph.yaml)
- Tier 3: Development Context (development-context.yaml)

**Output:** Brain system status for each tier

## Performance

**Benchmarks** (MacBook Air M2):
- Minimal Profile: 2m 15s
- Standard Profile: 4m 32s  
- Full Profile: 6m 48s

**Bottlenecks:**
- Python dependency installation: ~60% of time
- Brain tests: ~15% of time
- Git operations: ~10% of time

## Testing

Tested on:
- ✅ macOS Sonoma (M2, Intel)
- ✅ Windows 11 (x86_64)
- ✅ Ubuntu 22.04 LTS (x86_64)
- ✅ Fresh installs (no existing venv)
- ✅ Existing installations (update mode)

## Notes

**Setup is idempotent** - running it multiple times is safe. It will:
- Skip already-installed dependencies
- Update existing configuration
- Re-run tests to verify state
- Report current configuration

**CI/CD Integration:**
Use minimal profile for fast CI builds:
```yaml
# .github/workflows/test.yml
- name: Setup CORTEX
  run: python -m src.cortex_entry setup minimal
```
