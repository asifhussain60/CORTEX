# Phase 8: CORE-035 Remediation Plan
**Objective:** Consolidate 10 duplicate registry classes to single canonical implementations

**Status:** BLOCKED (10 violations) → IN PROGRESS

---

## Executive Summary

**Violations:** 10 duplicate class definitions across `cortex/` and `cortex_brain/`
**Root Cause:** Parallel architecture during development (cortex_brain was experimental layer)
**Resolution:** Migrate all imports to canonical locations, delete duplicates
**Effort:** ~2-3 hours (incremental, with tests)
**Risk:** Medium (widespread imports, must verify test coverage)

---

## Duplicate Registry Map

### 1. TemplateRegistry (3 locations)

**Current State:**
```
❌ cortex/orchestrators/response/response_templates.py:197
   - Class: TemplateRegistry
   - Methods: register(), get(), list_templates(), unregister()
   - Status: Response-template-specific implementation

❌ cortex/brain/core/template_engine.py:31
   - Class: TemplateRegistry
   - Methods: register_template(), get_template(), list_templates()
   - Status: Singleton pattern (_instance)

✅ cortex/tools/scaffolder_templates.py:654 (CANONICAL)
   - Class: TemplateRegistry
   - Methods: get(), register(), available_types()
   - Status: Template type registry for scaffolding
```

**Analysis:**
- All three serve **different purposes** (response vs. scaffolder vs. general)
- NOT true duplicates - they have different interfaces
- **Decision:** Keep all three, rename for clarity:
  - `ResponseTemplateRegistry` (response_templates.py)
  - `TemplateEngineRegistry` (template_engine.py)
  - `TemplateRegistry` (scaffolder_templates.py) ← canonical

**Action Items:**
- [ ] Rename `cortex/orchestrators/response/response_templates.py:TemplateRegistry` → `ResponseTemplateRegistry`
- [ ] Rename `cortex/brain/core/template_engine.py:TemplateRegistry` → `TemplateEngineRegistry`
- [ ] Update all imports in `cortex/orchestrators/response/` (1 file)
- [ ] Update all imports in `cortex/brain/core/` (2 files)
- [ ] Update test files (2 test files)

---

### 2. OrchestratorDependencyRegistry (2 locations)

**Current State:**
```
❌ cortex/brain/core/orchestrator_dependency_registry.py:159
   - Location: Experimental brain layer
   - Implementation: Full-featured with storage, validation
   - Methods: register_orchestrator(), add_tier_dependency(), validate()

✅ cortex/core/orchestrator_dependency_registry.py:1
   - Location: Core layer
   - Implementation: Stub placeholder
   - Methods: (none)
```

**Analysis:**
- Brain implementation is complete, core is stub
- Brain layer is experimental - needs consolidation to core
- **Decision:** Copy full implementation from brain → core, deprecate brain version

**Action Items:**
- [ ] Copy `cortex/brain/core/orchestrator_dependency_registry.py` → `cortex/core/orchestrator_dependency_registry.py`
- [ ] Update brain version to import from core (backward compat)
- [ ] Find all imports of brain version (3 files)
- [ ] Redirect imports to core version
- [ ] Delete brain version (after tests pass)

---

### 3. EventRegistry (2 locations)

**Current State:**
```
❌ cortex/brain/core/orchestrator/terminal_events.py
   - Location: Brain layer
   - Methods: register_event(), get_events()

✅ cortex/core/orchestrator/terminal_events.py
   - Location: Core layer (canonical)
   - Status: Source of truth
```

**Action Items:**
- [ ] Find all imports of `cortex/brain/core/orchestrator/terminal_events.py:EventRegistry` (2 files)
- [ ] Redirect to `cortex/core/orchestrator/terminal_events.py:EventRegistry`
- [ ] Delete brain version

---

### 4. DomainPluginRegistry (2 locations)

**Current State:**
```
❌ cortex/brain/domain_orchestrators/business/plugins.py
   - Location: Brain layer

✅ cortex/domain_orchestrators/business/plugins.py
   - Location: Canonical
```

**Action Items:**
- [ ] Find all imports of brain version (1 file)
- [ ] Redirect to canonical
- [ ] Delete brain version

---

### 5. GovernanceRegistry (2 locations)

