# CORTEX Phase 05: Orchestrator Rationalization + MCP Consolidation

## Executive Summary

**Status:** RED Phase Complete ✅  
**Tests Created:** 103 comprehensive RED tests (all in SKIPPED state, as expected)  
**Test Classes:** 17 categories covering complete specification  
**Priority:** P0 (Critical)  
**Risk:** HIGH (120 orchestrators → 44, complex dependency graph)  
**Dependencies:** Phase 04 (Brain Deduplication) — ✅ SATISFIED  

---

## Phase 05 Objectives

Transform CORTEX's orchestrator landscape from 120+ scattered classes to ~44 canonical,
workflow-template-driven orchestrators with consolidated MCP tools (34 → ~22).

### Success Criteria

| Criterion | Target | Status |
|-----------|--------|--------|
| Orchestrators Classified | 120 (all 3 categories) | 🔴 PENDING |
| Active Orchestrators | ~44 (±25% tolerance) | 🔴 PENDING |
| Dormant Orchestrators | ~30 (±25% tolerance) | 🔴 PENDING |
| Dead Orchestrators | ~40 (±25% tolerance) | 🔴 PENDING |
| Duplicates Resolved | 5 known groups | 🔴 PENDING |
| MCP Tools Consolidated | 34 → ~22 | 🔴 PENDING |
| Archived Orchestrators | ~76 (dormant+dead) | 🔴 PENDING |
| Workflow Templates Bound | 100% of active | 🔴 PENDING |
| SQLite Audit Wired | All orchestrators | 🔴 PENDING |
| Zero Broken Imports | Post-migration | 🔴 PENDING |

---

## RED Phase Test Specification

### Test Class 1: TestOrchestratorClassification (6 tests)
Defines orchestrator classification requirements and method.

**Classification Logic:**
- Has execute/run/process method? → Candidate for ACTIVE
- Has tests? → If no, DORMANT (unless MCP-exposed)
- Has callers (imported elsewhere)? → If no, DORMANT
- Is MCP-exposed? → If yes, ACTIVE regardless
- Has workflow template? → Track for binding

**Tests:**
- `test_orchestrator_classification_method_exists`
- `test_classification_returns_active_dormant_dead`
- `test_orchestrators_with_execute_method_candidates_for_active`
- `test_orchestrators_without_tests_candidates_for_dormant`
- `test_orchestrators_without_callers_candidates_for_dormant`
- `test_orchestrators_mcp_exposed_remain_active`

### Test Class 2: TestActiveOrchestratorCount (5 tests)
Validates count and properties of active orchestrators (~40 surviving).

**Tests:**
- `test_active_orchestrator_target_40_plus_minus_10` (±25% tolerance)
- `test_active_orchestrators_have_workflow_templates`
- `test_active_orchestrators_bound_to_lifecycle_templates`
- `test_active_orchestrators_have_execute_method`
- `test_active_orchestrators_listed_in_capability_manifest`

### Test Class 3: TestDormantOrchestratorCount (5 tests)
Validates dormant orchestrator archival (~30 orchestrators).

**Tests:**
- `test_dormant_orchestrator_target_30_plus_minus_10`
- `test_dormant_orchestrators_marked_for_archival`
- `test_dormant_orchestrator_archival_preserves_git_history`
- `test_dormant_orchestrator_imports_removed_from_active_code`
- `test_dormant_orchestrator_archival_creates_restore_plan`

### Test Class 4: TestDeadOrchestratorCount (5 tests)
Validates dead orchestrator archival (~40 orchestrators).

**Tests:**
- `test_dead_orchestrator_target_40_plus_minus_10`
- `test_dead_orchestrators_archived_to_archive_orchestrators`
- `test_dead_orchestrators_no_execute_method`
- `test_dead_orchestrators_fully_superseded_or_stubs`
- `test_dead_orchestrator_archival_permanent`

### Test Class 5: TestDuplicateResolution (10 tests)
Validates resolution of 5 known duplicate orchestrators.

**Known Duplicates:**
1. **EnforcementOrchestrator** (2 locations)
   - cortex/orchestrators/core/enforcement_orchestrator.py
   - cortex/orchestrators/git/enforcement_orchestrator.py
   - Action: Merge into core, extend with git capabilities

2. **RollbackOrchestrator** (2 locations)
   - cortex/orchestrators/support/rollback_orchestrator.py
   - cortex/deployment/rollback_orchestrator.py
   - Action: Merge into one orchestrator

3. **HotReload** (2 locations)
   - cortex/brain/devx/hot_reload.py (archived with Phase 04)
   - cortex/devx/hot_reload.py
   - Action: Keep one, archive other

4. **OrchestratorInventoryAuditor** (2 locations)
   - cortex/phase_38/orchestrator_inventory_auditor.py
   - cortex/tools/orchestrator_inventory_auditor.py
   - Action: Keep tools/ version, archive phase_38/

5. **PlanningOrchestrator** (2 locations)
   - cortex/orchestrators/domain/planning_orchestrator.py
   - cortex/orchestrators/domain/enhanced_planning_orchestrator.py
   - Action: Merge, rename enhanced→planning (no 'enhanced_' prefix)

### Test Class 6: TestWorkflowTemplateBinding (17 tests)
Validates workflow template binding for all active orchestrators.

**Parametrized Tests for:**
- Core orchestrators (9): MasterOrchestrator, TDDOrchestrator, EnforcementOrchestrator, etc.
- Domain orchestrators (3): PlanningOrchestrator, DashboardOrchestrator, RefactoringOrchestrator
- Git orchestrators (2): GitOrchestrator, GitPublishOrchestrator
- Additional validation: Template file existence, step definitions, init loading

### Test Class 7: TestMCPToolConsolidation (7 tests)
Validates MCP tool consolidation (34 → ~22 tools).

**Key Actions:**
- cortex_toolkit tools absorbed into orchestrator MCP methods
- Versioned tools merged (e.g., tool_v1 + tool_v2 → tool)
- Deprecated tools archived with documentation
- MCP server registry updated

### Test Class 8: TestMCPToolSpecificConsolidations (5 tests)
Validates specific tool consolidations.

**Key Consolidations:**
- cortex_challenge → MasterOrchestrator.governance_gate() (EA-009)
- Dashboard tools consolidated
- Refactoring tools consolidated
- Security tools consolidated

### Test Class 9: TestAuditIntegration (8 tests)
Validates SQLite audit database integration into every orchestrator.

**Audit Capture:**
- Orchestrator execution start/end times
- Success/failure status
- Governance violations
- Query interface by orchestrator name
- WAL mode enabled (CORE-058)

### Test Class 10: TestPostRationalizationIntegrity (6 tests)
Validates system integrity after rationalization.

**Tests:**
- No broken imports to archived orchestrators
- No imports to dormant/dead in active code
- All active orchestrator imports valid
- Workflow template references valid
- Governance rules enforced (CORE-048 import quarantine)

### Test Class 11: TestArchiveStructure (6 tests)
Validates _archive/ structure post-archival.

**Archive Layout:**
```
_archive/orchestrators/
├── dormant/          (restore-friendly)
├── dead/             (permanent)
├── metadata.yaml     (classification reasons)
└── restore-plan.yaml (for dormant orchestrators)
```

### Test Class 12: TestDependencyGraphValidation (4 tests)
Validates orchestrator dependency graph.

**Tests:**
- No circular dependencies (DAG requirement)
- Max call depth ≤ 5 levels
- All dependencies resolvable
- No cross-domain boundary violations

### Test Class 13: TestCapabilityManifestUpdate (4 tests)
Validates capability manifest reflects rationalized state.

**Tests:**
- Manifest lists all ~44 active orchestrators
- Manifest excludes archived orchestrators
- Manifest lists ~22 consolidated MCP tools
- Manifest references workflow templates for each orchestrator

### Test Class 14: TestRegressionFromPhase04 (5 tests)
Validates Phase 04 completeness preserved.

**Tests:**
- Brain deduplication archival (_archive/brain/) preserved
- Brain migration imports still resolve
- Phase 04 tests (41/41) still passing
- CORE governance rules enforced
- Package consolidation (1 package) valid

### Test Class 15: TestPhase05Completion (11 tests)
Validates Phase 05 completion criteria.

**Tests:**
- All 120 orchestrators classified
- Classification documented in registry
- 44 active orchestrators survive
- 76 dormant/dead orchestrators archived
- 5 known duplicates resolved
- 22 MCP tools consolidated
- All active orchestrators have tests
- All active orchestrators bound to workflow templates
- Master plan marked Phase 05 complete
- Zero new test failures

---

## Current Orchestrator Inventory

**Baseline (Pre-Phase 05):**
- Total orchestrator classes: 62+ (from grep)
- Total orchestrator Python files: 191
- Orchestrator directories: 26+ subdirectories

**Phase 05 Targets:**
- Active: ~44 (all with workflow templates, tests, execution methods)
- Dormant: ~30 (archivable, restoreable, no active callers)
- Dead: ~40 (stubs, superseded, permanent archival)

---

## Known Orchestrator Categories (Phase 05 Spec)

