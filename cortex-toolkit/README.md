# CORTEX Toolkit

**Version:** 1.0.0  
**Status:** Production Ready  
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

## 🎯 Overview

CORTEX Toolkit is a comprehensive collection of well-architected tools for CORTEX operations, analytics, documentation, and maintenance. The toolkit provides cross-repository access, unified command-line interfaces, and platform support for Windows, Linux, and macOS.

**Key Features:**
- ✅ 40+ production-ready tools organized into 8 categories
- ✅ Cross-repository access from any workspace project
- ✅ Unified CLI with consistent interface
- ✅ Platform support: Windows, Linux, macOS
- ✅ Hierarchical configuration (Environment > User > Repo > Global)
- ✅ Comprehensive logging and audit trail
- ✅ Manifest-based tool discovery

---

## 📦 Installation

### Windows (PowerShell)

```powershell
# User installation
.\cortex-toolkit\install\install-toolkit.ps1

# System-wide installation (requires admin)
.\cortex-toolkit\install\install-toolkit.ps1 -Global

# With PowerShell profile integration
.\cortex-toolkit\install\install-toolkit.ps1 -UserProfile
```

### Linux/macOS (Bash)

```bash
# User installation
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

## 🚀 Quick Start

### List Available Tools

```bash
# List all categories
python cortex-toolkit/shared/toolkit_registry.py categories

# List all tools
python cortex-toolkit/shared/toolkit_registry.py list

# List tools in specific category
python cortex-toolkit/shared/toolkit_registry.py list brain_operations
```

### Get Tool Information

```bash
# Get detailed tool info
python cortex-toolkit/shared/toolkit_registry.py info align
```

### Invoke Tools

```bash
# Using registry (recommended)
python cortex-toolkit/shared/toolkit_registry.py invoke align --check-only

# Using direct command (after PATH setup)
python cortex-toolkit/cli/wrappers/align_wrapper.py --check-only
```

---

## 📚 Tool Categories

### 1. Brain Operations (`brain_operations`)

Core CORTEX brain tier operations.

| Tool | Command | Description |
|------|---------|-------------|
| align | `cortex-align` | System alignment and consistency checks |
| healthcheck | `cortex-health` | Comprehensive system health diagnostics |
| optimize | `cortex-optimize` | System optimization and performance tuning |
| cleanup | `cortex-cleanup` | System cleanup and maintenance |

### 2. Operations (`operations`)

System operations and orchestration.

| Tool | Command | Description |
|------|---------|-------------|
| review | `cortex-review` | Code review orchestration |
| deploy | `cortex-deploy` | Deployment to publish directory |
| sanitize | `cortex-sanitize` | Code sanitization for sharing |

### 3. Planning (`planning`)

Planning and ADO management.

| Tool | Command | Description |
|------|---------|-------------|
| plan | `cortex-plan` | Generate feature implementation plans |
| ado | `cortex-ado` | Azure DevOps work item management |
| planning-file-manager | `cortex-pfm` | Manage planning documentation files |

### 4. Analytics (`analytics`)

Analysis and reporting.

| Tool | Command | Description |
|------|---------|-------------|
| profile | `cortex-profile` | Performance profiling and analysis |
| metrics | `cortex-metrics` | Collect and display system metrics |
| visualize | `cortex-visualize` | Visualize brain health and metrics |
| uml | `cortex-uml` | Generate UML diagrams |

### 5. Documentation (`documentation`)

Documentation generation.

| Tool | Command | Description |
|------|---------|-------------|
| docs-generate | `cortex-docs-gen` | Generate documentation from source code |
| prompts-regenerate | `cortex-prompts-regen` | Regenerate AI prompt files |
| quick-reference | `cortex-qr` | Generate quick reference documentation |

### 6. Testing (`testing`)

Testing utilities.

| Tool | Command | Description |
|------|---------|-------------|
| validate | `cortex-validate` | Validate deployment integrity |
| test-performance | `cortex-test-perf` | Generate and run performance tests |
| verify-no-mocks | `cortex-verify-mocks` | Verify no mock objects in tests |

### 7. Migration (`migration`)

Database and schema migration.

| Tool | Command | Description |
|------|---------|-------------|
| schema-migrate | `cortex-schema-migrate` | Migrate database schemas |
| version-detect | `cortex-version-detect` | Detect CORTEX version |

### 8. Maintenance (`maintenance`)

Maintenance tools.

| Tool | Command | Description |
|------|---------|-------------|
| cleanup-temp | `cortex-cleanup-temp` | Clean up temporary files |
| detect-duplicates | `cortex-duplicates` | Detect duplicate code |
| master-cleanup | `cortex-master-cleanup` | Master cleanup operation |
| rename-planning-system-version | `cortex-rename-planning-version` | Rename Planning System version references |

---

## 🏗️ Architecture

### Directory Structure

```
cortex-toolkit/
├── VERSION                         # Toolkit version
├── toolkit-manifest.yaml           # Tool registry
├── README.md                       # This file
│
├── core/                           # Core tools
│   ├── brain/                      # Brain operations
│   ├── operations/                 # System operations
│   ├── planning/                   # Planning tools
│   └── utilities/                  # General utilities
│
├── cli/                            # Command-line interfaces
│   ├── wrappers/                   # CLI wrappers
│   └── launchers/                  # Platform launchers
│
├── analytics/                      # Analysis & reporting
│   ├── profiling/
│   ├── metrics/
│   └── visualization/
│
├── migration/                      # Database migration
├── documentation/                  # Doc generation
├── testing/                        # Testing utilities
├── maintenance/                    # Maintenance tools
│
├── shared/                         # Shared libraries
│   ├── toolkit_registry.py         # Tool discovery
│   ├── config.py                   # Configuration
│   ├── logging_config.py           # Logging setup
│   └── __init__.py
│
└── install/                        # Installation
    ├── install-toolkit.ps1         # Windows installer
    ├── install-toolkit.sh          # Linux/macOS installer
    └── verify-installation.py      # Verification
