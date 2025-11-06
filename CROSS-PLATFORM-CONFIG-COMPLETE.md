# CORTEX Cross-Platform Configuration Guide

**Date:** November 6, 2025  
**Status:** ✅ COMPLETE - Config system operational

---

## ✅ What's Been Done

### 1. Configuration Management System

**File:** `CORTEX/src/config.py`

**Features:**
- ✅ Automatic hostname detection
- ✅ Machine-specific path resolution
- ✅ macOS ↔ Windows path translation
- ✅ Environment variable fallbacks
- ✅ Relative path discovery

### 2. Import System Fixed

**Changed:** Absolute imports → Relative imports

**Files Updated:**
- `CORTEX/src/entry_point/__init__.py`
- `CORTEX/src/entry_point/cortex_entry.py`
- `CORTEX/src/entry_point/request_parser.py`
- `CORTEX/src/entry_point/response_formatter.py`

### 3. Machine Configuration

**File:** `cortex.config.json`

**Configured Machines:**
```json
{
  "machines": {
    "Asifs-MacBook-Pro.local": {
      "rootPath": "/Users/asifhussain/PROJECTS/CORTEX",
      "brainPath": "/Users/asifhussain/PROJECTS/CORTEX/cortex-brain"
    },
    "AHHOME": {
      "rootPath": "D:\\PROJECTS\\CORTEX",
      "brainPath": "D:\\PROJECTS\\CORTEX\\cortex-brain"
    }
  }
}
```

---

## 🚀 How to Use (Works on Both Machines)

### Quick Test

```python
# Works on macOS and Windows!
from CORTEX.src.config import config
from CORTEX.src.entry_point import CortexEntry

# Automatically uses correct paths for current machine
cortex = CortexEntry()

# Process request
response = cortex.process("Create tests for auth.py")
print(response)
```

### From Command Line

```bash
# Test configuration
python -c "import sys; sys.path.insert(0, 'CORTEX'); from src.config import config; print(config.get_machine_info())"

# Run full test
python test_cortex.py
```

---

## 📋 Adding a New Machine

**Step 1:** Find your hostname
```bash
# macOS/Linux
hostname

# Windows PowerShell
$env:COMPUTERNAME
# or
hostname
```

**Step 2:** Add to `cortex.config.json`
```json
{
  "machines": {
    "YOUR-HOSTNAME-HERE": {
      "rootPath": "/path/to/CORTEX",      // macOS/Linux
      // or
      "rootPath": "C:\\path\\to\\CORTEX",  // Windows
      "brainPath": "/path/to/cortex-brain" // or Windows equivalent
    }
  }
}
```

**Step 3:** Test
```bash
python test_cortex.py
```

---

## 🔧 Configuration Priority

The config system checks in this order:

1. **Environment Variables** (highest priority)
   - `CORTEX_ROOT` - Override root path
   - `CORTEX_BRAIN_PATH` - Override brain path

2. **Machine-Specific Config**
   - `machines.{hostname}.rootPath`
   - `machines.{hostname}.brainPath`

3. **Default Config**
   - `application.rootPath`

4. **Relative Path Fallback** (lowest priority)
   - Auto-detects from file location

---

## 🏥 Current Status

### ✅ Working
- Config system loads correctly on both machines
- Paths automatically resolved
- Entry point initializes
- Relative imports functional

### ⚠️ Needs Setup (First Run)
- Database initialization (Tier 1, Tier 2 need schema creation)
- Brain directory structure creation

**Fix:** Run migrations on first use:
```python
from CORTEX.src.config import config

# Ensure directories exist
config.ensure_paths_exist()

# Then run tier migrations
# (Will be automated in setup script)
```

---

## 📊 Test Results

**Machine:** AHHOME (Windows)
```
Machine Configuration:
  hostname: AHHOME
  platform: nt
  root_path: D:\PROJECTS\CORTEX
  brain_path: D:\PROJECTS\CORTEX\cortex-brain
  src_path: D:\PROJECTS\CORTEX\CORTEX\src
  tests_path: D:\PROJECTS\CORTEX\CORTEX\tests
  config_loaded: True
  is_development: True

Initializing CORTEX...
=> CortexEntry initialized successfully!
```

**Result:** ✅ Config system fully operational

---

## 🎯 Next Steps

1. ✅ Config system complete
2. ⏳ Database initialization automation (needed for first run)
3. ⏳ Dashboard implementation (Sub-Group 4C)

---

## 💡 Benefits

1. **No More Path Issues** - Works automatically on any configured machine
2. **Easy Setup** - Just add hostname to config.json
3. **Environment Override** - Can use env vars for special cases
4. **Fallback Safety** - Uses relative paths if config missing
5. **Cross-Platform** - macOS and Windows paths handled automatically

---

**Status:** ✅ Ready for development on both machines!
