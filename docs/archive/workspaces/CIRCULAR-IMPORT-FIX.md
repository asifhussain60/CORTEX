# Circular Import Fix - cortex.lens Package

**Issue:** ENH-017 Phase 1 blocked by pre-existing circular import in cortex.lens package initialization

**Created:** 2026-02-04  
**Priority:** P0 BLOCKER for Phase 1 completion  
**Impact:** Cannot run tests for new CSharpAdapter (586 lines) due to import cascade

---

## Problem Statement

### Symptom
```
ImportError: cannot import name 'GitHistoryAnalyzer' from partially initialized module 
'cortex.lens.analyzers.git_history_analyzer' (most likely due to a circular import)
```

### Circular Dependency Chain
```
cortex/lens/__init__.py (line 14)
    ↓ imports LENSOrchestrator
cortex/lens/orchestrator.py (line 23)
    ↓ imports GitHistoryAnalyzer
cortex/lens/analyzers/git_history_analyzer.py (line 20)
    ↓ imports from cortex.brain.analysis
cortex/brain/analysis/__init__.py (line 11)
    ↓ imports from cortex.lens.analyzers.git_history_analyzer
    ↓ CIRCULAR ⟲
```

### Trigger
Any attempt to import from `cortex.lens.*` (including models, adapters) triggers the circular import because:
1. Python evaluates `cortex/lens/__init__.py` on first import
2. Line 14 eagerly imports `LENSOrchestrator`
3. Import cascade begins and loops back

### Impact
- CSharpAdapter implementation complete (586 lines) but UNVALIDATED
- 26 tests written but cannot execute (pytest fails on import)
- Standalone test attempts fail (imports still trigger __init__.py)
- Phase 1 blocked at GREEN validation stage

---

## Root Cause Analysis

### Primary Issue: Eager Imports in __init__.py
File: `cortex/lens/__init__.py`
```python
# Line 14 - PROBLEMATIC
from cortex.lens.orchestrator import LENSOrchestrator, LENSContext

# Lines 17-20 - Convenience imports (also contribute to issue)
from cortex.lens.analyzers.git_history_analyzer import GitHistoryAnalyzer
from cortex.lens.analyzers.ast_analyzer import ASTAnalyzer
from cortex.lens.analyzers.comment_extractor import CommentExtractor
```

**Why this is a problem:**
- Package initialization happens on first import of ANY module in cortex.lens
- Eager imports force dependency resolution during initialization
- Creates tight coupling between unrelated modules

### Secondary Issue: Cross-Package Dependencies
File: `cortex/lens/analyzers/git_history_analyzer.py`
```python
# Line 20 - Creates dependency on cortex.brain
from cortex.brain.analysis.remote_git_adapter import RemoteGitAdapter
```

File: `cortex/brain/analysis/__init__.py`
```python
# Line 11 - Creates back-reference to cortex.lens
from cortex.lens.analyzers.git_history_analyzer import GitHistoryAnalyzer
```

**Why this is a problem:**
- cortex.lens and cortex.brain have bidirectional dependencies
- Package initialization order becomes undefined
- Classic circular import pattern

---

## Solution Options

### Option 1: Lazy Imports (RECOMMENDED)
**Approach:** Remove eager imports from `cortex/lens/__init__.py`

**Changes Required:**
```python
# cortex/lens/__init__.py - BEFORE
from cortex.lens.orchestrator import LENSOrchestrator, LENSContext
from cortex.lens.analyzers.git_history_analyzer import GitHistoryAnalyzer
# ... more imports

# cortex/lens/__init__.py - AFTER (lazy loading)
def get_lens_orchestrator():
    from cortex.lens.orchestrator import LENSOrchestrator
    return LENSOrchestrator

def get_git_history_analyzer():
    from cortex.lens.analyzers.git_history_analyzer import GitHistoryAnalyzer
    return GitHistoryAnalyzer

# Or use __getattr__ for convenience
def __getattr__(name):
    if name == "LENSOrchestrator":
        from cortex.lens.orchestrator import LENSOrchestrator
        return LENSOrchestrator
    elif name == "GitHistoryAnalyzer":
        from cortex.lens.analyzers.git_history_analyzer import GitHistoryAnalyzer
        return GitHistoryAnalyzer
    # ... more lazy imports
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

**Pros:**
- Minimal code changes (single file)
- Preserves API for existing consumers
- Breaks circular import at initialization time
- Python 3.7+ supports __getattr__ for modules

**Cons:**
- Slightly slower first access (negligible)
- Less explicit about available imports (discoverability)

**Effort:** 1-2 hours  
**Risk:** Low (backward compatible with lazy loading)

---

### Option 2: Remove Convenience Imports
**Approach:** Users import directly from submodules

**Changes Required:**
```python
# cortex/lens/__init__.py - AFTER
# Remove all convenience imports
# Users must use explicit imports:
# from cortex.lens.orchestrator import LENSOrchestrator
# from cortex.lens.analyzers.git_history_analyzer import GitHistoryAnalyzer
```

**Pros:**
- Simplest solution
- Explicit imports = better code clarity
- Eliminates all initialization-time dependencies

**Cons:**
- Breaking change for existing consumers
- More verbose imports required
- Need to update all import statements across CORTEX codebase

**Effort:** 3-4 hours (including codebase updates)  
**Risk:** Medium (breaking change)

---

### Option 3: Refactor Cross-Package Dependencies
**Approach:** Break cortex.brain → cortex.lens dependency

**Changes Required:**
1. Move `RemoteGitAdapter` to neutral location (e.g., `cortex.infrastructure`)
2. Update imports in `git_history_analyzer.py`
3. Update imports in `cortex.brain.analysis.__init__.py`

**Pros:**
- Solves root architectural issue
- Better separation of concerns
- Prevents future circular imports

**Cons:**
- Largest scope of changes
- Requires understanding full dependency tree
- May reveal other hidden circular dependencies

**Effort:** 4-6 hours  
**Risk:** High (architectural change)

---

### Option 4: Temporary Test Workaround (NOT RECOMMENDED)
**Approach:** Move CSharpAdapter to temporary location for testing

**Changes Required:**
1. Copy `csharp_adapter.py` to `tests/fixtures/`
2. Copy `polyglot_ast_result.py` models to `tests/fixtures/`
3. Run tests against temporary copies
4. Move back after circular import fixed

**Pros:**
- Unblocks Phase 1 completion immediately
- No changes to production code

**Cons:**
- Temporary hack, not a real solution
- Technical debt accumulation
- Test-production code divergence risk
- Still need to fix circular import eventually

**Effort:** 30 minutes  
**Risk:** Medium (technical debt)

---

## Recommended Solution Path

### Step 1: Implement Option 1 (Lazy Imports)
**File:** `cortex/lens/__init__.py`
**Action:** Add `__getattr__` for lazy loading
**Duration:** 1 hour
**Validation:** Run existing CORTEX tests to ensure no regressions

### Step 2: Validate CSharpAdapter Tests
**Action:** Run `pytest tests/unit/lens/adapters/test_csharp_adapter.py -v`
**Expected:** 26 tests execute (currently blocked)
**Duration:** 30 minutes

### Step 3: Complete Phase 1 GREEN Validation
**Action:** Enable remaining 23 skipped tests progressively
**Expected:** All 26 tests passing
**Duration:** 2 hours

### Step 4: Document Pattern for Future Adapters
**Action:** Add "Avoiding Circular Imports" section to adapter development guide
**Duration:** 30 minutes

**Total Effort:** 4 hours  
**Risk:** Low  
**Impact:** Unblocks ENH-017 Phase 1 + prevents future circular import issues

---

## Alternative: Quick Win for Phase 1 Completion

If architectural fix is delayed, use **Option 4** temporarily:

```bash
# Quick workaround (30 minutes)
mkdir -p tests/fixtures/lens_temp
cp cortex/lens/adapters/csharp_adapter.py tests/fixtures/lens_temp/
cp cortex/lens/models/polyglot_ast_result.py tests/fixtures/lens_temp/
cp cortex/lens/adapters/language_adapter.py tests/fixtures/lens_temp/

