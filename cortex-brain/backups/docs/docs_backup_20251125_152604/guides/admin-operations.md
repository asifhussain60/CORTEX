# Admin Operations Guide

**Last Updated:** November 25, 2025  
**Author:** Asif Hussain  
**Status:** Production

---

## Overview

CORTEX provides admin-only operations for CORTEX development repository maintenance and optimization. These operations are **only available in the CORTEX development repository** (contains `cortex-brain/admin/` directory).

**Admin Detection:** CORTEX auto-detects admin environment by checking for:
- `cortex-brain/admin/` directory
- `src/operations/modules/admin/` directory

---

## System Alignment (`align`)

**Purpose:** Convention-based discovery and validation of all CORTEX enhancements without hardcoded lists.

**Commands:**
- `align` - Run full system alignment validation
- `align report` - Generate detailed alignment report with auto-remediation suggestions

### How It Works

**7-Layer Integration Scoring (0-100%):**
1. **Discovered** (20 pts) - Feature file exists in expected location
2. **Imported** (20 pts) - Module imports successfully
3. **Instantiable** (20 pts) - Class can be instantiated
4. **Documented** (10 pts) - Has user-facing documentation
5. **Tested** (10 pts) - Has test coverage
6. **Wired** (10 pts) - Connected to entry point
7. **Optimized** (10 pts) - Performance validated

**Health Status:**
- ✅ **Healthy** (90-100%) - Fully integrated
- ⚠️ **Warning** (70-89%) - Minor issues
- ❌ **Critical** (<70%) - Requires attention

### Key Features

**Convention-Based Discovery:**
- Auto-scans `src/operations/modules/` for orchestrators
- Auto-scans `src/agents/` for agents  
- Zero maintenance when adding features

**Auto-Remediation:**
- Generates wiring templates for unconnected features
- Creates test skeletons for untested modules
- Suggests documentation structure for undocumented features

