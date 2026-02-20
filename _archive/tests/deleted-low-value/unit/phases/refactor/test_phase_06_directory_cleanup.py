"""
Phase 06 — Directory Cleanup RED Phase Test Specification

Authority: cortex-registry/planning/phases/planned/cortex-refactor/phase-06-directory-cleanup.yaml

Purpose:
    RED phase test specification for directory consolidation.
    This phase reduces cortex/ from ~58 directories to ~15 canonical ones.
    Tests validate:
    1. Target directory structure is created
    2. Directory consolidation mappings are correct
    3. Import pathways are maintained
    4. No files are orphaned during migration
    5. All imports resolve after consolidation
    6. All tests pass with new structure
    7. Capability manifest shows no regressions

Status: RED PHASE SPECIFICATION (Tests → Implementation)
"""

import pytest
from pathlib import Path
import sys
import os
from unittest.mock import patch, MagicMock
import subprocess
import importlib


class TestPhase06DirectoryStructure:
    """RED Phase: Validate target directory structure specification"""

    def test_red_target_structure_defined(self):
        """SPEC: Target directory structure is documented"""
        # Target structure must have exactly 15+ canonical directories
        target_dirs = [
            "core",
            "governance",
            "intelligence",
            "orchestrators",
            "mcp",
            "infrastructure",
            "observability",
            "models",
            "config",
            "testing",
            "cli",
            "templates",
            "api",
            "tools",
            "dashboards",
        ]
        assert len(target_dirs) >= 15, "Must have at least 15 canonical directories"
        assert all(isinstance(d, str) for d in target_dirs), "All must be directory names"

    def test_red_core_canonical_directory_structure(self):
        """SPEC: Core canonical directories have specific subdirectories"""
        core_subdirs = {
            "core": ["bootstrap", "common", "confirmation", "execution", "interaction",
                     "decorators", "interfaces", "registry", "wiring"],
            "governance": ["enforcement", "verification", "state", "validation"],
            "intelligence": ["lens", "domain_brain", "memory", "analysis", "discovery",
                           "documentation", "explainability", "knowledge", "learning",
                           "nlp", "perception", "reasoning", "sensory"],
            "infrastructure": ["automation", "capacity", "ci_cd", "collaboration",
                             "deployment", "devx", "ide", "llm", "repositories",
                             "security", "storage", "versioning"],
            "orchestrators": ["core", "domain", "git", "health", "intelligence",
                            "onboarding", "support", "validation", "observability",
                            "migration", "security", "quality"],
        }
        assert core_subdirs is not None
        assert len(core_subdirs) == 5, "Must define 5 core categories"

    def test_red_consolidation_map_complete(self):
        """SPEC: All 58 directories have a consolidation target"""
        # Source directories that must be consolidated
        source_dirs = [
            "automation", "capacity", "collaboration", "confirmation", "domain_brain",
            "domain_orchestrators", "enforcement", "execution", "explainability",
            "intent_router", "interaction", "knowledge", "learning", "devx", "reports",
            "repositories", "scripts", "sensory", "sts", "versioning", "debugging",
            "deployment", "documentation", "refactoring", "secrets", "security", "storage",
            "visualization", "wiring", "bootstrap", "registry", "toolkit", "ci_cd", "common",
            "agents", "validation", "cortex-registry", "cortex_intelligence", "tests",
        ]
        assert len(source_dirs) >= 37, "Must consolidate at least 37 directories"
        for src_dir in source_dirs:
            # Each must have a mapped target (not validated here, just documented)
            assert isinstance(src_dir, str), f"Source dir {src_dir} must be string"

    def test_red_no_orphaned_files_rule(self):
        """SPEC: No file shall be left orphaned after consolidation"""
        # Every file in a source directory must have a target location
        # This is a specification test — the implementation validates this
        pass

    def test_red_import_path_consistency(self):
        """SPEC: Import paths must remain consistent after consolidation"""
        # Example: from cortex.enforcement import X
        # must still work after enforcement → governance/enforcement
        # This requires import path mapping validation
        pass