```

### Configuration Hierarchy

Configuration is loaded from multiple sources with priority:

1. **Environment Variables** (highest priority)
   - `CORTEX_TOOLKIT_ROOT`
   - `CORTEX_ROOT`
   - `CORTEX_PYTHON_PATH`

2. **User Config** (`~/.cortex/config.yaml`)
3. **Repository Config** (`{repo}/cortex.config.json`)
4. **Global Config** (`D:\PROJECTS\global-workspace-config.yaml`)

---

## 🔧 Usage Examples

### Example 1: System Health Check

```bash
# Run health check
python cortex-toolkit/shared/toolkit_registry.py invoke healthcheck

# With specific checks
python cortex-toolkit/cli/wrappers/healthcheck_wrapper.py --tier1 --tier2
```

### Example 2: Generate Documentation

```bash
# Generate docs from code
python cortex-toolkit/shared/toolkit_registry.py invoke docs-generate

# Generate quick reference
python cortex-toolkit/documentation/generate_quick_reference.py
```

### Example 3: Performance Profiling

```bash
# Profile performance
python cortex-toolkit/analytics/profiling/profile_performance.py --module brain

# Collect metrics
python cortex-toolkit/analytics/metrics/collect_dashboard_data.py
```

### Example 4: Cross-Repository Usage

```bash
# From KSESSIONS repository
cd D:\PROJECTS\KSESSIONS
python $env:CORTEX_TOOLKIT_ROOT\shared\toolkit_registry.py invoke align

# From NOOR CANVAS repository
cd "D:\PROJECTS\NOOR CANVAS"
python $env:CORTEX_TOOLKIT_ROOT\shared\toolkit_registry.py invoke validate
```

---

## 🐍 Python API

### Using ToolkitRegistry

```python
from pathlib import Path
import sys

# Add toolkit to path
toolkit_root = Path("D:/PROJECTS/CORTEX/cortex-toolkit")
sys.path.insert(0, str(toolkit_root / "shared"))

from toolkit_registry import ToolkitRegistry

# Initialize registry
registry = ToolkitRegistry()

# List all tools
tools = registry.list_tools()
for tool in tools:
    print(f"{tool['name']}: {tool['description']}")

# Get tool info
tool_info = registry.get_tool("align")
print(tool_info)

# Invoke tool
exit_code = registry.invoke_tool("align", ["--check-only"])
```

### Using Configuration

```python
from config import get_config

