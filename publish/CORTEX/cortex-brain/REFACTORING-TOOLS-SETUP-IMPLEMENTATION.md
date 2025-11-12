# Refactoring Tools Integration - Implementation Summary

**Date:** 2025-11-12  
**Status:** ✅ IMPLEMENTED  
**Architecture:** Zero-Footprint, User-Consent Required

---

## 🎯 What Was Implemented

### New Setup Module: `RefactoringToolsModule`

**Location:** `src/setup/modules/refactoring_tools_module.py`

**Purpose:** Detect and optionally install refactoring tools based on user's actual tech stack (C#, JavaScript, SQL, Python).

**Key Features:**
- ✅ **Zero-Footprint Design** - Detection only by default, no forced installs
- ✅ **Tech Stack Priority** - C# first, then JavaScript, SQL, Python last
- ✅ **Firewall-Aware** - Graceful degradation when tools blocked
- ✅ **Guidance-Based** - Provides installation instructions for missing tools
- ✅ **Optional Module** - Disabled by default, user must opt-in

---

## 🏗️ Architecture Alignment

### Follows CORTEX Refactoring Strategy (Revised)

**Reference:** `cortex-brain/REFACTORING-STRATEGY-REVISED.md`

**Core Principles Applied:**
1. **Detect, Don't Require** - Never forces installations
2. **User's Tech Stack First** - C# > JavaScript > SQL > Python priority
3. **Respect Org Constraints** - Handles firewall restrictions gracefully
4. **Guidance Fallback** - Shows manual steps when tools missing

---

## 🔧 Tools Detected by Category

### 1. C# / .NET Tools (HIGHEST PRIORITY)

| Tool | Command | Purpose | Install Command |
|------|---------|---------|----------------|
| dotnet CLI | `dotnet --version` | .NET SDK | Download from microsoft.com |
| dotnet format | `dotnet format` | Code formatter | `dotnet tool install -g dotnet-format` |
| Roslyn analyzers | (via dotnet) | Code analysis | Part of .NET SDK |

**Why First?** User's organization uses C#/.NET Core as primary language.

### 2. JavaScript/TypeScript Tools (HIGH PRIORITY)

| Tool | Command | Purpose | Install Command |
|------|---------|---------|----------------|
| Node.js | `node --version` | Runtime | Download from nodejs.org |
| npm | `npm --version` | Package manager | Included with Node.js |
| ESLint | `npx eslint` | Linter (Angular/React) | `npm install --save-dev eslint` |
| Prettier | `npx prettier` | Formatter | `npm install --save-dev prettier` |

**Why Second?** User's organization uses Angular and React for frontend.

**Note:** ESLint/Prettier checked in **project's node_modules** (zero-footprint - uses what's already there).

### 3. SQL Tools (MEDIUM PRIORITY)

| Tool | Command | Purpose | Install Command |
|------|---------|---------|----------------|
| sqlfluff | `sqlfluff --version` | SQL linter/formatter | `pip install sqlfluff` |

**Why Third?** User's organization uses SQL Server and Oracle databases.

### 4. Python Tools (LOWEST PRIORITY)

| Tool | Command | Purpose | Install Command |
|------|---------|---------|----------------|
| rope | `python -c "import rope"` | Refactoring library | `pip install rope` |
| black | `black --version` | Code formatter | `pip install black` |
| flake8 | `flake8 --version` | Linter | `pip install flake8` |
| mypy | `mypy --version` | Type checker | `pip install mypy` |

**Why Last?** These are for **CORTEX development only**, NOT user's apps!

---

## 📦 Integration Points

### 1. Setup Configuration YAML

**File:** `src/setup/setup_modules.yaml`