**Integration with Optimize:**
- Runs silently during `optimize` command
- Reports critical issues only
- Non-blocking (doesn't fail optimize on warnings)

### Example Output

```
🧠 CORTEX System Alignment
==========================================

📊 Discovery Results:
  Orchestrators: 12 found
  Agents: 8 found
  Entry Points: 5 found

🎯 Integration Scores:
  ✅ SystemAlignmentOrchestrator: 100% (Healthy)
  ⚠️  ViewDiscoveryAgent: 80% (Warning - Missing tests)
  ❌ NewFeature: 40% (Critical - Not wired)

⚙️ Auto-Remediation Suggestions:
  1. Add test: tests/agents/test_view_discovery_agent.py
  2. Wire NewFeature to cortex-operations.yaml
  3. Document NewFeature in docs/reference/

Overall Health: 87% (Warning)
```

**Reference:** `docs/reference/scripts/operations/system-alignment-orchestrator.md`

---

## Cleanup Operations (`cleanup`)

**Purpose:** Clean CORTEX brain data, remove old files, vacuum databases.

**Commands:**
- `cleanup` or `clean up` - Run all cleanup operations
- `cleanup dry run` - Preview what would be cleaned without changes

### What Gets Cleaned

1. **Old conversation captures** (>30 days in `cortex-brain/conversation-captures/`)
2. **Temporary crawler files** (`cortex-brain/crawler-temp/`)
3. **Old logs** (>7 days in `logs/`, `sweeper-logs/`)
4. **SQLite databases** (VACUUM to reclaim space)
5. **Orphaned files** (files without corresponding database entries)

### Space Savings

**Typical Results:**
- Space saved: 50-200 MB
- Database size reduction: 20-40%
- Performance improvement: 10-30% faster operations

**Reference:** `docs/reference/scripts/operations/cleanup-orchestrator.md`

---

## Design Sync (`design sync`)

**Purpose:** Synchronize design documentation with implementation.

**Commands:**
- `design sync` - Sync all design documentation
- `design sync [module]` - Sync specific module documentation

### What Gets Synced

1. **Architecture diagrams** - Updated with latest module structure
2. **Integration diagrams** - Updated with current wiring
3. **API documentation** - Regenerated from docstrings
4. **Module references** - Updated with new features

**Reference:** `docs/reference/scripts/operations/design-sync-orchestrator.md`

---

## Documentation Generation (`generate docs`)

**Purpose:** Generate comprehensive MkDocs documentation with diagrams and guides.

**Commands:**
- `generate docs` - Standard documentation generation
- `generate docs dry run` - Preview generation without changes
- `generate docs quick` - Fast generation (skip diagrams)
- `generate docs comprehensive` - Full generation with all features

### Features

1. **Architecture diagrams** - Auto-generated from code structure
2. **API reference** - Extracted from docstrings
3. **Real Live Data dashboards** (if analytics data exists)
4. **Cross-references** - Automatic link validation

### Profiles

- **quick** (30 sec) - Basic docs, no diagrams
- **standard** (2 min) - Full docs with key diagrams
- **comprehensive** (5 min) - Everything including optional features

**Reference:** `src/operations/modules/documentation/enterprise_documentation_orchestrator_module.py`

---

## Feedback Review (`review feedback`)

**Purpose:** Aggregate and analyze feedback reports from multiple user repositories.

**Commands:**
- `review feedback` - Sync Gist registry and process all feedback
- `feedback analytics` - Show aggregated analytics dashboard

### Features

1. **Gist Sync** - Downloads feedback from GitHub Gists
2. **Analytics DB** - Stores feedback in `cortex-brain/analytics/analytics.db`
3. **Trend Analysis** - Identifies common issues and patterns
4. **Admin Dashboard** - Visualizes feedback metrics

**Prerequisites:**
- GitHub token configured in `cortex.config.json`
- Admin environment (CORTEX repo only)

**Reference:** `src/operations/modules/feedback/enhanced_feedback_module.py`

---

## Upgrade System

**Purpose:** Manage CORTEX upgrades with zero data loss.

### Commands

- `upgrade` or `upgrade cortex` - Upgrade to latest version
- `upgrade --version X.Y.Z` - Upgrade to specific version
- `upgrade --dry-run` - Preview upgrade without changes

### Features

**Intelligent Upgrade Method:**
- Git-based (if git repository with remote configured)
- Download-based (file copy for embedded installations)
- Auto-detects installation type

**Safety Features:**
- Automatic brain backup before upgrade
- Path validation (prevents file corruption)
- Post-upgrade validation
- Rollback on failure

**Version Detection:**
- Supports plain text VERSION file (`v3.2.0`)
- Supports legacy JSON VERSION file
- Auto-strips `v` prefix for comparison

**Reference:** `docs/reference/scripts/operations/upgrade-orchestrator.md`

---

## Best Practices

### When to Use Admin Operations

**Daily Development:**
- Run `align` after adding new features
- Run `cleanup` weekly to reclaim space
- Run `design sync` before documentation releases

**Before Deployment:**
- Run `align` to verify all features integrated
- Run `generate docs` to update public documentation
- Run `review feedback` to address user issues

**After Major Changes:**
- Run `align` to detect integration gaps
- Run `cleanup` to remove obsolete files
- Run `upgrade` to test upgrade path

### Admin Environment Setup

**Required Directory Structure:**
```
CORTEX/
├── cortex-brain/
│   └── admin/                    # Admin marker
├── src/
│   └── operations/
│       └── modules/
│           └── admin/            # Admin operations
└── docs/
```

**Not Available In:**
- User repositories (embedded CORTEX installations)
- Standalone CORTEX installations without admin directory

---

## Troubleshooting

### "Admin-only operation" Error

**Cause:** Operation attempted in non-admin environment.

**Solution:** These operations only work in CORTEX development repository with `cortex-brain/admin/` directory.

### Alignment Reports Issues

**Cause:** Missing discovery scanners or database schema.

**Solution:** Run `setup environment` to verify all dependencies installed.

### Feedback Review Empty

**Cause:** No GitHub token configured or no feedback Gists found.

**Solution:** 
1. Add GitHub token to `cortex.config.json`
2. Ensure users have uploaded feedback via `feedback` command

---

## Related Documentation

- **System Alignment Reference:** `docs/reference/scripts/operations/system-alignment-orchestrator.md`
- **Upgrade Guide:** `.github/prompts/modules/upgrade-guide.md`
- **Feedback System:** `.github/prompts/CORTEX.prompt.md` (Feedback section)
- **Cleanup Rules:** `cortex-brain/cleanup-rules.yaml`

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
