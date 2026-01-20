# CORTEX Cross-Platform Root Cause Analysis & Remediation Plan

**Date:** January 20, 2026  
**Status:** DIAGNOSTIC REPORT - PHASE NOT STARTED  
**Severity:** P0 - CRITICAL BLOCKER  

---

## Executive Summary

**Question:** "CORTEX was built on a Mac machine and now being run on a Windows machine. Is that the root cause?"

**Answer:** **NO. This is NOT a platform issue.**

The root cause is a **structural code gap**: 170+ test files expect implementations in `src/` that either don't exist or are in different locations. The conftest.py already correctly handles cross-platform paths using `pathlib.Path`.

---

## Root Cause Analysis

### Problem Observed
```
pytest tests -v --tb=short -q
```
Returns **170 collection errors** (NOT runtime errors):

```
ModuleNotFoundError: No module named 'src.core.brain_populator'
ModuleNotFoundError: No module named 'src.core.config'
ModuleNotFoundError: No module named 'src.infrastructure.database'
... (163 more similar errors)
```

### Why This Is NOT a Platform Issue

1. **conftest.py is already cross-platform correct:**
   ```python
   from pathlib import Path
   
   project_root = Path(__file__).parent.parent
   sys.path.insert(0, str(project_root / "cortex"))        # Works on Mac/Windows
   sys.path.insert(0, str(project_root / "src"))           # Works on Mac/Windows
   sys.path.insert(0, str(project_root / "cortex_brain"))  # Works on Mac/Windows
   sys.path.insert(0, str(project_root))
   ```
   - ✅ Uses `pathlib.Path` (platform-independent)
   - ✅ No hardcoded slashes or backslashes
   - ✅ No OS-specific path separators
   - ✅ Correctly converts to strings with `.str()`

2. **Path separators are automatic on both platforms:**
   - Mac: `pathlib.Path` uses `/`
   - Windows: `pathlib.Path` uses `\`
   - Both are handled identically by Python

3. **The error is import-time, not runtime:**
   - Collection phase (before any code executes)
   - pytest cannot even find the modules to test
   - This would fail identically on Mac or Windows

### Actual Root Cause: Structural Gap

**What exists in `src/`:**
```
src/
├── complexity/
├── confirmation/
├── core/
│   ├── governance/        (11 files implemented)
│   ├── knowledge/         (13 files implemented)
│   ├── orchestrator/      (4 files implemented)
│   └── result.py
├── deployment/
├── infrastructure/
├── mcp/                   (9 files implemented)
├── orchestrators/
├── tools/
└── versioning/
```

**What tests expect (examples):**
```
src.core.brain_populator           ✗ Doesn't exist
src.core.config                    ✗ Doesn't exist
src.core.checkpoint_manager        ✗ Doesn't exist
src.infrastructure.database        ✗ Doesn't exist
src.infrastructure.retry_handler   ✗ Doesn't exist
src.orchestrators.core.master_orchestrator  ✗ Doesn't exist
src.api.chat_response_formatter    ✗ Doesn't exist
... (163 more)
```

### Why This Happened

Three likely scenarios:

1. **Refactoring:** Code was moved to `cortex/` or `cortex_brain/tierX/` but test imports weren't updated
2. **Partial Implementation:** Tests were written (TDD) but corresponding implementations are incomplete
3. **Different Repository Structure:** Mac development used one structure, Windows checkout uses another

---

## Impact Assessment

| Component | Status | Impact |
|-----------|--------|--------|
| **Test Collection** | ❌ Blocked (170 errors) | Cannot run any tests |
| **CI/CD Pipeline** | ❌ Blocked | Cannot verify before merge |
| **Production Readiness** | ❌ Cannot Verify | Claim "production_ready: true" is unvalidated |
| **Development Speed** | ⚠️ Slowed | Cannot catch regressions |
| **Governance Compliance** | ⚠️ Questionable | Cannot audit test coverage |

---

## Remediation Plan

Created new phase: **PHASE-REMEDIATION-CROSS-PLATFORM** (5 ACs, ~12 hours)

### AC-1: Inventory Missing Modules (2 hours)
- Scan all 170+ test import statements
- Create mapping: missing module → (exists elsewhere | needs creation)
- Output: `_workspaces/roadmap/reports/MODULE-IMPORT-MAPPING.yaml`
- Deliverable: Decision matrix for each module

### AC-2: Refactor Test Imports (4 hours)
- Update test files to import from correct locations
- Use automated refactoring where possible
- For modules in `cortex/`: update import paths
- For modules in `cortex_brain/tierX/`: update import paths
- Result: No ModuleNotFoundError on test collection

### AC-3: Create Stub Implementations (3 hours)
- For modules mapped as "missing": create minimal stubs
- Each stub has `__init__.py` and minimal class definitions
- Prevents collection errors while real implementation is added
- Follows governance rules (type hints, docstrings)

### AC-4: Validate Test Collection (2 hours)
- Run `pytest --collect-only` with no errors
- Achieve 80%+ importable test modules
- Generate baseline test run report
- Establishes pass/fail/skip baseline

### AC-5: Update Status & Create Gates (1 hour)
- Update `cortex-master.yaml` with accurate test status
- Add pre-commit hook to prevent future import regressions
- Document remediation in audit trail
- Update `PHASE-REMEDIATION-CROSS-PLATFORM-REPORT.md`

---

## What Does NOT Need Fixing

✅ **conftest.py** - Already platform-independent  
✅ **pathlib usage** - Already correct throughout  
✅ **sys.path setup** - Already comprehensive  
✅ **Cross-platform compatibility** - Already handled properly  

---

## Governance Compliance

All 5 ACs will follow CORTEX governance:

| Rule | Status |
|------|--------|
| CORE-008 (TDD) | ✓ Tests first approach |
| CORE-011 (Type hints) | ✓ All stubs typed |
| CORE-012 (Docstrings) | ✓ Google-style |
| CORE-013 (Exception handling) | ✓ No bare except |
| CORE-026 (Git checkpoints) | ✓ Before each AC |
| CORE-027 (Audit trail) | ✓ All changes logged |
| CORE-028 (Kebab-case) | ✓ Naming convention |

---

## Timeline

- **AC-1:** Jan 20, 2-3 hours (module inventory)
- **AC-2:** Jan 20, 4-5 hours (import refactoring)  
- **AC-3:** Jan 20-21, 3-4 hours (stub implementations)
- **AC-4:** Jan 21, 2 hours (validation & test run)
- **AC-5:** Jan 21, 1 hour (status update & gates)

**Est. Completion:** January 21, 2026

---

## Next Steps

1. ✅ Created `phase-remediation-cross-platform.yaml` with 5 ACs
2. ✅ Added phase to `cortex-master.yaml` (blocking PHASE-ONBOARDING-ORCHESTRATOR)
3. ⏳ **Ready for implementation** - Run AC-REM-CROSS-PLATFORM-001-01 to begin

---

## Key Takeaway

**This is 100% about code structure, NOT about platform compatibility.**

The Windows machine is working correctly. The conftest.py is working correctly. The problem is that the codebase has tests expecting implementations in locations where they don't exist.

Once the test imports are aligned with actual module locations, CORTEX will be fully wired and testable on any platform.
