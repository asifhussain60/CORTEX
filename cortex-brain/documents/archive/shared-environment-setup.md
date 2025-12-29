# Shared Environment Setup Guide

**CORTEX 3.6.0** - Universal shared Python environment for all CORTEX projects

---

## 🎯 Overview

CORTEX 3.6 introduces a **shared environment architecture** where all CORTEX projects link to a single Python virtual environment instead of maintaining individual `.venv` directories.

**Benefits:**
- ⚡ **83% faster setup** for additional projects (60s → 10s)
- 💾 **67% disk space reduction** (1.5GB → 500MB for 3 projects)
- 🔄 **Automatic synchronization** of dependencies across projects
- 🛡️ **Backward compatible** with existing `.venv` setups

---

## 📁 Architecture

### Directory Structure

```
~/.cortex/
└── venv/              # Shared Python environment (ALL projects)
    ├── bin/
    ├── lib/
    └── pyvenv.cfg

~/projects/
├── project1/
│   ├── cortex-brain/  # Project-specific brain data
│   └── cortex.config.json → points to ~/.cortex/venv/
├── project2/
│   ├── cortex-brain/
│   └── cortex.config.json → points to ~/.cortex/venv/
└── project3/
    ├── cortex-brain/
    └── cortex.config.json → points to ~/.cortex/venv/
```

### Key Principles

1. **One shared environment** at `~/.cortex/venv/` contains all CORTEX dependencies
2. **Project-specific brains** maintain independent conversation history and context
3. **Config files** reference the shared environment via `shared_env_path`
4. **Migration is optional** - existing `.venv` setups continue working

---

## 🚀 Setup Workflows

### First-Time Installation

```bash
# 1. Clone CORTEX
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX

# 2. Run setup (creates ~/.cortex/venv/)
python3 src/setup/setup_wizard.py

# 3. Setup automatically:
#    - Creates shared environment at ~/.cortex/venv/
#    - Installs all dependencies
#    - Creates user profile
#    - Initializes brain databases
#    - Registers response templates
```

**Time:** ~60 seconds (one-time)

### Linking Additional Projects

```bash
# 1. Navigate to new project
cd ~/projects/my-new-project

# 2. Run CORTEX link command
cortex link

# 3. Link automatically:
#    - References existing ~/.cortex/venv/
#    - Creates project-specific cortex-brain/
#    - Copies config template
#    - Validates environment
```

**Time:** ~5 seconds (per project)

### Migration from .venv

Existing projects with `.venv/` can migrate to shared environment:

```bash
# 1. Navigate to existing project
cd ~/projects/old-project

# 2. Run migration
cortex migrate --to-shared

# 3. Migration process:
#    - Extracts package list from .venv/
#    - Installs missing packages to ~/.cortex/venv/
#    - Updates cortex.config.json with shared_env_path
#    - Preserves user profile and brain data
#    - Optionally removes old .venv/ (with confirmation)
```

**Important:** Migration preserves all data - no information lost

---

## ⚙️ Configuration

### cortex.config.json Structure

```json
{
  "machines": {
    "YOUR-HOSTNAME": {
      "rootPath": "/absolute/path/to/project",
      "brainPath": "/absolute/path/to/project/cortex-brain"
    }
  },
  "shared_env_path": "/Users/username/.cortex/venv",
  "user": {
    "name": "Your Name",
    "preference": "concise",
    "role": "expert",
    "work_area": "backend",
    "language": "en"
  },
  "testing": {
    "enabled": false
  }
}
```

**Key Fields:**
- `shared_env_path`: Path to shared Python environment (new in 3.6)
- `user`: User profile for personalized responses
- `machines`: Machine-specific paths (supports multi-machine sync)

### User Profile Fields

| Field | Type | Options | Description |
|-------|------|---------|-------------|
| `name` | string | any | Your name |
| `preference` | Literal | concise, verbose, balanced | Response style |
| `role` | Literal | beginner, intermediate, expert | Experience level |
| `work_area` | Literal | backend, frontend, fullstack, web_dev, data_science, ai_ml, devops, mobile, general | Primary work domain |
| `language` | string | en, es, fr, etc. | Preferred language |

---

## 🔍 Verification

### Check Shared Environment

```bash
# Verify shared environment exists
ls -la ~/.cortex/venv/

# Check Python version
~/.cortex/venv/bin/python --version

# List installed packages
~/.cortex/venv/bin/pip list
```

### Check Project Configuration

```bash
# From project directory
cat cortex.config.json | grep shared_env_path

# Should output: "shared_env_path": "/Users/username/.cortex/venv"
```

### Validate Setup

```bash
# Run alignment check (validates all components)
cortex align

# Expected output:
# ✅ Shared environment: /Users/username/.cortex/venv
# ✅ Brain databases: tier1, tier2, tier3
# ✅ User profile: loaded
# ✅ Templates: 30+ registered
# ✅ Plan registry: initialized
```

---

## 🛠️ Troubleshooting

### Shared Environment Not Found

**Problem:** `shared_env_path` not set or invalid

**Solution:**
```bash
# Re-run setup wizard
python3 src/setup/setup_wizard.py

# Or manually set path
cortex config set shared_env_path ~/.cortex/venv
```

### Multiple Python Versions

**Problem:** Project requires different Python version

**Solution:**
```bash
# Create version-specific shared env
python3.10 -m venv ~/.cortex/venv-3.10
python3.11 -m venv ~/.cortex/venv-3.11

# Update config to point to correct version
cortex config set shared_env_path ~/.cortex/venv-3.11
```

### Dependency Conflicts

**Problem:** Projects need conflicting package versions

**Solution:**
```bash
# Use project-specific requirements.txt
pip install -r requirements.txt --target ./lib/

# Or maintain separate .venv for problematic project
# (backward compatibility - old approach still works)
```

---

## 📊 Performance Comparison

| Metric | Old (3 projects) | New (3 projects) | Improvement |
|--------|------------------|------------------|-------------|
| **Setup time** | 90s (3×30s) | 70s (60s+5s+5s) | **22% faster** |
| **Disk space** | 1.5GB (3×500MB) | 500MB | **67% less** |
| **Package sync** | Manual | Automatic | **100% automated** |
| **Dependency updates** | 3× time | 1× time | **67% faster** |

---

## 🔄 Backward Compatibility

**All existing setups continue working:**

- ✅ Projects with `.venv/` remain functional
- ✅ No forced migration required
- ✅ Old and new approaches can coexist
- ✅ Migration is optional and reversible

**Future-proof:**
- New projects automatically use shared environment
- Gradual migration supported
- No breaking changes to existing workflows

---

## 📚 Related Documentation

- **User Profiling Guide:** `user-profiling-guide.md`
- **Plan Management Guide:** `plan-management-guide.md`
- **System Alignment Guide:** `.github/prompts/modules/system-alignment-guide.md`
- **Upgrade Guide:** `.github/prompts/modules/upgrade-guide.md`

---

**Version:** 3.6.0  
**Last Updated:** 2025-01-29  
**Author:** Asif Hussain
