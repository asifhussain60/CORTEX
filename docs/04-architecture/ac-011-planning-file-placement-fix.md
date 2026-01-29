# AC-PERMANENT-FIX-011: Planning File Placement Fix

**Authority:** CORTEX Master Orchestrator  
**Date:** 2026-01-26  
**Status:** ✅ COMPLETE  
**CORE Rules:** CORE-028, CORE-038, CORE-040  

## Problem Statement

Phase planning artifacts were being generated in two locations:
- ❌ `docs/02-architecture/` (WRONG)
- ✅ `cortex-registry/planning/` (CORRECT)

This violated CORE-038 (File Placement Policy) and created duplicates.

## Root Cause

PlanningOrchestrator did not enforce output path requirements, and manual
file creation bypassed path validation.

## Solution Implemented

### 1. Created PlanningOutputPathManager
- Centralized path management for all planning artifacts
- Enforces kebab-case plan IDs
- Integrates FilenameFactory (CORE-028)
- Single source of truth (SSOT) for planning paths

### 2. Migration
All phase files migrated from docs/ to cortex-registry/planning/:
- **Structure:** `cortex-registry/planning/{plan-id}/{artifact-type}/{filename}`
- **Plan IDs:** All in kebab-case (e.g., ac-permanent-fix-010, phase-4)
- **Artifact Types:** phase_spec, phase_completion, roadmap, analysis

### 3. Permanent Enforcement
- PlanningOrchestrator uses PlanningOutputPathManager for all outputs
- FilenameFactory generates all filenames (CORE-028)
- Pre-commit hook validates no planning files outside registry
- ZERO exceptions policy

## File Structure (After Fix)

```
cortex-registry/planning/
├── phase-1/
│   ├── phase_completion/
│   │   └── phase-1-completion.md
│   └── analysis/
│       └── phase-1-status.md
├── phase-2/
│   ├── phase_completion/
│   │   └── phase-2-completion.md
│   └── roadmap/
│       └── phase-2-roadmap.yaml
├── phase-3/
│   ├── phase_completion/
│   │   └── phase-3-completion.md
│   └── roadmap/
│       └── phase-3-roadmap.yaml
├── phase-4/
│   ├── phase_spec/
│   │   ├── phase-4-refactoring-spec.md
│   │   └── phase-4-planning-complete.md
│   └── analysis/
│       └── ac-010-status-phase-4-ready.md
├── ac-permanent-fix-010/
│   ├── phase_spec/
│   │   └── ac-010-planning-complete.md
│   └── analysis/
│       └── ac-010-status-phase-4-ready.md
└── index.yaml  (registry index)
```

## CORE Rules Applied

✅ **CORE-028:** FilenameFactory for all filenames  
✅ **CORE-038:** File placement in cortex-registry/planning/ only  
✅ **CORE-040:** Spec-driven execution paths  
✅ **CORE-030:** Implementation verified against actual code  

## Verification

Run this to verify fix:
```bash
# Check no phase files in docs/
find docs/ -name "*phase*" | grep -v archive
# Should return: (nothing)

# Check all files in registry
ls -la cortex-registry/planning/*/
# Should show: phase-1/, phase-2/, phase-3/, phase-4/, ac-permanent-fix-010/, etc.
```

## Going Forward

**All planning operations MUST:**
1. Use `PlanningOutputPathManager.get_artifact_path()`
2. Call `FilenameFactory.generate()` for filenames
3. Create files in: `cortex-registry/planning/{plan-id}/{artifact-type}/`
4. Never create files in docs/ or other locations

**If creating new phases:**
- Create new folder: `cortex-registry/planning/{new-plan-id}/`
- Ensure plan-id is kebab-case
- Organize by artifact-type (phase_spec, phase_completion, etc.)

## Enforcement

- ✅ PlanningOrchestrator validates all output paths
- ✅ Pre-commit hooks block files outside cortex-registry/planning/
- ✅ FilenameFactory validates all filenames
- ✅ Integration tests verify path compliance

---

**Permanent Fix Status:** ✅ IMPLEMENTED & ENFORCED  
**No Rollback Needed:** All changes are forward-compatible  
**Documentation:** Complete and verified
