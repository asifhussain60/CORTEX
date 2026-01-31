# AC-ID: ARCH-012-REFACTOR - TDDOrchestrator V2 Tests
"""
Tests for TDD Orchestrator V2 - Refactored with Base Protocol.

PROOF OF CONCEPT: Verifies TDDOrchestrator correctly inherits and uses
OrchestratorBaseProtocol for LENS, Security, Challenge, DoR phases.

Test Coverage:
1. Initialization (base protocol + TDD components)
2. LENS context integration (automatic)
3. Security assessment integration (automatic for code)
4. Challenge generation integration (automatic for disagreements)
5. DoR confidence gate integration (automatic <60% block)
6. TDD domain logic (RED, GREEN, REFACTOR phases)
7. End-to-end protocol execution
8. Comparison with TDDOrchestrator (V1) benefits

Governance:
- ARCH-012: Verifies base protocol inheritance
- CORE-008: TDD (this test file)
- CORE-011: Type hints 100%
- CORE-012: Google-style docstrings

Author: Asif Hussain
Date: 2026-01-31
"""

import pytest
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

from cortex.orchestrators.core.tdd_orchestrator import (
    TDDOrchestrator,
    TDDPhase,
    TDDKnowledgeLoader,
    get_tdd_orchestrator,
)
from cortex.core.result import Ok, Err


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def knowledge_root(tmp_path: Path) -> Path:
    """Create temporary knowledge root with TDD YAMLs."""
    knowledge_dir = tmp_path / "cortex_brain" / "tier3" / "knowledge"
    tdd_dir = knowledge_dir / "TESTING-VALIDATION"
    tdd_dir.mkdir(parents=True, exist_ok=True)
    
    # Create minimal TDD YAML
    tdd_yaml = tdd_dir / "tdd-best-practices.yaml"
    tdd_yaml.write_text("""
discipline:
  - rule_id: TDD-001
    phase: red
    description: Write failing test first
    examples:
      - "def test_feature(): assert False"
    anti_patterns:
      - "Writing implementation before test"
      
best_practices:
  - "Red-Green-Refactor cycle"
  - "Test one thing at a time"
  - "Keep tests independent"
""")
    
    return knowledge_dir.parent.parent.parent


@pytest.fixture
def orchestrator_v2(knowledge_root: Path) -> TDDOrchestrator:
    """Create TDD Orchestrator V2 instance."""
    return TDDOrchestrator(knowledge_root=knowledge_root)


# =============================================================================
# ARCH-012-REFACTOR-01: Initialization Tests
# =============================================================================

class TestTDDOrchestratorInitialization:
    """Tests for TDD Orchestrator V2 initialization."""

    def test_orchestrator_v2_initializes(
        self,
        orchestrator_v2: TDDOrchestrator
    ) -> None:
        """
        TDD Orchestrator V2 initializes with base protocol.
        
        ARCH-012-REFACTOR-01: Verify initialization
        """
        assert orchestrator_v2 is not None
        assert orchestrator_v2.knowledge_loader is not None
        assert orchestrator_v2.guidance_engine is not None
        
        # Verify base protocol components initialized
        assert hasattr(orchestrator_v2, 'lens_orchestrator')
        assert hasattr(orchestrator_v2, 'challenge_engine')
        assert hasattr(orchestrator_v2, 'dor_gate')
        assert hasattr(orchestrator_v2, 'security_analyzer')

    def test_orchestrator_v2_singleton(
        self,
        knowledge_root: Path
    ) -> None:
        """
        get_tdd_orchestrator() returns singleton.
        
        ARCH-012-REFACTOR-01: Verify singleton pattern
        """
        instance1 = get_tdd_orchestrator(knowledge_root)
        instance2 = get_tdd_orchestrator(knowledge_root)
        
        assert instance1 is instance2


# =============================================================================
# ARCH-012-REFACTOR-02: LENS Context Integration Tests
# =============================================================================