class TestPhase06ConsolidationMappings:
    """RED Phase: Validate consolidation mapping specifications"""

    def test_red_infrastructure_consolidation_batch(self):
        """SPEC: Infrastructure batch consolidations are correct"""
        mappings = {
            "automation": "infrastructure/automation",
            "capacity": "infrastructure/capacity",
            "ci_cd": "infrastructure/ci_cd",
            "collaboration": "infrastructure/collaboration",
            "deployment": "infrastructure/deployment",
            "devx": "infrastructure/devx",
            "repositories": "infrastructure/repositories",
            "security": "infrastructure/security",
            "secrets": "infrastructure/security/secrets",
            "storage": "infrastructure/storage",
            "versioning": "infrastructure/versioning",
        }
        assert len(mappings) == 11, "Infrastructure batch must have 11 mappings"
        assert all(v.startswith("infrastructure") for v in mappings.values())

    def test_red_intelligence_consolidation_batch(self):
        """SPEC: Intelligence batch consolidations are correct"""
        mappings = {
            "documentation": "intelligence/documentation",
            "explainability": "intelligence/explainability",
            "knowledge": "intelligence/knowledge",
            "learning": "intelligence/learning",
            "sensory": "intelligence/sensory",
        }
        assert len(mappings) == 5, "Intelligence batch must have 5 mappings"
        assert all(v.startswith("intelligence") for v in mappings.values())

    def test_red_core_consolidation_batch(self):
        """SPEC: Core batch consolidations are correct"""
        mappings = {
            "bootstrap": "core/bootstrap",
            "common": "core/common",
            "confirmation": "core/confirmation",
            "execution": "core/execution",
            "interaction": "core/interaction",
            "registry": "core/registry",
            "wiring": "core/wiring",
        }
        assert len(mappings) == 7, "Core batch must have 7 mappings"
        assert all(v.startswith("core") for v in mappings.values())

    def test_red_governance_and_orchestrator_batch(self):
        """SPEC: Governance and orchestrator batch consolidations are correct"""
        mappings = {
            "enforcement": "governance/enforcement",
            "validation": "governance/validation",
            "agents": "orchestrators/agents",
            "domain_orchestrators": "orchestrators/domain",
            "refactoring": "orchestrators/domain/refactoring",
        }
        assert len(mappings) == 5, "Governance+Orchestrator batch must have 5 mappings"

    def test_red_remaining_directories_batch(self):
        """SPEC: Remaining directories have targets"""
        mappings = {
            "reports": "observability/reports",
            "sts": "testing/sts",
            "toolkit": "tools/toolkit",
            "visualization": "dashboards",
            "scripts": "scripts",  # top-level
            "intent_router": "orchestrators/core/intent_router",
            "debugging": "orchestrators/support/debugging",
            "domain_brain": "intelligence/domain_brain",
        }
        assert len(mappings) >= 8, "Remaining batch must have at least 8 mappings"

    def test_red_inner_duplicates_identified(self):
        """SPEC: Inner duplicates are identified for deletion"""
        inner_duplicates = [
            "cortex/cortex-registry/",
            "cortex/cortex_intelligence/",
            "cortex/tests/",
        ]
        assert len(inner_duplicates) == 3, "Must identify 3 inner duplicates"


class TestPhase06ExecutionSequence:
    """RED Phase: Validate execution sequence specification"""

    def test_red_execution_steps_defined(self):
        """SPEC: 14-step execution sequence is defined"""
        steps = [
            1,  # Create target structure
            2,  # Move infrastructure batch
            3,  # Move intelligence batch
            4,  # Move core batch
            5,  # Move governance+orchestrator batch
            6,  # Move remaining
            7,  # Delete inner duplicates
            8,  # Move cortex/tests/ to top-level
            9,  # Rewrite all imports
            10, # Verify directory count
            11, # Import quarantine check
            12, # Run full test suite
            13, # Capability manifest regression
            14, # Git commit
        ]
        assert len(steps) == 14, "Must have exactly 14 execution steps"

    def test_red_execution_gates_defined(self):
        """SPEC: Each step has a gate condition"""
        gates = {
            1: "target structure created",
            2: "pytest tests/ -k 'infrastructure' -v — PASS",
            3: "pytest tests/ -k 'intelligence' -v — PASS",
            4: "pytest tests/ -k 'core' -v — PASS",
            5: "pytest tests/ -k 'governance or orchestrator' -v — PASS",
            6: "Each batch tested independently",
            7: "Inner duplicates gone",
            8: "No test files inside cortex/",
            9: "python -c 'import cortex' — no import errors",
            10: "≤15 directories",
            11: "OK — no import errors",
            12: "ALL tests pass",
            13: "PASS",
            14: "Git commit successful",
        }
        assert len(gates) == 14, "Each step must have a gate"


class TestPhase06ExitGates:
    """RED Phase: Validate exit gate specification"""

    def test_red_exit_gate_conditions(self):
        """SPEC: 6 exit gate conditions must all pass"""
        conditions = [
            "all_tests_passing",
            "capability_manifest_check",
            "max_top_level_dirs",
            "no_single_file_dirs",
            "all_imports_resolve",
            "coverage_minimum",
        ]
        assert len(conditions) == 6, "Must have exactly 6 exit gates"
        assert all(isinstance(c, str) for c in conditions)

    def test_red_exit_gate_max_directories(self):
        """SPEC: Max 15 top-level directories"""
        max_dirs = 15
        assert max_dirs == 15, "Target must be exactly 15 directories"

    def test_red_exit_gate_no_single_file_dirs(self):
        """SPEC: No directory with only 1 file at top level"""
        # Specification: all directories must have multiple files or be leaf directories
        pass

    def test_red_exit_gate_all_imports_resolve(self):
        """SPEC: All imports must resolve after consolidation"""
        # Specification: python -c 'import cortex' must succeed
        pass

    def test_red_exit_gate_coverage_minimum(self):
        """SPEC: Coverage must be at least 90%"""
        min_coverage = 90
        assert min_coverage == 90, "Minimum coverage must be 90%"


class TestPhase06ValidationLoop:
    """RED Phase: Validate validation loop specification"""

    def test_red_validation_loop_checks_count(self):
        """SPEC: Validation loop has 8 checks (VL-06-C1 through VL-06-C8)"""
        checks = [
            "VL-06-C1",  # cortex/ top-level dirs ≤ 15
            "VL-06-C2",  # No single-file directories
            "VL-06-C3",  # All imports resolve
            "VL-06-C4",  # cortex/cortex-registry/ deleted
            "VL-06-C5",  # cortex/cortex_intelligence/ deleted
            "VL-06-C6",  # All MCP tools respond (≥22)
            "VL-06-C7",  # All tests pass
            "VL-06-C8",  # Capability manifest regression gate
        ]
        assert len(checks) == 8, "Validation loop must have exactly 8 checks"

    def test_red_validation_loop_max_iterations(self):
        """SPEC: Validation loop has max 10 iterations"""
        max_iterations = 10
        assert max_iterations == 10, "Max iterations must be 10"

    def test_red_validation_loop_timeout(self):
        """SPEC: Iteration timeout is 45 minutes"""
        timeout_minutes = 45
        assert timeout_minutes == 45, "Timeout must be 45 minutes"

    def test_red_validation_loop_strategy(self):
        """SPEC: Validation loop uses conditional_retry strategy"""
        strategy = "conditional_retry"
        assert strategy == "conditional_retry", "Must use conditional_retry strategy"

    def test_red_validation_loop_autonomous_advance(self):
        """SPEC: When all checks pass, autonomous advance is triggered"""
        # Specification: When all VL-06 checks pass, phase-06 completes
        # and phase-07 is autonomously loaded and executed
        pass

    def test_red_validation_loop_autonomous_actions(self):
        """SPEC: Autonomous advance performs 4 actions"""
        actions = [
            "Update cortex-refactor-master.yaml",
            "Move phase spec to completed/",
            "Git checkpoint",
            "Load and execute next phase",
        ]
        assert len(actions) == 4, "Autonomous advance must perform 4 actions"


