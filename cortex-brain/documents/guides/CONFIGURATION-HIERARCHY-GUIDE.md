# CORTEX Configuration Hierarchy Guide

**Version:** 3.2.0  
**Last Updated:** November 25, 2025  
**Purpose:** Complete reference for CORTEX configuration files, precedence rules, and merge behavior

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Configuration File Types](#configuration-file-types)
3. [Precedence Hierarchy](#precedence-hierarchy)
4. [Merge Behavior](#merge-behavior)
5. [Environment-Specific Configuration](#environment-specific-configuration)
6. [YAML Configuration Files](#yaml-configuration-files)
7. [Validation Rules](#validation-rules)
8. [Common Scenarios](#common-scenarios)
9. [Troubleshooting](#troubleshooting)

---

## Overview

CORTEX uses a **layered configuration system** with multiple files serving different purposes:

- **JSON configs** - Application settings, machine-specific paths, feature flags
- **YAML configs** - Templates, operation rules, brain protection, module definitions
- **Precedence-based merging** - Local overrides global, machine-specific overrides defaults

### Configuration Philosophy

```
Template → Example → Actual → Machine-Specific → Environment Variables
(Lowest)                                                        (Highest)
```

---

## Configuration File Types

### 1. JSON Configuration Files

Located in: **Repository Root**

| File | Purpose | Committed to Git | User Editable |
|------|---------|-----------------|---------------|
| `cortex.config.template.json` | Default values, documentation | ✅ Yes | ❌ No (reference only) |
| `cortex.config.example.json` | Example with comments | ✅ Yes | ❌ No (copy to create actual) |
| `cortex.config.json` | **Active configuration** | ⚠️ No (.gitignored) | ✅ Yes |

### 2. YAML Configuration Files

Located in: **`cortex-brain/`**

| File | Purpose | Committed to Git | Scope |
|------|---------|-----------------|-------|
| `response-templates.yaml` | Response format templates | ✅ Yes | Global |
| `operations-config.yaml` | Admin operation settings | ✅ Yes | Admin only |
| `publish-config.yaml` | Publishing/deployment rules | ✅ Yes | Admin only |
| `mkdocs-refresh-config.yaml` | Documentation generation | ✅ Yes | Admin only |
| `brain-protection-rules.yaml` | Tier 0 protection rules | ✅ Yes | Global (critical) |
| `module-definitions.yaml` | Module routing definitions | ✅ Yes | Global |
| `cleanup-rules.yaml` | Cleanup operation rules | ✅ Yes | Admin only |

### 3. Brain Component Configurations

Located in: **`cortex-brain/protection-layers/`**, **`cortex-brain/reference/`**

Multiple YAML files defining:
- Layer-specific protection rules
- API references for Tier 1/2/3
- Plugin development guidelines
- Agent system definitions

---

## Precedence Hierarchy

### JSON Configuration (cortex.config.json)

**Precedence Order (Highest to Lowest):**

```
1. Machine-Specific Overrides (machines.{hostname})
2. Main Configuration Values
3. Template Defaults (cortex.config.template.json)
```

### Example Precedence

```json
// cortex.config.template.json (Lowest Priority)
{
  "governance": {
    "requireGitValidation": true,
    "testQualityThreshold": 70
  }
}

// cortex.config.json (Medium Priority)
{
  "governance": {
    "testQualityThreshold": 80  // Overrides template
  }
}

// Machine-specific (Highest Priority)
{
  "machines": {
    "Asifs-MacBook-Pro.local": {
      "rootPath": "/Users/asifhussain/PROJECTS/CORTEX"  // Machine-specific
    }
  }
}
```

**Result:**
- `requireGitValidation`: `true` (from template)
- `testQualityThreshold`: `80` (from main config, overrides template)
- `rootPath`: `/Users/asifhussain/PROJECTS/CORTEX` (machine-specific)

---

## Merge Behavior

### JSON Deep Merge Strategy

CORTEX uses **deep merge** for JSON configuration:

```python
# Merge logic
final_config = deep_merge(
    template_config,      # Base layer
    main_config,          # Override layer
    machine_config        # Final override
)
```

### Deep Merge Rules

1. **Primitive Values** - Overwrite completely
2. **Objects** - Merge recursively
3. **Arrays** - Replace entirely (no merging)
4. **Null Values** - Remove keys

### Example: Object Merge

```json
// Template
{
  "testing": {
    "framework": "None",
    "timeout": 30,
    "headlessDefault": false
  }
}

// User config
{
  "testing": {
    "framework": "Playwright",
    "timeout": 60
    // headlessDefault not specified
  }
}

// Result (merged)
{
  "testing": {
    "framework": "Playwright",    // Overridden
    "timeout": 60,                // Overridden
    "headlessDefault": false      // Preserved from template
  }
}
```

### Example: Array Replace

```json
// Template
{
  "features": {
    "enabled": ["planning", "tdd"]
  }
}

// User config
{
  "features": {
    "enabled": ["planning", "tdd", "crawlers"]
  }
}

// Result (array replaced, not merged)
{
  "features": {
    "enabled": ["planning", "tdd", "crawlers"]
  }
}
```

---

## Environment-Specific Configuration

### Machine Detection

CORTEX automatically detects the hostname and applies machine-specific configuration:

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

### Hostname Resolution

1. Python: `socket.gethostname()`
2. Match against `machines` keys
3. Apply machine-specific overrides
4. Fall back to root-level values if no match

### Adding New Machines

```json
{
  "machines": {
    "your-machine-name": {
      "rootPath": "/path/to/CORTEX",
      "brainPath": "/path/to/CORTEX/cortex-brain"
    }
  }
}
```

**Find your hostname:**
```bash
# Mac/Linux
hostname

# Windows (PowerShell)
$env:COMPUTERNAME
```

---

## YAML Configuration Files

### Loading Strategy

YAML files are **loaded individually** (no merging across files):

```python
# Each YAML file is independent
response_templates = load_yaml("response-templates.yaml")
operations_config = load_yaml("operations-config.yaml")
brain_protection = load_yaml("brain-protection-rules.yaml")
```

### Caching Behavior

- ✅ **Cached:** First load stores in memory
- ⚡ **Performance:** 99.9% faster on subsequent loads
- 🔄 **Refresh:** Restart CORTEX to reload YAML changes

### YAML File Purposes

#### `response-templates.yaml`
**Purpose:** Pre-formatted response templates for common operations

**Structure:**
```yaml
templates:
  help:
    trigger: "help"
    format: "5-part-format"
    content: "..."
  
  admin_help:
    trigger: "admin help"
    context_required: "admin_operations"
    content: "..."
```

**Usage:** Auto-detected by user intent, reduces token usage by 97.2%

#### `operations-config.yaml`
**Purpose:** Admin operation configurations (deploy, docs generation, alignment)

**Scope:** Only active in CORTEX development repository

#### `brain-protection-rules.yaml`
**Purpose:** Tier 0 protection rules (7 layers)

**Critical:** Changes require extensive testing (affects all operations)

#### `module-definitions.yaml`
**Purpose:** Module routing and intent detection

**Structure:**
```yaml
modules:
  planning:
    file: "modules/planning-system-guide.md"
    triggers:
      - "plan"
      - "planning"
    priority: "high"
```

---

## Validation Rules

### Startup Validation

CORTEX validates configuration on startup:

```python
# src/config.py
class CortexConfig:
    def validate(self):
        # 1. Check required paths exist
        assert self.root_path.exists()
        assert self.brain_path.exists()
        
        # 2. Validate JSON structure
        assert "application" in self.config
        assert "machines" in self.config
        
        # 3. Check YAML files loadable
        for yaml_file in critical_yamls:
            assert yaml_file.exists()
            load_yaml(yaml_file)  # Syntax check
```

### Required Fields

**`cortex.config.json`:**
- `application.name` - String, non-empty
- `application.rootPath` - Valid path (or in machines config)
- `testing.framework` - String (can be "None")
- `governance.requireGitValidation` - Boolean

**Machine configs:**
- `rootPath` - Absolute path
- `brainPath` - Absolute path

### Validation Script

```bash
# Validate configuration
python3 -m src.config --validate

# Output
✅ Configuration valid
✅ All paths exist
✅ YAML files loadable
✅ No syntax errors
```

---

## Common Scenarios

### Scenario 1: New User Setup

**Goal:** Create configuration for first-time use

**Steps:**
```bash
# 1. Copy template to active config
cp cortex.config.template.json cortex.config.json

# 2. Add your machine
# Edit cortex.config.json:
{
  "machines": {
    "your-hostname": {
      "rootPath": "/your/path/to/CORTEX",
      "brainPath": "/your/path/to/CORTEX/cortex-brain"
    }
  }
}

# 3. Validate
python3 -m src.config --validate
```

### Scenario 2: Multi-Machine Development

**Goal:** Work on different machines with same config file

**Solution:** Add all machines to `machines` section

```json
{
  "machines": {
    "work-laptop": {
      "rootPath": "/Users/me/work/CORTEX",
      "brainPath": "/Users/me/work/CORTEX/cortex-brain"
    },
    "home-desktop": {
      "rootPath": "C:\\Projects\\CORTEX",
      "brainPath": "C:\\Projects\\CORTEX\\cortex-brain"
    },
    "remote-server": {
      "rootPath": "/opt/cortex",
      "brainPath": "/opt/cortex/cortex-brain"
    }
  }
}
```

**Benefit:** Same config file syncs via Git, auto-detects current machine

### Scenario 3: Enable/Disable Features

**Goal:** Turn features on/off without code changes

**Example:**
```json
{
  "token_optimization": {
    "enabled": false  // Disable token optimization
  },
  "governance": {
    "requireGitValidation": false  // Skip Git checks (dev mode)
  }
}
```

### Scenario 4: Customize Response Templates

**Goal:** Modify CORTEX response format

**File:** `cortex-brain/response-templates.yaml`

**Important:** 
- ⚠️ Changes affect all users
- ✅ Commit to Git after testing
- 🔄 Restart CORTEX to reload

### Scenario 5: Admin Operations Only

**Goal:** Enable admin commands in CORTEX repo

**Detection:** Automatic based on directory structure
```
If cortex-brain/admin/ exists:
  → Admin operations enabled
Else:
  → Admin operations hidden
```

**No configuration needed** - context-aware

---

## Troubleshooting

### Issue: Configuration Not Loading

**Symptoms:** CORTEX uses template values instead of your config

**Check:**
```bash
# 1. Verify file exists
ls -la cortex.config.json

# 2. Check JSON syntax
python3 -c "import json; json.load(open('cortex.config.json'))"

# 3. Validate structure
python3 -m src.config --validate
```

**Common Causes:**
- JSON syntax error (trailing comma, missing quote)
- File not named exactly `cortex.config.json`
- File in wrong directory

### Issue: Machine-Specific Config Not Applied

**Symptoms:** Wrong paths used

**Check:**
```bash
# 1. Verify hostname
python3 -c "import socket; print(socket.gethostname())"

# 2. Check config has matching key
cat cortex.config.json | grep "$(hostname)"

# 3. Test path resolution
python3 -m src.config --show-paths
```

**Fix:** Ensure hostname in `machines` matches exactly

### Issue: YAML Changes Not Reflected

**Symptoms:** Edited YAML but CORTEX shows old values

**Cause:** YAML files are cached in memory

**Solution:**
```bash
# Restart CORTEX (reload all YAML)
# In GitHub Copilot Chat: "restart CORTEX"
```

### Issue: Paths Invalid on Startup

**Symptoms:** Error: "rootPath does not exist"

**Check:**
```bash
# Verify paths
python3 << EOF
from pathlib import Path
import socket

hostname = socket.gethostname()
print(f"Hostname: {hostname}")

# Check your config
import json
config = json.load(open('cortex.config.json'))
machine = config['machines'].get(hostname, {})
root_path = Path(machine.get('rootPath', ''))
brain_path = Path(machine.get('brainPath', ''))

print(f"Root: {root_path} (exists: {root_path.exists()})")
print(f"Brain: {brain_path} (exists: {brain_path.exists()})")
EOF
```

**Fix:** Correct paths in machine-specific config

---

## Configuration Best Practices

### ✅ DO

1. **Start with template** - Copy `cortex.config.template.json`
2. **Add machine configs** - One entry per development machine
3. **Use absolute paths** - Avoid relative paths
4. **Validate after changes** - Run `--validate` script
5. **Document custom settings** - Add comments in JSON (or separate doc)
6. **Backup before major changes** - `cp cortex.config.json cortex.config.backup.json`

### ❌ DON'T

1. **Don't commit `cortex.config.json`** - Machine-specific, in `.gitignore`
2. **Don't edit template files** - Use actual config instead
3. **Don't use relative paths** - Machine portability issues
4. **Don't skip validation** - Catch errors early
5. **Don't modify critical YAMLs** - Without understanding impact
6. **Don't edit archived configs** - `cortex-brain/archives/` is read-only

---

## Configuration Schema

### JSON Schema (Reference)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["application", "machines", "testing", "governance"],
  "properties": {
    "application": {
      "type": "object",
      "required": ["name", "framework"],
      "properties": {
        "name": {"type": "string"},
        "framework": {"type": "string"},
        "rootPath": {"type": "string"},
        "buildCommand": {"type": "string"},
        "runCommand": {"type": "string"}
      }
    },
    "machines": {
      "type": "object",
      "patternProperties": {
        ".*": {
          "type": "object",
          "properties": {
            "rootPath": {"type": "string"},
            "brainPath": {"type": "string"}
          }
        }
      }
    },
    "testing": {
      "type": "object",
      "properties": {
        "framework": {"type": "string"},
        "testCommand": {"type": "string"},
        "headlessDefault": {"type": "boolean"}
      }
    },
    "governance": {
      "type": "object",
      "properties": {
        "requireGitValidation": {"type": "boolean"},
        "testQualityThreshold": {"type": "integer"}
      }
    },
    "token_optimization": {
      "type": "object",
      "properties": {
        "enabled": {"type": "boolean"},
        "soft_limit": {"type": "integer"},
        "target_reduction": {"type": "number"}
      }
    }
  }
}
```

---

## Summary

### Quick Reference Table

| What | File | Priority | Editable | Committed |
|------|------|----------|----------|-----------|
| **Active Config** | `cortex.config.json` | High | ✅ Yes | ❌ No |
| **Template** | `cortex.config.template.json` | Low | ❌ No | ✅ Yes |
| **Example** | `cortex.config.example.json` | N/A | ❌ No | ✅ Yes |
| **Response Templates** | `response-templates.yaml` | N/A | ⚠️ Careful | ✅ Yes |
| **Brain Protection** | `brain-protection-rules.yaml` | Critical | ❌ No | ✅ Yes |
| **Operations** | `operations-config.yaml` | Admin | ⚠️ Careful | ✅ Yes |

### Merge Order (Precedence)

```
Environment Variables (if implemented)
    ↓
Machine-Specific Config (machines.{hostname})
    ↓
Main Configuration (cortex.config.json)
    ↓
Template Defaults (cortex.config.template.json)
```

---

**Document Version:** 1.0  
**Author:** CORTEX Configuration System  
**Last Updated:** November 25, 2025  
**Next Review:** As needed (configuration changes)