**Current State:**
```
❌ cortex/brain/core/governance_registry.py
   - Location: Brain layer (experimental)

✅ cortex/orchestrators/core/governance_registry.py
   - Location: Canonical
```

**Action Items:**
- [ ] Find all imports of brain version (2 files)
- [ ] Redirect to canonical
- [ ] Delete brain version

---

### 6. OrchestratorRegistry (3 locations - true duplicates)

**Current State:**
```
✅ cortex/orchestrators/registry/__init__.py:19 (CANONICAL)
   - Stub registry for backward compat
   - Methods: instance(), get(), list_all()

❌ cortex/orchestrators/registry/discovery_engine.py
   - Full implementation duplicate

❌ cortex/brain/core/decorators/orchestrator.py:35
   - Singleton with register(), get_by_id(), get_by_name()
```

**Action Items:**
- [ ] Consolidate implementations into `cortex/orchestrators/registry/__init__.py`
- [ ] Keep brain version as import-bridge for backward compat
- [ ] Delete duplicate in discovery_engine.py
- [ ] Update 5+ files importing from wrong location

---

### 7. IGovernanceRegistry (2 locations)

**Current State:**
```
❌ cortex/brain/core/interfaces/i_audit_logger.py
   - Location: Brain layer (wrong module)

✅ cortex/brain/core/interfaces.py
   - Location: Canonical interfaces module
```

**Action Items:**
- [ ] Move `IGovernanceRegistry` from i_audit_logger.py → interfaces.py
- [ ] Delete duplicate from i_audit_logger.py
- [ ] Update imports (1 file)

---

## Migration Roadmap

### Phase 8.1: Non-Breaking Renames (Template Registries)
**Risk:** Low - template code is isolated
**Effort:** 1 hour
```bash
# Step 1: Rename in response_templates.py
# Step 2: Rename in template_engine.py
# Step 3: Run tests
# Step 4: Update imports
```

### Phase 8.2: Orchestrator Dependencies
**Risk:** Medium - core functionality
**Effort:** 1.5 hours
```bash
# Step 1: Copy brain implementation to core
# Step 2: Create backward-compat bridge in brain
# Step 3: Run full test suite
# Step 4: Update imports across system
```

### Phase 8.3: Registries Consolidation
**Risk:** Medium - registry is used by wiring system
**Effort:** 1 hour
```bash
# Step 1: Consolidate implementations
# Step 2: Update discovery_engine.py imports
# Step 3: Run orchestrator tests
# Step 4: Delete duplicates
```

### Phase 8.4: Validation & Cleanup
**Risk:** Low - final verification
**Effort:** 0.5 hours
```bash
# Step 1: Run full test suite
# Step 2: Run CORE-035 enforcement
# Step 3: Commit consolidated code
```

---

## Detailed Action Items

### Item 1: ResponseTemplateRegistry Rename

**File:** `cortex/orchestrators/response/response_templates.py`

**Change:**
```python
# Line 145
-class TemplateRegistry:
+class ResponseTemplateRegistry:
```

**Imports to Update:**
- `cortex/orchestrators/response/__init__.py`
- `tests/unit/orchestrators/test_response_templates.py`

---

### Item 2: TemplateEngineRegistry Rename

**File:** `cortex/brain/core/template_engine.py`

**Change:**
```python
# Line 31
-class TemplateRegistry:
+class TemplateEngineRegistry:
```

**Imports to Update:**
- `cortex/brain/core/response_template_engine.py` (imports TemplateRegistry)
- `tests/unit/core/test_template_engine.py`

---

### Item 3: OrchestratorDependencyRegistry Consolidation

**Phase 3a - Copy Implementation:**

Copy full implementation from:
```
cortex/brain/core/orchestrator_dependency_registry.py (159-350 lines)
```

To:
```
cortex/core/orchestrator_dependency_registry.py (replace stub)
```

**Phase 3b - Create Bridge:**

In `cortex/brain/core/orchestrator_dependency_registry.py`:
```python
# Backward compatibility bridge
from cortex.core.orchestrator_dependency_registry import OrchestratorDependencyRegistry

__all__ = ['OrchestratorDependencyRegistry']
```

**Imports to Update:**
- `cortex/orchestrators/domain/planning_orchestrator.py`
- `cortex/brain/core/decorators/orchestrator.py`
- `tests/unit/core/test_orchestrator_dependency_registry.py`

---

### Item 4: EventRegistry Consolidation

**Files Importing Brain Version:**
```
1. cortex/brain/core/orchestrator/terminal_events.py
2. cortex/orchestrators/core/master_orchestrator.py
```

**Update:**
```python
# FROM:
from cortex.brain.core.orchestrator.terminal_events import EventRegistry

# TO:
from cortex.core.orchestrator.terminal_events import EventRegistry
```

**Cleanup:**
```bash
rm cortex/brain/core/orchestrator/terminal_events.py
```

---

### Item 5: DomainPluginRegistry Consolidation

**Files Importing Brain Version:**
```
1. cortex/brain/domain_orchestrators/business/plugins.py
```

**Update:**
```python
# FROM:
from cortex.brain.domain_orchestrators.business.plugins import DomainPluginRegistry

# TO:
from cortex.domain_orchestrators.business.plugins import DomainPluginRegistry
```

---

### Item 6: GovernanceRegistry Consolidation

**Files Importing Brain Version:**
```
1. cortex/brain/core/decorators/orchestrator.py
2. cortex/orchestrators/core/governance_registry.py
```

**Update All:**
```python
# FROM:
from cortex.brain.core.governance_registry import GovernanceRegistry

# TO:
from cortex/orchestrators/core/governance_registry import GovernanceRegistry
```

---

### Item 7: OrchestratorRegistry Consolidation

**Canonical Location:**
```
cortex/orchestrators/registry/__init__.py:19
```

**Consolidate From:**
1. `cortex/orchestrators/registry/discovery_engine.py` (duplicate)
2. `cortex/brain/core/decorators/orchestrator.py` (enhanced version)

**Decision:** Keep enhanced version in canonical, create bridge in brain

**Files Importing Wrong Version:**
- `cortex/orchestrators/registry/discovery_engine.py` (remove this file)
- `cortex/brain/core/decorators/orchestrator.py` (import from canonical)
- All files importing from brain decorator (5+ files)

---

### Item 8: IGovernanceRegistry Move

**File:** `cortex/brain/core/interfaces/i_audit_logger.py`

**Move To:** `cortex/brain/core/interfaces.py`

**Cleanup:**
```bash
rm cortex/brain/core/interfaces/i_audit_logger.py
```

---

## Testing Strategy

### Pre-Refactor Tests
```bash
pytest tests/unit/ -v --tb=short
# Expected: Baseline pass rate
```

### Post-Rename Tests (Templates)
```bash
pytest tests/unit/orchestrators/test_response_templates.py -v
pytest tests/unit/core/test_template_engine.py -v
```

### Post-Consolidation Tests (Registries)
```bash
pytest tests/unit/core/test_orchestrator_dependency_registry.py -v
pytest tests/unit/orchestrators/ -v
```

### CORE-035 Verification
```bash
python cortex/ci_cd/enforce_core_035.py --verbose
# Expected: 0 violations
```

---

## Rollback Plan

If issues arise:

1. **Quick Rollback:**
   ```bash
   git revert <commit-hash>
   ```

2. **Partial Rollback:**
   - Keep renames (low risk)
   - Revert consolidations only

3. **Testing Rollback:**
   - Run baseline tests first
   - Compare before/after

---

## Success Criteria

- [ ] All 10 duplicate classes consolidated
- [ ] All imports updated (0 "from cortex_brain" imports of registries)
- [ ] Full test suite passes (172+ tests)
- [ ] CORE-035 enforcement reports 0 violations
- [ ] Production readiness verification: 15/15 checks pass
- [ ] Pre-push verification: PASSES (green)

---

## Timeline

**Estimated:** 4-5 hours total
- Phase 8.1 (Templates): 1 hour
- Phase 8.2 (Dependencies): 1.5 hours
- Phase 8.3 (Registries): 1 hour
- Phase 8.4 (Validation): 0.5 hours
- **Buffer:** 0.5 hours (unexpected issues)

---

## Next Steps

1. ✅ Review this plan (current)
2. ⏳ Execute Phase 8.1 (template renames)
3. ⏳ Execute Phase 8.2 (dependency consolidation)
4. ⏳ Execute Phase 8.3 (registry consolidation)
5. ⏳ Execute Phase 8.4 (validation)
6. ⏳ Commit & push with green tests

**Ready to proceed?** Confirm, and I'll begin Phase 8.1
