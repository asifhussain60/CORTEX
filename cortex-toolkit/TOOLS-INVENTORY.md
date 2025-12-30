# CORTEX Toolkit - Tools Inventory

**Version:** 1.0.1  
**Last Updated:** December 30, 2025  
**Total Tools:** 27 production-ready tools  
**Categories:** 9  

---

## 📊 Quick Stats

| Metric | Count |
|--------|-------|
| **Total Tools** | 27 |
| **Categories** | 9 |
| **CLI Wrappers** | 7 |
| **Platforms Supported** | Windows, Linux, macOS |
| **Admin-Required Tools** | 2 |
| **Execution Methods** | cli_wrapper, copilot_chat, cli |

---

## 🗂️ Tools by Category

### 1. Brain Operations (4 tools)

Core CORTEX brain tier operations for system health and optimization.

| # | Tool | Command | Execution | Admin | Description |
|---|------|---------|-----------|-------|-------------|
| 1 | **align** | `cortex-align` | cli_wrapper | No | System alignment and consistency checks |
| 2 | **healthcheck** | `cortex-health` | cli_wrapper | No | Comprehensive system health diagnostics |
| 3 | **optimize** | `cortex-optimize` | cli_wrapper | No | System optimization and performance tuning |
| 4 | **cleanup** | `cortex-cleanup` | cli_wrapper | No | System cleanup and maintenance |

**Scripts:**
- `core/brain/align.py`
- `core/brain/healthcheck.py`
- `core/brain/optimize.py`
- `core/brain/cleanup.py`

**Wrappers:**
- `cli/wrappers/align_wrapper.py`
- `cli/wrappers/healthcheck_wrapper.py`
- `cli/wrappers/optimize_wrapper.py`
- `cli/wrappers/cleanup_wrapper.py`

---

### 2. Operations (3 tools)

System operations and orchestration for code management.

| # | Tool | Command | Execution | Admin | Description |
|---|------|---------|-----------|-------|-------------|
| 5 | **review** | `cortex-review` | cli_wrapper | No | Code review orchestration |
| 6 | **deploy** | `cortex-deploy` | cli_wrapper | **Yes** | Deployment to publish directory |
| 7 | **sanitize** | `cortex-sanitize` | cli_wrapper | No | Code sanitization for sharing |

**Scripts:**
- `core/operations/review.py`
- `core/operations/deploy.py`
- `core/operations/sanitize.py`

**Wrappers:**
- `cli/wrappers/review_wrapper.py`
- `cli/wrappers/deploy_wrapper.py`
- `cli/wrappers/sanitize_wrapper.py`

---

### 3. Planning (3 tools)

Feature planning and Azure DevOps work item management.

| # | Tool | Command | Execution | Admin | Description |
|---|------|---------|-----------|-------|-------------|
| 8 | **plan** | `cortex-plan` | copilot_chat | No | Generate feature implementation plans |
| 9 | **ado** | `cortex-ado` | copilot_chat | No | Azure DevOps work item management |
| 10 | **planning-file-manager** | `cortex-pfm` | cli | No | Manage planning documentation files |

**Scripts:**
- `core/planning/plan_generator.py`
- `core/planning/ado_manager.py`
- `core/planning/planning_file_manager.py`

---

### 4. Analytics (4 tools)

Performance profiling, metrics collection, and visualization.

| # | Tool | Command | Execution | Admin | Description |
|---|------|---------|-----------|-------|-------------|
| 11 | **profile** | `cortex-profile` | cli | No | Performance profiling and analysis |
| 12 | **metrics** | `cortex-metrics` | cli | No | Collect and display system metrics |
| 13 | **visualize** | `cortex-visualize` | cli | No | Visualize brain health and metrics |
| 14 | **uml** | `cortex-uml` | cli | No | Generate UML diagrams |

**Scripts:**
- `analytics/profiling/profile_performance.py`
- `analytics/metrics/collect_dashboard_data.py`
- `analytics/visualization/visualize_brain_health.py`
- `analytics/visualization/generate_uml_standalone.py`

---

### 5. Documentation (3 tools)

Documentation generation and maintenance.

| # | Tool | Command | Execution | Admin | Description |
|---|------|---------|-----------|-------|-------------|
| 15 | **docs-generate** | `cortex-docs-gen` | cli | No | Generate documentation from source code |
| 16 | **prompts-regenerate** | `cortex-prompts-regen` | cli_wrapper | **Yes** | Regenerate AI prompt files |
| 17 | **quick-reference** | `cortex-qr` | cli | No | Generate quick reference documentation |

**Scripts:**
- `documentation/generate_docs_from_code.py`
- `documentation/regenerate_prompts.py`
- `documentation/generate_quick_reference.py`

**Wrappers:**
- `cli/wrappers/regenerate_prompts_wrapper.py`

---

### 6. Testing (3 tools)

Test validation and performance testing.

| # | Tool | Command | Execution | Admin | Description |
|---|------|---------|-----------|-------|-------------|
| 18 | **validate** | `cortex-validate` | cli | No | Validate deployment integrity |
| 19 | **test-performance** | `cortex-test-perf` | cli | No | Generate and run performance tests |
| 20 | **verify-no-mocks** | `cortex-verify-mocks` | cli | No | Verify no mock objects in tests |

**Scripts:**
- `testing/validate_deployment.py`
- `testing/generate_performance_tests.py`
- `testing/verify_no_mocks.py`

---

### 7. Migration (2 tools)

Database schema and version migration utilities.

| # | Tool | Command | Execution | Admin | Description |
|---|------|---------|-----------|-------|-------------|
| 21 | **schema-migrate** | `cortex-schema-migrate` | cli | No | Migrate database schemas |
| 22 | **version-detect** | `cortex-version-detect` | cli | No | Detect CORTEX version |

**Scripts:**
- `migration/schema_migrator.py`
- `migration/version_detector.py`

---

### 8. Maintenance (3 tools)

System maintenance and cleanup utilities.

| # | Tool | Command | Execution | Admin | Description |
|---|------|---------|-----------|-------|-------------|
| 23 | **cleanup-temp** | `cortex-cleanup-temp` | cli | No | Clean up temporary files |
| 24 | **detect-duplicates** | `cortex-duplicates` | cli | No | Detect duplicate code |
| 25 | **full-cleanup** | `cortex-full-cleanup` | cli | No | Comprehensive 5-phase cleanup orchestrator |

**Scripts:**
- `maintenance/cleanup_temp_files.py`
- `maintenance/detect_duplicates.py`
- `maintenance/full_cleanup.py`

---

### 9. Utilities (2 tools)

General utility tools for version and token management.

| # | Tool | Command | Execution | Admin | Description |
|---|------|---------|-----------|-------|-------------|
| 26 | **token-calculator** | `cortex-tokens` | cli | No | Calculate prompt token usage |
| 27 | **version-manager** | `cortex-version` | cli | No | Manage CORTEX versions |

**Scripts:**
- `core/utilities/measure_prompt_tokens.py`
- `core/utilities/version_manager.py`

---

## 🔧 Execution Methods

### cli_wrapper (7 tools)
Tools requiring file system operations with CLI wrapper integration:
- align, healthcheck, optimize, cleanup
- review, deploy, sanitize
- prompts-regenerate

### copilot_chat (2 tools)
Interactive multi-turn workflows via Copilot Chat:
- plan, ado

### cli (18 tools)
Direct CLI execution:
- All analytics, documentation (except prompts-regenerate), testing, migration, maintenance, and utility tools

---

## 🔐 Admin-Required Tools (2)

| Tool | Reason |
|------|--------|
| **deploy** | Writes to publish directory |
| **prompts-regenerate** | Modifies system prompt files |

---

## 📂 Directory Structure

```
cortex-toolkit/
├── VERSION                         # 1.0.0
├── toolkit-manifest.yaml           # Tool registry (27 tools)
├── README.md                       # Main documentation
├── TOOLS-INVENTORY.md              # This file
│
├── core/                           # 11 tools
│   ├── brain/                      # 4 tools
│   ├── operations/                 # 3 tools
│   ├── planning/                   # 3 tools
│   └── utilities/                  # 2 tools
│
├── cli/                            # CLI infrastructure
│   └── wrappers/                   # 7 wrappers
│
├── analytics/                      # 4 tools
│   ├── profiling/
│   ├── metrics/
│   └── visualization/
│
├── documentation/                  # 3 tools
├── testing/                        # 3 tools
├── migration/                      # 2 tools
├── maintenance/                    # 3 tools
│
├── shared/                         # Shared libraries
│   ├── toolkit_registry.py
│   ├── config.py
│   └── logging_config.py
│
├── install/                        # Installation
│   ├── install-toolkit.ps1
│   ├── install-toolkit.sh
│   └── verify-installation.py
│
└── tests/                          # Test suite
```

---

## 🚀 Usage Examples

### List All Tools

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

# Show tool script path
python cortex-toolkit/shared/toolkit_registry.py info align --show-path
```

### Invoke Tools

```bash
# Using registry (recommended)
python cortex-toolkit/shared/toolkit_registry.py invoke align --check-only

# Using direct path
python cortex-toolkit/core/brain/align.py --check-only

# Using CLI wrapper
python cortex-toolkit/cli/wrappers/align_wrapper.py --check-only
```

### Cross-Repository Usage

```bash
# From KSESSIONS repository
cd D:\PROJECTS\KSESSIONS
python D:\PROJECTS\CORTEX\cortex-toolkit\shared\toolkit_registry.py invoke healthcheck

# From NOOR CANVAS repository
cd "D:\PROJECTS\NOOR CANVAS"
python D:\PROJECTS\CORTEX\cortex-toolkit\shared\toolkit_registry.py invoke validate
```

---

## ✅ Verification

Run the verification script to ensure all tools are properly installed:

```bash
python cortex-toolkit/install/verify-installation.py
```

**Expected Output:**
```
=== CORTEX Toolkit Installation Verification ===

[1/6] Checking toolkit root...
  ✓ Toolkit root: D:\PROJECTS\CORTEX\cortex-toolkit

[2/6] Checking manifest...
  ✓ Manifest loaded
  ✓ Version: 1.0.0
  ✓ Categories: 9
  ✓ Tools: 27

[3/6] Checking Python version...
  ✓ Python 3.13.7

[4/6] Checking platform...
  ✓ Platform: Windows
  ✓ Architecture: AMD64

[5/6] Checking dependencies...
  ✓ yaml
  ✓ json
  ✓ pathlib

[6/6] Checking sample tools...
  ✓ align (platform: True)
  ✓ healthcheck (platform: True)
  ✓ plan (platform: True)

=== Summary ===
✓ All checks passed!

Toolkit is ready to use.
```

---

## 📊 Tool Metrics

| Metric | Value |
|--------|-------|
| **Total Tools** | 27 |
| **CLI Wrappers** | 7 |
| **Scripts** | 27 |
| **Categories** | 9 |
| **Platform Support** | 3 (Windows, Linux, macOS) |
| **Admin-Required** | 2 (7.4%) |
| **Interactive (Copilot)** | 2 (7.4%) |
| **Direct CLI** | 18 (66.7%) |

---

## 🔄 Tool Dependencies

### No External Dependencies
Most tools use Python standard library only.

### Optional Dependencies
- **UML Generation:** `plantuml` (optional)
- **Visualization:** `matplotlib`, `graphviz` (optional)
- **Documentation:** `sphinx` (optional)

---

## 📝 Changelog

### v1.0.0 (2025-12-16)

**Initial Release:**
- ✅ 27 production-ready tools
- ✅ 9 categories (brain, operations, planning, analytics, documentation, testing, migration, maintenance, utilities)
- ✅ 7 CLI wrappers with unified interface
- ✅ Cross-repository access
- ✅ Platform support: Windows, Linux, macOS
- ✅ Manifest-based registry system
- ✅ Comprehensive documentation

---

## 🔗 Related Documentation

- **Main README:** `cortex-toolkit/README.md`
- **Architecture Plan:** `cortex-brain/documents/planning/CORTEX-TOOLKIT-ARCHITECTURE-PLAN.md`
- **Manifest:** `cortex-toolkit/toolkit-manifest.yaml`
- **Installation Guide:** `cortex-toolkit/install/`

---

## 📄 License

Copyright © 2025 Asif Hussain. All rights reserved.

---

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX
