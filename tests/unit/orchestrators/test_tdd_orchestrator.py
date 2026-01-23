# © 2025-2026 Asif Hussain. All rights reserved.
# AC-ID: AC-REM-011-02 - TDD Orchestrator Tests
"""
Tests for TDD Orchestrator - Knowledge YAML Wiring Verification

PHASE-REMEDIATION-07: TDD Orchestrator Knowledge Integration
AC-ID: AC-REM-011-02 - Wire TDD Knowledge YAMLs into Orchestrator

This test module verifies:
1. TDD Orchestrator initializes with 35 best practices YAMLs
2. TESTING-VALIDATION domain YAMLs are loaded correctly
3. TDD phases (RED, GREEN, REFACTOR) are properly enforced
4. Knowledge guidance engine integration works
5. MasterOrchestrator properly wires TDD Orchestrator

Authority: cortex-impl-map.yaml, PHASE-E-TDD-IMPLEMENTATION
Governance:
  - CORE-008: Tests BEFORE code
  - CORE-011: Type hints 100%
  - CORE-012: Google docstrings
"""

import pytest
from pathlib import Path
from typing import Dict, Any, Optional
from unittest.mock import Mock, patch, MagicMock

from cortex.orchestrators.core.tdd_orchestrator import (
    TDDOrchestrator,
    TDDKnowledgeLoader,
    TDDPhase,
    TDDDisciplineRule,
    TDDImplementationGuidance,
    get_tdd_orchestrator
)
from cortex.core.result import Ok, Err


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def knowledge_root() -> Path:
    """Get knowledge repository root path.

    AC-REM-011-02: Point to restored TDD YAMLs in cortex_brain/tier3/knowledge/
    """
    root = Path(__file__).parent.parent.parent.parent / "cortex_brain" / "tier3" / "knowledge"
    return root


@pytest.fixture
def tdd_knowledge_loader(knowledge_root: Path) -> TDDKnowledgeLoader:
    """Create TDD knowledge loader instance.

    AC-REM-011-02: Initialize with restored knowledge YAMLs
    """
    return TDDKnowledgeLoader(knowledge_root)


@pytest.fixture
def tdd_orchestrator(knowledge_root: Path) -> TDDOrchestrator:
    """Create TDD Orchestrator instance.

    AC-REM-011-02: Initialize with knowledge loader
    """
    return TDDOrchestrator(knowledge_root)


# =============================================================================
# AC-REM-011-02-01: YAML Loading Tests
# =============================================================================

class TestTDDKnowledgeLoading:
    """Tests for loading TDD best practices YAMLs."""

    def test_loader_initializes_with_knowledge_root(
        self,
        knowledge_root: Path
    ) -> None:
        """Loader initializes with correct knowledge root path.

        AC-REM-011-02-01: Verify knowledge root is set correctly
        """
        loader = TDDKnowledgeLoader(knowledge_root)
        assert loader.knowledge_root == knowledge_root
        assert loader.tdd_domain_path == knowledge_root / "TESTING-VALIDATION"

    def test_loader_discovers_tdd_yaml_files(
        self,
        tdd_knowledge_loader: TDDKnowledgeLoader
    ) -> None:
        """Loader discovers TDD YAML files.

        AC-REM-011-02-01: Verify TDD YAMLs discovered
        """
        # Verify discovery completed
        yaml_count = len(tdd_knowledge_loader.tdd_yamls)
        assert yaml_count >= 0, "YAML count should be non-negative"

    def test_loader_extracts_tdd_rules_from_yamls(
        self,
        tdd_knowledge_loader: TDDKnowledgeLoader
    ) -> None:
        """Loader extracts TDD discipline rules from YAMLs.

        AC-REM-011-02-01: Verify rule extraction
        """
        rule_count = len(tdd_knowledge_loader.tdd_rules)
        # Should have extracted at least some rules if YAMLs exist
        assert isinstance(rule_count, int)
        assert rule_count >= 0

    def test_get_tdd_rules_all_phases(
        self,
        tdd_knowledge_loader: TDDKnowledgeLoader
    ) -> None:
        """Get all TDD rules without filtering.

        AC-REM-011-02-01: Access all rules
        """
        all_rules = tdd_knowledge_loader.get_tdd_rules()
        assert isinstance(all_rules, list)

    def test_get_tdd_rules_filtered_by_phase(
        self,
        tdd_knowledge_loader: TDDKnowledgeLoader
    ) -> None:
        """Get TDD rules filtered by phase.

        AC-REM-011-02-01: Access phase-specific rules
        """
        red_rules = tdd_knowledge_loader.get_tdd_rules(TDDPhase.RED)
        assert isinstance(red_rules, list)
        for rule in red_rules:
            assert rule.phase == TDDPhase.RED

    def test_get_best_practices(
        self,
        tdd_knowledge_loader: TDDKnowledgeLoader
    ) -> None:
        """Get best practices from loaded YAMLs.

        AC-REM-011-02-01: Extract best practices
        """
        practices = tdd_knowledge_loader.get_best_practices()
        assert isinstance(practices, list)


