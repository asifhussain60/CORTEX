# KDS Legacy Archive

**Date Archived:** November 6, 2025  
**Reason:** Rebranding from KDS to CORTEX  
**Status:** Historical Reference Only

---

## What Happened?

The **KDS** (Key Data Streams) system has been officially rebranded to **CORTEX** (Cognitive Operations and Reasoning TEXture) as part of the project's evolution and independence strategy.

## Files Archived

- `kds-entry-point-legacy.md` - The original KDS Universal Entry Point (4422 lines)

## Migration Details

### What Changed?

1. **Entry Point Renamed:**
   - Old: `prompts/user/kds.md`
   - New: `prompts/user/cortex.md`

2. **Branding Updated:**
   - All references to "KDS" → "CORTEX"
   - All paths like `kds-brain` → `cortex-brain`
   - All configs like `kds.config.json` → `cortex.config.json`

3. **New Shortcuts Created:**
   - Shell alias: `cortex` - Opens CORTEX entry point in VS Code
   - Shell alias: `cdcortex` - Navigate to CORTEX directory
   - Script: `run-cortex.sh` - Quick launcher for CORTEX

### How to Use CORTEX Now

**In GitHub Copilot Chat:**
```
#file:/Users/asifhussain/PROJECTS/CORTEX/prompts/user/cortex.md

[Your request here]
```

**From Terminal:**
```bash
# Open CORTEX entry point
cortex

# Or run the launcher script
./run-cortex.sh

# Navigate to CORTEX project
cdcortex
```

## Why This Archive Exists

This archive preserves the original KDS entry point for:
- Historical reference
- Rollback capability (if needed)
- Documentation of the migration process
- Future comparisons and audits

## Related Documentation

- **Migration Plan:** `cortex-design/IMPLEMENTATION-PLAN-V3.md`
- **CORTEX DNA:** `cortex-design/CORTEX-DNA.md`
- **Migration Strategy:** `cortex-design/MIGRATION-STRATEGY.md`

---

**DO NOT USE FILES IN THIS ARCHIVE FOR ACTIVE DEVELOPMENT**

Use `prompts/user/cortex.md` instead.
