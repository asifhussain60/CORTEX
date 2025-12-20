# Archived: Orchestration 3.0 Legacy Tests

**Archive Date:** December 20, 2025, 08:56 AM
**Reason:** CORTEX 4.0 migration - orchestration_3_0 module removed
**Phase:** CORTEX 4.0 Phase 6 (Orchestrator Consolidation)

## Context

These 28 test files were archived during the CORTEX 3.0 → 4.0 migration because they reference `src.orchestration_3_0.*` modules that no longer exist in CORTEX 4.0.

## Archived Files

### Scaffolding Tests (9 files)
- `test_1_ast_parsing.py` - AST parsing with CodeAnalyzer
- `test_2_dependency_graph.py` - Dependency graph generation
- `test_3_hotspot_identification.py` - Code hotspot detection
- `test_4_pattern_recognition.py` - Architecture pattern recognition
- `test_5_service_decomposition.py` - Service boundary identification
- `test_6_strangler_fig.py` - Strangler fig migration patterns
- `test_7_risk_assessment.py` - Migration risk analysis
- `test_8_folder_structure.py` - Scaffold folder structure generation
- `test_9_boilerplate_validation.py` - Boilerplate code validation

### Planning System Tests (7 files)
- `test_planning_orchestrator.py` - Planning orchestrator integration
- `test_planning_production_validation.py` - Production plan validation
- `test_planning_scenarios_validation.py` - Plan scenario testing
- `test_planning_system_3_0_integration.py` - Full planning system integration
- `test_planning_system_8_phase_validation.py` - 8-phase plan validation
- `test_custom_plan_folder_structure.py` - Custom plan organization
- `test_phase_validator.py` - Phase validation logic

### Orchestrator Smoke Tests (5 files)
- `test_documentation_orchestrator_smoke.py` - Documentation generation
- `test_intelligence_orchestrator_smoke.py` - Intelligence gathering
- `test_observability_orchestrator_smoke.py` - Observability integration
- `test_onboarding_orchestrator_smoke.py` - User onboarding flows
- `test_intelligent_dashboard_smoke.py` - Dashboard generation

### Infrastructure Tests (7 files)
- `test_code_refinement_toolkit.py` - Code quality toolkit
- `test_cortex_implants_e2e.py` - End-to-end implants testing
- `test_dependency_container.py` - Dependency injection container
- `test_edge_case_validator.py` - Edge case detection
- `test_session_manager.py` - Session management
- `test_state_machine.py` - FSM state transitions
- `test_tdd_components.py` - TDD workflow components

## Migration Status

**Orchestration 3.0 → 4.0 Changes:**
- `src.orchestration_3_0.*` → `src.orchestration_4_0.*` + `src.orchestrators.*`
- Consolidated 15+ orchestrators into 8 core workflows
- Removed scaffolding orchestrators (legacy monolith migration features)
- Refactored planning system (now integrated with `src.orchestrators.planning.*`)
- Session management moved to `src.orchestrators.planning.session_manager`

## Future Action

**Option 1: Rewrite Tests (Recommended)**
- Adapt tests to CORTEX 4.0 architecture
- Use new orchestration_4_0 APIs
- Target current active orchestrators in `src.orchestrators.*`

**Option 2: Keep Archived**
- Preserve as historical reference
- Tests for deprecated features (scaffolding, legacy planning)
- No maintenance required

## Related Documentation

- CORTEX 4.0 Migration: `docs/architecture/CORTEX-4.0-MIGRATION.md`
- Orchestration 4.0 Design: `docs/orchestration_4_0/README.md`
- Archive Report: `archive/ARCHIVE_REPORT.md`

---

**Archive Authority:** Admin Governor
**Approval:** Automated migration cleanup (Phase 6)