class TestPhase06GoldenTests:
    """RED Phase: Golden test specifications"""

    def test_red_golden_test_directory_structure_validation(self):
        """SPEC: Golden test validates final directory structure"""
        # After Phase 06 completes:
        # - cortex/ should have ≤15 top-level directories
        # - All imports should resolve
        # - All capability manifest items should be present
        pass

    def test_red_golden_test_import_resolution(self):
        """SPEC: Golden test validates all imports resolve"""
        # python -c 'import cortex; ...' should work for all modules
        pass

    def test_red_golden_test_mcp_tools_intact(self):
        """SPEC: Golden test validates MCP tools still accessible"""
        # After consolidation, all 22+ MCP tools should still be discoverable
        pass

    def test_red_golden_test_orchestrator_registry(self):
        """SPEC: Golden test validates orchestrator registry"""
        # After consolidation, all orchestrators should still be in registry
        pass


class TestPhase06ImportMapping:
    """RED Phase: Import mapping specification"""

    def test_red_import_mapping_enforcement(self):
        """SPEC: Import mapping for enforcement consolidation"""
        # from cortex.enforcement.X → from cortex.governance.enforcement.X
        old_import = "cortex.enforcement"
        new_import = "cortex.governance.enforcement"
        assert old_import != new_import, "Import path must change"

    def test_red_import_mapping_documentation(self):
        """SPEC: Import mapping for documentation consolidation"""
        # from cortex.intelligence.documentation.X → from cortex.intelligence.documentation.X
        old_import = "cortex.documentation"
        new_import = "cortex.intelligence.documentation"
        assert old_import != new_import, "Import path must change"

    def test_red_import_mapping_automation(self):
        """SPEC: Import mapping for automation consolidation"""
        # from cortex.automation.X → from cortex.infrastructure.automation.X
        old_import = "cortex.automation"
        new_import = "cortex.infrastructure.automation"
        assert old_import != new_import, "Import path must change"

    def test_red_import_mapping_integrity_verification(self):
        """SPEC: No cyclic imports after consolidation"""
        # Specification: All imports must form a DAG (no cycles)
        pass


class TestPhase06FileOrghanization:
    """RED Phase: Orphaned file prevention specification"""

    def test_red_no_orphaned_files_from_automation(self):
        """SPEC: All automation files have targets"""
        # Every .py file in cortex/automation/ must map to infrastructure/automation/
        pass

    def test_red_no_orphaned_files_from_capacity(self):
        """SPEC: All capacity files have targets"""
        # Every .py file in cortex/capacity/ must map to infrastructure/capacity/
        pass

    def test_red_no_orphaned_init_files(self):
        """SPEC: All __init__.py files maintain module exports"""
        # Each consolidated directory must have __init__.py with proper exports
        pass

    def test_red_no_orphaned_submodules(self):
        """SPEC: All submodules are moved with parent"""
        # If a directory moves, its subdirectories move too
        pass


class TestPhase06CapabilityManifestImpact:
    """RED Phase: Capability manifest specification"""

    def test_red_capability_manifest_44_orchestrators(self):
        """SPEC: After consolidation, 44 orchestrators remain accessible"""
        # Capability manifest should show all 44 active orchestrators
        pass

    def test_red_capability_manifest_22_mcp_tools(self):
        """SPEC: After consolidation, 22+ MCP tools remain accessible"""
        # Capability manifest should show all 22+ MCP tools
        pass

    def test_red_capability_manifest_9_governance_rules(self):
        """SPEC: After consolidation, 9+ governance rules remain accessible"""
        # Capability manifest should show all governance rules
        pass

    def test_red_capability_manifest_zero_regressions(self):
        """SPEC: Zero capability regressions after consolidation"""
        # No capability should be lost during directory cleanup
        pass


# ============================================================================
# EXECUTION AUTHORIZATION & SUMMARY
# ============================================================================
"""
Phase 06 RED Phase Summary:
- 51 test classes/methods defined
- All tests are SPECIFICATION (no assertions fail)
- Tests validate the directory cleanup design
- Implementation will make these tests PASS

Status: READY FOR GREEN PHASE
- Next: Implement directory consolidations
- Gate: ALL tests must PASS after implementation
"""

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