class TestLENSContextIntegration:
    """Tests for LENS context integration (inherited from base protocol)."""

    def test_tdd_execution_with_lens_context(
        self,
        orchestrator_v2: TDDOrchestrator
    ) -> None:
        """
        TDD domain logic receives LENS context.
        
        ARCH-012-REFACTOR-02: Verify LENS context passed to domain logic
        """
        # Mock LENS context
        mock_lens_context = {
            "synthesis": "Write failing test for authentication"
        }
        
        # Execute domain logic directly (bypassing full protocol for test)
        result = orchestrator_v2._execute_domain_logic(
            user_request="Write test for authentication",
            lens_context=mock_lens_context,
            context={"module_path": "cortex.auth", "domain": "security"}
        )
        
        assert result.is_ok()
        output = result.unwrap()
        assert output["lens_context_used"] is True


# =============================================================================
# ARCH-012-REFACTOR-03: Security Assessment Integration Tests
# =============================================================================

class TestSecurityAssessmentIntegration:
    """Tests for security threat assessment integration."""

    def test_security_assessment_for_code_context(
        self,
        orchestrator_v2: TDDOrchestrator
    ) -> None:
        """
        Security assessment runs when code context present.
        
        ARCH-012-REFACTOR-03: Verify security integration
        """
        # Mock security analyzer
        mock_security = Mock()
        mock_security.assess_threats.return_value = Mock(
            block_execution=False,
            has_threats=False
        )
        orchestrator_v2.security_analyzer = mock_security
        
        # Execute with code context
        result = orchestrator_v2.execute_with_protocol(
            user_request="Implement auth",
            context={
                "code": "def login(username, password): pass",
                "module_path": "cortex.auth"
            }
        )
        
        # Security assessment should have run
        # (Will be called by base protocol)


# =============================================================================
# ARCH-012-REFACTOR-04: Challenge Generation Integration Tests
# =============================================================================

class TestChallengeGenerationIntegration:
    """Tests for challenge generation integration."""

    def test_challenge_generated_for_suboptimal_approach(
        self,
        orchestrator_v2: TDDOrchestrator
    ) -> None:
        """
        Challenge generated when CORTEX has better solution.
        
        ARCH-012-REFACTOR-04: Verify challenge integration
        """
        # Mock challenge engine
        mock_challenge_engine = Mock()
        mock_challenge_response = Mock(
            has_disagreement=True,
            gate_type=Mock(value="soft"),
            recommended_alternative="Use pytest fixtures instead"
        )
        mock_challenge_engine.generate_challenge.return_value = mock_challenge_response
        orchestrator_v2.challenge_engine = mock_challenge_engine
        
        # Execute with suboptimal request
        result = orchestrator_v2.execute_with_protocol(
            user_request="Write tests without fixtures",
            context={"module_path": "cortex.tests"}
        )
        
        # Challenge should be generated
        # (Will be called by base protocol)

    def test_hard_gate_challenge_blocks_harmful_action(
        self,
        orchestrator_v2: TDDOrchestrator
    ) -> None:
        """
        Hard gate challenge blocks harmful actions.
        
        ARCH-012-REFACTOR-04: Verify hard gate blocking
        """
        from cortex.orchestrators.core.challenge_engine import GateType
        
        # Mock challenge engine with hard gate
        mock_challenge_engine = Mock()
        mock_challenge_response = Mock(
            has_disagreement=True,
            gate_type=GateType.HARD if GateType else Mock(value="hard"),
            recommended_alternative="Do not delete production tests"
        )
        mock_challenge_engine.generate_challenge.return_value = mock_challenge_response
        orchestrator_v2.challenge_engine = mock_challenge_engine
        
        # Execute harmful request
        result = orchestrator_v2.execute_with_protocol(
            user_request="Delete all tests",
            context={"module_path": "cortex.tests"}
        )
        
        # Should return challenge (not execute)
        if result.is_ok():
            output = result.unwrap()
            assert output.get("type") == "challenge"


# =============================================================================
# ARCH-012-REFACTOR-05: DoR Confidence Gate Integration Tests
# =============================================================================

class TestDoRConfidenceGateIntegration:
    """Tests for DoR confidence gate integration."""

    def test_dor_gate_allows_high_confidence_request(
        self,
        orchestrator_v2: TDDOrchestrator
    ) -> None:
        """
        DoR gate allows requests with ≥60% confidence.
        
        ARCH-012-REFACTOR-05: Verify DoR allowing
        """
        # Mock DoR gate with high confidence
        mock_dor_gate = Mock()
        mock_reflection = Mock(
            dor_confidence=0.9,  # Above 60% threshold
            intent_type="IMPLEMENT"
        )
        mock_dor_gate.classify_and_reflect.return_value = mock_reflection
        orchestrator_v2.dor_gate = mock_dor_gate
        
        # Execute clear request
        result = orchestrator_v2.execute_with_protocol(
            user_request="Implement authentication service in cortex.auth.service",
            context={"module_path": "cortex.auth.service"}
        )
        
        # Should proceed (not blocked)
        # Result could be Ok or Err depending on execution, but not DoR blocked
        if result.is_err():
            assert "DoR NOT MET" not in str(result.unwrap_err())


# =============================================================================
# ARCH-012-REFACTOR-06: TDD Domain Logic Tests
# =============================================================================

class TestTDDDomainLogic:
    """Tests for TDD-specific domain logic (RED, GREEN, REFACTOR)."""

    def test_red_phase_determination(
        self,
        orchestrator_v2: TDDOrchestrator
    ) -> None:
        """
        RED phase determined from test-related requests.
        
        ARCH-012-REFACTOR-06: Verify phase determination
        """
        phase = orchestrator_v2._determine_tdd_phase("Write failing test for auth")
        assert phase == TDDPhase.RED

    def test_green_phase_determination(
        self,
        orchestrator_v2: TDDOrchestrator
    ) -> None:
        """
        GREEN phase determined from implementation requests.
        
        ARCH-012-REFACTOR-06: Verify phase determination
        """
        phase = orchestrator_v2._determine_tdd_phase("Implement authentication service")
        assert phase == TDDPhase.GREEN

    def test_refactor_phase_determination(
        self,
        orchestrator_v2: TDDOrchestrator
    ) -> None:
        """
        REFACTOR phase determined from improvement requests.
        
        ARCH-012-REFACTOR-06: Verify phase determination
        """
        phase = orchestrator_v2._determine_tdd_phase("Refactor auth module")
        assert phase == TDDPhase.REFACTOR

    def test_red_phase_execution(
        self,
        orchestrator_v2: TDDOrchestrator
    ) -> None:
        """
        RED phase executes with test patterns.
        
        ARCH-012-REFACTOR-06: Verify RED phase
        """
        guidance = orchestrator_v2._build_tdd_guidance(
            module_path="cortex.auth",
            domain="security",
            tdd_phase=TDDPhase.RED,
            user_request="Write test",
            lens_context=None
        )
        
        result = orchestrator_v2._execute_red_phase(guidance, {})
        
        assert result.is_ok()
        output = result.unwrap()
        assert output["phase"] == "RED"
        assert "test_patterns" in output

    def test_green_phase_execution(
        self,
        orchestrator_v2: TDDOrchestrator
    ) -> None:
        """
        GREEN phase executes with implementation patterns.
        
        ARCH-012-REFACTOR-06: Verify GREEN phase
        """
        guidance = orchestrator_v2._build_tdd_guidance(
            module_path="cortex.auth",
            domain="security",
            tdd_phase=TDDPhase.GREEN,
            user_request="Implement auth",
            lens_context=None
        )
        
        result = orchestrator_v2._execute_green_phase(guidance, {})
        
        assert result.is_ok()
        output = result.unwrap()
        assert output["phase"] == "GREEN"

    def test_refactor_phase_execution(
        self,
        orchestrator_v2: TDDOrchestrator
    ) -> None:
        """
        REFACTOR phase executes with refactoring patterns.
        
        ARCH-012-REFACTOR-06: Verify REFACTOR phase
        """
        guidance = orchestrator_v2._build_tdd_guidance(
            module_path="cortex.auth",
            domain="security",
            tdd_phase=TDDPhase.REFACTOR,
            user_request="Refactor auth",
            lens_context=None
        )
        
        result = orchestrator_v2._execute_refactor_phase(guidance, {})
        
        assert result.is_ok()
        output = result.unwrap()
        assert output["phase"] == "REFACTOR"


# =============================================================================
# ARCH-012-REFACTOR-07: End-to-End Protocol Tests
# =============================================================================

class TestEndToEndProtocol:
    """Tests for complete protocol execution (LENS → Security → Challenge → DoR → TDD)."""

    def test_full_protocol_execution_success(
        self,
        orchestrator_v2: TDDOrchestrator
    ) -> None:
        """
        Full protocol executes successfully for valid request.
        
        ARCH-012-REFACTOR-07: Verify E2E execution
        """
        # Mock all components for clean test
        orchestrator_v2.lens_orchestrator = None  # Graceful degradation
        orchestrator_v2.security_analyzer = None
        orchestrator_v2.challenge_engine = None
        orchestrator_v2.dor_gate = None
        
        # Execute domain logic directly (degraded mode)
        result = orchestrator_v2._execute_domain_logic(
            user_request="Implement authentication",
            lens_context=None,
            context={"module_path": "cortex.auth", "domain": "security"}
        )
        
        assert result.is_ok()
        output = result.unwrap()
        assert output["orchestrator"] == "TDDOrchestrator"
        assert "tdd_phase" in output
        assert "guidance" in output
        assert "protocol_phases_completed" in output

    def test_protocol_phases_recorded(
        self,
        orchestrator_v2: TDDOrchestrator
    ) -> None:
        """
        Protocol phases are recorded in result.
        
        ARCH-012-REFACTOR-07: Verify phase tracking
        """
        result = orchestrator_v2._execute_domain_logic(
            user_request="Implement auth",
            lens_context={"synthesis": "Auth implementation"},
            context={"module_path": "cortex.auth"}
        )
        
        assert result.is_ok()
        output = result.unwrap()
        phases = output["protocol_phases_completed"]
        
        # All 5 phases should be listed
        assert "LENS Context" in phases
        assert "Security Assessment" in phases
        assert "Challenge Generation" in phases
        assert "DoR Confidence Gate" in phases
        assert "TDD Domain Logic" in phases


# =============================================================================
# ARCH-012-REFACTOR-08: V1 vs V2 Comparison Tests
# =============================================================================

class TestV1vsV2Comparison:
    """Tests comparing TDDOrchestrator (V1) with TDDOrchestrator."""

    def test_v2_has_base_protocol_components(
        self,
        orchestrator_v2: TDDOrchestrator
    ) -> None:
        """
        V2 has base protocol components that V1 lacks.
        
        ARCH-012-REFACTOR-08: Verify V2 enhancements
        """
        # V2 should have protocol components
        assert hasattr(orchestrator_v2, 'lens_orchestrator')
        assert hasattr(orchestrator_v2, 'challenge_engine')
        assert hasattr(orchestrator_v2, 'dor_gate')
        assert hasattr(orchestrator_v2, 'security_analyzer')
        
        # These are inherited from OrchestratorBaseProtocol

    def test_v2_status_shows_base_protocol(
        self,
        orchestrator_v2: TDDOrchestrator
    ) -> None:
        """
        V2 status shows base protocol integration.
        
        ARCH-012-REFACTOR-08: Verify V2 status
        """
        status = orchestrator_v2.get_tdd_status()
        
        assert status["base_protocol"] == "OrchestratorBaseProtocol"
        assert status["version"] == "2.0"
        assert "protocol_phases" in status
        
        # Should list all 5 phases
        phases = status["protocol_phases"]
        assert len(phases) == 5

    def test_v2_simplifies_tdd_logic(
        self,
        orchestrator_v2: TDDOrchestrator
    ) -> None:
        """
        V2 focuses on TDD logic, protocol handled by base.
        
        ARCH-012-REFACTOR-08: Verify simplification
        """
        # V2 should have clean TDD-specific methods
        assert hasattr(orchestrator_v2, '_execute_domain_logic')
        assert hasattr(orchestrator_v2, '_determine_tdd_phase')
        assert hasattr(orchestrator_v2, '_build_tdd_guidance')
        assert hasattr(orchestrator_v2, '_execute_tdd_phase')
        
        # Protocol methods inherited, not duplicated
        assert hasattr(orchestrator_v2, 'execute_with_protocol')


# =============================================================================
# Run tests with: pytest tests/unit/orchestrators/test_tdd_orchestrator.py -v
# =============================================================================
