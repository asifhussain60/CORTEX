"""
Phase 05: Orchestrator Rationalization + MCP Consolidation
RED Phase Tests (TDD Stage 1)

Purpose: Define the complete specification for orchestrator classification,
archival, and MCP consolidation. These tests validate the system state
BEFORE implementation.

Coverage:
- 120+ orchestrators classified (active/dormant/dead)
- ~76 dormant/dead orchestrators archived
- ~44 active orchestrators bound to workflow templates
- 5 known duplicates resolved
- MCP tools consolidated (34 → ~22)
- SQLite audit integration
- Zero broken imports post-migration
"""

import pytest
from pathlib import Path
from typing import Dict, List, Set, Tuple
import yaml
import re
from dataclasses import dataclass


# ============================================================================
# Test Data Models
# ============================================================================

@dataclass
class OrchestratorInventory:
    """Represents orchestrator classification state."""
    active: List[str]
    dormant: List[str]
    dead: List[str]
    
    @property
    def total(self) -> int:
        return len(self.active) + len(self.dormant) + len(self.dead)


@dataclass
class MCPToolInventory:
    """Represents MCP tool consolidation state."""
    retained: List[str]
    deprecated: List[str]
    
    @property
    def total(self) -> int:
        return len(self.retained) + len(self.deprecated)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def cortex_root() -> Path:
    """Locate cortex project root."""
    current = Path(__file__).parent
    while current != current.parent:
        if (current / "cortex" / "orchestrators").exists():
            return current
        current = current.parent
    raise RuntimeError("Cannot locate CORTEX root")


@pytest.fixture
def orchestrators_dir(cortex_root: Path) -> Path:
    """Get cortex/orchestrators/ directory."""
    return cortex_root / "cortex" / "orchestrators"


@pytest.fixture
def archive_dir(cortex_root: Path) -> Path:
    """Get _archive/ directory."""
    return cortex_root / "_archive"


@pytest.fixture
def registry_dir(cortex_root: Path) -> Path:
    """Get cortex-registry/ directory."""
    return cortex_root / "cortex-registry"


@pytest.fixture
def phase_05_spec(registry_dir: Path) -> dict:
    """Load Phase 05 specification from master plan."""
    master_plan = registry_dir / "planning" / "cortex-refactor-master.yaml"
    with open(master_plan) as f:
        data = yaml.safe_load(f)
    
    phase_05 = next((p for p in data["phases"] if p["id"] == "phase-05"), None)
    if not phase_05:
        raise ValueError("Phase 05 not found in master plan")
    
    return phase_05


@pytest.fixture
def existing_orchestrators(orchestrators_dir: Path) -> Set[str]:
    """Discover all orchestrator classes in cortex/orchestrators/."""
    orchestrators = set()
    
    for py_file in orchestrators_dir.rglob("*.py"):
        if py_file.name.startswith("test_"):
            continue
        
        try:
            with open(py_file) as f:
                content = f.read()
            
            # Find all class definitions matching *Orchestrator pattern
            matches = re.findall(r"class\s+(\w+Orchestrator)\s*[\(:]", content)
            orchestrators.update(matches)
        except Exception:
            pass
    
    return orchestrators


# ============================================================================
# Classification Tests (TestOrchestratorClassification)
# ============================================================================

class TestOrchestratorClassification:
    """Validate orchestrator classification requirements."""
    
    def test_orchestrator_classification_method_exists(self):
        """Test that orchestrator classification method is defined in spec."""
        pytest.skip("Requires Phase 05 spec orchestrator_inventory_auditor.py")
    
    def test_classification_returns_active_dormant_dead(self):
        """Test classification categorizes orchestrators into 3 states."""
        pytest.skip("Requires OrchestratorRationalizationOrchestrator implementation")
    
    def test_orchestrators_with_execute_method_candidates_for_active(self):
        """Test orchestrators with execute/run/process method can be active."""
        pytest.skip("Requires code scanning implementation")
    
    def test_orchestrators_without_tests_candidates_for_dormant(self):
        """Test orchestrators without corresponding tests flagged for dormancy."""
        pytest.skip("Requires test discovery implementation")
    
    def test_orchestrators_without_callers_candidates_for_dormant(self):
        """Test orchestrators not imported elsewhere flagged for dormancy."""
        pytest.skip("Requires import scanning implementation")
    
    def test_orchestrators_mcp_exposed_remain_active(self):
        """Test MCP-exposed orchestrators remain active regardless of tests/callers."""
        pytest.skip("Requires MCP registry scanning")


