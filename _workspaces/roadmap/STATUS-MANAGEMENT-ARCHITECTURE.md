# Status Management Architecture - Single Source of Truth

**Date:** 2026-01-22  
**Authority:** cortex-builder.prompt.md + governance enforcement  
**Status:** IMPLEMENTED ✅

## Overview

This document clarifies the separation of concerns for phase status tracking in CORTEX to eliminate confusion and establish a single source of truth.

## Architecture Decision

### ✅ AUTHORIZED: cortex-impl-map.yaml
**Role:** Centralized phase execution state management  
**Content:** Real-time status, execution history, test results, timestamps  
**Authority:** Single source of truth for all phase status information

**Status Fields in cortex-impl-map.yaml:**
```yaml
phase_execution_tracking:
  {machine}_track_state:
    phase_states:
      - phase_id: "phase-name"
        status: "PENDING | EXECUTING | COMPLETED | BLOCKED | SKIPPED"
        executed_by: "machine:mac/win/eval"
        start_time: "ISO-8601 timestamp"
        end_time: "ISO-8601 timestamp"
        duration_seconds: number
        passed: boolean
        error_message: string or null
        notes: "execution details"
        # ... additional fields
```

### ❌ PROHIBITED: Phase YAML Files
**Role:** Implementation specifications only  
**Content:** Acceptance criteria, dependencies, governance rules, effort estimates  
**Restriction:** NO execution status fields (status, completion_date, executed_by, etc.)

**Prohibited in phase/*.yaml files:**
```yaml
metadata:
  status: "NOT_STARTED" | "IN_PROGRESS" | "COMPLETED"  # ❌ USE cortex-impl-map.yaml INSTEAD
  completion_date: "2026-01-22"  # ❌ USE phase_execution_tracking INSTEAD
  executed_by: "machine:mac"  # ❌ USE phase_execution_tracking INSTEAD
  last_updated: "timestamp"  # ❌ USE phase_execution_tracking INSTEAD
```

## Current State Verification

### cortex-impl-map.yaml Status
✅ **IMPLEMENTED** - Contains complete `phase_execution_tracking` section with:
- Machine-specific tracks (mac, win, eval)
- Phase execution states with timestamps
- Test pass rates and error tracking
- Dependency resolution information
- Comprehensive audit trail

**Location:** Line 3399+  
**Structure:** Hierarchical by machine track with detailed phase_states array

### Phase YAML Files Status
✅ **CLEAN** - No YAML-structured execution status fields found

**Verification Results:**
```
grep -r "^  status:" phases/ → NO MATCHES
grep -r "^  completion_date:" phases/ → NO MATCHES
grep -r "^  executed_by:" phases/ → NO MATCHES
```

**Note:** Some phase files contain status references in:
- Comments (e.g., `# Status: in_progress`)
- Markdown text blocks (e.g., `**Phase Status:** ✅ COMPLETE`)

These are informational only and do not affect YAML structure. They may be removed or preserved per file discretion since they are not authoritative (cortex-impl-map.yaml is authoritative).

## Sync Protocol

When updating phase status:

1. **Machine Track Executes Phase**
   - Phase YAML file contains only specifications
   - No status modifications to phase file

2. **Autonomous Loop Updates cortex-impl-map.yaml**
   ```yaml
   phase_execution_tracking.{machine}_track_state.phase_states:
     - phase_id: "name"
       status: "COMPLETED"  # ← Update here ONLY
       end_time: "timestamp"
       passed: true/false
   ```

3. **Query Phase Status**
   - Always read from: `cortex-impl-map.yaml` → `phase_execution_tracking`
   - Never query: Individual phase YAML files

## Governance Rules

| Rule | Requirement | Enforcement |
|------|-------------|-------------|
| **CORE-SYNC-001** | All phase status must be in cortex-impl-map.yaml | Audit script validates before execution |
| **CORE-SYNC-002** | Phase YAML files contain specifications only | Phase loader ignores execution fields |
| **CORE-SYNC-003** | Single source of truth for status | Automated audit prevents duplicate records |
| **CORE-SYNC-004** | Status queries must use cortex-impl-map.yaml | Phase loader provides read-only interface to phase specs |

## Benefits of This Architecture

1. **No Duplication** - Status exists in exactly one place
2. **No Conflicts** - No risk of phase file and cortex-impl-map.yaml getting out of sync
3. **Clear Roles** - Phase YAML = specs, cortex-impl-map.yaml = execution state
4. **Audit Trail** - All status changes logged in centralized location
5. **Autonomous Friendly** - Machine loops can update single file (cortex-impl-map.yaml)
6. **Version Control** - Phase YAML changes indicate spec updates, not execution state

## Verification Checklist

- [x] cortex-impl-map.yaml has `phase_execution_tracking` section with all phases
- [x] Phase YAML files contain no YAML-structured status/completion_date fields
- [x] Informational status references (comments/markdown) do not affect YAML parsing
- [x] Governance rules documented (CORE-SYNC-001 through CORE-SYNC-004)
- [x] Autonomous execution loops configured to update cortex-impl-map.yaml only
- [x] Single source of truth established and documented

## Testing This Architecture

```bash
# Verify cortex-impl-map.yaml is valid YAML with phase_execution_tracking
python3 -c "import yaml; yaml.safe_load(open('cortex-impl-map.yaml'))" && echo "✓ Valid YAML"

# Verify all phases in cortex-impl-map.yaml
grep -c "phase_id:" cortex-impl-map.yaml

# Verify no status fields in phase YAML files
cd phases && grep -r "^  status:" . && echo "❌ Found status in phase files" || echo "✓ No status in phase files"
```

## Next Steps

No action required - architecture is fully implemented. Phase YAML files naturally contain only specifications (ACs, dependencies, governance rules) and execution status is managed exclusively through cortex-impl-map.yaml.

---

**Authorized By:** cortex-builder.prompt.md  
**Enforced By:** CORE-SYNC governance rules  
**Last Verified:** 2026-01-22  
**Status:** STABLE ✅
