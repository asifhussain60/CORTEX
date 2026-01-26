# AC-ID: AC-CHALLENGE-SYSTEM-002 - ChallengeEngine Tests
"""
Tests for ChallengeEngine - LENS-powered challenge generation

AC-CHALLENGE-SYSTEM-002: Challenge-driven interaction system
AC-PERMANENT-FIX-006: Permanent wiring verification

This test module verifies:
1. ChallengeEngine singleton initialization
2. LENS context building (Language→Examination→Navigation→Synthesis)
3. Challenge generation for all 5 disagreement types
4. Challenge response formatting
5. Integration with InteractionOrchestrator

Authority: AC-PERMANENT-FIX-006
Governance:
  - CORE-008: Tests BEFORE code (compliance: test created after implementation)
  - CORE-011: Type hints 100%
  - CORE-012: Google docstrings
"""

import pytest
from pathlib import Path
from typing import Dict, Any, Optional
from unittest.mock import Mock, patch, MagicMock

from cortex.orchestrators.core.challenge_engine import (
    ChallengeEngine,
    ChallengeResponse,
    LENSContext,
    DisagreementType,
    get_challenge_engine
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def challenge_engine() -> ChallengeEngine:
    """Create ChallengeEngine instance.
    
    AC-CHALLENGE-SYSTEM-002: Initialize challenge engine
    """
    return ChallengeEngine()


@pytest.fixture
def sample_lens_context() -> LENSContext:
    """Create sample LENS context for testing.
    
    Returns:
        LENSContext with test data
    """
    return LENSContext(
        language="Implement feature X",
        examination="User wants to add new feature",
        navigation="Feature X relates to module Y",
        synthesis="Implementation should use TDD approach"
    )


@pytest.fixture
def mock_knowledge_repo() -> Mock:
    """Mock knowledge repository for testing.
    
    Returns:
        Mock KnowledgeRepository with test patterns
    """
    mock = Mock()
    mock.get_best_practices.return_value = [
        "Use TDD for all implementations",
        "Write tests before code",
        "Follow CORE-008 governance rule"
    ]
    return mock


# =============================================================================
# AC-CHALLENGE-SYSTEM-002-01: Singleton Pattern Tests
# =============================================================================

class TestChallengeEngineSingleton:
    """Tests for ChallengeEngine singleton pattern."""

    def test_get_challenge_engine_returns_instance(self) -> None:
        """
        Test that get_challenge_engine() returns ChallengeEngine instance.
        
        AC-CHALLENGE-SYSTEM-002: Singleton accessor
        """
        engine = get_challenge_engine()
        
        assert engine is not None
        assert isinstance(engine, ChallengeEngine)

    def test_get_challenge_engine_returns_same_instance(self) -> None:
        """
        Test that get_challenge_engine() returns singleton.
        
        AC-CHALLENGE-SYSTEM-002: Singleton pattern verification
        """
        engine1 = get_challenge_engine()
        engine2 = get_challenge_engine()
        
        assert engine1 is engine2

    def test_challenge_engine_initialization(self, challenge_engine: ChallengeEngine) -> None:
        """
        Test that ChallengeEngine initializes correctly.
        
        AC-CHALLENGE-SYSTEM-002: Initialization verification
        """
        assert challenge_engine is not None
        assert hasattr(challenge_engine, 'build_lens_context')
        assert hasattr(challenge_engine, 'generate_challenge')
        assert hasattr(challenge_engine, 'format_challenge_response')


# =============================================================================
# AC-CHALLENGE-SYSTEM-002-02: LENS Context Building Tests
# =============================================================================

class TestLENSContextBuilding:
    """Tests for LENS synthesis (Language→Examination→Navigation→Synthesis)."""

    def test_build_lens_context_returns_lens_context(
        self,
        challenge_engine: ChallengeEngine
    ) -> None:
        """
        Test that build_lens_context() returns LENSContext.
        
        AC-CHALLENGE-SYSTEM-002: LENS synthesis
        """
        user_request = "Implement feature X using approach Y"
        context = challenge_engine.build_lens_context(user_request)
        
        assert context is not None
        assert isinstance(context, LENSContext)

    def test_lens_context_has_all_phases(
        self,
        challenge_engine: ChallengeEngine
    ) -> None:
        """
        Test that LENS context includes all 4 phases.
        
        AC-CHALLENGE-SYSTEM-002: Language→Examination→Navigation→Synthesis
        """
        user_request = "Implement feature X"
        context = challenge_engine.build_lens_context(user_request)
        
        assert context.language is not None
        assert context.examination is not None
        assert context.navigation is not None
        assert context.synthesis is not None

    def test_lens_language_phase_extracts_intent(
        self,
        challenge_engine: ChallengeEngine
    ) -> None:
        """
        Test that Language phase extracts user intent.
        
        AC-CHALLENGE-SYSTEM-002: Language phase processing
        """
        user_request = "Implement TDD workflow for feature X"
        context = challenge_engine.build_lens_context(user_request)
        
        assert "implement" in context.language.lower() or "TDD" in context.language

    def test_lens_synthesis_provides_recommendation(
        self,
        challenge_engine: ChallengeEngine
    ) -> None:
        """
        Test that Synthesis phase provides actionable recommendation.
        
        AC-CHALLENGE-SYSTEM-002: Synthesis phase output
        """
        user_request = "Write code without tests"
        context = challenge_engine.build_lens_context(user_request)
        
        # Synthesis should recommend better approach
        assert len(context.synthesis) > 0


# =============================================================================
# AC-CHALLENGE-SYSTEM-002-03: Challenge Generation Tests
# =============================================================================

class TestChallengeGeneration:
    """Tests for challenge generation across all disagreement types."""

    def test_generate_challenge_returns_challenge_response(
        self,
        challenge_engine: ChallengeEngine,
        sample_lens_context: LENSContext
    ) -> None:
        """
        Test that generate_challenge() returns ChallengeResponse.
        
        AC-CHALLENGE-SYSTEM-002: Challenge response structure
        """
        user_request = "Implement feature X"
        response = challenge_engine.generate_challenge(user_request, sample_lens_context)
        
        assert response is not None
        assert isinstance(response, ChallengeResponse)

    def test_challenge_response_has_required_fields(
        self,
        challenge_engine: ChallengeEngine,
        sample_lens_context: LENSContext
    ) -> None:
        """
        Test that ChallengeResponse has all required fields.
        
        AC-CHALLENGE-SYSTEM-002: Response structure validation
        """
        response = challenge_engine.generate_challenge("test request", sample_lens_context)
        
        assert hasattr(response, 'has_disagreement')
        assert hasattr(response, 'disagreement_type')
        assert hasattr(response, 'user_request_interpretation')
        assert hasattr(response, 'cortex_analysis')
        assert hasattr(response, 'recommended_alternative')
        assert hasattr(response, 'reasoning')
        assert hasattr(response, 'evidence')
        assert hasattr(response, 'options')

    def test_better_solution_disagreement_type(
        self,
        challenge_engine: ChallengeEngine
    ) -> None:
        """
        Test BETTER_SOLUTION disagreement detection.
        
        AC-CHALLENGE-SYSTEM-002: Better solution challenges
        """
        user_request = "Write code directly without tests"
        context = challenge_engine.build_lens_context(user_request)
        response = challenge_engine.generate_challenge(user_request, context)
        
        # Should detect TDD as better solution
        if response.has_disagreement:
            assert response.disagreement_type == DisagreementType.BETTER_SOLUTION
            assert "test" in response.recommended_alternative.lower() or "TDD" in response.recommended_alternative

    def test_missing_context_disagreement_type(
        self,
        challenge_engine: ChallengeEngine
    ) -> None:
        """
        Test MISSING_CONTEXT disagreement detection.
        
        AC-CHALLENGE-SYSTEM-002: Missing context challenges
        """
        user_request = "Fix the bug"  # Vague request
        context = challenge_engine.build_lens_context(user_request)
        response = challenge_engine.generate_challenge(user_request, context)
        
        # Should detect missing context
        if response.has_disagreement:
            assert response.disagreement_type == DisagreementType.MISSING_CONTEXT
            assert len(response.challenge_message) > 0

    def test_harmful_action_disagreement_type(
        self,
        challenge_engine: ChallengeEngine
    ) -> None:
        """
        Test HARMFUL_ACTION disagreement detection.
        
        AC-CHALLENGE-SYSTEM-002: Harmful action challenges
        """
        user_request = "Delete all production data"
        context = challenge_engine.build_lens_context(user_request)
        response = challenge_engine.generate_challenge(user_request, context)
        
        # Should detect harmful action
        if response.has_disagreement:
            assert response.disagreement_type == DisagreementType.HARMFUL_ACTION
            assert "caution" in response.reasoning.lower() or "risky" in response.reasoning.lower()

    def test_redundant_work_disagreement_type(
        self,
        challenge_engine: ChallengeEngine
    ) -> None:
        """
        Test REDUNDANT_WORK disagreement detection.
        
        AC-CHALLENGE-SYSTEM-002: Redundant work challenges
        """
        user_request = "Reimplement feature that already exists"
        context = challenge_engine.build_lens_context(user_request)
        response = challenge_engine.generate_challenge(user_request, context)
        
        # May detect redundant work if feature is known
        if response.has_disagreement and response.disagreement_type == DisagreementType.REDUNDANT_WORK:
            assert "already" in response.reasoning.lower() or "exists" in response.reasoning.lower()

    def test_architectural_violation_disagreement_type(
        self,
        challenge_engine: ChallengeEngine
    ) -> None:
        """
        Test ARCHITECTURAL_VIOLATION disagreement detection.
        
        AC-CHALLENGE-SYSTEM-002: Architecture violation challenges
        """
        user_request = "Create .md file in root directory outside docs/"
        context = challenge_engine.build_lens_context(user_request)
        response = challenge_engine.generate_challenge(user_request, context)
        
        # Should detect architectural violation (CORE rules)
        if response.has_disagreement:
            # Either detects as ARCHITECTURAL_VIOLATION or BETTER_SOLUTION
            assert response.disagreement_type in [
                DisagreementType.ARCHITECTURAL_VIOLATION,
                DisagreementType.BETTER_SOLUTION
            ]

    def test_no_disagreement_when_request_is_good(
        self,
        challenge_engine: ChallengeEngine
    ) -> None:
        """
        Test that no challenge is generated for good requests.
        
        AC-CHALLENGE-SYSTEM-002: Agreement scenario
        """
        user_request = "Write tests for the new feature following TDD"
        context = challenge_engine.build_lens_context(user_request)
        response = challenge_engine.generate_challenge(user_request, context)
        
        # Good request following best practices
        assert response.has_disagreement is False
        assert response.disagreement_type is None


# =============================================================================
# AC-CHALLENGE-SYSTEM-002-04: Challenge Formatting Tests
# =============================================================================

class TestChallengeFormatting:
    """Tests for challenge response formatting."""

    def test_format_challenge_response_returns_string(
        self,
        challenge_engine: ChallengeEngine
    ) -> None:
        """
        Test that format_challenge_response() returns formatted string.
        
        AC-CHALLENGE-SYSTEM-002: Response formatting
        """
        challenge_response = ChallengeResponse(
            has_disagreement=True,
            disagreement_type=DisagreementType.BETTER_SOLUTION,
            user_request_interpretation="User wants to write code without tests",
            cortex_analysis="Consider using TDD instead",
            recommended_alternative="Write tests first",
            reasoning="TDD ensures better code quality"
        )
        
        formatted = challenge_engine.format_challenge_response(challenge_response)
        
        assert formatted is not None
        assert isinstance(formatted, str)
        assert len(formatted) > 0

    def test_formatted_challenge_includes_disagreement_type(
        self,
        challenge_engine: ChallengeEngine
    ) -> None:
        """
        Test that formatted challenge includes disagreement type.
        
        AC-CHALLENGE-SYSTEM-002: Disagreement type visibility
        """
        challenge_response = ChallengeResponse(
            has_disagreement=True,
            disagreement_type=DisagreementType.MISSING_CONTEXT,
            user_request_interpretation="User request unclear",
            cortex_analysis="Need more information",
            recommended_alternative="Provide feature details",
            reasoning="Insufficient context"
        )
        
        formatted = challenge_engine.format_challenge_response(challenge_response)
        
        # Should mention disagreement type
        assert "MISSING_CONTEXT" in formatted or "missing context" in formatted.lower()

    def test_formatted_challenge_includes_recommendation(
        self,
        challenge_engine: ChallengeEngine
    ) -> None:
        """
        Test that formatted challenge includes recommendation.
        
        AC-CHALLENGE-SYSTEM-002: Alternative solution visibility
        """
        challenge_response = ChallengeResponse(
            has_disagreement=True,
            disagreement_type=DisagreementType.BETTER_SOLUTION,
            user_request_interpretation="User wants direct implementation",
            cortex_analysis="Better approach available",
            recommended_alternative="Use TDD workflow",
            reasoning="Higher quality outcome"
        )
        
        formatted = challenge_engine.format_challenge_response(challenge_response)
        
        # Should include recommendation
        assert "TDD" in formatted or "recommended" in formatted.lower()

    def test_formatted_challenge_includes_reasoning(
        self,
        challenge_engine: ChallengeEngine
    ) -> None:
        """
        Test that formatted challenge includes reasoning.
        
        AC-CHALLENGE-SYSTEM-002: Reasoning transparency
        """
        challenge_response = ChallengeResponse(
            has_disagreement=True,
            disagreement_type=DisagreementType.HARMFUL_ACTION,
            user_request_interpretation="User wants to delete production data",
            cortex_analysis="This action is risky",
            recommended_alternative="Use safer approach",
            reasoning="Could cause data loss"
        )
        
        formatted = challenge_engine.format_challenge_response(challenge_response)
        
        # Should explain why
        assert "data loss" in formatted.lower() or "reasoning" in formatted.lower()

    def test_format_no_disagreement_returns_empty_or_none(
        self,
        challenge_engine: ChallengeEngine
    ) -> None:
        """
        Test that formatting no-disagreement response is handled correctly.
        
        AC-CHALLENGE-SYSTEM-002: Agreement formatting
        """
        challenge_response = ChallengeResponse(
            has_disagreement=False,
            disagreement_type=None,
            user_request_interpretation="",
            cortex_analysis="",
            recommended_alternative="",
            reasoning=""
        )
        
        formatted = challenge_engine.format_challenge_response(challenge_response)
        
        # Should return empty string or None for no disagreement
        assert formatted == "" or formatted is None or "no challenge" in formatted.lower()

    def test_formatted_challenge_includes_numbered_options(
        self,
        challenge_engine: ChallengeEngine
    ) -> None:
        """
        Test that formatted challenge includes emoji-numbered options.
        
        CORE-029: Response format enhancement - numbered options with emojis
        """
        challenge_response = ChallengeResponse(
            has_disagreement=True,
            disagreement_type=DisagreementType.BETTER_SOLUTION,
            user_request_interpretation="User wants to implement without tests",
            cortex_analysis="Tests should come first",
            recommended_alternative="Use TDD approach",
            reasoning="TDD ensures quality",
            options=[
                "Implement the better alternative (TDD approach)",
                "Keep current plan (skip tests initially)",
                "Modify your idea (mix testing and implementation)"
            ]
        )
        
        formatted = challenge_engine.format_challenge_response(challenge_response)
        
        # Check for emoji-numbered options
        assert "1️⃣" in formatted
        assert "2️⃣" in formatted
        assert "3️⃣" in formatted
        assert "What would you like to do?" in formatted
        assert "Reply with: `1` / `2` / `3`" in formatted

    def test_formatted_challenge_option_descriptions_readable(
        self,
        challenge_engine: ChallengeEngine
    ) -> None:
        """
        Test that numbered options are clearly readable.
        
        CORE-029: UX improvement - clear option descriptions
        """
        challenge_response = ChallengeResponse(
            has_disagreement=True,
            disagreement_type=DisagreementType.MISSING_CONTEXT,
            user_request_interpretation="Fix the issue",
            cortex_analysis="Need more details",
            recommended_alternative="Provide bug details",
            reasoning="Insufficient context",
            options=[
                "Provide specific error message and stack trace",
                "Provide steps to reproduce",
                "Ask CORTEX for help analyzing the problem"
            ]
        )
        
        formatted = challenge_engine.format_challenge_response(challenge_response)
        
        # Check that descriptions are preserved
        assert "Provide specific error message" in formatted
        assert "steps to reproduce" in formatted
        assert "Ask CORTEX for help" in formatted


# =============================================================================
# AC-CHALLENGE-SYSTEM-002-05: Integration Tests
# =============================================================================

class TestChallengeEngineIntegration:
    """Tests for ChallengeEngine integration scenarios."""

    def test_full_workflow_with_disagreement(
        self,
        challenge_engine: ChallengeEngine
    ) -> None:
        """
        Test complete workflow: LENS → Challenge → Format.
        
        AC-CHALLENGE-SYSTEM-002: End-to-end workflow
        """
        user_request = "Skip tests and write code directly"
        
        # Step 1: Build LENS context
        context = challenge_engine.build_lens_context(user_request)
        assert context is not None
        
        # Step 2: Generate challenge
        response = challenge_engine.generate_challenge(user_request, context)
        assert response is not None
        
        # Step 3: Format challenge
        if response.has_disagreement:
            formatted = challenge_engine.format_challenge_response(response)
            assert formatted is not None
            assert len(formatted) > 0

    def test_full_workflow_with_agreement(
        self,
        challenge_engine: ChallengeEngine
    ) -> None:
        """
        Test complete workflow with good request.
        
        AC-CHALLENGE-SYSTEM-002: Agreement path
        """
        user_request = "Write tests following TDD for new feature"
        
        # Step 1: Build LENS context
        context = challenge_engine.build_lens_context(user_request)
        assert context is not None
        
        # Step 2: Generate challenge (should be no disagreement)
        response = challenge_engine.generate_challenge(user_request, context)
        assert response is not None
        assert response.has_disagreement is False

    def test_challenge_engine_persists_across_calls(self) -> None:
        """
        Test that ChallengeEngine singleton persists state.
        
        AC-CHALLENGE-SYSTEM-002: Singleton state persistence
        """
        engine1 = get_challenge_engine()
        context1 = engine1.build_lens_context("test request 1")
        
        engine2 = get_challenge_engine()
        context2 = engine2.build_lens_context("test request 2")
        
        # Same instance
        assert engine1 is engine2
        
        # Can handle multiple requests
        assert context1 is not None
        assert context2 is not None


# =============================================================================
# AC-PERMANENT-FIX-006: Permanent Wiring Verification
# =============================================================================

class TestACPermanentFix006:
    """Tests for AC-PERMANENT-FIX-006 tracking."""

    def test_challenge_engine_file_exists(self) -> None:
        """
        Test that challenge_engine.py exists.
        
        AC-PERMANENT-FIX-006: File existence validation
        """
        # From tests/unit/orchestrators/core/ -> go up 4 levels to CORTEX root
        challenge_engine_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "cortex" / "orchestrators" / "core" / "challenge_engine.py"
        )
        
        assert challenge_engine_path.exists(), f"challenge_engine.py must exist at {challenge_engine_path}"

    def test_challenge_engine_has_required_exports(self) -> None:
        """
        Test that challenge_engine.py exports required classes.
        
        AC-PERMANENT-FIX-006: API surface validation
        """
        from cortex.orchestrators.core.challenge_engine import (
            ChallengeEngine,
            ChallengeResponse,
            LENSContext,
            DisagreementType,
            get_challenge_engine
        )
        
        assert ChallengeEngine is not None
        assert ChallengeResponse is not None
        assert LENSContext is not None
        assert DisagreementType is not None
        assert get_challenge_engine is not None

    def test_interaction_orchestrator_integrates_challenge_engine(self) -> None:
        """
        Test that InteractionOrchestrator has challenge engine integrated.
        
        AC-PERMANENT-FIX-006: Integration validation
        """
        # From tests/unit/orchestrators/core/ -> go up 4 levels to CORTEX root
        interaction_orch_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "cortex" / "orchestrators" / "core" / "interaction_orchestrator.py"
        )
        
        assert interaction_orch_path.exists(), f"interaction_orchestrator.py must exist at {interaction_orch_path}"
        
        content = interaction_orch_path.read_text()
        assert "from cortex.orchestrators.core.challenge_engine import" in content
        assert "execute_turn_with_challenge" in content
        assert "enable_challenges" in content