**Added Module:**
```yaml
- module_id: refactoring_tools
  name: Refactoring Tools Detection
  description: Detect and optionally install refactoring tools for user's tech stack
  phase: DEPENDENCIES
  priority: 30  # After python_dependencies
  dependencies: [platform_detection]
  optional: true  # User must opt-in
  enabled_by_default: false  # Not forced
  config:
    detect_only: true  # Detection mode by default
    auto_install: false  # Never install without consent
    tech_stacks:
      - csharp  # .NET, C#
      - javascript  # Angular, React
      - sql  # SQL Server, Oracle
      - python  # CORTEX dev only
```

**Execution Phases:**
1. PRE_VALIDATION (10)
2. ENVIRONMENT (20)
3. **DEPENDENCIES (30)** ← Refactoring tools here
4. FEATURES (40)
5. VALIDATION (50)
6. POST_SETUP (60)

### 2. Module Factory Registration

**File:** `src/setup/module_factory.py`

**Added Auto-Registration:**
```python
try:
    from .modules.refactoring_tools_module import RefactoringToolsModule
    register_module_class('refactoring_tools', RefactoringToolsModule)
except ImportError as e:
    logger.warning(f"Could not load RefactoringToolsModule: {e}")
```

### 3. Module Package Export

**File:** `src/setup/modules/__init__.py`

**Added Import:**
```python
from .refactoring_tools_module import RefactoringToolsModule

__all__ = [
    'PlatformDetectionModule',
    'VisionAPIModule',
    'BrainInitializationModule',
    'PythonDependenciesModule',
    'RefactoringToolsModule',  # NEW
]
```

### 4. Setup Profiles

**Updated Profile:** `full`

```yaml
full:
  description: Full setup - all modules including optional features
  modules:
    - project_validation
    - platform_detection
    - git_sync
    - virtual_environment
    - python_dependencies
    - optional_dependencies
    - refactoring_tools  # NEW - Only in full profile
    - vision_api
    - conversation_tracking
    - brain_initialization
    - mkdocs_setup
    - brain_tests
    - tooling_verification
    - setup_completion
```

**Other Profiles:**
- `minimal` - Does NOT include refactoring_tools
- `standard` - Does NOT include refactoring_tools
- `full` - ✅ Includes refactoring_tools

---

## 🚀 How Users Activate It

### Method 1: Full Setup Profile

```
/setup full
```

or

```
setup environment full
```

**Result:** Runs ALL modules including refactoring tools detection.

### Method 2: Explicit Module Enable (Future)

```yaml
# In cortex.config.json (future enhancement)
{
  "setup": {
    "modules": {
      "refactoring_tools": {
        "enabled": true,
        "auto_install": false  # Detection only
      }
    }
  }
}
```

---

## 📊 Execution Flow

### When User Runs `/setup full`

```
1. project_validation → Verify CORTEX structure
2. platform_detection → Detect Mac/Windows/Linux
3. git_sync → Pull latest code
4. virtual_environment → Setup Python venv
5. python_dependencies → Install requirements.txt
6. optional_dependencies → Install extras (pillow, opencv)
7. refactoring_tools → **DETECT TOOLS** ← NEW STEP
   ├─ Check C# tools (dotnet, dotnet format)
   ├─ Check JS tools (node, npm, eslint, prettier)
   ├─ Check SQL tools (sqlfluff)
   └─ Check Python tools (rope, black, flake8, mypy)
8. vision_api → Setup Vision API
9. brain_initialization → Init brain DBs
10. brain_tests → Run validation tests
11. setup_completion → Mark complete
```

---

## 🎯 Example Output

### When Tools Missing (Warning Status)

