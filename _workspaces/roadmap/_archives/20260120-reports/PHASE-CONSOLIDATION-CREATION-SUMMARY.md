# PHASE-CONSOLIDATION-SRC-CORTEX: Remediation Plan Created

**Date:** 2026-01-20  
**Status:** ✅ PHASE CREATED, READY FOR EXECUTION  
**Priority:** P0 CRITICAL BLOCKER  
**Blocks:** All production phases until complete

---

## Executive Summary

**Problem Found:** CORTEX has TWO source folders creating critical import failures:
- `src/` → 79 files (incomplete, no root `__init__.py`)
- `cortex/` → 388 files (complete with `__init__.py`)
- Tests import from `src.*` but implementations in `cortex.*` → **170+ ModuleNotFoundError**

**Root Cause:** Not missing code. Not platform issue. **DUAL FOLDER AMBIGUITY.**

**Solution:** **Single canonical source folder: `cortex/`**

---

## Analysis Completed

### Delivered Artifacts

| Document | Location | Purpose |
|----------|----------|---------|
| **Consolidation Analysis** | `_workspaces/roadmap/reports/CONSOLIDATION-ANALYSIS-SRC-VS-CORTEX.md` | Full root cause & recommendation |
| **Phase Specification** | `_workspaces/roadmap/phases/phase-consolidation-src-cortex.yaml` | 5 ACs, 9.5h effort, acceptance criteria |
| **Master Roadmap** | `_workspaces/roadmap/cortex-master.yaml` (UPDATED) | Added phase to tracker, updated status |

### Key Findings

**Current State:**
```
src/               (79 files - LEGACY)          cortex/         (388 files - CANONICAL)
├── core/*         (37 files)                   ├── core/*       (17 files)
├── orchestrators/ (11 files)                   ├── orchestrators/ (41 files)
├── infrastructure/(3 files)  ← MINIMAL         ├── infrastructure/ (22 files) ← COMPLETE
├── mcp/           (10 files)                   ├── brain/       (269 files)
├── tools/         (1 file)                     ├── api/         (8 files)
├── deployment/    (10 files) ← UNIQUE         └── tools/       (16 files)
├── complexity/    (2 files)  ← UNIQUE
├── confirmation/  (4 files)  ← UNIQUE
├── versioning/    (1 file)   ← UNIQUE
└── NO __init__.py ❌ CRITICAL              └── __init__.py   ✅ CORRECT
```

**Why Two Folders?** Migration in progress: Code moved src → cortex but test imports not updated

---

## Remediation Phase Created

### PHASE-CONSOLIDATION-SRC-CORTEX

**Goal:** Establish cortex/ as single canonical source location

**5 Acceptance Criteria:**

| AC | Title | Effort |
|----|-------|--------|
| AC-CONS-001-01 | Audit & validate src/ vs cortex/ content | 1h |
| AC-CONS-002-01 | Archive & migrate unique src/ content | 1h |
| AC-CONS-003-01 | Refactor all test imports (src.* → cortex.*) | 3h |
| AC-CONS-003-02 | Update conftest.py path resolution | 0.5h |
| AC-CONS-004-01 | Validate test collection & verify execution | 1h |
| AC-CONS-004-02 | Execute full test suite & baseline metrics | 2h |
| AC-CONS-005-01 | Documentation & status updates | 1h |

**Total:** 9.5 hours, 409+ tests

---

## Changes to cortex-master.yaml

### Added

**PHASE-CONSOLIDATION-SRC-CORTEX** (new)
- Status: NOT_STARTED
- Locked: false
- Blocking: true
- Requires: PHASE-ENV-SETUP
- Required_for: PHASE-ONBOARDING-ORCHESTRATOR

### Updated

**PHASE-REMEDIATION-CROSS-PLATFORM**
- Status: SUPERSEDED_BY_CONSOLIDATION
- Blocking: false (consolidated into new phase)
- Note: Root cause analysis identified real issue was dual folders, not missing code

**PHASE-ONBOARDING-ORCHESTRATOR**
- Status: BLOCKED_AWAITING_CONSOLIDATION (changed from COMPLETED)
- Locked: false (changed from true)
- Notes: Reason for unblock = no working test suite

### Metadata Updated

- `status`: Now reflects blocker: "PHASE-CONSOLIDATION-SRC-CORTEX required"
- `total_ac_ids`: 112 (107 complete + 5 new from consolidation)
- `completion_percentage`: 95.5% (up from 100%, reflecting realistic state)
- `pending_phases`: 1 (CONSOLIDATION)
- `blocking_phase`: PHASE-CONSOLIDATION-SRC-CORTEX

---

## Success Criteria (When Complete)

✅ **After PHASE-CONSOLIDATION-SRC-CORTEX:**
- Zero ModuleNotFoundError on pytest collection
- All 409 tests discoverable
- Single canonical source: cortex/
- All downstream phases unblocked
- Test suite executable (pass/fail baseline established)
- Governance compliance verified (CORE-008 TDD can now be validated)

---

## Impact Assessment

| Stakeholder | Impact | Timeline |
|-------------|--------|----------|
| CI/CD Pipeline | UNBLOCKED | After AC-CONS-004-01 complete |
| Production Phases | UNBLOCKED | After AC-CONS-005-01 complete |
| Developers | Clarity gained | Immediately upon phase lock |
| Test Coverage | Executable | Phase completion |

---

## Next Steps (Recommended)

1. **Review** analysis document: `CONSOLIDATION-ANALYSIS-SRC-VS-CORTEX.md`
2. **Confirm** cortex-builder.prompt.md to start implementation
3. **Execute** ACs in sequence: AC-001 → AC-002 → AC-003 → AC-004 → AC-005
4. **Git checkpoint** at each AC completion (CORE-026 governance)
5. **Lock phase** when all 5 ACs complete and 409 tests pass collection

---

## Resources

- **Analysis:** `_workspaces/roadmap/reports/CONSOLIDATION-ANALYSIS-SRC-VS-CORTEX.md`
- **Phase Spec:** `_workspaces/roadmap/phases/phase-consolidation-src-cortex.yaml`
- **Master Plan:** `_workspaces/roadmap/cortex-master.yaml` (lines 4700-4800 approx)
- **Governance:** Follow cortex-builder.prompt.md for CORE-008, CORE-026, CORE-027 compliance

---

## Status Update

**Before:** "CORTEX 100% complete, all phases locked" ❌ Incorrect (tests don't run)  
**Now:** "PHASE-CONSOLIDATION-SRC-CORTEX blocks all production work" ✅ Accurate  
**Path Forward:** Single phase, 9.5 hours, then all downstream work unblocked

---

**Prepared by:** CORTEX Analysis Agent  
**Verified by:** Consolidation analysis methodology  
**Ready for:** cortex-builder implementation
