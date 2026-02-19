# Phase 05 GREEN: Duplicate Resolution Plan

## Objective
Resolve 5 known duplicate orchestrator groups by merging, archiving, and consolidating.

## 1. EnforcementOrchestrator ✅ IDENTIFIED
**Locations:**
- `cortex/orchestrators/core/enforcement_orchestrator.py` (1492 lines - General governance)
- `cortex/orchestrators/git/enforcement_orchestrator.py` (420 lines - Git-specific)

**Analysis:**
- Core version: General governance enforcement with 8 specialized agents for CORE rules
- Git version: Pre-commit enforcement with 9 git-specific checks

**Resolution Strategy:**
- **Action:** Keep core version as canonical
- **Merge:** Extract git-specific checks from git version
- **Enhancement:** Add git capabilities to core version as optional module
- **Archive:** Move git version to `_archive/orchestrators/enforcement_orchestrator_git_legacy.py`
- **Tests:** Consolidate tests from both versions
- **Command:** `git mv cortex/orchestrators/git/enforcement_orchestrator.py _archive/orchestrators/enforcement_orchestrator_git_legacy.py`

---

## 2. RollbackOrchestrator ✅ IDENTIFIED
**Locations:**
- `cortex/orchestrators/support/rollback_orchestrator.py`
- `cortex/deployment/rollback_orchestrator.py`

**Analysis:**
- Support version: General rollback orchestration
- Deployment version: Deployment-specific rollback

**Resolution Strategy:**
- **Action:** Keep support version as primary (better directory for cross-domain use)
- **Merge:** Extract deployment-specific logic from deployment version
- **Enhancement:** Add deployment context awareness to support version
- **Archive:** Move deployment version to `_archive/orchestrators/rollback_orchestrator_deployment_legacy.py`
- **Tests:** Consolidate tests
- **Command:** `git mv cortex/deployment/rollback_orchestrator.py _archive/orchestrators/rollback_orchestrator_deployment_legacy.py`

---

## 3. HotReloadOrchestrator ✅ IDENTIFIED
**Locations:**
- `cortex/brain/devx/hot_reload.py` ❌ (Not found - archived in Phase 04)
- `cortex/devx/hot_reload.py` ✅ (Primary - active)

**Analysis:**
- Brain version was already archived in Phase 04
- DevX version is canonical

**Resolution Strategy:**
- **Action:** Keep devx version as canonical
- **Status:** Already resolved (brain version archived)
- **Verification:** Confirm brain version is in archive
- **Command:** No action needed

---

## 4. OrchestratorInventoryAuditor ✅ IDENTIFIED
**Locations:**
- `cortex/phase_38/orchestrator_inventory_auditor.py` (Phase 38 experimental)
- `cortex/tools/orchestrator_inventory_auditor.py` (Tools version)

**Analysis:**
- Phase 38 version: Experimental inventory auditor
- Tools version: Canonical, stable version

**Resolution Strategy:**
- **Action:** Keep tools version as canonical
- **Archive:** Move phase 38 version to `_archive/orchestrators/orchestrator_inventory_auditor_phase38.py`
- **Tests:** Use tools version tests
- **Command:** `git mv cortex/phase_38/orchestrator_inventory_auditor.py _archive/orchestrators/orchestrator_inventory_auditor_phase38.py`

---

## 5. PlanningOrchestrator ✅ IDENTIFIED
**Locations:**
- `cortex/orchestrators/domain/planning_orchestrator.py` (Original)
- `cortex/orchestrators/domain/enhanced_planning_orchestrator.py` (Enhanced)

**Analysis:**
- Original version: Base planning orchestrator
- Enhanced version: Extended planning with additional capabilities

**Resolution Strategy:**
- **Action:** Merge enhanced into original, remove 'enhanced_' prefix
- **Merge:** Extract unique logic from enhanced version into original
- **Consolidate:** planning_orchestrator.py absorbs all enhanced capabilities
- **Archive:** Move enhanced version to `_archive/orchestrators/planning_orchestrator_legacy_enhanced.py`
- **Rename:** Keep `planning_orchestrator.py` as canonical (no 'enhanced_' prefix)
- **Tests:** Consolidate all tests under planning orchestrator tests
- **Commands:**
  - `git mv cortex/orchestrators/domain/planning_orchestrator.py cortex/orchestrators/domain/planning_orchestrator_backup.py`
  - Merge logic from `enhanced_planning_orchestrator.py` into new `planning_orchestrator.py`
  - `git mv cortex/orchestrators/domain/planning_orchestrator_backup.py cortex/orchestrators/domain/planning_orchestrator.py`
  - `git mv cortex/orchestrators/domain/enhanced_planning_orchestrator.py _archive/orchestrators/planning_orchestrator_legacy_enhanced.py`

---

## Implementation Phases

### Phase 05.2A: Enforcement Orchestrator Resolution
1. Analyze git-specific checks in git version
2. Extract git capability module
3. Enhance core version with optional git module
4. Consolidate tests (both versions)
5. Archive git version with git history preserved
6. Verify no broken imports

### Phase 05.2B: Rollback Orchestrator Resolution
1. Analyze deployment-specific logic in deployment version
2. Extract deployment context awareness
3. Enhance support version with deployment context
4. Consolidate tests
5. Archive deployment version
6. Verify no broken imports

### Phase 05.2C: Inventory Auditor Resolution
1. Verify tools version is current
2. Archive phase 38 version
3. Update imports if necessary
4. Verify tests pass

### Phase 05.2D: Planning Orchestrator Resolution
1. Extract unique logic from enhanced version
2. Merge into original planning orchestrator
3. Remove all 'enhanced_' references
4. Consolidate tests
5. Archive enhanced version
6. Update all imports

### Phase 05.2E: HotReload Verification
1. Confirm brain version is archived (Phase 04)
2. Verify devx version is canonical
3. No additional action needed

---

## Verification Checklist

- [ ] All 5 duplicates identified and located
- [ ] Canonical versions selected for each
- [ ] Merge strategies documented
- [ ] Tests consolidated
- [ ] Archive directory created: `_archive/orchestrators/`
- [ ] Git history preserved via `git mv`
- [ ] No broken imports post-merge
- [ ] All 112 orchestrators properly classified
- [ ] Dependency graph updated
- [ ] Phase 05 tests (TestDuplicateResolution) passing

---

## Success Criteria
- [ ] 5 duplicate groups resolved → 3 canonical instances
- [ ] All merge logic consolidated into canonical versions
- [ ] Legacy versions archived with restore capability
- [ ] Zero broken imports across codebase
- [ ] All tests pass
- [ ] Git history preserved for all archival
- [ ] Phase 05 GREEN proceeds to workflow template binding

---

## Status
🟡 **READY FOR IMPLEMENTATION** (Discovery phase complete, duplicate resolution pending)

---

**Authority:** CORE-035 (Single Canonical Implementation), CORE-008 (TDD)
**Phase:** 05 GREEN (Orchestrator Rationalization)
**Target Completion:** Current phase
**Next Stage:** Workflow template binding (44 active orchestrators)