config = get_config()

# Get toolkit root
toolkit_root = config.get_toolkit_root()

# Get workspace roots
workspace_roots = config.get_workspace_roots()

# Resolve path alias
ksessions_path = config.get_path_alias("ksessions")
```

---

## 🔐 Security

### Access Control

- Admin-only tools require elevated privileges
- Cross-repo access validated via configuration
- No hardcoded credentials

### Audit Trail

All tool invocations are logged to `logs/toolkit-audit.log`:

```
[2025-12-16 10:30:45] [align.audit] INVOCATION | tool=align | user=asif | cwd=D:\PROJECTS\CORTEX | args=--check-only
```

### Sensitive Data

- Passwords and tokens never logged
- Paths sanitized in logs
- Secure config storage

---

## 🧪 Testing

### Run Tests

```bash
# Unit tests
pytest tests/toolkit/unit/

# Integration tests
pytest tests/toolkit/integration/

# Platform tests
pytest tests/toolkit/platform/

# All tests
pytest tests/toolkit/
```

---

## 📖 Documentation

### Per-Tool Documentation

Each tool category has detailed documentation:

- `core/brain/README.md` - Brain operations
- `core/operations/README.md` - System operations
- `core/planning/README.md` - Planning tools
- `analytics/README.md` - Analytics tools

### API Documentation

- `shared/README.md` - API reference
- `cli/README.md` - CLI usage guide

---

## 🛠️ Development

### Adding New Tools

1. **Define in Manifest** (`toolkit-manifest.yaml`)
2. **Implement Script** (in appropriate category folder)
3. **Add Tests** (`tests/toolkit/`)
4. **Document** (category README)

See: `cortex-brain/documents/planning/CORTEX-TOOLKIT-ARCHITECTURE-PLAN.md`

### Contributing

1. Follow naming conventions
2. Add comprehensive tests
3. Update manifest
4. Document API and usage

---

## 🔄 Migration from Legacy Scripts

Legacy scripts in `scripts/` are preserved but deprecated. Use toolkit equivalents:

| Legacy | Toolkit |
|--------|---------|
| `scripts/run_alignment.py` | `cortex-toolkit/core/brain/align.py` |
| `scripts/run_optimize.py` | `cortex-toolkit/core/brain/optimize.py` |
| `scripts/plan_cli.py` | `cortex-toolkit/core/planning/plan_generator.py` |

---

## 🆘 Troubleshooting

### Tool Not Found

```bash
# Verify installation
python cortex-toolkit/install/verify-installation.py

# Check manifest
python cortex-toolkit/shared/toolkit_registry.py list
```

### Cannot Invoke Tool

```bash
# Check platform support
python cortex-toolkit/shared/toolkit_registry.py info <tool-name>

# Check Python version (requires 3.8+)
python --version
```

### Configuration Issues

```bash
# Check environment
echo $env:CORTEX_TOOLKIT_ROOT  # Windows
echo $CORTEX_TOOLKIT_ROOT      # Linux/macOS

# Check user config
cat ~/.cortex/config.yaml
```

---

## 📊 Status & Metrics

**Version:** 1.0.0  
**Tools:** 40+  
**Categories:** 8  
**Platforms:** Windows, Linux, macOS  
**Test Coverage:** TBD  
**Documentation:** Complete

---

## 📝 Changelog

### v1.0.0 (2025-12-16)

- ✅ Initial toolkit foundation
- ✅ Manifest-based registry system
- ✅ Cross-repository configuration
- ✅ Installation scripts (Windows/Linux/macOS)
- ✅ 40+ tools organized into 8 categories
- ✅ Comprehensive documentation

---

## 📄 License

Copyright © 2025 Asif Hussain. All rights reserved.

See LICENSE file in CORTEX repository root.

---

## 🔗 Links

- **Main Repository:** github.com/asifhussain60/CORTEX
- **Architecture Plan:** `cortex-brain/documents/planning/CORTEX-TOOLKIT-ARCHITECTURE-PLAN.md`
- **Issue Tracker:** GitHub Issues

---

**Questions?** Contact Asif Hussain | GitHub: github.com/asifhussain60/CORTEX
