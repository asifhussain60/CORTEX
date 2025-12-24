# User Path Configuration Guide

**Version:** 3.8.0  
**Feature:** Customizable File Paths for Tests and Documents  
**Author:** Asif Hussain  
**Updated:** 2025-12-04

---

## 🎯 Overview

CORTEX now supports **user-configurable paths** for test files and generated documents. This allows you to:

✅ **Customize test directory** - Choose where application tests are created  
✅ **Configure document locations** - Control where CORTEX stores reports, analysis, and summaries  
✅ **Multi-language support** - Path configuration integrates with existing 12-language support  
✅ **Auto-detection** - CORTEX scans your repository and suggests optimal paths  
✅ **Flexible structure** - Support for flat or nested test directories  

---

## 📋 Configuration Schema

### User Path Configuration

```json
{
  "user_paths": {
    "test_directory": "tests",
    "reports_directory": "cortex-brain/documents/reports",
    "documents_directory": "cortex-brain/documents",
    "planning_directory": "cortex-brain/documents/planning",
    "analysis_directory": "cortex-brain/documents/analysis",
    "summaries_directory": "cortex-brain/documents/summaries",
    "investigations_directory": "cortex-brain/documents/investigations",
    "temp_directory": ".cortex-temp",
    "custom_paths": {
      "logs": "logs",
      "screenshots": "test-screenshots"
    }
  }
}
```

### Field Descriptions

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `test_directory` | string | `"tests"` | Where application tests are created |
| `reports_directory` | string | `"cortex-brain/documents/reports"` | Validation and status reports |
| `documents_directory` | string | `"cortex-brain/documents"` | Base directory for CORTEX documents |
| `planning_directory` | string | `"cortex-brain/documents/planning"` | Feature plans and ADO work items |
| `analysis_directory` | string | `"cortex-brain/documents/analysis"` | Code and architecture analysis |
| `summaries_directory` | string | `"cortex-brain/documents/summaries"` | Project summaries and progress |
| `investigations_directory` | string | `"cortex-brain/documents/investigations"` | Bug investigations |
| `temp_directory` | string | `".cortex-temp"` | Temporary files |
| `custom_paths` | object | `{}` | User-defined paths |

---

## 🚀 Interactive Setup

### During CORTEX Setup

```bash
# Run CORTEX setup (includes path configuration)
python -m src.setup.setup_wizard

# Path configuration is part of the setup process:
# 1. User profile questions (name, language, preferences)
# 2. Path configuration (test directory, documents)
# 3. Environment setup
```

### Standalone Path Configuration

```bash
# Configure paths without full setup
python -m src.setup.modules.path_config_questionnaire
```

### Interactive Flow

```
📁 CORTEX Path Configuration
============================================================

🔍 Scanning repository structure...

📋 Application Test Directory Configuration
   (Where should CORTEX create/find your application tests?)

   ℹ️  Found 1 test directory:
   1. tests (pytest) - 45 tests (confidence: 95%)
   2. Use suggested path ('tests')
   3. Specify custom path

   Choice (1-3, default: 1): 1

📄 Document directories can be customized or use defaults.
   Customize document paths? [y/N]: n

✅ Path Configuration Complete
============================================================
   Test Directory:          tests
   Reports:                 cortex-brain/documents/reports
   Analysis:                cortex-brain/documents/analysis
   Summaries:               cortex-brain/documents/summaries
   Planning:                cortex-brain/documents/planning
   Investigations:          cortex-brain/documents/investigations
   Temp Files:              .cortex-temp
============================================================
```

---

## 🔍 Auto-Detection

CORTEX automatically scans your repository to detect:

### Test Directory Detection

**Patterns Searched:**
- `tests/`
- `test/`
- `__tests__/`
- `Tests/`
- `spec/`

**Scoring Factors:**
- Directory name match (higher score for exact matches)
- Number of test files found
- Presence of test framework config (pytest.ini, jest.config.js, etc.)
- Framework detection (pytest, Jest, xUnit, unittest)

**Example Detection:**

```python
from src.setup.modules.path_detector import PathDetector

detector = PathDetector("/path/to/repo")
test_dirs = detector.find_test_directories()

# Results:
# [
#   {
#     "path": "tests",
#     "absolute_path": "/path/to/repo/tests",
#     "test_count": 45,
#     "framework": "pytest",
#     "confidence": 0.95
#   }
# ]
```

### Framework-Specific Suggestions

| Project Type | Suggested Test Directory |
|--------------|--------------------------|
| Python (pytest) | `tests/` |
| JavaScript/TypeScript (Jest) | `__tests__/` |
| C# (xUnit) | `Tests/` |
| Unknown | `tests/` |

---

## 💻 Programmatic Usage

### Load Path Configuration

```python
from src.setup.modules.user_profile_storage import UserProfileStorage

storage = UserProfileStorage()
path_config = storage.load_path_config()

if path_config:
    print(f"Test directory: {path_config.test_directory}")
    print(f"Reports directory: {path_config.reports_directory}")
```

### Resolve Paths

```python
from src.setup.modules.path_resolver import PathResolver

resolver = PathResolver(workspace_root="/path/to/repo")

# Get test directory
test_dir = resolver.get_test_directory(create=True)
print(f"Tests will be created in: {test_dir}")

# Get document path
report_path = resolver.get_document_path(
    filename="validation-report.md",
    category="reports"
)
print(f"Report will be saved to: {report_path}")

# Get custom path
logs_dir = resolver.get_custom_path("logs", create=True)
```

### TDD Workflow Integration

```python
from src.setup.modules.tdd_path_adapter import TDDWorkflowPathAdapter

adapter = TDDWorkflowPathAdapter(workspace_root="/path/to/repo")

# Get test path for source file
source_file = "src/login.py"
test_path = adapter.get_test_path_for_source(source_file)
# Returns: "/path/to/repo/tests/test_login.py"

# Check if file is a test
is_test = adapter.is_test_file("tests/test_login.py")
# Returns: True

# Find source for test
source = adapter.get_source_for_test("tests/test_login.py")
# Returns: "/path/to/repo/src/login.py"
```

---

## 🛠️ Manual Configuration

### Edit cortex.config.json Directly

```json
{
  "version": "3.8.0",
  "user": {
    "name": "Your Name",
    "preference": "balanced",
    "role": "intermediate",
    "work_area": "backend",
    "language": "en"
  },
  "user_paths": {
    "test_directory": "__tests__",
    "reports_directory": "docs/cortex/reports",
    "documents_directory": "docs/cortex",
    "planning_directory": "docs/cortex/planning",
    "analysis_directory": "docs/cortex/analysis",
    "summaries_directory": "docs/cortex/summaries",
    "investigations_directory": "docs/cortex/investigations",
    "temp_directory": ".temp",
    "custom_paths": {
      "logs": "logs/cortex",
      "screenshots": "test-results/screenshots"
    }
  }
}
```

### Create Configuration Programmatically

```python
from src.setup.models.user_path_config import UserPathConfig
from src.setup.modules.user_profile_storage import UserProfileStorage

# Create configuration
config = UserPathConfig(
    test_directory="__tests__",
    reports_directory="docs/cortex/reports",
    documents_directory="docs/cortex",
    planning_directory="docs/cortex/planning",
    analysis_directory="docs/cortex/analysis",
    summaries_directory="docs/cortex/summaries",
    investigations_directory="docs/cortex/investigations",
    temp_directory=".temp",
    custom_paths={
        "logs": "logs/cortex",
        "screenshots": "test-results/screenshots"
    }
)

# Save to config file
storage = UserProfileStorage()
storage.save_path_config(config)
```

---

## 📐 Path Resolution Rules

### Relative vs Absolute Paths

- **Relative paths** are resolved relative to workspace root
- **Absolute paths** are used as-is

**Example:**
```python
# Workspace root: /home/user/project

# Relative path
test_directory: "tests"
# Resolved to: /home/user/project/tests

# Absolute path
test_directory: "/opt/shared-tests"
# Resolved to: /opt/shared-tests
```

### Directory Structure Preservation

For nested source files, CORTEX preserves directory structure:

```
Source:     src/models/user.py
Test:       tests/models/test_user.py

Source:     app/controllers/auth/login.py
Test:       tests/controllers/auth/test_login.py
```

### Automatic Directory Creation

Directories are created automatically when:
- Using `create=True` parameter
- Writing files to non-existent paths
- Running TDD workflow

**Python Projects:**
- `__init__.py` files are created in test directories automatically

---

## 🔧 Integration with Existing Systems

### TDD Mastery Workflow

The TDD Mastery workflow automatically uses configured paths:

```python
# TDD workflow respects user configuration
# No changes needed to your workflow!

from src.workflows.tdd_workflow_orchestrator import TDDWorkflowOrchestrator

orchestrator = TDDWorkflowOrchestrator(workspace_root="/path/to/repo")

# Tests are created in user-configured directory
orchestrator.start_red_phase(source_file="src/login.py")
# Test created in: {user_paths.test_directory}/test_login.py
```

### Document Generation

All CORTEX document generation respects path configuration:

```python
# Reports go to configured location
from src.setup.modules.path_resolver import resolve_document_path

report_path = resolve_document_path(
    category="reports",
    filename="validation-report.md"
)
# Uses: {user_paths.reports_directory}/validation-report.md
```

---

## ⚙️ Advanced Configuration

### Custom Paths

Add your own custom paths for specific needs:

```json
{
  "user_paths": {
    "test_directory": "tests",
    "custom_paths": {
      "integration_tests": "tests/integration",
      "e2e_tests": "tests/e2e",
      "fixtures": "tests/fixtures",
      "mocks": "tests/mocks",
      "logs": "logs/cortex",
      "screenshots": "test-results/screenshots",
      "performance_reports": "docs/performance"
    }
  }
}
```

**Usage:**

```python
from src.setup.modules.path_resolver import PathResolver

resolver = PathResolver()
integration_dir = resolver.get_custom_path("integration_tests", create=True)
fixtures_dir = resolver.get_custom_path("fixtures", create=True)
```

### Per-Machine Configuration

Path configuration is stored in `cortex.config.json`, which is:
- ❌ **Not committed to Git** (in `.gitignore`)
- ✅ **Machine-specific**
- ✅ **User-specific**

Each developer can have different path preferences!

---

## 🧪 Validation and Testing

### Validate Configuration

```python
from src.setup.modules.path_resolver import PathResolver

resolver = PathResolver()
results = resolver.validate_configuration()

print(f"Valid: {results['valid']}")
print(f"Warnings: {results['warnings']}")
print(f"Errors: {results['errors']}")
```

### Test Setup Validation

```python
from src.setup.modules.tdd_path_adapter import TDDWorkflowPathAdapter

adapter = TDDWorkflowPathAdapter("/path/to/repo")
validation = adapter.validate_test_setup()

if validation["valid"]:
    print("✅ Test setup is valid")
else:
    print("❌ Test setup has errors:")
    for error in validation["errors"]:
        print(f"  - {error}")
```

---

## 📚 Best Practices

### 1. Use Relative Paths

```json
// ✅ Good - Portable across machines
"test_directory": "tests"

// ❌ Avoid - Machine-specific
"test_directory": "/home/user/project/tests"
```

### 2. Follow Project Conventions

Match your project's existing structure:

```
Python project with pytest → tests/
JavaScript project with Jest → __tests__/
C# project with xUnit → Tests/
```

### 3. Keep CORTEX Documents Separate

```json
// ✅ Good - Isolated from application code
"reports_directory": "cortex-brain/documents/reports"

// ⚠️  Caution - Mixed with application code
"reports_directory": "docs/reports"
```

### 4. Use Auto-Detection

Let CORTEX scan and suggest paths during setup:
- Analyzes existing structure
- Detects test frameworks
- Calculates confidence scores
- Suggests optimal defaults

---

## 🐛 Troubleshooting

### Issue: Test Directory Not Found

**Solution:**
```python
from src.setup.modules.path_resolver import PathResolver

resolver = PathResolver()
test_dir = resolver.get_test_directory(create=True)
# Directory will be created automatically
```

### Issue: Permission Denied

**Check:**
- Write permissions on target directory
- Disk space availability
- Parent directory exists

**Validate:**
```python
from src.setup.modules.tdd_path_adapter import TDDWorkflowPathAdapter

adapter = TDDWorkflowPathAdapter("/path/to/repo")
validation = adapter.validate_test_setup()
print(validation["errors"])
```

### Issue: Path Configuration Not Loaded

**Check:**
1. `cortex.config.json` exists
2. File has valid JSON
3. `user_paths` section present

**Reload:**
```python
from src.setup.modules.user_profile_storage import UserProfileStorage

storage = UserProfileStorage()
config = storage.load_path_config()

if not config:
    # Run setup to create configuration
    from src.setup.modules.path_config_questionnaire import PathConfigQuestionnaire
    questionnaire = PathConfigQuestionnaire()
    config = questionnaire.run()
    storage.save_path_config(config)
```

---

## 🔗 Related Documentation

- **User Profile System:** `.github/prompts/modules/user-profiling-guide.md`
- **TDD Mastery:** `.github/prompts/modules/tdd-mastery-guide.md`
- **Setup Guide:** `docs/SETUP-CORTEX.md`
- **Multi-language Support:** `cortex-brain/documents/planning/MULTILINGUAL-SUPPORT-SUMMARY.md`

---

## 📝 Schema Reference

### UserPathConfig Model

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict

class UserPathConfig(BaseModel):
    test_directory: Optional[str] = Field(default=None)
    reports_directory: Optional[str] = Field(default="cortex-brain/documents/reports")
    documents_directory: Optional[str] = Field(default="cortex-brain/documents")
    planning_directory: Optional[str] = Field(default="cortex-brain/documents/planning")
    analysis_directory: Optional[str] = Field(default="cortex-brain/documents/analysis")
    summaries_directory: Optional[str] = Field(default="cortex-brain/documents/summaries")
    investigations_directory: Optional[str] = Field(default="cortex-brain/documents/investigations")
    temp_directory: Optional[str] = Field(default=None)
    custom_paths: Dict[str, str] = Field(default_factory=dict)
```

---

**Version:** 3.8.0  
**Last Updated:** 2025-12-04  
**Author:** Asif Hussain
