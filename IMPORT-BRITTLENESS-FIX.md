# Import Brittleness Fix - Holistic Design Review

**Date:** 2026-01-12  
**Issue:** Mixed absolute and relative imports causing path resolution errors  
**Root Cause:** Inconsistent import strategy across codebase  
**Severity:** CRITICAL - Blocks test collection

---

## Problem Analysis

### Current State
- **File:** `src/orchestrators/core/master_orchestrator.py` (Line 31)
- **Import:** `from ..infrastructure.response_header_footer_manager import`
- **Issue:** Uses 2 dots (`..`) but infrastructure is NOT at `orchestrators/` level

### Import Path Hierarchy
```
src/
  ├── orchestrators/
  │   ├── core/              ← master_orchestrator.py is here (depth 3)
  │   │   └── master_orchestrator.py
  │   └── middleware/
  ├── infrastructure/        ← response_header_footer_manager.py is here (depth 2)
  └── main.py
```

### Relative vs Absolute
- **From core/master_orchestrator.py to infrastructure/:**
  - Using 2 dots: `..infrastructure` → goes to `orchestrators/infrastructure` ✗ (WRONG)
  - Using 3 dots: `...infrastructure` → goes to `src/infrastructure` ✓ (CORRECT)
  - Using absolute: `from src.infrastructure` → goes to `src/infrastructure` ✓ (BEST)

### Design Brittleness Indicators
1. **Mixed patterns in same file** (review_orchestrator.py has both relative and absolute)
2. **Inconsistent dot counts** across similar files
3. **Assumption of sibling locations** that don't match actual structure
4. **No centralized import validation** to catch path errors

---

## Holistic Solution: Standardize to Absolute Imports

### Why Absolute Imports
✓ **Resilient:** Works regardless of file depth or moves  
✓ **Clear:** No mental math required (how many dots?)  
✓ **Discoverable:** Tools can easily trace dependencies  
✓ **Standard:** Industry best practice for larger projects  
✗ **Requires:** src/ in PYTHONPATH (handled by pytest.ini)

### Implementation Strategy

#### Phase 1: Fix Critical Import Error (IMMEDIATE)
**File:** `src/orchestrators/core/master_orchestrator.py`
- **Line 31:** `from ..infrastructure.response_header_footer_manager` → ERROR
- **Fix:** `from src.infrastructure.response_header_footer_manager` → OK
- **Impact:** Unblocks test collection

#### Phase 2: Standardize Core Module (HOLISTIC)
**Files:** All in `src/orchestrators/core/`
- **Pattern:** ALL relative imports → absolute imports
- **Consistency:** All imports follow `from src.X import Y` pattern
- **Validation:** Run import check script before each commit

#### Phase 3: Extend to Orchestrators (OPTIONAL)
**Files:** All in `src/orchestrators/`
- **Pattern:** Convert remaining relative imports
- **Priority:** Low (Phase 1+2 unblock functionality)

#### Phase 4: Add Design Guard (PREVENTION)
**New File:** `scripts/validate_import_consistency.py`
- **Rule 1:** Relative imports only within same subtree
- **Rule 2:** Cross-package imports use absolute paths
- **Rule 3:** No `.infrastructure` patterns (always `src.infrastructure`)
- **Integration:** Pre-commit hook

---

## Fixed Import Statements

### master_orchestrator.py (Lines 17-34)

**Current (BROKEN):**
```python
from ..middleware.orchestrator_lifecycle import (
    OrchestratorLifecycle,
    LifecycleState,
    LifecycleError
)
from .todo_orchestrator import TodoOrchestrator
from .governance_merger import GovernanceMerger
from ..state_manager import StateManager
from ..audit_logger import get_audit_logger, AuditCategory
from ..phase_boundary_cleanup import (
    PhaseBoundaryCleanup,
    CleanupEvidenceBundle
)
from ..housekeeping_orchestrator import HousekeepingOrchestrator
from ..infrastructure.response_header_footer_manager import (
    ResponseHeaderFooterManager,
    get_header_footer_manager,
    wrap_cortex_response
)
```

**Fixed (ABSOLUTE IMPORTS):**
```python
from src.orchestrators.middleware.orchestrator_lifecycle import (
    OrchestratorLifecycle,
    LifecycleState,
    LifecycleError
)
from src.orchestrators.core.todo_orchestrator import TodoOrchestrator
from src.orchestrators.core.governance_merger import GovernanceMerger
from src.orchestrators.state_manager import StateManager
from src.orchestrators.audit_logger import get_audit_logger, AuditCategory
from src.orchestrators.phase_boundary_cleanup import (
    PhaseBoundaryCleanup,
    CleanupEvidenceBundle
)
from src.orchestrators.housekeeping_orchestrator import HousekeepingOrchestrator
from src.infrastructure.response_header_footer_manager import (
    ResponseHeaderFooterManager,
    get_header_footer_manager,
    wrap_cortex_response
)
```

---

## Validation Plan

### 1. Immediate Test
```bash
python3 -m pytest tests/integration/test_feat04_end_to_end.py -v
```
Expected: Import error resolved, tests run

### 2. Full Suite
```bash
python3 -m pytest tests/ --co -q
```
Expected: 1476 tests collected, 0 errors

### 3. Design Validation
```bash
python3 scripts/validate_import_consistency.py
```
Expected: All patterns compliant

---

## Regression Prevention

### Pre-commit Hook
Location: `.git/hooks/pre-commit`
```bash
#!/bin/bash
python3 scripts/validate_import_consistency.py
if [ $? -ne 0 ]; then
    echo "❌ Import brittleness detected. Fix before commit."
    exit 1
fi
```

### Design Review Checklist
Before adding new imports:
- [ ] Is import from `src/`? If not, WHY?
- [ ] Could this file move? If so, use absolute imports
- [ ] Does this create a circular dependency? Check with `scripts/check_circular_deps.py`
- [ ] Are ALL similar imports consistent?

---

## Success Metrics

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Test Collection | ✗ 2 errors | ✓ 0 errors | 0 errors |
| Import Consistency | Mixed (30+ patterns) | Standardized (absolute) | 100% absolute |
| Code Resilience | Fragile (paths break on moves) | Resilient (depth-independent) | Design-proof |
| Maintainability | Hard (implicit structure) | Easy (explicit structure) | > 80% team understanding |

---

## References

- **PEP 8:** Import formatting best practices
- **CORTEX Rule:** CORE-005 (Path Portability)
- **Affected ACs:** AC-ORCH-001, AC-TEST-001 (now unblocked)

