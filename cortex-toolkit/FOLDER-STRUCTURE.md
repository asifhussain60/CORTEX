# CORTEX Toolkit - Folder Structure

**Version:** 1.0.0  
**Last Updated:** December 16, 2025  
**Total Files:** 47 Python scripts + config files  

---

## 📂 Complete Directory Tree

```
cortex-toolkit/
│
├── 📄 VERSION                              # Version identifier (1.0.0)
├── 📄 toolkit-manifest.yaml                # Tool registry and metadata
├── 📄 README.md                            # Main documentation
├── 📄 TOOLS-INVENTORY.md                   # Complete tools list
├── 📄 FOLDER-STRUCTURE.md                  # This file
│
├── 📁 core/                                # Core tools (11 scripts)
│   │
│   ├── 📁 brain/                           # Brain operations (4 scripts)
│   │   ├── align.py                        # System alignment
│   │   ├── cleanup.py                      # System cleanup
│   │   ├── healthcheck.py                  # Health diagnostics
│   │   ├── optimize.py                     # Performance optimization
│   │   └── README.md                       # Brain operations guide
│   │
│   ├── 📁 operations/                      # System operations (3 scripts)
│   │   ├── deploy.py                       # Deployment orchestration
│   │   ├── review.py                       # Code review automation
│   │   ├── sanitize.py                     # Code sanitization
│   │   └── README.md                       # Operations guide
│   │
│   ├── 📁 planning/                        # Planning tools (3 scripts)
│   │   ├── ado_manager.py                  # Azure DevOps integration
│   │   ├── plan_generator.py               # Feature planning
│   │   ├── planning_file_manager.py        # Planning docs management
│   │   └── README.md                       # Planning guide
│   │
│   └── 📁 utilities/                       # General utilities (2 scripts)
│       ├── measure_prompt_tokens.py        # Token calculation
│       ├── version_manager.py              # Version management
│       └── README.md                       # Utilities guide
│
├── 📁 cli/                                 # Command-line interfaces
│   │
│   └── 📁 wrappers/                        # CLI wrappers (10 scripts)
│       ├── __init__.py                     # Package initialization
│       ├── base_wrapper.py                 # Base wrapper class
│       ├── align_wrapper.py                # Align CLI wrapper
│       ├── cleanup_wrapper.py              # Cleanup CLI wrapper
│       ├── deploy_wrapper.py               # Deploy CLI wrapper
│       ├── healthcheck_wrapper.py          # Healthcheck CLI wrapper
│       ├── optimize_wrapper.py             # Optimize CLI wrapper
│       ├── regenerate_prompts_wrapper.py   # Prompts regeneration wrapper
│       ├── review_wrapper.py               # Review CLI wrapper
│       ├── sanitize_wrapper.py             # Sanitize CLI wrapper
│       └── generate_ra_specs.py            # RA specs generator
│
├── 📁 analytics/                           # Analysis & reporting (7 scripts)
│   │
│   ├── 📁 profiling/                       # Performance profiling (2 scripts)
│   │   ├── profile_performance.py          # Runtime profiling
│   │   └── profile_startup.py              # Startup profiling
│   │
│   ├── 📁 metrics/                         # Metrics collection (2 scripts)
│   │   ├── collect_dashboard_data.py       # Dashboard data collector
│   │   └── monitor_brain_health.py         # Brain health monitor
│   │
│   └── 📁 visualization/                   # Data visualization (3 scripts)
│       ├── dependency_graph_generator.py   # Dependency graphs
│       ├── generate_uml_standalone.py      # UML diagram generation
│       ├── visualize_brain_health.py       # Brain health visualization
│       └── README.md                       # Visualization guide
│
├── 📁 documentation/                       # Documentation tools (3 scripts)
│   ├── generate_docs_from_code.py          # Auto-doc generation
│   ├── generate_quick_reference.py         # Quick reference generator
│   ├── regenerate_prompts.py               # Prompt regeneration
│   └── README.md                           # Documentation guide
│
├── 📁 testing/                             # Testing utilities (3 scripts)
│   ├── generate_performance_tests.py       # Performance test generator
│   ├── validate_deployment.py              # Deployment validator
│   ├── verify_no_mocks.py                  # Mock verification
│   └── README.md                           # Testing guide
│
├── 📁 migration/                           # Database migration (2 scripts)
│   ├── schema_migrator.py                  # Schema migration tool
│   ├── version_detector.py                 # Version detection
│   └── README.md                           # Migration guide
│
├── 📁 maintenance/                         # Maintenance tools (3 scripts)
│   ├── cleanup_temp_files.py               # Temp file cleanup
│   ├── detect_duplicates.py                # Duplicate code detection
│   ├── master_cleanup.py                   # Master cleanup orchestrator
│   └── README.md                           # Maintenance guide
│
├── 📁 shared/                              # Shared libraries (4 scripts)
│   ├── __init__.py                         # Package initialization
│   ├── config.py                           # Configuration management
│   ├── logging_config.py                   # Logging setup
│   ├── toolkit_registry.py                 # Tool registry & discovery
│   └── README.md                           # API documentation
│
├── 📁 install/                             # Installation scripts
│   ├── install-toolkit.ps1                 # Windows installer (PowerShell)
│   ├── install-toolkit.sh                  # Linux/macOS installer (Bash)
│   ├── verify-installation.py              # Installation verification
│   └── README.md                           # Installation guide
│
└── 📁 tests/                               # Test suite
    ├── test_toolkit_core.py                # Core functionality tests
    └── README.md                           # Testing documentation

```

