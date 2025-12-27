# CORTEX Toolkit Documentation

**Version:** 1.0.0  
**Last Updated:** December 27, 2025  
**Total Tools:** 57 Python Scripts  
**Status:** ✅ Production Ready

---

## 📚 Table of Contents

1. [Overview](#overview)
2. [Directory Structure](#directory-structure)
3. [Tool Categories](#tool-categories)
4. [Installation & Setup](#installation--setup)
5. [Usage Examples](#usage-examples)
6. [API Reference](#api-reference)
7. [Development Guide](#development-guide)
8. [Troubleshooting](#troubleshooting)
9. [HTML Tools Guide](#html-tools-guide) ⭐ NEW

---

## 🎯 Overview

The **CORTEX Toolkit** is a comprehensive collection of 57 Python tools organized into 8 categories, providing cross-repository functionality for brain operations, system maintenance, planning, analytics, documentation quality, and more.

### Key Features

- **Cross-Repository Support**: Use tools from any CORTEX-aware repository
- **Unified Registry**: Single `toolkit_registry.py` for discovery and invocation
- **Platform Support**: Windows, Linux, macOS compatible
- **Modular Architecture**: Clean separation of concerns with 8 logical categories
- **CLI Wrappers**: Consistent interface for all system operations

### Architecture Principles

1. **Single Source of Truth**: All toolkit code lives in `cortex-toolkit/`
2. **Relative Imports**: Tools use relative imports for portability
3. **Registry-Based Discovery**: `toolkit-manifest.yaml` defines all tools
4. **Execution Methods**: Three types (cli_wrapper, copilot_chat, cli)

---

## 📂 Directory Structure

```
cortex-toolkit/
├── VERSION                         # Version file (1.0.0)
├── toolkit-manifest.yaml           # Tool registry manifest
├── README.md                       # Main documentation
├── TOOLS-INVENTORY.md              # Detailed tool inventory
├── FOLDER-STRUCTURE.md             # Structure documentation
│
├── analytics/                      # Analytics & Monitoring (7 tools)
│   ├── metrics/                    # 2 tools (dashboard data, brain health)
│   ├── profiling/                  # 2 tools (performance, startup)
│   └── visualization/              # 3 tools (graphs, UML, brain health viz)
│
├── cli/                            # CLI Infrastructure
│   └── wrappers/                   # 20 CLI wrappers
│       ├── __init__.py
│       ├── base_wrapper.py         # ✅ Base class for all wrappers
│       ├── align_wrapper.py
│       ├── cleanup_wrapper.py
│       ├── deploy_wrapper.py
│       ├── healthcheck_wrapper.py
│       ├── optimize_wrapper.py
│       ├── regenerate_prompts_wrapper.py
│       ├── review_wrapper.py
│       ├── sanitize_wrapper.py
│       ├── extract_schemas_wrapper.py
│       ├── generate_legacy_specs_wrapper.py
│       ├── generate_ra_specs_v4_wrapper.py
│       └── generate_ra_specs.py
│
├── core/                           # Core Functionality (17 tools)
│   ├── brain/                      # 4 brain operations
│   │   ├── align.py
│   │   ├── cleanup.py
│   │   ├── healthcheck.py
│   │   └── optimize.py
│   ├── generators/                 # 5 generator tools
│   │   ├── __init__.py
│   │   ├── narrative_validator.py
│   │   ├── openapi_generator_v4.py
│   │   ├── schema_extractor.py
│   │   └── schema_registry.py
│   ├── operations/                 # 3 system operations
│   │   ├── deploy.py
│   │   ├── review.py
│   │   └── sanitize.py
│   ├── planning/                   # 3 planning tools
│   │   ├── ado_manager.py
│   │   ├── plan_generator.py
│   │   └── planning_file_manager.py
│   └── utilities/                  # 2 utility tools
│       ├── measure_prompt_tokens.py
│       └── version_manager.py
│
├── documentation/                  # Documentation Tools (3 tools)
│   ├── generate_docs_from_code.py
│   ├── generate_quick_reference.py
│   └── regenerate_prompts.py
│
├── install/                        # Installation Scripts
│   ├── install-toolkit.ps1         # Windows installer
│   ├── install-toolkit.sh          # Linux/macOS installer
│   └── verify-installation.py      # Verification script
│
├── maintenance/                    # Maintenance Tools (3 tools)
│   ├── cleanup_temp_files.py
│   ├── detect_duplicates.py
│   └── master_cleanup.py
│
├── migration/                      # Migration Tools (2 tools)
│   ├── schema_migrator.py
│   └── version_detector.py
│
├── shared/                         # Shared Libraries (4 modules)
│   ├── __init__.py
│   ├── config.py                   # Configuration management
│   ├── logging_config.py           # Logging setup
│   └── toolkit_registry.py         # ✅ Main registry (discovery & invocation)
│
├── testing/                        # Testing Tools (3 tools)
│   ├── generate_performance_tests.py
│   ├── validate_deployment.py
│   └── verify_no_mocks.py
│
└── tests/                          # Test Suite
```

**Total File Count:** 55 Python scripts + supporting files

---

## 🔧 Tool Categories

### 1. Brain Operations (4 tools)

Core CORTEX brain tier operations.

| Tool | Command | File | Description |
|------|---------|------|-------------|
| align | `cortex-align` | `core/brain/align.py` | System alignment checks |
| healthcheck | `cortex-health` | `core/brain/healthcheck.py` | Health diagnostics |
| optimize | `cortex-optimize` | `core/brain/optimize.py` | Performance tuning |
| cleanup | `cortex-cleanup` | `core/brain/cleanup.py` | System cleanup |

### 2. System Operations (3 tools)

Critical system operations with CLI wrappers.

| Tool | Command | File | Description |
|------|---------|------|-------------|
| review | `cortex-review` | `core/operations/review.py` | Code review orchestration |
| deploy | `cortex-deploy` | `core/operations/deploy.py` | Deployment to publish |
| sanitize | `cortex-sanitize` | `core/operations/sanitize.py` | Code sanitization |

### 3. Planning Tools (3 tools)

Feature planning and ADO management.

| Tool | Command | File | Description |
|------|---------|------|-------------|
| plan | `cortex-plan` | `core/planning/plan_generator.py` | Generate implementation plans |
| ado | `cortex-ado` | `core/planning/ado_manager.py` | Azure DevOps work items |
| planning-file-manager | `cortex-pfm` | `core/planning/planning_file_manager.py` | Manage planning files |

### 4. Analytics (7 tools)

Performance profiling, metrics collection, and visualization.

**Metrics (2 tools):**
- `analytics/metrics/collect_dashboard_data.py` - Collect dashboard data
- `analytics/metrics/monitor_brain_health.py` - Monitor brain health

**Profiling (2 tools):**
- `analytics/profiling/profile_performance.py` - Performance profiling
- `analytics/profiling/profile_startup.py` - Startup profiling

**Visualization (3 tools):**
- `analytics/visualization/dependency_graph_generator.py` - Generate dependency graphs
- `analytics/visualization/generate_uml_standalone.py` - Generate UML diagrams
- `analytics/visualization/visualize_brain_health.py` - Visualize brain health

### 5. Documentation (5 tools)

Automated documentation generation and HTML quality assurance.

**Documentation Generators (3 tools):**
- `documentation/generate_docs_from_code.py` - Generate docs from code
- `documentation/generate_quick_reference.py` - Generate quick references
- `documentation/regenerate_prompts.py` - Regenerate prompt files

**HTML Quality Tools (2 tools):**
- `documentation/html-tools/html_style_centralizer.py` - **HTML Style Centralizer**: Removes inline CSS styles from HTML files and moves them to centralized stylesheets. Improves maintainability by ensuring 100% CSS centralization per docgen.prompt.md standards.
- `documentation/html-tools/html_validator.py` - **HTML Validator**: Validates HTML syntax, checks for unclosed tags, malformed attributes, and structural issues. Ensures all documentation pages are syntactically correct.

### 6. Testing (3 tools)

Test generation and validation.

- `testing/generate_performance_tests.py` - Generate performance tests
- `testing/validate_deployment.py` - Validate deployments
- `testing/verify_no_mocks.py` - Verify no mock objects

### 7. Migration (2 tools)

Schema migration and version management.

- `migration/schema_migrator.py` - Migrate database schemas
- `migration/version_detector.py` - Detect toolkit version

### 8. Maintenance (3 tools)

System maintenance and cleanup.

- `maintenance/cleanup_temp_files.py` - Clean temporary files
- `maintenance/detect_duplicates.py` - Detect duplicate files
- `maintenance/master_cleanup.py` - Master cleanup orchestrator

### 9. Generators (5 tools)

Schema and OpenAPI generation.

- `core/generators/narrative_validator.py` - Validate narratives
- `core/generators/openapi_generator_v4.py` - Generate OpenAPI specs
- `core/generators/schema_extractor.py` - Extract schemas
- `core/generators/schema_registry.py` - Schema registry

### 10. CLI Wrappers (20 tools)

Unified CLI wrapper infrastructure.

**Base Infrastructure:**
- `cli/wrappers/base_wrapper.py` - ✅ Base class for all wrappers
- `cli/wrappers/__init__.py` - Package exports

**Core Wrappers (7):**
- `align_wrapper.py`, `cleanup_wrapper.py`, `deploy_wrapper.py`
- `healthcheck_wrapper.py`, `optimize_wrapper.py`
- `regenerate_prompts_wrapper.py`, `review_wrapper.py`

**Specialized Wrappers (12):**
- `sanitize_wrapper.py`, `extract_schemas_wrapper.py`
- `generate_legacy_specs_wrapper.py`, `generate_ra_specs_v4_wrapper.py`
- `generate_ra_specs.py`, and more...

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8+
- CORTEX repository cloned locally

### Installation

**Option 1: Windows (PowerShell)**
```powershell
# Navigate to CORTEX root
cd D:\PROJECTS\CORTEX

# Run installer
.\cortex-toolkit\install\install-toolkit.ps1

# With PowerShell profile integration
.\cortex-toolkit\install\install-toolkit.ps1 -UserProfile
```

**Option 2: Linux/macOS (Bash)**
```bash
# Navigate to CORTEX root
cd ~/PROJECTS/CORTEX

# Run installer
bash cortex-toolkit/install/install-toolkit.sh

# With shell profile integration
bash cortex-toolkit/install/install-toolkit.sh --shell-profile
```

### Verification

```bash
# Verify installation
python cortex-toolkit/install/verify-installation.py

# List all tools
python cortex-toolkit/shared/toolkit_registry.py list
```

---

## 💻 Usage Examples

### Example 1: List All Tools

```bash
# List all categories
python cortex-toolkit/shared/toolkit_registry.py categories

# List all tools
python cortex-toolkit/shared/toolkit_registry.py list

# List tools in specific category
python cortex-toolkit/shared/toolkit_registry.py list brain_operations
```

### Example 2: Get Tool Information

```bash
# Get detailed tool info
python cortex-toolkit/shared/toolkit_registry.py info align

# Output:
# Tool: align
# Command: cortex-align
# Description: System alignment and consistency checks
# Script: core/brain/align.py
# Wrapper: cli/wrappers/align_wrapper.py
# Platforms: windows, linux, macos
```

### Example 3: Invoke Tools

```bash
# Using registry (recommended)
python cortex-toolkit/shared/toolkit_registry.py invoke align --check-only

# Using direct path
python cortex-toolkit/core/brain/align.py --check-only

# Using CLI wrapper
python cortex-toolkit/cli/wrappers/align_wrapper.py --check-only
```

### Example 4: HTML Documentation Quality

**For Non-Technical Users:**

These tools help keep your HTML documentation clean and error-free. Think of them like spell-checkers for your web pages - they find and fix common problems automatically.

**HTML Style Centralizer** - Cleans up messy inline styles:
```bash
# What it does: Moves all style="..." attributes to a central CSS file
# Why: Makes your website easier to update (change colors in one place, not 100 places)
# When to use: After creating new HTML pages or before publishing documentation

python cortex-toolkit/documentation/html-tools/html_style_centralizer.py

# Expected output:
# ✅ features/tdd-mastery.html: 88 inline styles removed
# ✅ architecture/agent-system.html: 254 inline styles removed
# Files Modified: 37
# Inline Styles Removed: 2,488
```

**HTML Validator** - Checks for broken HTML:
```bash
# What it does: Finds missing closing tags, broken links, syntax errors
# Why: Prevents "broken" pages that don't display correctly in browsers
# When to use: Before deploying documentation, after bulk edits

python cortex-toolkit/documentation/html-tools/html_validator.py

# Expected output:
# ✅ Valid: 48/50 files
# ⚠️  Valid with Warnings: 2 files (duplicate class attributes - safe to ignore)
# ❌ Invalid: 0 files
# 
# 🎉 ALL HTML FILES ARE SYNTACTICALLY CORRECT!
```

**For Technical Users:**

```bash
# Style Centralizer - Remove inline styles, preserve exceptions
python cortex-toolkit/documentation/html-tools/html_style_centralizer.py

# Features:
# - HTMLParser-based (safe, structure-preserving)
# - Preserves story/viewer.html interactive styles
# - Preserves D3.js dynamic template literals
# - Creates reusable CSS classes in main.css
# - Backup via git (reversible)

# Validator - Comprehensive HTML5 validation
python cortex-toolkit/documentation/html-tools/html_validator.py

# Features:
# - Tag stack tracking (opening/closing validation)
# - Self-closing tag verification (<br/>, <img/>)
# - Attribute syntax validation
# - Nesting structure checks
# - Duplicate attribute detection
# - Line-by-line error reporting
```

### Example 5: System Health Check

```bash
# Run health check
python cortex-toolkit/shared/toolkit_registry.py invoke healthcheck

# With specific tiers
python cortex-toolkit/cli/wrappers/healthcheck_wrapper.py --tier1 --tier2
```

### Example 5: Cross-Repository Usage

```bash
# From KSESSIONS repository
cd ~/PROJECTS/KSESSIONS
python ~/PROJECTS/CORTEX/cortex-toolkit/shared/toolkit_registry.py invoke healthcheck

# From NOOR CANVAS repository
cd ~/PROJECTS/NOOR-CANVAS
python ~/PROJECTS/CORTEX/cortex-toolkit/shared/toolkit_registry.py invoke align
```

---

## 📖 API Reference

### ToolkitRegistry Class

Located in: `cortex-toolkit/shared/toolkit_registry.py`

```python
from pathlib import Path
import sys

# Add toolkit to path
toolkit_root = Path("~/PROJECTS/CORTEX/cortex-toolkit").expanduser()
sys.path.insert(0, str(toolkit_root / "shared"))

from toolkit_registry import ToolkitRegistry

# Initialize registry
registry = ToolkitRegistry()
```

#### Methods

**`list_categories() -> List[str]`**
Returns list of all tool categories.

**`list_tools(category: Optional[str] = None) -> List[Dict]`**
Returns list of tools, optionally filtered by category.

**`get_tool(name: str) -> Optional[Dict]`**
Get information about a specific tool.

**`resolve_script_path(tool_name: str) -> Optional[Path]`**
Resolve absolute path to tool script.

**`resolve_wrapper_path(tool_name: str) -> Optional[Path]`**
Resolve absolute path to CLI wrapper.

**`is_platform_supported(tool_name: str) -> bool`**
Check if tool is supported on current platform.

**`invoke_tool(tool_name: str, args: List[str] = None) -> int`**
Invoke tool and return exit code.

#### Usage Example

```python
from toolkit_registry import ToolkitRegistry

registry = ToolkitRegistry()

# List all tools
tools = registry.list_tools()
for tool in tools:
    print(f"{tool['name']}: {tool['description']}")

# Get tool info
tool_info = registry.get_tool("align")
print(tool_info)

# Check platform support
if registry.is_platform_supported("align"):
    # Invoke tool
    exit_code = registry.invoke_tool("align", ["--check-only"])
    print(f"Exit code: {exit_code}")
```

---

## 🛠️ Development Guide

### Adding a New Tool

**Step 1: Create the Tool Script**

```python
# cortex-toolkit/core/utilities/my_tool.py
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="My useful tool")
    parser.add_argument("--option", help="An option")
    args = parser.parse_args()
    
    # Tool logic here
    print(f"Running my tool with option: {args.option}")
    return 0

if __name__ == "__main__":
    exit(main())
```

**Step 2: Register in Manifest**

Edit `cortex-toolkit/toolkit-manifest.yaml`:

```yaml
utilities:
  description: Utility tools
  tools:
    - name: my-tool
      command: cortex-mytool
      script: core/utilities/my_tool.py
      description: Does something useful
      platforms: [windows, linux, macos]
      requires_admin: false
      execution_method: cli
```

**Step 3: Create CLI Wrapper (Optional)**

```python
# cortex-toolkit/cli/wrappers/my_tool_wrapper.py
from .base_wrapper import BaseCLIWrapper, main_template

class MyToolWrapper(BaseCLIWrapper):
    def get_operation_name(self) -> str:
        return "my-tool"
    
    def get_orchestrator(self):
        # Return orchestrator instance
        pass

if __name__ == "__main__":
    main_template(MyToolWrapper)
```

**Step 4: Test**

```bash
# Test tool directly
python cortex-toolkit/core/utilities/my_tool.py --option test

# Test via registry
python cortex-toolkit/shared/toolkit_registry.py invoke my-tool --option test
```

### Import Guidelines

**✅ DO:**
- Use relative imports within same category: `from .base_wrapper import BaseCLIWrapper`
- Use absolute imports from shared: `from pathlib import Path`
- Add toolkit to path in standalone scripts

**❌ DON'T:**
- Import from `scripts.*` (deprecated)
- Use `cortex_toolkit.*` absolute imports (not installed as package)
- Cross-category relative imports (use sys.path manipulation)

### Testing

```bash
# Run all toolkit tests
pytest cortex-toolkit/tests/

# Run specific test
pytest cortex-toolkit/tests/test_toolkit_registry.py

# With coverage
pytest --cov=cortex-toolkit cortex-toolkit/tests/
```

---

## 🆘 Troubleshooting

### Tool Not Found

**Problem:** `ToolkitRegistry` cannot find a tool.

**Solution:**
```bash
# Verify installation
python cortex-toolkit/install/verify-installation.py

# Check manifest
python cortex-toolkit/shared/toolkit_registry.py list

# Verify tool exists in manifest
grep "my-tool" cortex-toolkit/toolkit-manifest.yaml
```

### Import Errors

**Problem:** `ModuleNotFoundError` when running tool.

**Solution:**
```python
# Add toolkit to path at top of script
import sys
from pathlib import Path

toolkit_root = Path(__file__).parent.parent  # Adjust as needed
sys.path.insert(0, str(toolkit_root / "shared"))
```

### Platform Not Supported

**Problem:** Tool doesn't run on current platform.

**Solution:**
```bash
# Check platform support
python cortex-toolkit/shared/toolkit_registry.py info <tool-name>

# Look for "platforms" field in output
```

### Permission Denied

**Problem:** Tool requires admin privileges.

**Solution:**
```bash
# Check if tool requires admin
python cortex-toolkit/shared/toolkit_registry.py info <tool-name>

# Run with appropriate privileges
# Windows: Run as Administrator
# Linux/macOS: sudo python ...
```

---

---

## 📄 HTML Tools Guide

**NEW: Specialized tools for HTML documentation quality assurance**

The CORTEX Toolkit now includes two powerful HTML quality tools designed for both technical and non-technical users:

### Tools Overview

1. **HTML Style Centralizer** - Removes inline CSS and centralizes styles
   - **User-Friendly Name:** Style Cleanup Tool
   - **What it does:** Moves `style="..."` attributes to a central CSS file
   - **Why use it:** Makes website updates easier (change once, affect all pages)
   - **When to use:** After creating new pages, before publishing

2. **HTML Validator** - Checks HTML syntax and structure
   - **User-Friendly Name:** HTML Error Checker
   - **What it does:** Finds missing closing tags, broken attributes, syntax errors
   - **Why use it:** Prevents broken pages that don't display correctly
   - **When to use:** Before deployment, after bulk edits

### Quick Start

```bash
# Centralize inline styles
python cortex-toolkit/documentation/html-tools/html_style_centralizer.py

# Validate HTML syntax
python cortex-toolkit/documentation/html-tools/html_validator.py
```

### Detailed Documentation

� **[HTML Tools Complete Guide](HTML-TOOLS-GUIDE.md)**

Comprehensive guide covering:
- For Non-Technical Users: Simple explanations and step-by-step instructions
- For Technical Users: Algorithm details, safety features, command options
- Common Workflows: Pre-deployment checks, bulk cleanup, error fixing
- Troubleshooting: Solutions for common issues
- Success Metrics: How to measure quality improvements

---

## �📊 Statistics

**Version:** 1.0.0  
**Total Tools:** 57 Python scripts ⬆️ (+2 HTML tools)  
**Categories:** 10  
**CLI Wrappers:** 20  
**Platforms:** Windows, Linux, macOS  
**Python Version:** 3.8+  
**Test Coverage:** TBD

---

## 🔗 Related Documentation

- [CORTEX.prompt.md](/.github/prompts/CORTEX.prompt.md) - Main CORTEX instructions
- [HTML-TOOLS-GUIDE.md](HTML-TOOLS-GUIDE.md) - ⭐ HTML quality tools guide
- [toolkit-manifest.yaml](/cortex-toolkit/toolkit-manifest.yaml) - Tool registry
- [TOOLS-INVENTORY.md](/cortex-toolkit/TOOLS-INVENTORY.md) - Detailed tool inventory
- [FOLDER-STRUCTURE.md](/cortex-toolkit/FOLDER-STRUCTURE.md) - Directory structure
- [STATUS-REPORT.md](/cortex-toolkit/STATUS-REPORT.md) - Current status

---

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX  
**Copyright © 2025 Asif Hussain. All rights reserved.**
