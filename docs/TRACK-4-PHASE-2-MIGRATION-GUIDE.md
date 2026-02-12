# Track 4 Phase 2: Conservative Deprecation & Gradual Migration Guide

**Status:** IN PROGRESS  
**Phase:** 2 of 3  
**Timeline:** 2026-02-10 to 2026-03-15 (estimated 4 weeks)  
**Strategy:** Conservative validation with deprecation warnings  
**Sunset Date:** 2026-03-31 (Phase 3 deletion begins)

---

## Executive Summary

Track 4 Phase 2 implements a **safe, gradual migration path** from deprecated orchestrators (26 → 16) to unified orchestrators. Instead of aggressively updating imports, we:

1. **Keep old imports working** (backward compatible)
2. **Add deprecation warnings** (notify developers)
3. **Provide adapter functions** (bridge old/new APIs)
4. **Monitor usage patterns** (validate safety)
5. **Delay deletion** (until 2026-03-31)

This approach ensures **zero breaking changes** while establishing clear migration path.

---

## Phase 2 Approach: Three-Tier Migration Strategy

### Tier 1: Current (2026-02-10 to 2026-02-28)
**Goal:** Establish monitoring infrastructure and adapter functions

```
┌─────────────────────────────────────────┐
│ OLD CODE (Tier 1)                       │
│ from lens_orchestrator import LENS...   │
│ orchestrator = LENSOrchestrator()        │
│ result = orchestrator.analyze_file()    │
└────────────────┬────────────────────────┘
                 │
                 ▼
         [DEPRECATED WRAPPER]
         Emits warning to stderr
         Delegates to unified APIs
                 │
                 ▼
        [UNIFIED ORCHESTRATOR]
        New implementation
        Tested & verified
```

**Deliverables:**
- ✅ API compatibility layer (254 LOC)
- 🔄 Deprecation warning system
- 🔄 Import usage monitoring
- 🔄 Test harness for compatibility verification

**Files to Create:**
1. `cortex/orchestrators/support/api_compatibility.py` ✅ (DONE)
2. `cortex/orchestrators/support/deprecation_monitor.py` (PENDING)
3. `cortex/orchestrators/support/migration_validator.py` (PENDING)

---

### Tier 2: Gradual Migration (2026-03-01 to 2026-03-15)
**Goal:** Update external imports with adapter functions

```
┌─────────────────────────────────────────┐
│ NEW CODE (Tier 2)                       │
│ from api_compatibility import analyze.. │
│ result = analyze_file_via_unified()     │
└────────────────┬────────────────────────┘
                 │
                 ▼
        [ADAPTER FUNCTION]
        Maps old params to new
        Handles compatibility
                 │
                 ▼
        [UNIFIED ORCHESTRATOR]
        New implementation
        Tested & verified
```

**Gradual Update Priority:**
1. **Priority A (High):** Internal wiring/factories (non-breaking)
   - `cortex/orchestrators/support/` (internal)
   - Target: Week 1 of Tier 2

2. **Priority B (Medium):** Governance/analysis tools (mid-impact)
   - `cortex/mcp/adapters/recommendation_adapter.py`
   - `cortex/mcp/tools/security.py`
   - Target: Week 2 of Tier 2

3. **Priority C (Lower):** CLI/onboarding (user-facing but safe)
   - `cortex/cli/commands/onboard.py`
   - `cortex/mcp/tools/onboarding_tools.py`
   - Target: Week 3 of Tier 2

**Key Principle:** Update one file at a time, run full test suite after each update

---

### Tier 3: Safe Deletion (2026-03-31+)
**Goal:** Remove deprecated files after validation period

```
┌─────────────────────────────────────────┐
│ FINAL CODE (Tier 3)                     │
│ from orchestrator_factories import...   │
│ orchestrator = get_unified_analysis...  │
│ result = orchestrator.analyze()         │
└─────────────────────────────────────────┘
                 │
                 ▼
        [UNIFIED ORCHESTRATOR ONLY]
        No more wrappers/adapters
        All imports modern
        Final state: 12-14 orchestrators
```

**Deletion Checklist:**
- [ ] Verify zero imports of deprecated modules
- [ ] Run deprecation warning audit (grep for import statements)
- [ ] Backup deprecated files to archive/
- [ ] Execute atomic deletion
- [ ] Run full test suite (target: 100% passing)
- [ ] Update __wiring_contract__.yaml (remove deprecated entries)
- [ ] Final orchestrator count: 12-14 (50-54% reduction from 26)

---

## Migration File-by-File

### 1. tiered_lens_analyzer.py
**Current Issue:** Uses old LENS API with `analyze_file()` method  
**Old API:**
```python
from cortex.orchestrators.support.lens_orchestrator import LENSOrchestrator

self.lens_orchestrator = LENSOrchestrator(repo_path=repo_path)
result = self.lens_orchestrator.analyze_file(file_path)
```

**New Approach (Adapter):**
```python
from cortex.orchestrators.support.api_compatibility import analyze_file_via_unified

# No need to create orchestrator instance
result = analyze_file_via_unified(file_path, repo_path)
```

**Migration Steps:**
1. Replace import
2. Remove orchestrator instantiation
3. Replace method calls with adapter functions
4. Run tests: `pytest tests/test_tiered_lens_analyzer.py -v`
5. Verify zero test failures
6. Commit

**Expected Timeline:** 30-60 minutes

---

### 2. onboarding/__init__.py
**Current Issue:** Uses old SetupOrchestrator  
**Old API:**
```python
from cortex.orchestrators.core.setup_orchestrator import SetupOrchestrator

setup_orch = SetupOrchestrator()
setup_orch.setup_environment()
```

**New Approach (Adapter):**
```python
from cortex.orchestrators.support.api_compatibility import onboard_repository_via_unified

result = onboard_repository_via_unified(repo_path)
```

**Migration Steps:**
1. Identify all SetupOrchestrator usage
2. Map old methods to adapter functions
3. Update imports
4. Run integration tests
5. Commit

**Expected Timeline:** 45-90 minutes

---

### 3. cli/commands/onboard.py
**Current Issue:** Direct RepositoryOnboardingOrchestrator import  
**Migration Steps:**
1. Update to use factory function (modern approach)
2. Test CLI end-to-end
3. Commit

**Expected Timeline:** 30-45 minutes

---

### 4. mcp/adapters/recommendation_adapter.py
**Current Issue:** Uses RecommendationEngine (deprecated)  
**Migration Steps:**
1. Switch to adapter function
2. Verify MCP tool tests pass
3. Commit

**Expected Timeline:** 20-30 minutes

---

### 5. mcp/middleware/onboarding_gate.py
**Current Issue:** Uses deprecated onboarding import  
**Migration Steps:**
1. Update import
2. Test middleware behavior
3. Commit

**Expected Timeline:** 20-30 minutes

---

### 6. mcp/tools/security.py
**Current Issue:** Uses deprecated security engine  
**Migration Steps:**
1. Switch to unified adapter
2. Run security tests
3. Commit

**Expected Timeline:** 15-25 minutes

---

### 7. mcp/tools/onboarding_tools.py
**Current Issue:** Multiple deprecated imports  
**Migration Steps:**
1. Update all imports
2. Use adapter functions
3. Test MCP tools
4. Commit

**Expected Timeline:** 45-75 minutes

---

## Deprecation Warning System

**Goal:** Notify developers about deprecated imports

### Implementation Pattern

```python
# In deprecated orchestrator modules:

import warnings
from datetime import datetime

# At module load time:
warnings.warn(
    f"RepositoryOnboardingOrchestrator is deprecated. "
    f"Use cortex.orchestrators.support.orchestrator_factories."
    f"get_unified_onboarding_orchestrator() instead. "
    f"Sunset: 2026-03-31",
    DeprecationWarning,
    stacklevel=2
)
```

### Monitoring Dashboard

Track deprecation warning frequency:
- [ ] Create monitoring script to capture warnings
- [ ] Daily aggregation
- [ ] Alert if new imports detected
- [ ] Record which files emit most warnings

---

## Phase 2 Success Criteria

✅ **All criteria must be met to proceed to Phase 3:**

| Criterion | Target | Status |
|-----------|--------|--------|
| Adapter functions working | 3/3 | 🔄 IN PROGRESS |
| External imports identified | 7/7 | ✅ COMPLETE |
| API compatibility layer | 100% | 🔄 IN PROGRESS |
| Deprecation warnings | All modules | ⏳ PENDING |
| Zero new test failures | 0 failures | ✅ (baseline) |
| Migration validation suite | Passes | ⏳ PENDING |
| Documentation complete | 100% | 🔄 IN PROGRESS |

---

## Phase 2 Execution Plan

**Week 1 (2026-02-10 to 2026-02-16):**
```
┌─────────────────────────────────────────┐
│ Tier 1: Monitoring Infrastructure       │
├─────────────────────────────────────────┤
│ ✅ API compatibility layer (254 LOC)    │
│ 🔄 Deprecation monitor system           │
│ 🔄 Import tracking utilities            │
│ 🔄 Validation test suite                │
└─────────────────────────────────────────┘
```

**Week 2-3 (2026-02-17 to 2026-03-02):**
```
┌─────────────────────────────────────────┐
│ Tier 2: Gradual Import Updates          │
├─────────────────────────────────────────┤
│ Priority A: Internal wiring (0 breaking │
│ Priority B: Mid-impact tools            │
│ Priority C: User-facing CLI             │
└─────────────────────────────────────────┘
```

**Week 4 (2026-03-03 to 2026-03-15):**
```
┌─────────────────────────────────────────┐
│ Validation & Monitoring                 │
├─────────────────────────────────────────┤
│ Run full integration test suite         │
│ Monitor deprecation warnings            │
│ Document any API gaps                   │
│ Prepare Phase 3 deletion checklist      │
└─────────────────────────────────────────┘
```

---

## Key Principles

1. **NO Breaking Changes** - Old code continues to work
2. **Gradual Migration** - One file at a time
3. **Full Testing** - Run tests after every update
4. **Conservative Approach** - Validation before deletion
5. **Clear Timeline** - Sunset date: 2026-03-31

---

## Next Steps

1. ✅ Create API compatibility layer (`api_compatibility.py`)
2. 🔄 Create deprecation monitoring system
3. 🔄 Create migration validation suite
4. 🔄 Update external imports (Tier 2)
5. 🔄 Validate all changes with full test run
6. ⏳ Post-2026-03-31: Execute Phase 3 deletion

---

**Document Version:** 1.0  
**Last Updated:** 2026-02-10  
**Phase:** 2 of 3  
**Orchestrator Reduction:** 26 → 16 (38% complete, target 50-54%)