```
🔍 Detecting refactoring tools for your tech stack...
   (Zero-footprint mode: detection only, no forced installs)

   ✅ dotnet CLI: 8.0.100
   ❌ dotnet format: Not installed
   ✅ Node.js: v18.17.0
   ✅ npm: 9.6.7
   ❌ ESLint (project): Not installed
   ❌ Prettier (project): Not installed
   ❌ sqlfluff: Not installed
   ❌ rope (Python refactoring library): Not installed
   ✅ black (Code formatter): 23.7.0
   ✅ flake8 (Linter): 6.0.0
   ❌ mypy (Type checker): Not installed

⚠️  Refactoring Tools Detection: Some tools missing (4/11 installed)
   Duration: 1,245ms
   
   Guidance for missing tools:
   
   C# Tools:
   - dotnet format: dotnet tool install -g dotnet-format
   
   JavaScript Tools:
   - ESLint (project): npm install --save-dev eslint
   - Prettier (project): npm install --save-dev prettier
   
   SQL Tools:
   - sqlfluff: pip install sqlfluff
   
   Python Tools:
   - rope (Python refactoring library): pip install rope
   - mypy (Type checker): pip install mypy
```

### When All Tools Installed (Success Status)

```
🔍 Detecting refactoring tools for your tech stack...
   (Zero-footprint mode: detection only, no forced installs)

   ✅ dotnet CLI: 8.0.100
   ✅ dotnet format: 8.0.453106
   ✅ Node.js: v18.17.0
   ✅ npm: 9.6.7
   ✅ ESLint (project): 8.45.0
   ✅ Prettier (project): 3.0.0
   ✅ sqlfluff: 2.1.0
   ✅ rope (Python refactoring library): 1.9.0
   ✅ black (Code formatter): 23.7.0
   ✅ flake8 (Linter): 6.0.0
   ✅ mypy (Type checker): 1.4.1

✅ Refactoring Tools Detection: All refactoring tools installed (11/11)
   Duration: 987ms
```

---

## 🔒 Zero-Footprint Guarantees

### What This Module NEVER Does

❌ Install tools without asking  
❌ Force dependencies on users  
❌ Fail setup if tools missing  
❌ Download external packages automatically  
❌ Modify user's global environment  
❌ Install npm packages globally  
❌ Install pip packages globally  

### What This Module ALWAYS Does

✅ Detect existing tools first  
✅ Use what's already installed  
✅ Check project-local node_modules (not global)  
✅ Provide clear installation guidance  
✅ Respect organizational firewalls  
✅ Succeed with warnings (not failures)  
✅ Update context with detected tools  

---

## 🧪 Testing Recommendations

### Unit Tests Needed

**File:** `tests/setup/test_refactoring_tools_module.py`

```python
def test_detect_csharp_tools_when_dotnet_installed():
    """Verify C# tools detected when dotnet CLI available."""
    # Mock: shutil.which('dotnet') returns path
    # Assert: dotnet CLI marked as installed
    
def test_detect_csharp_tools_when_dotnet_missing():
    """Verify guidance provided when dotnet CLI missing."""
    # Mock: shutil.which('dotnet') returns None
    # Assert: dotnet CLI marked as NOT installed
    # Assert: Guidance includes download link

def test_detect_javascript_tools_local_node_modules():
    """Verify ESLint detected in project's node_modules."""
    # Mock: project_root/node_modules/eslint exists
    # Assert: ESLint marked as installed (local)
    
def test_zero_footprint_no_installations():
    """Verify module NEVER installs without consent."""
    # Mock: all tools missing
    # Assert: No subprocess.run calls with 'install'
    # Assert: Only detection commands executed

def test_tech_stack_priority_order():
    """Verify C# checked first, Python last."""
    # Assert: detected_tools['csharp'] processed before ['python']
```

### Integration Tests Needed

```python
def test_full_setup_profile_includes_refactoring_tools():
    """Verify 'full' profile includes refactoring tools module."""
    # Load setup_modules.yaml
    # Assert: 'refactoring_tools' in profiles['full']['modules']

def test_standard_profile_excludes_refactoring_tools():
    """Verify 'standard' profile excludes refactoring tools (opt-in)."""
    # Load setup_modules.yaml
    # Assert: 'refactoring_tools' NOT in profiles['standard']['modules']

def test_module_succeeds_with_warnings_when_tools_missing():
    """Verify module doesn't fail when tools missing."""
    # Mock: All tools return None
    # Execute: module.execute(context)
    # Assert: result.status == SetupStatus.WARNING (not FAILED)
```

