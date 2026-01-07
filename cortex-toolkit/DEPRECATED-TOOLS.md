# Deprecated Tools

**Version:** 1.0.0  
**Last Updated:** December 31, 2025  
**Author:** Asif Hussain

This document lists all deprecated tools in the CORTEX Toolkit, along with their replacement, removal timeline, and migration guidance.

---

## Overview

| Tool | Status | Replacement | Removal Date |
|------|--------|-------------|--------------|
| `cleanup-temp` | ⚠️ Deprecated | `cleanup --mode=temp` | 2026-03-31 |
| `detect-duplicates` | ⚠️ Deprecated | `RequestAnalyzer` | 2026-03-31 |
| `rename-planning-system-version` | ⚠️ Deprecated | N/A | 2026-01-31 |
| `clear-caches` | ⚠️ Deprecated | `cleanup --mode=cache` | 2026-03-31 |

---

## Deprecated Tool Details

### cleanup-temp

**Status:** ⚠️ Deprecated  
**Deprecated:** 2025-12-31  
**Removal:** 2026-03-31  
**Replacement:** `cleanup --mode=temp`

#### Reason for Deprecation

This tool has been consolidated into the unified `cleanup` tool as part of Phase 8 (Migration & Cleanup) of the Toolkit Manager implementation. The unified cleanup tool provides all functionality with a consistent interface.

#### Migration Guide

```bash
# Before (deprecated)
cortex-cleanup-temp --path /path/to/clean

# After (recommended)
cortex-cleanup --mode=temp --path /path/to/clean

# Or use full cleanup
cortex-cleanup --mode=full
```

#### Feature Mapping

| Old Command | New Command |
|-------------|-------------|
| `cortex-cleanup-temp` | `cortex-cleanup --mode=temp` |
| `cortex-cleanup-temp --dry-run` | `cortex-cleanup --mode=temp --dry-run` |
| `cortex-cleanup-temp --verbose` | `cortex-cleanup --mode=temp -v` |

---

### detect-duplicates

**Status:** ⚠️ Deprecated  
**Deprecated:** 2025-12-31  
**Removal:** 2026-03-31  
**Replacement:** `RequestAnalyzer` (built into Toolkit Manager)

#### Reason for Deprecation

The `detect-duplicates` tool used simple content-based comparison for finding duplicate code. This has been superseded by the `RequestAnalyzer` component in the Toolkit Manager, which provides:

- **Semantic analysis** - Understands code meaning, not just text
- **Capability matching** - Detects functional overlap
- **Proactive prevention** - Blocks duplicate tool creation
- **Integration** - Works automatically with all toolkit operations

#### Migration Guide

The `RequestAnalyzer` is integrated into the Toolkit Manager and runs automatically. For manual duplicate detection:

```python
from core.request_analyzer import RequestAnalyzer, ToolRequest

analyzer = RequestAnalyzer(toolkit_root)

# Check if a new tool would duplicate existing functionality
request = ToolRequest(
    name="my-new-tool",
    description="Clean up temporary files",
    capabilities=["cleanup", "temp-files"]
)

result = analyzer.analyze_request(request)

if result.recommendation_type == RecommendationType.BLOCK:
    print(f"Similar tool exists: {result.overlapping_tools[0].name}")
```

#### Why RequestAnalyzer is Better

| Feature | detect-duplicates | RequestAnalyzer |
|---------|-------------------|-----------------|
| Analysis Type | Content hash | Semantic |
| Scope | Files only | Tools + capabilities |
| Prevention | Reactive | Proactive |
| Integration | Standalone | Built into Manager |
| Accuracy | Low (false positives) | High |

---

### rename-planning-system-version

**Status:** ⚠️ Deprecated  
**Deprecated:** 2025-12-31  
**Removal:** 2026-01-31  
**Replacement:** None (one-time utility)

#### Reason for Deprecation

This was a one-time migration utility created to rename "Planning System 3.0" references to "Planning System 4.0" across the codebase. The migration is complete, and this tool is no longer needed.

#### No Migration Required

This tool should not be used. All Planning System version references have been updated. If you need to update version references in the future, use standard find/replace or create a new versioned migration script.

---

### clear-caches

**Status:** ⚠️ Deprecated  
**Deprecated:** 2025-12-31  
**Removal:** 2026-03-31  
**Replacement:** `cleanup --mode=cache`

#### Reason for Deprecation

Consolidated into the unified `cleanup` tool for consistent interface and better maintainability.

#### Migration Guide

```bash
# Before (deprecated)
cortex-clear-caches

# After (recommended)
cortex-cleanup --mode=cache
```

---

## Deprecation Policy

### Timeline

1. **Announcement** (Day 0): Tool marked deprecated in manifest
2. **Warning Period** (90 days): Tool logs deprecation warning on use
3. **Removal** (Day 90+): Tool removed from manifest and codebase

### What Happens on Removal

- Tool entry removed from `toolkit-manifest.yaml`
- Tool script archived to `cortex-toolkit/archives/deprecated/`
- CLI command no longer available
- Documentation moved to historical reference

### Getting Help

If you're using a deprecated tool and need help migrating:

1. Check this document for migration guides
2. Run `cortex-<tool> --help` (while still available) for updated guidance
3. Consult `cortex-toolkit/docs/toolkit-manager-guide.md`
4. Open an issue if you need additional support

---

## Archived Tools

Tools that have been fully removed are archived here for historical reference.

| Tool | Removed | Reason | Archive Location |
|------|---------|--------|------------------|
| (none yet) | - | - | - |

---

## Adding Deprecation Notices

When deprecating a tool, update:

1. **toolkit-manifest.yaml** - Add `lifecycle: deprecated` fields
2. **tool-inventory.yaml** - Update lifecycle and add deprecation info
3. **This file** - Add entry with migration guide
4. **Tool script** - Add deprecation warning:

```python
import warnings
warnings.warn(
    "cortex-<tool> is deprecated and will be removed on YYYY-MM-DD. "
    "Use <replacement> instead.",
    DeprecationWarning
)
```

---

*Generated by CORTEX Toolkit Manager*  
*Last Updated: December 31, 2025*
