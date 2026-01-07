# CORTEX Toolkit - Brain Operations

Brain tier operations for CORTEX system maintenance and health.

## Tools

### align (`cortex-align`)

**Purpose:** System alignment and consistency checks across all brain tiers.

**Usage:**
```bash
python cortex-toolkit/core/brain/align.py
python cortex-toolkit/shared/toolkit_registry.py invoke align
```

**Implementation:** `cli/wrappers/align_wrapper.py`

---

### healthcheck (`cortex-health`)

**Purpose:** Comprehensive system health diagnostics for all CORTEX components.

**Usage:**
```bash
python cortex-toolkit/core/brain/healthcheck.py
python cortex-toolkit/shared/toolkit_registry.py invoke healthcheck
```

**Implementation:** `cli/wrappers/healthcheck_wrapper.py`

---

### optimize (`cortex-optimize`)

**Purpose:** System optimization and performance tuning.

**Usage:**
```bash
python cortex-toolkit/core/brain/optimize.py
python cortex-toolkit/shared/toolkit_registry.py invoke optimize
```

**Implementation:** `cli/wrappers/optimize_wrapper.py`

---

### cleanup (`cortex-cleanup`)

**Purpose:** System cleanup and maintenance operations.

**Usage:**
```bash
python cortex-toolkit/core/brain/cleanup.py
python cortex-toolkit/shared/toolkit_registry.py invoke cleanup
```

**Implementation:** `cli/wrappers/cleanup_wrapper.py`

---

## Architecture

All brain operations follow a delegator pattern:
1. Core script (`core/brain/*.py`) delegates to CLI wrapper
2. CLI wrapper (`cli/wrappers/*_wrapper.py`) contains implementation
3. Toolkit registry provides unified invocation interface

## Common Options

Most brain operations support:
- `--check-only` - Dry run mode
- `--verbose` - Detailed output
- `--help` - Show usage information
