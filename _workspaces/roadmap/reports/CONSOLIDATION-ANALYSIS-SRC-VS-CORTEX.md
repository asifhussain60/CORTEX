# Folder Consolidation Analysis: src/ vs cortex/

**Date:** 2026-01-20  
**Author:** CORTEX Analysis Agent  
**Status:** ANALYSIS COMPLETE - Ready for Remediation Phase Creation

---

## Executive Summary

The CORTEX project has **TWO source folders** creating critical ambiguity:

| Folder | Files | Status | Structure | Import Pattern |
|--------|-------|--------|-----------|-----------------|
| `src/` | 79 | Incomplete | Missing `__init__.py` at root | None (broken) |
| `cortex/` | 388 | **CANONICAL** | Complete with `__init__.py` | `cortex.*` works |
| `cortex_brain/` | 13 | Support tier | Governance & state | `cortex_brain.*` |

**Problem:** Tests import from `src.*` but all implementations are in `cortex.*`

**Solution:** **Consolidate to single folder `cortex/` as canonical source location**

---

## Current State Analysis

### Folder Structure Inventory

**`src/` (79 files, incomplete):**
```
src/
├── core/                    (37 files) - partial: governance, knowledge, orchestrator
├── orchestrators/           (11 files) - partial implementation
├── mcp/                     (10 files) - partial
├── deployment/              (10 files)
├── tools/                   (1 file)
├── complexity/              (2 files)
├── confirmation/            (4 files)
├── infrastructure/          (3 files) - MINIMAL
├── versioning/              (1 file)
└── NO ROOT __init__.py      ❌ CRITICAL GAP
```

**`cortex/` (388 files, complete):**
```
cortex/
├── __init__.py              ✅ CANONICAL ROOT
├── core/                    (17 files) - config, discovery, governance, knowledge, registry, resilience, safety, schemas, security, state
├── orchestrators/           (41 files) - master, adaptive, execution context, etc.
├── infrastructure/          (22 files) - database, transaction manager, audit logger, etc.
├── brain/                   (269 files) - MCP, traits, tools, schemas, etc.
├── tools/                   (16 files)
├── api/                     (8 files)
├── mcp/                     (7 files)
└── scripts/                 (2 files)
```

**`cortex_brain/` (13 files, tier state):**
```
cortex_brain/
├── __init__.py              ✅ ROOT
├── tier0/                   - Governance rules
├── tier1/                   - Implementation tier
├── tier2/                   - Advanced tier
└── state/                   - Knowledge repository, state mgmt
```

### Import Conflict Analysis

**Test Files Expected:** `from src.core.config import ...`  
**Actual Location:** `cortex/core/config.py`  
**Result:** 170+ ModuleNotFoundError on pytest collection

### Module Distribution

**In both locations (overlap):**
- `core/`
- `orchestrators/`
- `infrastructure/`
- `mcp/`
- `tools/`

**Unique to `cortex/` (IMPLEMENTED):**
- `brain/` (269 files) - Most complete, integrated
- `api/`
- Various submodules (governance, resilience, safety, etc.)

**Unique to `src/` (LEGACY/INCOMPLETE):**
- `deployment/`
- `complexity/`
- `confirmation/`
- `versioning/`

---

## Root Cause Assessment

### Why Two Folders?

Evidence from commit history suggests:
1. **Migration attempt:** Code moved from `src/` → `cortex/` but not completed
2. **Dual maintenance:** Both folders kept during transition (incomplete)
3. **Test updates incomplete:** Tests still reference old `src.*` import paths
4. **conftest.py compensates:** Adds both to sys.path, but this is a workaround

### Why Tests Import from `src.*`

- Tests written during development
- Expected `src.core.config`, `src.infrastructure.database`, etc.
- Imports were not updated when code moved to `cortex/`
- conftest.py adds both paths but Python finds nothing in `src/` root (no `__init__.py`)

---

## Impact Assessment

### Current Risks

| Risk | Severity | Impact |
|------|----------|--------|
| Dual folder maintenance | HIGH | Code diverges, fixes applied to wrong folder |
| Import ambiguity | CRITICAL | Tests fail, CI/CD blocked |
| Missing `src/__init__.py` | HIGH | `src.core.*` imports fail at runtime |
| Test discoverability | CRITICAL | pytest cannot collect 170+ tests |
| Developer confusion | HIGH | Which folder is canonical? |

### Governance Impact

- **CORE-008 (TDD):** Tests cannot run → cannot verify compliance
- **CORE-026 (Git checkpoints):** Cannot mark work complete if tests don't run
- **CORE-027 (Audit trail):** Cannot log AC_START/EXECUTE/COMPLETE without working tests

---

## Consolidation Options

### Option A: Migrate to `cortex/` (RECOMMENDED ✅)

**Advantages:**
- ✅ 388 files already in `cortex/` = complete implementation
- ✅ `cortex/__init__.py` exists and is properly configured
- ✅ Simplest: just update test imports
- ✅ Brain integration (269 files) already in cortex/
- ✅ Aligns with current sys.path setup

**Steps:**
1. Update all test imports: `src.*` → `cortex.*`
2. Delete empty `src/` (or archive)
3. Update conftest.py to remove `src` path entry
4. Verify all 409 tests discover and run

**Effort:** 4-6 hours

---

### Option B: Consolidate to `src/` (NOT RECOMMENDED ❌)

**Disadvantages:**
- Need to move 388 files from cortex → src
- Brain (269 files) integration would break
- More error-prone
- Reverses recent migration work

**Effort:** 16-20 hours (high risk)

---

### Option C: Create import shim (TEMPORARY WORKAROUND ❌)

**Not recommended:** Masks underlying problem, creates tech debt

---

## Recommended Remediation Path

### Phase Design: PHASE-CONSOLIDATION-SRC-CORTEX (New)

**Goal:** Single canonical source folder `cortex/`

**ACs:**

| AC | Title | Effort | Blocker |
|----|-------|--------|---------|
| AC-CONS-001-01 | **Audit & Validate Migration** - Catalog what's in src/ vs cortex/, identify unique content | 1h | NO |
| AC-CONS-002-01 | **Archive `src/` Legacy Content** - Move unique src/ files (deployment, complexity, confirmation, versioning) to `cortex/` or `_archives/` | 1h | YES |
| AC-CONS-002-02 | **Delete Duplicate `src/` Modules** - Remove core/, orchestrators/, infrastructure/, mcp/, tools/ from `src/` (duplicates) | 0.5h | YES |
| AC-CONS-003-01 | **Refactor Test Imports** - Update all 409 test files: `from src.*` → `from cortex.*` | 3h | **CRITICAL** |
| AC-CONS-003-02 | **Update conftest.py** - Remove `src` from sys.path, verify cortex path resolution | 0.5h | YES |
| AC-CONS-004-01 | **Validate Test Collection** - Run pytest --collect-only, verify 0 import errors | 1h | YES |
| AC-CONS-004-02 | **Execute Full Test Suite** - Run pytest, verify 100%+ test execution capability | 2h | YES |
| AC-CONS-005-01 | **Update Documentation** - cortex-master.yaml, prompts, README | 1h | NO |

**Total Estimated Effort:** 9.5 hours  
**Dependencies:** AC-CONS-001-01 → AC-CONS-002-01 → AC-CONS-003-01 → AC-CONS-004-01

---

## Unique Content in `src/` (Needs Handling)

### Investigation Results

Files ONLY in `src/`:
- `src/deployment/*` (10 files) - Deployment orchestration
- `src/complexity/*` (2 files) - Complexity analysis
- `src/confirmation/*` (4 files) - Confirmation logic
- `src/versioning/*` (1 file) - Version management

**Decision:** Move these to `cortex/` under appropriate subdirectories before deletion

---

## Test Import Refactoring Scope

**Scale:** 409 test files to update

**Pattern:** 
```python
# BEFORE
from src.core.config import Config
from src.infrastructure.database import DatabaseManager

# AFTER
from cortex.core.config import Config
from cortex.infrastructure.database import DatabaseManager
```

**Automation:** Use AST + regex replacement to minimize manual work

---

## Success Criteria

- ✅ Single canonical source folder: `cortex/`
- ✅ Zero import errors in pytest collection
- ✅ All 409 tests discoverable
- ✅ 100%+ test execution (pass/fail/error all execute)
- ✅ conftest.py correctly resolves `cortex.*` imports
- ✅ No remaining files in `src/` except legacy archives
- ✅ git checkpoint created at completion
- ✅ Audit trail: AC_START → AC_EXECUTE → AC_COMPLETE

---

## Governance Compliance

**Phases Blocked Until Complete:**
- PHASE-ONBOARDING-ORCHESTRATOR (depends on working test suite)
- All production phases (cannot verify without tests)

**Gate Status:** BLOCKING - All test collection errors must resolve before Phase-N progression

**Audit Requirement:** CORE-026 (git checkpoint), CORE-027 (audit trail)

---

## Recommendations

1. **Create PHASE-CONSOLIDATION-SRC-CORTEX** - Add to cortex-master.yaml
2. **Mark PHASE-REMEDIATION-CROSS-PLATFORM as parent** - Consolidation depends on complete mapping
3. **Implement in order:** AC-001 → AC-002 → AC-003 → AC-004 → AC-005
4. **Parallel consideration:** AC-CONS-001 can be parallelized while AC-REM-CROSS-PLATFORM-001 completes
5. **Unblock ONBOARDING** - This consolidation is critical blocker for all subsequent phases

---

## Next Steps

1. ✅ Analysis complete (this document)
2. ⏳ Create PHASE-CONSOLIDATION-SRC-CORTEX in cortex-master.yaml
3. ⏳ Unlock/unblock by adding to phase_tracker
4. ⏳ Implement ACs in sequence
5. ⏳ Update cortex-master.yaml status when complete