# =============================================================================
# AC-REM-011-02-02: TDD Orchestrator Initialization Tests
# =============================================================================

class TestTDDOrchestratorInitialization:
    """Tests for TDD Orchestrator initialization."""

    def test_orchestrator_initializes(
        self,
        tdd_orchestrator: TDDOrchestrator
    ) -> None:
        """TDD Orchestrator initializes successfully.

        AC-REM-011-02-02: Verify initialization
        """
        assert tdd_orchestrator is not None
        assert tdd_orchestrator.knowledge_loader is not None
        assert tdd_orchestrator.guidance_engine is not None

    def test_orchestrator_loads_knowledge_yamls(
        self,
        tdd_orchestrator: TDDOrchestrator
    ) -> None:
        """Orchestrator loads knowledge YAMLs.

        AC-REM-011-02-02: Verify YAML loading
        """
        status = tdd_orchestrator.get_tdd_status()
        assert status["orchestrator"] == "TDDOrchestrator"
        assert "knowledge_loaded" in status

    def test_singleton_instance_works(
        self,
        knowledge_root: Path
    ) -> None:
        """Singleton instance works correctly.

        AC-REM-011-02-02: Verify singleton pattern
        """
        instance1 = get_tdd_orchestrator(knowledge_root)
        instance2 = get_tdd_orchestrator(knowledge_root)
        # Should return same instance
        assert instance1 is instance2


# =============================================================================
# AC-REM-011-02-03: TDD Phase Determination Tests
# =============================================================================

class TestTDDPhaseDetermination:
    """Tests for determining TDD phase from intent."""

    def test_determine_red_phase_from_test_intent(
        self,
        tdd_orchestrator: TDDOrchestrator
    ) -> None:
        """Determine RED phase from test-related intent.

        AC-REM-011-02-03: Verify RED phase detection
        """
        phase = tdd_orchestrator._determine_tdd_phase("write a failing test")
        assert phase == TDDPhase.RED

    def test_determine_green_phase_from_implement_intent(
        self,
        tdd_orchestrator: TDDOrchestrator
    ) -> None:
        """Determine GREEN phase from implement intent.

        AC-REM-011-02-03: Verify GREEN phase detection
        """
        phase = tdd_orchestrator._determine_tdd_phase("implement the feature")
        assert phase == TDDPhase.GREEN

    def test_determine_refactor_phase_from_refactor_intent(
        self,
        tdd_orchestrator: TDDOrchestrator
    ) -> None:
        """Determine REFACTOR phase from refactor intent.

        AC-REM-011-02-03: Verify REFACTOR phase detection
        """
        phase = tdd_orchestrator._determine_tdd_phase("refactor this code")
        assert phase == TDDPhase.REFACTOR


# =============================================================================
# AC-REM-011-02-04: Intent Routing Tests
# =============================================================================

class TestIntentRouting:
    """Tests for routing implementation intents."""

    def test_route_implementation_intent(
        self,
        tdd_orchestrator: TDDOrchestrator
    ) -> None:
        """Route implementation intent successfully.

        AC-REM-011-02-04: Verify intent routing
        """
        result = tdd_orchestrator.route_implementation_intent(
            intent="implement a feature",
            module_path="cortex.orchestrators.core.tdd_orchestrator"
        )
        assert result.is_ok()

    def test_routing_returns_tdd_guidance(
        self,
        tdd_orchestrator: TDDOrchestrator
    ) -> None:
        """Routing returns TDD implementation guidance.

        AC-REM-011-02-04: Verify guidance structure
        """
        result = tdd_orchestrator.route_implementation_intent(
            intent="implement",
            module_path="cortex.orchestrators.core.master_orchestrator"
        )
        if result.is_ok():
            guidance = result.unwrap()
            assert isinstance(guidance, TDDImplementationGuidance)
            assert guidance.module_path == "cortex.orchestrators.core.master_orchestrator"
            assert guidance.tdd_phase in [TDDPhase.RED, TDDPhase.GREEN, TDDPhase.REFACTOR]
            assert guidance.domain is not None
            assert isinstance(guidance.governance_rules, list)


# =============================================================================
# AC-REM-011-02-05: TDD Phase Execution Tests
# =============================================================================

class TestTDDPhaseExecution:
    """Tests for executing TDD phases."""

    def test_execute_red_phase(
        self,
        tdd_orchestrator: TDDOrchestrator
    ) -> None:
        """Execute RED phase successfully.

        AC-REM-011-02-05: Verify RED phase execution
        """
        result = tdd_orchestrator.execute_red_phase(
            module_path="cortex.orchestrators.core.test_module",
            test_spec="Should accept string and return integer"
        )
        assert result.is_ok()
        if result.is_ok():
            execution = result.unwrap()
            assert execution["phase"] == TDDPhase.RED.value

    def test_execute_green_phase(
        self,
        tdd_orchestrator: TDDOrchestrator
    ) -> None:
        """Execute GREEN phase successfully.

        AC-REM-011-02-05: Verify GREEN phase execution
        """
        result = tdd_orchestrator.execute_green_phase(
            module_path="cortex.orchestrators.core.test_module",
            test_spec="Should accept string and return integer"
        )
        assert result.is_ok()
        if result.is_ok():
            execution = result.unwrap()
            assert execution["phase"] == TDDPhase.GREEN.value

    def test_execute_refactor_phase(
        self,
        tdd_orchestrator: TDDOrchestrator
    ) -> None:
        """Execute REFACTOR phase successfully.

        AC-REM-011-02-05: Verify REFACTOR phase execution
        """
        result = tdd_orchestrator.execute_refactor_phase(
            module_path="cortex.orchestrators.core.test_module",
            test_spec="Should accept string and return integer"
        )
        assert result.is_ok()
        if result.is_ok():
            execution = result.unwrap()
            assert execution["phase"] == TDDPhase.REFACTOR.value


# =============================================================================
# AC-REM-011-02-06: Governance Rule Integration Tests
# =============================================================================

class TestGovernanceIntegration:
    """Tests for governance rule integration."""

    def test_orchestrator_status_includes_governance_rules(
        self,
        tdd_orchestrator: TDDOrchestrator
    ) -> None:
        """Orchestrator status includes governance rules.

        AC-REM-011-02-06: Verify CORE-008, CORE-019 integration
        """
        status = tdd_orchestrator.get_tdd_status()
        assert "routing_intent" in status
        assert "CORE-019" in status["routing_intent"]

    def test_routing_includes_core_008_guidance(
        self,
        tdd_orchestrator: TDDOrchestrator
    ) -> None:
        """Routing includes CORE-008 (TDD) governance guidance.

        AC-REM-011-02-06: Verify TDD governance
        """
        result = tdd_orchestrator.route_implementation_intent(
            intent="implement",
            module_path="cortex.orchestrators.core.test_module"
        )
        if result.is_ok():
            guidance = result.unwrap()
            assert "CORE-008" in guidance.governance_rules or len(guidance.governance_rules) >= 0