---

## 📊 File Count by Category

| Category | Python Scripts | Config/Docs | Total |
|----------|----------------|-------------|-------|
| **core/** | 11 | 4 READMEs | 15 |
| **cli/** | 10 | 0 | 10 |
| **analytics/** | 7 | 1 README | 8 |
| **documentation/** | 3 | 1 README | 4 |
| **testing/** | 3 | 1 README | 4 |
| **migration/** | 2 | 1 README | 3 |
| **maintenance/** | 3 | 1 README | 4 |
| **shared/** | 4 | 1 README | 5 |
| **install/** | 3 | 1 README | 4 |
| **tests/** | 1 | 1 README | 2 |
| **Root** | 0 | 5 docs | 5 |
| **TOTAL** | **47** | **17** | **64** |

---

## 🗂️ Logical Organization

### Tier 1: Core Operations (11 scripts)

**Purpose:** Essential CORTEX brain and system operations

```
core/
├── brain/          # Brain tier operations (align, health, optimize, cleanup)
├── operations/     # System operations (review, deploy, sanitize)
├── planning/       # Planning & ADO (plan, ado, pfm)
└── utilities/      # General utilities (tokens, version)
```

### Tier 2: CLI Infrastructure (10 scripts)

**Purpose:** Command-line wrappers for unified interface

```
cli/
└── wrappers/       # 7 main wrappers + base + utilities
```

### Tier 3: Analytics & Insights (7 scripts)

**Purpose:** Performance, metrics, and visualization

```
analytics/
├── profiling/      # Performance profiling
├── metrics/        # Metrics collection
└── visualization/  # Data visualization & UML
```

### Tier 4: Developer Tools (11 scripts)

**Purpose:** Documentation, testing, migration, maintenance

```
documentation/      # 3 scripts (docs, prompts, quick-ref)
testing/            # 3 scripts (validate, perf, verify)
migration/          # 2 scripts (schema, version)
maintenance/        # 3 scripts (cleanup, duplicates, master)
```

### Tier 5: Infrastructure (8 scripts)

**Purpose:** Shared libraries, installation, testing

```
shared/             # 4 scripts (registry, config, logging)
install/            # 3 scripts (2 installers + verify)
tests/              # 1 script (core tests)
```

---

## 🔧 File Types Breakdown

### Python Scripts (47 total)

| Type | Count | Examples |
|------|-------|----------|
| **Core Tools** | 11 | align.py, healthcheck.py, plan_generator.py |
| **CLI Wrappers** | 10 | align_wrapper.py, deploy_wrapper.py |
| **Analytics** | 7 | profile_performance.py, visualize_brain_health.py |
| **Documentation** | 3 | generate_docs_from_code.py, regenerate_prompts.py |
| **Testing** | 3 | validate_deployment.py, verify_no_mocks.py |
| **Migration** | 2 | schema_migrator.py, version_detector.py |
| **Maintenance** | 3 | cleanup_temp_files.py, detect_duplicates.py |
| **Shared** | 4 | toolkit_registry.py, config.py |
| **Install** | 3 | verify-installation.py, installers (shell) |
| **Tests** | 1 | test_toolkit_core.py |

### Configuration Files (5)

- `VERSION` - Version identifier
- `toolkit-manifest.yaml` - Tool registry (YAML)
- `README.md` - Main documentation
- `TOOLS-INVENTORY.md` - Tools list
- `FOLDER-STRUCTURE.md` - This file

### Documentation Files (12 READMEs)

- Root: `README.md` (main)
- Each category folder: README.md (11 total)

### Installation Scripts (2)

- `install-toolkit.ps1` (Windows PowerShell)
- `install-toolkit.sh` (Linux/macOS Bash)

---

## 🎯 Navigation Guide

### Finding Brain Operations

```
cortex-toolkit/core/brain/
├── align.py            # System alignment
├── healthcheck.py      # Health diagnostics
├── optimize.py         # Performance tuning
└── cleanup.py          # System cleanup
```

### Finding CLI Wrappers

```
cortex-toolkit/cli/wrappers/
├── base_wrapper.py                 # Base class
├── {operation}_wrapper.py          # 7 main wrappers
└── generate_ra_specs.py            # RA specs generator
```

### Finding Analytics Tools

```
cortex-toolkit/analytics/
├── profiling/profile_performance.py        # Main profiler
├── metrics/collect_dashboard_data.py       # Main collector
└── visualization/visualize_brain_health.py # Main visualizer
```

### Finding Documentation Tools

```
cortex-toolkit/documentation/
├── generate_docs_from_code.py      # Auto-doc generator
├── regenerate_prompts.py           # Prompt regenerator
└── generate_quick_reference.py     # Quick-ref generator
```

---

## 🚀 Quick Access Paths

### Registry & Discovery

```bash
python cortex-toolkit/shared/toolkit_registry.py
```

### Installation Verification

```bash
python cortex-toolkit/install/verify-installation.py
```

### Core Operations

```bash
# Brain operations
python cortex-toolkit/core/brain/align.py
python cortex-toolkit/core/brain/healthcheck.py

# System operations
python cortex-toolkit/core/operations/review.py
python cortex-toolkit/core/operations/sanitize.py
```

### CLI Wrappers

```bash
# Using wrappers (recommended)
python cortex-toolkit/cli/wrappers/align_wrapper.py
python cortex-toolkit/cli/wrappers/healthcheck_wrapper.py
```

---

## 📈 Growth Plan

### Planned Additions

**Future tools to add:**
- `core/brain/vacuum.py` - Database vacuum operation
- `core/brain/refresh_prompts.py` - Prompt refresh orchestrator
- `analytics/metrics/generate_report.py` - Metrics reporting
- `testing/run_smoke_tests.py` - Smoke test runner

**Future categories:**
- `backup/` - Backup and restore utilities
- `export/` - Data export tools
- `integration/` - External integrations (GitHub, ADO, etc.)

---

## 🔍 Search Patterns

### Find All Tools

```bash
Get-ChildItem -Path "cortex-toolkit" -Recurse -Filter "*.py" -Exclude "__init__.py","*_wrapper.py"
```

### Find All Wrappers

```bash
Get-ChildItem -Path "cortex-toolkit/cli/wrappers" -Filter "*_wrapper.py"
```

### Find All READMEs

```bash
Get-ChildItem -Path "cortex-toolkit" -Recurse -Filter "README.md"
```

---

## ✅ Organization Checklist

- ✅ All tools in organized category folders
- ✅ Consistent naming conventions
- ✅ README in every category folder
- ✅ Manifest covers all tools
- ✅ No loose scripts in root
- ✅ Clear separation of concerns
- ✅ Platform-agnostic structure
- ✅ Scalable for future growth

---

## 📝 Naming Conventions

### Python Scripts

- **Tools:** Descriptive names (e.g., `align.py`, `healthcheck.py`)
- **Wrappers:** Tool name + `_wrapper.py` (e.g., `align_wrapper.py`)
- **Utilities:** Function + purpose (e.g., `measure_prompt_tokens.py`)

### Folders

- **Lowercase:** All folder names are lowercase
- **Descriptive:** Clear purpose (e.g., `analytics`, `documentation`)
- **Plural:** Category names are plural (e.g., `operations`, `utilities`)

### Commands

- **Prefix:** All commands start with `cortex-`
- **Hyphenated:** Multi-word commands use hyphens (e.g., `cortex-test-perf`)
- **Short:** Abbreviations when appropriate (e.g., `cortex-pfm`, `cortex-qr`)

---

## 🔗 Related Documentation

- **Tools Inventory:** `TOOLS-INVENTORY.md` - Complete tools list
- **Main README:** `README.md` - Usage guide
- **Manifest:** `toolkit-manifest.yaml` - Tool registry
- **Architecture Plan:** `../cortex-brain/documents/planning/CORTEX-TOOLKIT-ARCHITECTURE-PLAN.md`

---

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX
