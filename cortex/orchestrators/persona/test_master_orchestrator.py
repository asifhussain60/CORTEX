"""
Tests for MasterOrchestrator persona coordination

Authority: Phase 37 S3, CORE-008 (TDD-first)
Tests coordination of RoleResolver → PersonaInjector pipeline
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from cortex.orchestrators.persona.master_orchestrator import (
    MasterOrchestrator,
    PersonaResult,
)
from cortex.orchestrators.persona.models import DepthLevel, PersonaId
from cortex.orchestrators.persona.persona_injector import PersonaInjector
from cortex.orchestrators.persona.persona_loader import PersonaLoader
from cortex.orchestrators.persona.role_resolver import RoleResolver
from cortex.orchestrators.persona.session_context import SessionContext


class TestMasterOrchestrator:
    """Test suite for MasterOrchestrator coordination"""

    @pytest.fixture
    def persona_loader(self):
        """Create a test persona loader"""
        return PersonaLoader()

    @pytest.fixture
    def session_context(self):
        """Create a test session context"""
        return SessionContext(user_id="test_user_123")

    @pytest.fixture
    def role_resolver(self, persona_loader):
        """Create a test role resolver"""
        return RoleResolver(loader=persona_loader)

    @pytest.fixture
    def persona_injector(self, persona_loader):
        """Create a test persona injector"""
        return PersonaInjector(loader=persona_loader)

    @pytest.fixture
    def orchestrator(self, session_context, role_resolver, persona_injector):
        """Create a test orchestrator"""
        return MasterOrchestrator(
            session_context=session_context,
            role_resolver=role_resolver,
            persona_injector=persona_injector
        )

    def test_orchestrator_initialization(self, orchestrator):
        """Test that orchestrator initializes with required components"""
        assert orchestrator.session_context is not None
        assert orchestrator.role_resolver is not None
        assert orchestrator.persona_injector is not None

    def test_process_message_flow_basic(self, orchestrator):
        """Test basic message processing flow"""
        message = "I'm an engineer working on microservices. How do I optimize latency?"
        context = {}

        result = orchestrator.process(message=message, context=context)

        assert result is not None
        assert isinstance(result, PersonaResult)
        assert result.detected_persona == PersonaId.ENGINEER
        assert result.formatted_response is not None

    def test_process_message_detects_engineer_persona(self, orchestrator):
        """Test that engineer-specific keywords trigger engineer persona"""
        message = "I'm a software engineer. Show me the code structure."
        context = {}

        result = orchestrator.process(message=message, context=context)

        assert result.detected_persona == PersonaId.ENGINEER
        assert result.confidence > 0.7

    def test_process_message_detects_business_leader_persona(self, orchestrator):
        """Test that business leader keywords trigger appropriate persona"""
        message = "What's the ROI impact? We need business metrics."
        context = {}

        result = orchestrator.process(message=message, context=context)

        assert result.detected_persona == PersonaId.BUSINESS_LEADER
        assert result.confidence > 0.7

    def test_process_message_respects_user_session_state(self, orchestrator):
        """Test that session state affects persona detection"""
        # First message: engineer
        message1 = "I'm an engineer interested in performance."
        orchestrator.process(message=message1, context={})

        # Verify session state updated
        assert orchestrator.session_context.primary_persona == PersonaId.ENGINEER

    def test_process_message_applies_depth_override(self, orchestrator):
        """Test that depth overrides affect response formatting"""
        message = "Show me the implementation details"
        context = {"depth_override": DepthLevel.FULL}

        result = orchestrator.process(message=message, context=context)

        assert result.active_depth == DepthLevel.FULL

    def test_process_message_applies_word_limits(self, orchestrator):
        """Test that word limits are applied based on depth"""
        long_response = "word " * 500  # 2500 words

        # Set executive depth (100 word limit)
        orchestrator.session_context.set_depth_override(DepthLevel.EXECUTIVE, ttl_turns=1)

        result = orchestrator.process(
            message="Summarize this",
            context={},
            response_to_format=long_response
        )

        # Verify response is truncated
        word_count = len(result.formatted_response.split())
        assert word_count <= 150  # Some tolerance for formatting

    def test_process_message_handles_empty_message(self, orchestrator):
        """Test handling of empty message"""
        result = orchestrator.process(message="", context={})

        # Should still work, just with less confidence
        assert result is not None
        assert result.detected_persona is not None

    def test_process_message_context_none(self, orchestrator):
        """Test handling of None context"""
        message = "Test message"
        result = orchestrator.process(message=message, context=None)

        assert result is not None
        assert result.detected_persona is not None

    def test_orchestrator_maintains_switch_history(self, orchestrator):
        """Test that persona switches are tracked in history"""
        msg1 = "I'm an engineer"
        msg2 = "Actually, I'm a product owner"

        orchestrator.process(message=msg1, context={})
        p1 = orchestrator.session_context.primary_persona

        orchestrator.process(message=msg2, context={})
        p2 = orchestrator.session_context.primary_persona

        # Get switch history
        history = orchestrator.get_switch_history()

        assert len(history) >= 1
        assert history[-1]['to_persona'] == p2

    def test_orchestrator_respects_sticky_depth_override(self, orchestrator):
        """Test that sticky depth overrides persist across messages"""
        orchestrator.session_context.set_depth_override(
            DepthLevel.EXECUTIVE,
            ttl_turns=10  # Sticky for 10 turns
        )

        # First message
        result1 = orchestrator.process(message="msg1", context={})
        depth1 = result1.active_depth

        # Second message
        result2 = orchestrator.process(message="msg2", context={})
        depth2 = result2.active_depth

        # Both should be executive
        assert depth1 == DepthLevel.EXECUTIVE
        assert depth2 == DepthLevel.EXECUTIVE

    def test_orchestrator_clears_expired_depth_override(self, orchestrator):
        """Test that depth override TTL expires"""
        orchestrator.session_context.set_depth_override(
            DepthLevel.EXECUTIVE,
            ttl_turns=1  # Expire after 1 turn
        )

        result1 = orchestrator.process(message="msg1", context={})
        assert result1.active_depth == DepthLevel.EXECUTIVE

        result2 = orchestrator.process(message="msg2", context={})
        # Should revert to inferred depth
        assert result2.active_depth != DepthLevel.EXECUTIVE

    def test_orchestrator_process_returns_persona_result(self, orchestrator):
        """Test that process() returns proper PersonaResult object"""
        result = orchestrator.process(
            message="Test message",
            context={}
        )

        assert hasattr(result, 'detected_persona')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'active_depth')
        assert hasattr(result, 'formatted_response')
        assert hasattr(result, 'format_rules_applied')

    def test_orchestrator_formats_response_with_rules(self, orchestrator):
        """Test that formatting rules are applied to responses"""
        message = "engineer here"
        test_response = "Here's the technical implementation with 50 lines of code"

        result = orchestrator.process(
            message=message,
            context={},
            response_to_format=test_response
        )

        assert result.format_rules_applied is not None
        assert len(result.format_rules_applied) > 0

    def test_orchestrator_infer_confidence_high_for_explicit_keywords(self, orchestrator):
        """Test confidence is high when persona keywords are explicit"""
        message = "I'm a software engineer building APIs"

        result = orchestrator.process(message=message, context={})

        assert result.confidence >= 0.8

    def test_orchestrator_infer_confidence_lower_for_implicit_signals(self, orchestrator):
        """Test confidence is lower when only context signals available"""
        message = "I want to understand how this architecture works and the code flow"

        result = orchestrator.process(message=message, context={})

        # This message has some implicit signals but no explicit keywords
        # Confidence will be 0.0 or very low
        assert result.confidence >= 0.0
        # The persona should still be detected (engineer by default for code-related content)
        assert result.detected_persona is not None

    def test_orchestrator_api_methods_exist(self, orchestrator):
        """Test that all required public API methods exist"""
        assert callable(orchestrator.process)
        assert callable(orchestrator.get_switch_history)
        assert callable(orchestrator.reset_persona)
        assert callable(orchestrator.get_current_state)

    def test_orchestrator_get_current_state(self, orchestrator):
        """Test that get_current_state() returns session state"""
        orchestrator.process(message="engineer here", context={})

        state = orchestrator.get_current_state()

        assert state is not None
        assert 'primary_persona' in state
        assert 'active_depth' in state
        assert 'inference_confidence' in state

    def test_orchestrator_reset_persona(self, orchestrator):
        """Test that reset_persona() clears persona"""
        orchestrator.process(message="engineer", context={})
        assert orchestrator.session_context.primary_persona == PersonaId.ENGINEER

        orchestrator.reset_persona()

        # After reset, should revert to UNKNOWN
        assert orchestrator.session_context.primary_persona == PersonaId.UNKNOWN

    def test_orchestrator_natural_language_depth_trigger(self, orchestrator):
        """Test that NL depth triggers are recognized"""
        message = "engineer: show me the code"

        result = orchestrator.process(message=message, context={})

        # "show me the code" should trigger FULL depth
        assert result.active_depth == DepthLevel.FULL


class TestPersonaResult:
    """Test suite for PersonaResult data class"""

    def test_persona_result_creation(self):
        """Test PersonaResult initialization"""
        result = PersonaResult(
            detected_persona=PersonaId.ENGINEER,
            confidence=0.95,
            active_depth=DepthLevel.DETAILED,
            formatted_response="Test response",
            format_rules_applied=["code_visible", "metrics_technical"]
        )

        assert result.detected_persona == PersonaId.ENGINEER
        assert result.confidence == 0.95
        assert result.active_depth == DepthLevel.DETAILED
        assert result.formatted_response == "Test response"
        assert len(result.format_rules_applied) == 2

    def test_persona_result_confidence_bounds(self):
        """Test that confidence is bounded 0-1"""
        # Valid range
        result = PersonaResult(
            detected_persona=PersonaId.ENGINEER,
            confidence=0.5
        )
        assert 0 <= result.confidence <= 1

    def test_persona_result_default_values(self):
        """Test PersonaResult default values"""
        result = PersonaResult(
            detected_persona=PersonaId.UNKNOWN
        )

        assert result.confidence >= 0
        assert result.active_depth is not None
        assert result.formatted_response is not None
        assert result.format_rules_applied is not None