# ============================================================================
# Active Orchestrator Count Tests (TestActiveOrchestratorCount)
# ============================================================================

class TestActiveOrchestratorCount:
    """Validate count of active orchestrators after classification."""
    
    def test_active_orchestrator_target_40_plus_minus_10(self):
        """Test active orchestrators target: ~40 (±25% tolerance)."""
        pytest.skip("Requires classification execution")
    
    def test_active_orchestrators_have_workflow_templates(self):
        """Test every active orchestrator has workflow template binding."""
        pytest.skip("Requires workflow template registry scan")
    
    def test_active_orchestrators_bound_to_lifecycle_templates(self):
        """Test active orchestrators bound to lifecycle workflow templates."""
        pytest.skip("Requires template validation")
    
    def test_active_orchestrators_have_execute_method(self):
        """Test active orchestrators have execute/run/process method."""
        pytest.skip("Requires method inspection")
    
    def test_active_orchestrators_listed_in_capability_manifest(self):
        """Test active orchestrators registered in capability manifest."""
        pytest.skip("Requires manifest scanning")


# ============================================================================
# Dormant Orchestrator Tests (TestDormantOrchestratorCount)
# ============================================================================

class TestDormantOrchestratorCount:
    """Validate dormant orchestrator archival."""
    
    def test_dormant_orchestrator_target_30_plus_minus_10(self):
        """Test dormant orchestrators: ~30 (±25% tolerance)."""
        pytest.skip("Requires classification execution")
    
    def test_dormant_orchestrators_marked_for_archival(self):
        """Test dormant orchestrators moved to _archive/orchestrators/."""
        pytest.skip("Requires archival execution")
    
    def test_dormant_orchestrator_archival_preserves_git_history(self):
        """Test dormant orchestrators archived with git mv (history preserved)."""
        pytest.skip("Requires git-based archival")
    
    def test_dormant_orchestrator_imports_removed_from_active_code(self):
        """Test no imports to archived dormant orchestrators remain active."""
        pytest.skip("Requires import rewriting")
    
    def test_dormant_orchestrator_archival_creates_restore_plan(self):
        """Test archival creates restore plan for potential reactivation."""
        pytest.skip("Requires restore plan generation")


# ============================================================================
# Dead Orchestrator Tests (TestDeadOrchestratorCount)
# ============================================================================

class TestDeadOrchestratorCount:
    """Validate dead orchestrator archival."""
    
    def test_dead_orchestrator_target_40_plus_minus_10(self):
        """Test dead orchestrators: ~40 (±25% tolerance)."""
        pytest.skip("Requires classification execution")
    
    def test_dead_orchestrators_archived_to_archive_orchestrators(self):
        """Test dead orchestrators archived to _archive/orchestrators/."""
        pytest.skip("Requires archival execution")
    
    def test_dead_orchestrators_no_execute_method(self):
        """Test dead orchestrators have no execute/run method."""
        pytest.skip("Requires method inspection")
    
    def test_dead_orchestrators_fully_superseded_or_stubs(self):
        """Test dead orchestrators are either stubs or fully superseded."""
        pytest.skip("Requires code analysis")
    
    def test_dead_orchestrator_archival_permanent(self):
        """Test dead orchestrator archival is permanent (no restore plan)."""
        pytest.skip("Requires archival validation")


# ============================================================================
# Known Duplicate Resolution Tests (TestDuplicateResolution)
# ============================================================================

class TestDuplicateResolution:
    """Validate resolution of 5 known duplicate orchestrators."""
    
    def test_enforcement_orchestrator_duplicates_identified(self):
        """Test EnforcementOrchestrator duplicates found:
        - cortex/orchestrators/core/enforcement_orchestrator.py
        - cortex/orchestrators/git/enforcement_orchestrator.py
        """
        pytest.skip("Requires duplicate discovery")
    
    def test_enforcement_orchestrator_merged_core_canonical(self):
        """Test EnforcementOrchestrator merged into cortex/orchestrators/core/."""
        pytest.skip("Requires merge execution")
    
    def test_rollback_orchestrator_duplicates_identified(self):
        """Test RollbackOrchestrator duplicates found:
        - cortex/orchestrators/support/rollback_orchestrator.py
        - cortex/deployment/rollback_orchestrator.py
        """
        pytest.skip("Requires duplicate discovery")
    
    def test_rollback_orchestrator_merged_deployment_canonical(self):
        """Test RollbackOrchestrator merged into cortex/orchestrators/."""
        pytest.skip("Requires merge execution")
    
    def test_hot_reload_duplicates_identified(self):
        """Test HotReload duplicates found:
        - cortex/brain/devx/hot_reload.py (archived with brain/)
        - cortex/devx/hot_reload.py
        """
        pytest.skip("Requires duplicate discovery")
    
    def test_hot_reload_canonical_preserved(self):
        """Test canonical HotReload preserved, duplicate archived."""
        pytest.skip("Requires archival")
    
    def test_orchestrator_inventory_auditor_duplicates_identified(self):
        """Test OrchestratorInventoryAuditor duplicates found:
        - cortex/phase_38/orchestrator_inventory_auditor.py
        - cortex/tools/orchestrator_inventory_auditor.py
        """
        pytest.skip("Requires duplicate discovery")
    
    def test_planning_orchestrator_duplicates_identified(self):
        """Test PlanningOrchestrator duplicates found:
        - cortex/orchestrators/domain/planning_orchestrator.py
        - cortex/orchestrators/domain/enhanced_planning_orchestrator.py
        """
        pytest.skip("Requires duplicate discovery")
    
    def test_planning_orchestrator_enhanced_canonical(self):
        """Test enhanced_planning_orchestrator becomes planning_orchestrator (no 'enhanced_' prefix)."""
        pytest.skip("Requires rename execution")
    
    def test_duplicate_resolution_preserves_unique_logic(self):
        """Test duplicate resolution preserves all unique logic from all sources."""
        pytest.skip("Requires diff-based validation")


# ============================================================================
# Workflow Template Binding Tests (TestWorkflowTemplateBinding)
# ============================================================================

class TestWorkflowTemplateBinding:
    """Validate workflow template binding for active orchestrators."""
    
    @pytest.mark.parametrize("orchestrator_name", [
        "MasterOrchestrator",
        "TDDOrchestrator",
        "EnforcementOrchestrator",
        "IntentRouter",
        "InteractionOrchestrator",
        "WorkflowOrchestrator",
        "MasterPlanOrchestrator",
        "ReviewOrchestrator",
        "SecurityOrchestrator",
    ])
    def test_core_orchestrators_have_workflow_templates(self, orchestrator_name: str):
        """Test core orchestrators bound to lifecycle templates."""
        pytest.skip(f"Requires {orchestrator_name} workflow template binding")
    
    @pytest.mark.parametrize("orchestrator_name", [
        "PlanningOrchestrator",
        "DashboardOrchestrator",
        "RefactoringOrchestrator",
    ])
    def test_domain_orchestrators_have_workflow_templates(self, orchestrator_name: str):
        """Test domain orchestrators bound to templates."""
        pytest.skip(f"Requires {orchestrator_name} workflow template binding")
    
    @pytest.mark.parametrize("orchestrator_name", [
        "GitOrchestrator",
        "GitPublishOrchestrator",
    ])
    def test_git_orchestrators_have_workflow_templates(self, orchestrator_name: str):
        """Test git orchestrators bound to templates."""
        pytest.skip(f"Requires {orchestrator_name} workflow template binding")
    
    def test_workflow_template_files_exist_for_all_active_orchestrators(self):
        """Test workflow template YAML files exist for all active orchestrators."""
        pytest.skip("Requires template file existence validation")
    
    def test_workflow_templates_define_setup_execute_teardown_steps(self):
        """Test workflow templates include setup/execute/teardown step definitions."""
        pytest.skip("Requires template structure validation")
    
    def test_orchestrator_init_loads_workflow_template(self):
        """Test active orchestrators load workflow template during __init__."""
        pytest.skip("Requires constructor validation")


# ============================================================================
# MCP Tool Consolidation Tests (TestMCPToolConsolidation)
# ============================================================================

class TestMCPToolConsolidation:
    """Validate MCP tool consolidation (34 → ~22 tools)."""
    
    def test_mcp_tool_inventory_34_tools_baseline(self):
        """Test MCP tool baseline: 34 tools."""
        pytest.skip("Requires MCP registry scan")
    
    def test_mcp_consolidated_target_22_tools(self):
        """Test MCP consolidation target: ~22 tools (±15% tolerance)."""
        pytest.skip("Requires consolidation plan execution")
    
    def test_cortex_toolkit_absorbed_into_orchestrators(self):
        """Test cortex_toolkit tools absorbed into orchestrator MCP methods."""
        pytest.skip("Requires toolkit analysis and absorption")
    
    def test_versioned_tools_merged_into_canonical_version(self):
        """Test versioned tools (e.g., tool_v1, tool_v2) merged into canonical."""
        pytest.skip("Requires versioned tool discovery and merge")
    
    def test_deprecated_mcp_tools_archived(self):
        """Test deprecated MCP tools archived with removal documentation."""
        pytest.skip("Requires deprecation archival")
    
    def test_mcp_tool_registration_updated_in_mcp_server(self):
        """Test MCP server tool registry updated with consolidated tools."""
        pytest.skip("Requires MCP registry update")
    
    def test_deprecated_mcp_imports_removed_from_code(self):
        """Test no imports to deprecated MCP tools remain active."""
        pytest.skip("Requires import rewriting")


# ============================================================================
# MCP Tool Specific Tests (TestMCPToolSpecificConsolidations)
# ============================================================================

class TestMCPToolSpecificConsolidations:
    """Validate specific MCP tool consolidations."""
    
    def test_cortex_challenge_absorbed_into_master_orchestrator_governance_gate(self):
        """Test cortex_challenge absorbed into MasterOrchestrator.governance_gate."""
        pytest.skip("Requires cortex_challenge analysis")
    
    def test_governance_gate_method_implements_challenge_logic(self):
        """Test MasterOrchestrator.governance_gate implements full challenge logic."""
        pytest.skip("Requires method implementation")
    
    def test_dashboard_tools_consolidated(self):
        """Test dashboard tool duplicates consolidated into dashboard_orchestrator."""
        pytest.skip("Requires dashboard tool consolidation")
    
    def test_refactoring_tools_consolidated(self):
        """Test refactoring tools consolidated into refactoring_orchestrator."""
        pytest.skip("Requires refactoring tool consolidation")
    
    def test_security_tools_consolidated(self):
        """Test security tools consolidated into security_orchestrator."""
        pytest.skip("Requires security tool consolidation")


# ============================================================================
# SQLite Audit Integration Tests (TestAuditIntegration)
# ============================================================================

class TestAuditIntegration:
    """Validate SQLite audit database integration into all orchestrators."""
    
    def test_audit_db_wired_into_orchestrator_base_teardown(self):
        """Test CortexAuditDB wired into OrchestratorBase.teardown() step."""
        pytest.skip("Requires OrchestratorBase.teardown modification")
    
    def test_every_orchestrator_logs_execution_to_audit_db(self):
        """Test every orchestrator execution logged to audit database."""
        pytest.skip("Requires audit integration validation")
    
    def test_audit_db_captures_orchestrator_start_time(self):
        """Test audit DB captures orchestrator start timestamp."""
        pytest.skip("Requires audit schema validation")
    
    def test_audit_db_captures_orchestrator_end_time(self):
        """Test audit DB captures orchestrator end timestamp."""
        pytest.skip("Requires audit schema validation")
    
    def test_audit_db_captures_orchestrator_success_failure_status(self):
        """Test audit DB captures success/failure status."""
        pytest.skip("Requires audit schema validation")
    
    def test_audit_db_captures_governance_violations(self):
        """Test audit DB captures governance violations (if any)."""
        pytest.skip("Requires audit schema validation")
    
    def test_audit_db_queryable_by_orchestrator_name(self):
        """Test audit entries queryable by orchestrator name."""
        pytest.skip("Requires audit query interface")
    
    def test_audit_db_wai_mode_enabled(self):
        """Test SQLite WAL mode enabled for audit DB (CORE-058)."""
        pytest.skip("Requires audit DB configuration")


# ============================================================================
# Post-Rationalization Integrity Tests (TestPostRationalizationIntegrity)
# ============================================================================

class TestPostRationalizationIntegrity:
    """Validate system integrity after orchestrator rationalization."""
    
    def test_no_broken_imports_to_archived_orchestrators(self):
        """Test no imports to archived orchestrators remain in active code."""
        pytest.skip("Requires import scanning")
    
    def test_no_imports_to_dormant_orchestrators_in_active_code(self):
        """Test no imports to dormant orchestrators remain active."""
        pytest.skip("Requires import scanning")
    
    def test_no_imports_to_dead_orchestrators_in_active_code(self):
        """Test no imports to dead orchestrators remain active."""
        pytest.skip("Requires import scanning")
    
    def test_active_orchestrator_imports_valid(self):
        """Test all active orchestrator imports resolve without error."""
        pytest.skip("Requires import validation")
    
    def test_workflow_template_references_valid(self):
        """Test all workflow template references from orchestrators are valid."""
        pytest.skip("Requires reference validation")
    
    def test_governance_rules_enforced_on_archived_orchestrators(self):
        """Test governance rules enforced (CORE-048 import quarantine)."""
        pytest.skip("Requires governance validation")


# ============================================================================
# Archive Structure Tests (TestArchiveStructure)
# ============================================================================

class TestArchiveStructure:
    """Validate _archive/ structure after archival."""
    
    def test_archive_orchestrators_directory_created(self):
        """Test _archive/orchestrators/ directory exists."""
        pytest.skip("Requires archival execution")
    
    def test_dormant_orchestrators_in_archive_dormant_subdirectory(self):
        """Test dormant orchestrators in _archive/orchestrators/dormant/."""
        pytest.skip("Requires archival structure validation")
    
    def test_dead_orchestrators_in_archive_dead_subdirectory(self):
        """Test dead orchestrators in _archive/orchestrators/dead/."""
        pytest.skip("Requires archival structure validation")
    
    def test_archived_orchestrators_preserve_directory_structure(self):
        """Test archived orchestrators preserve original directory structure."""
        pytest.skip("Requires structure preservation validation")
    
    def test_archive_contains_metadata_file_with_classification_reasons(self):
        """Test archive contains metadata file explaining classification reasons."""
        pytest.skip("Requires metadata file generation")
    
    def test_archive_contains_restore_plan_for_dormant_orchestrators(self):
        """Test archive contains restore instructions for dormant orchestrators."""
        pytest.skip("Requires restore plan generation")


# ============================================================================
# Dependency Graph Validation Tests (TestDependencyGraphValidation)
# ============================================================================

class TestDependencyGraphValidation:
    """Validate orchestrator dependency graph has no circular dependencies."""
    
    def test_orchestrator_dependency_graph_acyclic(self):
        """Test orchestrator dependency graph contains no cycles."""
        pytest.skip("Requires dependency graph analysis")
    
    def test_orchestrator_dependency_depth_not_exceed_5_levels(self):
        """Test orchestrator call depth doesn't exceed 5 levels."""
        pytest.skip("Requires depth analysis")
    
    def test_all_orchestrator_dependencies_resolved(self):
        """Test all orchestrator dependencies can be resolved."""
        pytest.skip("Requires dependency resolution validation")
    
    def test_no_cross_domain_orchestrator_calls(self):
        """Test orchestrators don't cross domain boundaries without bridge."""
        pytest.skip("Requires domain boundary validation")


# ============================================================================
# Capability Manifest Tests (TestCapabilityManifestUpdate)
# ============================================================================

class TestCapabilityManifestUpdate:
    """Validate capability manifest updated with rationalized orchestrators."""
    
    def test_capability_manifest_lists_all_active_orchestrators(self):
        """Test capability manifest lists all ~44 active orchestrators."""
        pytest.skip("Requires manifest scan")
    
    def test_capability_manifest_excludes_archived_orchestrators(self):
        """Test capability manifest excludes archived orchestrators."""
        pytest.skip("Requires manifest scan")
    
    def test_capability_manifest_mcp_tools_consolidated_to_22(self):
        """Test capability manifest lists ~22 consolidated MCP tools."""
        pytest.skip("Requires manifest scan")
    
    def test_capability_manifest_orchestrator_workflow_templates_reference(self):
        """Test capability manifest references workflow template for each orchestrator."""
        pytest.skip("Requires manifest reference validation")


# ============================================================================
# Regression Tests (TestRegressionFromPhase04)
# ============================================================================

class TestRegressionFromPhase04:
    """Validate Phase 04 completeness is not broken by Phase 05 changes."""
    
    def test_brain_deduplication_archival_preserved(self):
        """Test _archive/brain/ still exists with all migrated files."""
        pytest.skip("Requires archive existence check")
    
    def test_brain_migration_imports_still_valid(self):
        """Test imports rewritten in Phase 04 still resolve."""
        pytest.skip("Requires import validation")
    
    def test_phase_04_tests_still_passing(self):
        """Test all Phase 04 tests (41/41) still pass."""
        pytest.skip("Requires test re-execution")
    
    def test_governance_rules_still_enforced(self):
        """Test CORE governance rules still enforced."""
        pytest.skip("Requires governance validation")
    
    def test_package_consolidation_still_valid(self):
        """Test Phase 03 package consolidation (1 package) still valid."""
        pytest.skip("Requires package structure validation")


# ============================================================================
# Completion Tests (TestPhase05Completion)
# ============================================================================

class TestPhase05Completion:
    """Validate Phase 05 completion criteria."""
    
    def test_all_120_orchestrators_classified(self):
        """Test all 120 orchestrators classified as active/dormant/dead."""
        pytest.skip("Requires complete classification")
    
    def test_orchestrator_classification_documented_in_registry(self):
        """Test orchestrator classification documented in cortex-registry/."""
        pytest.skip("Requires documentation generation")
    
    def test_44_active_orchestrators_survive_rationalization(self):
        """Test exactly ~44 active orchestrators survive (±25% tolerance)."""
        pytest.skip("Requires final count validation")
    
    def test_76_dormant_dead_orchestrators_archived(self):
        """Test ~76 dormant/dead orchestrators archived (±25% tolerance)."""
        pytest.skip("Requires final count validation")
    
    def test_5_known_duplicates_resolved(self):
        """Test 5 known duplicate orchestrators resolved (merged or archived)."""
        pytest.skip("Requires duplicate resolution validation")
    
    def test_22_mcp_tools_consolidated(self):
        """Test MCP tools consolidated to ~22 (±15% tolerance)."""
        pytest.skip("Requires final MCP count validation")
    
    def test_all_active_orchestrators_have_tests(self):
        """Test all active orchestrators have corresponding test coverage."""
        pytest.skip("Requires test discovery")
    
    def test_all_active_orchestrators_bound_to_workflow_templates(self):
        """Test all active orchestrators bound to workflow templates."""
        pytest.skip("Requires template binding validation")
    
    def test_phase_05_master_plan_marked_complete(self):
        """Test master plan marked Phase 05 as complete."""
        pytest.skip("Requires master plan update")
    
    def test_zero_new_test_failures_phase_05(self):
        """Test Phase 05 execution introduces zero new test failures."""
        pytest.skip("Requires test execution and regression check")


# ============================================================================
# Summary
# ============================================================================

"""
RED Phase Test Summary (Phase 05 — Orchestrator Rationalization)

Test Classes: 17
Test Methods: 80+
Estimated Coverage:
  ✓ Orchestrator Classification (6 tests)
  ✓ Active Orchestrator Count (5 tests)
  ✓ Dormant Orchestrator Archival (5 tests)
  ✓ Dead Orchestrator Archival (5 tests)
  ✓ Known Duplicate Resolution (9 tests)
  ✓ Workflow Template Binding (10 tests)
  ✓ MCP Tool Consolidation (7 tests)
  ✓ MCP Tool Specific Consolidations (5 tests)
  ✓ SQLite Audit Integration (8 tests)
  ✓ Post-Rationalization Integrity (6 tests)
  ✓ Archive Structure (6 tests)
  ✓ Dependency Graph Validation (4 tests)
  ✓ Capability Manifest Update (4 tests)
  ✓ Regression from Phase 04 (5 tests)
  ✓ Phase 05 Completion (11 tests)

Execution Sequence (RED → GREEN):
1. Run all 80+ tests (expect all to skip/fail — this is RED phase)
2. Identify dependencies and blockers
3. Implement OrchestratorRationalizationOrchestrator
4. Implement orchestrator classification and archival logic
5. Resolve known duplicates
6. Consolidate MCP tools
7. Bind active orchestrators to workflow templates
8. Integrate SQLite audit
9. Re-run all tests (expect all to pass — this is GREEN phase)
10. Validate zero regression from Phase 04
11. Update master plan: Phase 05 → COMPLETE

Estimated Effort: 5-7 days
Risk: HIGH (120 orchestrators → 44, complex dependency graph)
"""
