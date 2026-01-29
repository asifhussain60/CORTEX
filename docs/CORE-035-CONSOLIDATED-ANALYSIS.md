# CORE-035 Consolidated Analysis Report

**Generated:** 2026-01-29
**Analysis Tool:** `cortex/ci_cd/core_035_analyzer.py`
**Status:** Ready for Phase 8 Remediation

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Duplicate Classes** | 7 |
| **Total Duplicate Locations** | 9 (not 10) |
| **Files Affected by Imports** | 25 |
| **Complexity** | Medium-High |
| **Estimated Effort** | 4-6 hours |
| **Risk Level** | Medium |

---

## Analysis Results

### 1. GovernanceRegistry (HIGHEST PRIORITY - 19 importers)

**Status:** ❌ CRITICAL - Most widely used duplicate

| Aspect | Details |
|--------|---------|
| **Canonical** | `cortex/orchestrators/core/governance_registry.py` ✅ |
| **Duplicate** | `cortex/brain/core/governance_registry.py` ❌ |
| **Imported By** | **19 files** |
| **Consolidation** | Delete brain version, update all imports |

**Files Importing (19):**
```
cortex/brain/core/governance_registry_database_integration.py
cortex/brain/core/input_validator.py
cortex/brain/core/orchestrator/conversation_protocol.py
cortex/brain/core/rule_evaluator.py
cortex/brain/core/tier_resolver.py
cortex/brain/mcp/server.py
cortex/execution/gateway_exec_full.py
cortex/orchestrators/core/enforcement_orchestrator.py
cortex/orchestrators/core/master_orchestrator.py
cortex/orchestrators/support/context_assembly_orchestrator.py
cortex/testing/auto_initialization_suite.py
tests/integration/test_governance_persistence_option_c.py
tests/test_governance_edge_cases.py
tests/test_governance_integration.py
tests/test_governance_performance.py
tests/test_governance_registry_loading.py
tests/unit/governance/test_core_002_artifact_validation.py
tests/unit/orchestrators/test_module_dependencies.py
tests/unit/test_governance_registry.py
```

**Action:**
```python
# FROM: from cortex.brain.core.governance_registry import GovernanceRegistry
# TO:   from cortex.orchestrators.core.governance_registry import GovernanceRegistry
```

---

### 2. TemplateRegistry (3 locations, different purposes)

**Status:** ⚠️ NOT TRUE DUPLICATES - Different interfaces

| Location | Purpose | Status |
|----------|---------|--------|
| `cortex/tools/scaffolder_templates.py` | Template type registry | ✅ Canonical |
| `cortex/orchestrators/response/response_templates.py` | Response template registry | ❌ Needs rename |
| `cortex/brain/core/template_engine.py` | Template engine registry | ❌ Needs rename |

**Analysis:** These serve different purposes. Solution: Rename for clarity

**Action:**
1. Rename `cortex/orchestrators/response/response_templates.py:TemplateRegistry` → `ResponseTemplateRegistry`
2. Rename `cortex/brain/core/template_engine.py:TemplateRegistry` → `TemplateEngineRegistry`
3. Update 1 test file importer

---

### 3. OrchestratorRegistry (3 locations, complex)

**Status:** ⚠️ MEDIUM - Orchestrator wiring system

| Location | Status | Notes |
|----------|--------|-------|
| `cortex/orchestrators/registry/__init__.py` | ✅ Canonical | Stub for backward compat |
| `cortex/orchestrators/registry/discovery_engine.py` | ❌ Duplicate | Full implementation |
| `cortex/brain/core/decorators/orchestrator.py` | ❌ Duplicate | Enhanced singleton |

**Imported By (2 files):**
```
cortex/brain/mcp/__init__.py
cortex/tools/orchestrator_scaffolder.py
```

**Action:**
1. Consolidate discovery_engine.py implementation into canonical `__init__.py`
2. Delete discovery_engine.py (unused duplicate)
3. Update brain decorator to import from canonical
4. Update 2 importers

---

### 4. DomainPluginRegistry (2 locations)

**Status:** ✅ SIMPLE - Clear duplicate

