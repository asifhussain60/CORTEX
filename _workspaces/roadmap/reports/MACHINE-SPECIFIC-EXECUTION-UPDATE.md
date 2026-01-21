# Machine-Specific Execution Enhancement
**Date:** 2026-01-21  
**Authority:** cortex-builder.prompt.md v2.0  
**Status:** ✅ IMPLEMENTED

## Summary

Updated `cortex-builder.prompt.md` to support efficient machine-specific phase execution, enabling autonomous filtering and execution of phases based on `machine` property.

## Changes Made

### 1. New Machine-Specific Execution Section (Top of File)
- **Location:** Lines 6-25
- **Purpose:** Define behavior when user specifies `machine:mac` or `machine:win`
- **Key Features:**
  - Immediate filtering of cortex-impl-map.yaml
  - Autonomous execution without confirmation prompts
  - Sequential execution of all machine-specific phases

### 2. Enhanced Status Commands
- **Location:** Lines 138-143
- **New Commands:**
  - `/status machine:mac` → Show all mac-assigned phases
  - `/status machine:win` → Show all win-assigned phases  
  - `/next machine:mac` → Next incomplete phase for mac
  - `/next machine:win` → Next incomplete phase for win

### 3. Updated Executive Summary Format
- **Location:** Lines 149-205
- **Changes:**
  - Added machine label to phase titles
  - Conditional behavior: skip "Proceed?" when machine specified
  - New completion message for machine-specific completion
  - "Continuing to PHASE-YY (machine:X)..." auto-advancement

### 4. Enhanced Response Guidelines
- **Location:** Lines 210-241
- **New Section:** "Machine-Specific Execution Mode"
  - Fully autonomous execution
  - No confirmation prompts between phases
  - Strict filtering by machine property
  - Brief status updates only

### 5. Updated Critical Rules
- **Location:** Lines 318-323
- **Exception Added:** Skip confirmation when machine specified
- **New Rule:** Machine filtering requirement

### 6. New Machine-Specific Workflow
- **Location:** Lines 328-350
- **Workflow Details:**
  1. Load cortex-impl-map.yaml
  2. Filter by machine property
  3. Sort by priority (P0→P1→P2→P3)
  4. Execute all phases autonomously
  5. Output completion summary

## Machine Assignments in cortex-impl-map.yaml

### Mac-Assigned Phases (3 phases)
1. **impl-export-completion** (Phase F)
   - Priority: P0-CRITICAL
   - Effort: 4-6 hours (1 day)
   - Purpose: Add 44 missing exports

2. **impl-circular-import-fix** (Phase G)
   - Priority: P0-CRITICAL
   - Effort: 1-2 days
   - Purpose: Fix 15 RecursionErrors
   - Depends on: impl-export-completion

3. **PHASE-E-TDD-IMPLEMENTATION**
   - Priority: P0-CRITICAL
   - Effort: 15-20 days
   - Purpose: Implement 125 modules (76 errors → 0)
   - Depends on: impl-export-completion, impl-circular-import-fix

### Win-Assigned Phases (5 phases)
1. **impl-e2e-validation** (Phase H)
   - Priority: P1-HIGH
   - Effort: 3-4 days
   - Purpose: E2E test suite

2. **impl-cicd-validation** (Phase I)
   - Priority: P1-HIGH
   - Effort: 2-3 days
   - Purpose: Pipeline validation

3. **impl-governance-content** (Phase J)
   - Priority: P1-MEDIUM
   - Effort: 2-3 days
   - Purpose: Tier1/tier2 rules

4. **impl-features-registry-001**
   - Priority: P1
   - Effort: 6-9 hours
   - Purpose: Live manifest system

5. **cortex-registry-001-migration**
   - Priority: P0
   - Effort: 18-21 hours
   - Purpose: Folder structure migration

## Usage Examples

### Mac Development Session
```
User: "continue with machine:mac"
Assistant Actions:
1. Filters cortex-impl-map.yaml for machine: "mac"
2. Identifies: impl-export-completion (NOT_STARTED, P0-CRITICAL)
3. Executes Phase F autonomously:
   - Adds 44 missing exports
   - Runs tests to verify
   - Updates cortex-impl-map.yaml
4. Moves to Phase G (impl-circular-import-fix) WITHOUT PAUSING
5. Executes Phase G:
   - Fixes 15 RecursionErrors
   - Tests verify 0 collection errors
6. Moves to PHASE-E (TDD Implementation)
7. Continues until all mac phases complete

Output: Brief summaries after each phase, no confirmation prompts
```

### Windows Development Session
```
User: "continue with machine:win"

Assistant Actions:
1. Filters for machine: "win"
2. Identifies: cortex-registry-001-migration (P0)
3. Checks dependencies: impl-recovery-003 ✓, impl-ops-004 ✓
4. Executes registry migration autonomously
5. Moves to impl-e2e-validation (P1-HIGH)
6. Executes E2E test suite creation
7. Continues through all win phases

Output: Status updates only, fully autonomous
```

## Benefits

- **Efficiency:** No context switching between phases
- **Autonomous:** No confirmation prompts
- **Parallel:** Mac + Win developers work independently
- **Clear:** Explicit machine assignments

## Verification

```bash
# Check machine assignments
grep "machine:" _workspaces/roadmap/cortex-impl-map.yaml

# Verify prompt updates  
grep "machine:" .github/prompts/cortex-builder.prompt.md
```

---

**Status:** ✅ Ready for use
**Next:** Execute `continue with machine:mac` to test