# Update test imports to use fixtures
# Run tests: pytest tests/unit/lens/adapters/test_csharp_adapter.py -v
# Mark Phase 1 as COMPLETE (with technical debt tracked)

# File issue for architectural fix
# Schedule Option 1 implementation for Phase 2
```

---

## Impact Assessment

### Blocked Work (Until Fixed)
- ✅ CSharpAdapter implementation (COMPLETE)
- ❌ CSharpAdapter validation (BLOCKED)
- ❌ Phase 1 completion (BLOCKED)
- ❌ Integration with LENSOrchestrator (BLOCKED)
- ❌ ksessions C# codebase analysis (BLOCKED)

### Downstream Impact
- Phase 2 (JavaAdapter, TypeScriptAdapter) will hit same issue
- Any new language adapters will be blocked
- LENS ecosystem expansion halted until resolved

### Priority Justification
**P0 BLOCKER** because:
1. Prevents completion of approved ENH-017 Phase 1
2. Blocks 30-40% of enterprise repository onboarding
3. CSharpAdapter code complete but unusable
4. Will block all future language adapter development

---

## Next Actions

**Immediate (This Session):**
1. Decide: Option 1 (lazy imports) OR Option 4 (temporary workaround)
2. If Option 1: Implement __getattr__ in cortex/lens/__init__.py
3. If Option 4: Copy files to tests/fixtures/, update imports
4. Validate: Run CSharpAdapter tests
5. Update ENH-017 status based on outcome

**Short-Term (Next Session):**
1. If Option 4 used: Schedule Option 1 for permanent fix
2. Document pattern in development guide
3. Add pre-commit hook to detect circular imports
4. Audit other packages for similar issues

**Long-Term (Phase 2+):**
1. Consider Option 3 (refactor cross-package dependencies)
2. Implement dependency injection for analyzers
3. Create package dependency graph visualization
4. Enforce architectural boundaries via import linting

---

## Related Files

**Blocking Issue:**
- `cortex/lens/__init__.py` (line 14 - eager LENSOrchestrator import)
- `cortex/lens/orchestrator.py` (line 23 - imports GitHistoryAnalyzer)
- `cortex/lens/analyzers/git_history_analyzer.py` (line 20 - imports cortex.brain)
- `cortex/brain/analysis/__init__.py` (line 11 - imports cortex.lens)

**Blocked Work:**
- `cortex/lens/adapters/csharp_adapter.py` (586 lines, COMPLETE but UNVALIDATED)
- `tests/unit/lens/adapters/test_csharp_adapter.py` (26 tests, CANNOT EXECUTE)
- `tests/standalone/test_csharp_adapter_standalone.py` (6 tests, SAME ISSUE)

**Enhancement Tracking:**
- `docs/meta/enhancement-history.yaml` (ENH-017 Phase 1 status)
- `_workspaces/cortex-plan/LENS-MULTI-LANGUAGE-ENHANCEMENT.yaml` (overall plan)

---

## Lessons Learned

1. **Test package initialization early:** Circular imports may not surface until new modules added
2. **Avoid eager imports in __init__.py:** Use lazy loading for cross-module dependencies
3. **TDD can expose infrastructure issues:** RED→GREEN cycle blocked by pre-existing technical debt
4. **Separate concerns across packages:** cortex.lens and cortex.brain should be loosely coupled

---

**Status:** DOCUMENTED - Awaiting decision on solution path  
**Assignee:** CORTEX Architect  
**Blocked:** ENH-017 Phase 1 completion