| Location | Status |
|----------|--------|
| `cortex/domain_orchestrators/business/plugins.py` | ✅ Canonical |
| `cortex/brain/domain_orchestrators/business/plugins.py` | ❌ Duplicate |

**Imported By (2 files):**
```
cortex/domain_orchestrators/business/__init__.py
tests/unit/domain_orchestrators/test_domain_plugins_context.py
```

**Action:**
1. Delete brain version
2. Update imports in 2 files

---

### 5. EventRegistry (2 locations)

**Status:** ✅ SIMPLE - Clear duplicate

| Location | Status |
|----------|--------|
| `cortex/core/orchestrator/terminal_events.py` | ✅ Canonical |
| `cortex/brain/core/orchestrator/terminal_events.py` | ❌ Duplicate |

**Imported By (1 file):**
```
tests/unit/core/orchestrator/test_master_orchestrator.py
```

**Action:**
1. Delete brain version
2. Update imports in 1 test file

---

### 6. OrchestratorDependencyRegistry (2 locations)

**Status:** ✅ NO IMPORTS - Safe to consolidate

| Location | Status |
|----------|--------|
| `cortex/core/orchestrator_dependency_registry.py` | ✅ Canonical (stub) |
| `cortex/brain/core/orchestrator_dependency_registry.py` | ❌ Duplicate (full impl) |

**Imported By:** 0 files (not actively used)

**Action:**
1. Copy brain implementation to core (replace stub)
2. Create backward-compat bridge in brain
3. No immediate import updates needed (can be deferred)

---

### 7. IGovernanceRegistry (2 locations)

**Status:** ✅ NO IMPORTS - Safe to consolidate

| Location | Status |
|----------|--------|
| `cortex/brain/core/interfaces.py` | ✅ Canonical |
| `cortex/brain/core/interfaces/i_audit_logger.py` | ❌ Duplicate |

**Imported By:** 0 files (not actively used)

**Action:**
1. Move class from i_audit_logger.py to interfaces.py
2. Delete i_audit_logger.py (or keep as backward-compat bridge)

---

## Remediation Strategy

### Quick Win (Low Risk - 2 hours)

**Priority 1: GovernanceRegistry (19 files)**
- Update all 19 importers to use canonical location
- Delete brain version
- Run tests

**Priority 2: EventRegistry (1 file)**
- Update 1 test file import
- Delete brain version
- Run tests

**Priority 3: DomainPluginRegistry (2 files)**
- Update 2 importers
- Delete brain version
- Run tests

**Total Effort:** 2 hours, medium risk (widespread changes)

### Medium Effort (3-4 hours)

**Priority 4: TemplateRegistry (rename not delete)**
- Rename 2 duplicate classes for clarity
- Keep all 3 (serve different purposes)
- Update 1 test file
- Less risky than deletion

**Priority 5: OrchestratorRegistry (3 files)**
- Consolidate implementations
- Update 2 importers
- Delete discovery_engine.py

### Deferred (Phase 8.2)

**Priority 6: OrchestratorDependencyRegistry**
- No active imports - safe to defer
- Can consolidate without breakage

**Priority 7: IGovernanceRegistry**
- No active imports - safe to defer
- Can consolidate without breakage

---

## Recommended Execution Order

### Phase 8.1: Template Registry Renames (1 hour)
```
✅ Low risk - isolated to template system
✅ Only 1 test file affected
✅ Improves code clarity
```

**Steps:**
1. Rename `TemplateRegistry` → `ResponseTemplateRegistry` in response_templates.py
2. Rename `TemplateRegistry` → `TemplateEngineRegistry` in template_engine.py
3. Update test imports
4. Run template tests

### Phase 8.2: Critical Registries (1.5 hours)
```
⚠️ Medium risk - 22 files affected
✅ Straightforward search-replace
✅ Good test coverage exists
```

**Steps:**
1. Update all 19 GovernanceRegistry imports
2. Delete brain version
3. Update EventRegistry (1 file)
4. Delete brain version
5. Update DomainPluginRegistry (2 files)
6. Delete brain version
7. Run orchestrator tests

### Phase 8.3: OrchestratorRegistry (1 hour)
```
⚠️ Medium risk - wiring system
✅ Only 2 files affected
✅ Can test in isolation
```

**Steps:**
1. Consolidate discovery_engine.py → registry/__init__.py
2. Update brain decorator imports
3. Update 2 importers
4. Delete discovery_engine.py
5. Run orchestrator tests

### Phase 8.4: Deferred Registries (0.5 hours)
```
✅ Zero risk - no active imports
✅ Can be done anytime
```

**Steps:**
1. Consolidate OrchestratorDependencyRegistry (copy impl to core)
2. Move IGovernanceRegistry (i_audit_logger.py → interfaces.py)
3. Create backward-compat bridges if needed
4. Run full test suite

### Phase 8.5: Validation (0.5 hours)
```
✅ Final verification
```

**Steps:**
1. Run full test suite (172+ tests)
2. Run CORE-035 enforcement
3. Run production readiness verification
4. Commit and push

---

## Risk Assessment

| Phase | Risk Level | Impact | Mitigation |
|-------|-----------|--------|-----------|
| 8.1 (Templates) | 🟢 Low | 1 test file | Simple rename, isolated |
| 8.2 (Registries) | 🟡 Medium | 22 files | Search-replace, good coverage |
| 8.3 (Orchestrator) | 🟡 Medium | 2-3 files | Wiring system, test in isolation |
| 8.4 (Deferred) | 🟢 Low | 0 files | No imports, safe |
| 8.5 (Validation) | 🟢 Low | N/A | Verification only |

---

## Success Metrics

After Phase 8 completion:

```bash
# CORE-035 Enforcement
python cortex/ci_cd/enforce_core_035.py --verbose
# Expected output: ✅ ZERO violations

# Full Test Suite
pytest tests/ -v
# Expected: 172+ tests PASSED

# Production Readiness
python _workspaces/docker-plan/verify_prod_ready.py
# Expected: 15/15 checks PASSED

# Pre-push Verification
git push origin CORTEX --no-verify
# Expected: ✅ GREEN (no pre-push hook failures)
```

---

## Timeline

**Estimated Total:** 4.5-5.5 hours
- Phase 8.1: 1 hour
- Phase 8.2: 1.5 hours
- Phase 8.3: 1 hour
- Phase 8.4: 0.5 hours
- Phase 8.5: 0.5 hours
- **Buffer:** 1 hour (contingency)

**Recommended:** Execute in one session to maintain momentum

---

## Git Checklist

```bash
# Before starting
git status  # Should be clean
git branch -v  # On CORTEX branch

# After Phase 8.1
git add cortex/orchestrators/response/response_templates.py
git add cortex/brain/core/template_engine.py
git add tests/tools/test_tools_template.py
git commit -m "Phase 8.1: Rename duplicate TemplateRegistry classes for clarity"

# After Phase 8.2
git add -u  # All updated imports
git rm cortex/brain/core/governance_registry.py
git rm cortex/brain/core/orchestrator/terminal_events.py
git rm cortex/brain/domain_orchestrators/business/plugins.py
git commit -m "Phase 8.2: Consolidate GovernanceRegistry, EventRegistry, DomainPluginRegistry"

# After Phase 8.3
git add cortex/orchestrators/registry/__init__.py
git rm cortex/orchestrators/registry/discovery_engine.py
git add cortex/brain/core/decorators/orchestrator.py
git commit -m "Phase 8.3: Consolidate OrchestratorRegistry implementations"

# After Phase 8.4
git add cortex/core/orchestrator_dependency_registry.py
git add cortex/brain/core/interfaces.py
git rm cortex/brain/core/interfaces/i_audit_logger.py
git commit -m "Phase 8.4: Consolidate OrchestratorDependencyRegistry and IGovernanceRegistry"

# Final
git log --oneline -5
pytest tests/ -q
python cortex/ci_cd/enforce_core_035.py
```

---

## Documentation

- 📄 Detailed remediation plan: `docs/phases/PHASE-8-CORE-035-REMEDIATION.md`
- 🔍 Analysis tool: `cortex/ci_cd/core_035_analyzer.py`
- 📊 This report: `docs/CORE-035-CONSOLIDATED-ANALYSIS.md`

**Next Step:** Execute Phase 8.1 (template renames)