---

## 📝 Documentation Updates Needed

### 1. Setup Guide

**File:** `prompts/shared/setup-guide.md`

**Add Section:**
```markdown
## Refactoring Tools Detection (Optional)

CORTEX can detect and help you install refactoring tools for your tech stack.

**Detected Tools:**
- C# / .NET: dotnet format, Roslyn analyzers
- JavaScript/TypeScript: ESLint, Prettier
- SQL: sqlfluff
- Python: rope, black, flake8, mypy

**Enable during setup:**
```
/setup full
```

**Zero-footprint:** Only detects tools, never installs without asking.
```

### 2. Technical Reference

**File:** `prompts/shared/technical-reference.md`

**Add API Documentation:**
```markdown
### RefactoringToolsModule API

**Module ID:** `refactoring_tools`

**Purpose:** Detect refactoring tools for user's tech stack

**Methods:**
- `execute(context)` - Detect all tools, return results
- `_detect_csharp_tools(context)` - C# / .NET tools
- `_detect_javascript_tools(project_root)` - JS/TS tools
- `_detect_sql_tools(context)` - SQL tools
- `_detect_python_tools(context)` - Python tools

**Context Requirements:**
- `project_root` (Path) - CORTEX root directory
- `platform` (str) - Current platform (win32, darwin, linux)
- `python_command` (str) - Python executable path

**Context Updates:**
- `refactoring_tools_detected` (bool) - Detection completed
- `detected_tools` (dict) - All detected tools by category
- `installed_tools_count` (int) - Number of installed tools
- `missing_tools_count` (int) - Number of missing tools
```

---

## 🎯 Next Steps for User

### Immediate Actions

1. **Run Full Setup:**
   ```
   /setup full
   ```
   
2. **Review Detected Tools:**
   - Check which tools are installed
   - Note missing tools in output
   
3. **Install Missing Tools (Optional):**
   - Follow guidance provided by module
   - Install only tools you need
   - Skip tools blocked by org firewall

### Future Enhancements (Not Implemented Yet)

1. **Interactive Installation:**
   ```
   Would you like to install dotnet format? [y/n]
   ```
   
2. **Per-Tool Configuration:**
   ```yaml
   refactoring_tools:
     csharp:
       dotnet_format: auto  # auto | manual | skip
     javascript:
       eslint: auto
   ```
   
3. **Org Firewall Profiles:**
   ```yaml
   firewall_profile: strict  # permissive | moderate | strict
   ```

---

## 🏆 Success Criteria

### ✅ Implementation Complete

- [x] Zero-footprint architecture (detection only)
- [x] Tech stack priority (C# > JS > SQL > Python)
- [x] Graceful degradation (warnings, not failures)
- [x] Guidance-based fallback
- [x] Optional module (disabled by default)
- [x] Integrated with setup orchestrator
- [x] Registered in module factory
- [x] Added to full profile only

### ⏳ Pending (Future Work)

- [ ] Unit tests (test_refactoring_tools_module.py)
- [ ] Integration tests (setup orchestrator)
- [ ] Documentation updates (setup guide, technical reference)
- [ ] User consent for installations
- [ ] Per-tool configuration
- [ ] Firewall profile support

---

## 📚 Related Documents

- **Strategy:** `cortex-brain/REFACTORING-STRATEGY-REVISED.md` - Overall refactoring approach
- **Analysis:** `cortex-brain/CODE-REFACTORING-STRATEGY-ANALYSIS.md` - Initial analysis
- **Setup YAML:** `src/setup/setup_modules.yaml` - Module configuration
- **Base Module:** `src/setup/base_setup_module.py` - Module interface
- **Module Factory:** `src/setup/module_factory.py` - Registration system

---

**Status:** ✅ READY FOR TESTING  
**Next Action:** Run `/setup full` and verify tool detection works

**Implementation:** Asif Hussain  
**Date:** 2025-11-12