### Core Orchestrators (9 expected ACTIVE)
- **MasterOrchestrator** → lifecycle/master-orchestration.yaml (MCP-exposed)
- **TDDOrchestrator** → tdd/tdd-feature-implementation.yaml (MCP-exposed)
- **EnforcementOrchestrator** → governance/enforcement-pipeline.yaml (MCP-exposed, merged)
- **IntentRouter** → lifecycle/intent-routing.yaml
- **InteractionOrchestrator** → lifecycle/interaction-pipeline.yaml
- **WorkflowOrchestrator** → lifecycle/workflow-execution.yaml (MCP-exposed)
- **MasterPlanOrchestrator** → lifecycle/master-plan-execution.yaml (MCP-exposed)
- **ReviewOrchestrator** → quality/code-review.yaml
- **SecurityOrchestrator** → security/security-compliance-audit.yaml (MCP-exposed)

### Domain Orchestrators (3 expected ACTIVE)
- **PlanningOrchestrator** → lifecycle/planning-workflow.yaml (MCP-exposed)
- **DashboardOrchestrator** → lifecycle/dashboard-generation.yaml (MCP-exposed)
- **RefactoringOrchestrator** → quality/refactor-holistic-sweep.yaml (MCP-exposed)

### Git Orchestrators (2+ expected ACTIVE)
- **GitOrchestrator** → lifecycle/git-operations.yaml (MCP-exposed)
- **GitPublishOrchestrator** → (needs workflow template)

---

## Phase 05 Implementation Plan (GREEN Phase)

### Stage 1: Discovery & Classification (Days 1-2)
1. Scan all 120+ orchestrators using classification heuristic
2. Build orchestrator inventory with metadata (location, tests, callers, MCP-exposed)
3. Identify all 5 known duplicates
4. Generate classification report (active/dormant/dead counts)
5. Document orchestrator dependency graph

### Stage 2: Duplicate Resolution (Day 2)
1. Merge EnforcementOrchestrator (core canonical, extends git capabilities)
2. Merge RollbackOrchestrator (deployment canonical with general + deployment features)
3. Keep HotReload (cortex/devx/), archive cortex/brain/devx/hot_reload.py
4. Keep OrchestratorInventoryAuditor (cortex/tools/), archive cortex/phase_38/
5. Rename enhanced_planning_orchestrator.py → planning_orchestrator.py, archive old

### Stage 3: Archival (Days 2-3)
1. Create _archive/orchestrators/dormant/ and _archive/orchestrators/dead/
2. Use git mv to preserve history for each archived orchestrator
3. Generate metadata files (classification_reasons.yaml, restore_plan.yaml)
4. Remove imports to archived orchestrators from active code
5. Validate import quarantine (CORE-048)

### Stage 4: Workflow Template Binding (Days 3-4)
1. Verify workflow template YAML files exist for all 44 active orchestrators
2. Create missing templates (if any)
3. Update OrchestratorBase to load workflow template during __init__
4. Validate template structure (setup/execute/teardown steps)
5. Test orchestrator initialization with templates

### Stage 5: MCP Tool Consolidation (Days 4-5)
1. Inventory all 34 MCP tools
2. Identify versioned duplicates (tool_v1 + tool_v2 → tool)
3. Merge toolkit tools into orchestrator MCP methods
4. Absorb cortex_challenge into MasterOrchestrator.governance_gate()
5. Update MCP server registry with ~22 consolidated tools
6. Remove deprecated tool imports

### Stage 6: SQLite Audit Integration (Days 5-6)
1. Wire CortexAuditDB into OrchestratorBase.teardown()
2. Add execution logging to every orchestrator
3. Capture: start_time, end_time, success/failure, governance_violations
4. Implement audit query interface (by orchestrator_name)
5. Verify WAL mode enabled (CORE-058)

### Stage 7: Validation & Regression (Day 6-7)
1. Run all 103 GREEN tests (expect 103/103 passing)
2. Run Phase 04 regression tests (41/41 still passing)
3. Run core test suite (61+ tests still passing)
4. Validate import quarantine (no stale imports)
5. Validate workflow template references
6. Update capability manifest with rationalized state

### Stage 8: Master Plan Update & Commit (Day 7)
1. Update master plan: Phase 05 → COMPLETE
2. Update progress metrics (tests_passing: 103, coverage_pct: 100)
3. Update baseline: 120→44 orchestrators, 34→22 MCP tools
4. Commit with full execution statistics
5. Verify all deliverables documented in registry

---

## Metrics & Thresholds

| Metric | Baseline | Target | ±Tolerance | Status |
|--------|----------|--------|------------|--------|
| Orchestrator Classes | 120+ | 44 | ±25% (33-55) | 🔴 PENDING |
| MCP Tools | 34 | 22 | ±15% (19-25) | 🔴 PENDING |
| Archived Orchestrators | 0 | 76 | ±15% | 🔴 PENDING |
| Tests Passing | 0 | 103 | 100% | 🔴 PENDING |
| Test Coverage | 0% | 100% | 100% | 🔴 PENDING |
| Regression | - | 0 new failures | ZERO | 🔴 PENDING |

---

## Risk Assessment

### HIGH RISK Factors
1. **Large Scope:** 120 orchestrators across 26+ directories
2. **Complex Dependencies:** Orchestrator call graph may have circular references
3. **Breaking Changes:** Duplicate resolution may affect existing code
4. **Import Impact:** Archival requires comprehensive import rewriting
5. **Workflow Template Binding:** All 44 active orchestrators must have templates

### Mitigation Strategies
1. Use git mv to preserve history (reversible)
2. Create restore plans for dormant orchestrators
3. Comprehensive import scanning before and after
4. Incremental validation (classify → resolve → archive → bind)
5. Phase 04 regression gates (must pass before Phase 05 commit)

### Rollback Plan
- All orchestrators committed to git with full history
- _archive/orchestrators/ contains restore instructions
- restore_plan.yaml provides automated restoration for dormant orchestrators
- If critical failure: `git reset --hard HEAD~1` and investigate

---

## Deliverables

### D1: Orchestrator Classification Report
- Location: `cortex-registry/planning/artifacts/phase-05/orchestrator-inventory.yaml`
- Content: All 120 orchestrators classified (active/dormant/dead) with metadata

### D2: Duplicate Resolution Documentation
- Location: `cortex-registry/planning/artifacts/phase-05/duplicate-resolution.yaml`
- Content: 5 duplicate groups, merge actions, unique logic preserved

### D3: Archived Orchestrators
- Location: `_archive/orchestrators/`
- Content: dormant/ + dead/ subdirectories with metadata

### D4: Workflow Template Bindings
- Location: `cortex-registry/workflows/templates/`
- Content: 44 workflow template YAML files (1 per active orchestrator)

### D5: MCP Tool Consolidation Map
- Location: `cortex-registry/planning/artifacts/phase-05/mcp-consolidation.yaml`
- Content: 34 → 22 tools, merge decisions, deprecated tools

### D6: SQLite Audit Integration
- Location: `cortex/infrastructure/audit_db.py` (enhanced)
- Content: Orchestrator execution logging schema, teardown hook

### D7: Updated Capability Manifest
- Location: `cortex-registry/core/capability-manifest.yaml`
- Content: 44 active orchestrators, 22 MCP tools, workflow template references

---

## Next Steps

1. ✅ **RED Phase Complete:** 103 tests created, all skipped (as expected)
2. 🔴 **Review Specification:** User review of Phase 05 DoR
3. 🔴 **GREEN Phase:** Implement OrchestratorRationalizationOrchestrator
4. 🔴 **Execute Migration:** Run orchestrator classification, archival, consolidation
5. 🔴 **Validation:** All 103 tests passing post-implementation
6. 🔴 **Commit & Close:** Master plan Phase 05 → COMPLETE

---

## File Structure

```
tests/unit/phases/refactor/
├── test_phase_01_foundation.py                        (49 tests, ✅ COMPLETE)
├── test_phase_02_governance.py                        (38 tests, ✅ COMPLETE)
├── test_phase_03_packages.py                          (64 tests, ✅ COMPLETE)
├── test_phase_04_brain_deduplication.py               (41 tests, ✅ COMPLETE)
└── test_phase_05_orchestrator_rationalization.py      (103 tests, 🔴 SKIPPED — RED PHASE)
```

**Total RED/GREEN Tests:** 295 tests across 5 phases
**Phases Complete:** 4/10 (Phase 01, 02, 03, 04)
**Tests Passing (Phases 1-4):** 192/192 ✅
**Phases Pending:** 6/10 (Phase 05-10)

---

## Estimated Effort

- **RED Phase:** ✅ Complete (4 hours)
- **GREEN Phase:** 5-7 days (discovery, implementation, validation)
- **Total Phase 05 Duration:** 1 week (parallel work possible)

---

## Status Summary

```
╔════════════════════════════════════════════════════════════╗
║  PHASE 05: ORCHESTRATOR RATIONALIZATION + MCP CONSOLIDATION  ║
╠════════════════════════════════════════════════════════════╣
║  Status:         🔴 RED PHASE COMPLETE                      ║
║  Tests Created:  103 (17 test classes)                      ║
║  Tests Skipped:  103 (expected — awaiting implementation)   ║
║  Priority:       P0 (Critical)                              ║
║  Risk:           HIGH (complex dependency graph)            ║
║  Dependencies:   Phase 04 ✅ SATISFIED                      ║
║                                                             ║
║  Ready for:      GREEN Phase Implementation                 ║
║  Next Action:    Build OrchestratorRationalizationOrchestrator ║
╚════════════════════════════════════════════════════════════╝
```

---

**Generated:** 2026-02-19  
**TDD Stage:** RED ✅ (Test Specification Complete)  
**Awaiting:** GREEN Phase (Implementation & Execution)