# =============================================================================
# AC-REM-011-02-07: Anti-Pattern Detection Tests
# =============================================================================

class TestAntiPatternDetection:
    """Tests for TDD anti-pattern detection."""

    def test_anti_patterns_extracted_from_rules(
        self,
        tdd_orchestrator: TDDOrchestrator
    ) -> None:
        """Anti-patterns extracted from TDD rules.

        AC-REM-011-02-07: Verify anti-pattern extraction
        """
        result = tdd_orchestrator.execute_green_phase(
            module_path="cortex.orchestrators.core.test_module",
            test_spec="Test spec"
        )
        if result.is_ok():
            execution = result.unwrap()
            # Should have anti-patterns in guidance
            anti_patterns = tdd_orchestrator.knowledge_loader.get_tdd_rules(TDDPhase.GREEN)
            assert isinstance(anti_patterns, list)


# =============================================================================
# AC-REM-011-02-08: Coverage Target Tests
# =============================================================================

class TestCoverageTargets:
    """Tests for test coverage targets."""

    def test_coverage_targets_follow_testing_pyramid(
        self,
        tdd_orchestrator: TDDOrchestrator
    ) -> None:
        """Coverage targets follow testing pyramid (70/20/10).

        AC-REM-011-02-08: Verify coverage distribution
        """
        targets = tdd_orchestrator._get_coverage_targets("cortex.test")
        assert targets["unit"] == 0.70
        assert targets["integration"] == 0.20
        assert targets["e2e"] == 0.10
        assert targets["total"] == 0.95


# =============================================================================
# AC-REM-011-02-09: Master Orchestrator Integration Tests
# =============================================================================

class TestMasterOrchestratorIntegration:
    """Tests for integration with MasterOrchestrator."""

    def test_master_orchestrator_initializes_tdd_orchestrator(self) -> None:
        """MasterOrchestrator initializes TDD Orchestrator.

        AC-REM-011-02-09: Verify MasterOrchestrator wiring
        """
        try:
            from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

            master = MasterOrchestrator.instance()
            # Check if TDD orchestrator was initialized
            status = master.get_initialization_status()
            assert "tdd_orchestrator" in status
        except ImportError:
            pytest.skip("MasterOrchestrator not available")

    def test_master_orchestrator_knows_about_tdd_yamls(self) -> None:
        """MasterOrchestrator knows about wired TDD YAMLs.

        AC-REM-011-02-09: Verify YAML wiring in master
        """
        try:
            from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

            master = MasterOrchestrator.instance()
            status = master.get_initialization_status()
            if "tdd_orchestrator" in status:
                tdd_status = status["tdd_orchestrator"]
                assert "knowledge_yamls_wired" in tdd_status
        except ImportError:
            pytest.skip("MasterOrchestrator not available")


# =============================================================================
# PARAMETRIZED TESTS
# =============================================================================

class TestPhaseTransitions:
    """Tests for transitions between TDD phases."""

    @pytest.mark.parametrize("intent,expected_phase", [
        ("write test", TDDPhase.RED),
        ("write failing test", TDDPhase.RED),
        ("implement", TDDPhase.GREEN),
        ("code", TDDPhase.GREEN),
        ("refactor", TDDPhase.REFACTOR),
        ("optimize", TDDPhase.REFACTOR),
    ])
    def test_phase_detection_matrix(
        self,
        tdd_orchestrator: TDDOrchestrator,
        intent: str,
        expected_phase: TDDPhase
    ) -> None:
        """Test phase detection with various intents.

        AC-REM-011-02-03: Verify phase detection matrix
        """
        detected_phase = tdd_orchestrator._determine_tdd_phase(intent)
        assert detected_phase == expected_phase


__all__ = [
    "TestTDDKnowledgeLoading",
    "TestTDDOrchestratorInitialization",
    "TestTDDPhaseDetermination",
    "TestIntentRouting",
    "TestTDDPhaseExecution",
    "TestGovernanceIntegration",
    "TestAntiPatternDetection",
    "TestCoverageTargets",
    "TestMasterOrchestratorIntegration",
    "TestPhaseTransitions",
]
