"""
Tests for Persona MCP Tools

Authority: Phase 37 S4, CORE-008 (TDD-first)
Tests 5 MCP tools for persona management via cortex_set_persona, cortex_get_persona, 
cortex_set_depth, cortex_infer_persona, cortex_persona_history
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any

from cortex.mcp.tools.persona_tools import (
    PersonaTools,
    PersonaSetResult,
    PersonaState,
    DepthSetResult,
    InferenceResult,
)
from cortex.orchestrators.persona.models import PersonaId, DepthLevel
from cortex.orchestrators.persona.master_orchestrator import MasterOrchestrator
from cortex.orchestrators.persona.session_context import SessionContext


class TestPersonaTools:
    """Test suite for persona MCP tools"""

    @pytest.fixture
    def mock_orchestrator(self):
        """Create a mock MasterOrchestrator"""
        orchestrator = Mock(spec=MasterOrchestrator)
        orchestrator.session_context = Mock(spec=SessionContext)
        return orchestrator

    @pytest.fixture
    def persona_tools(self, mock_orchestrator):
        """Create PersonaTools instance with mock orchestrator"""
        tools = PersonaTools(orchestrator=mock_orchestrator)
        return tools

    # Test cortex_set_persona
    def test_cortex_set_persona_basic(self, persona_tools, mock_orchestrator):
        """Test setting persona to engineer"""
        mock_orchestrator.session_context.primary_persona = PersonaId.ENGINEER
        
        result = persona_tools.cortex_set_persona(role="engineer", save=False)
        
        assert isinstance(result, PersonaSetResult)
        assert result.success is True
        assert result.persona == PersonaId.ENGINEER

    def test_cortex_set_persona_business_leader(self, persona_tools, mock_orchestrator):
        """Test setting persona to business_leader"""
        mock_orchestrator.session_context.primary_persona = PersonaId.BUSINESS_LEADER
        
        result = persona_tools.cortex_set_persona(role="business_leader", save=False)
        
        assert result.success is True
        assert result.persona == PersonaId.BUSINESS_LEADER

    def test_cortex_set_persona_with_save(self, persona_tools, mock_orchestrator):
        """Test setting persona with persistence"""
        mock_orchestrator.session_context.primary_persona = PersonaId.PRODUCT_OWNER
        
        result = persona_tools.cortex_set_persona(role="product_owner", save=True)
        
        assert result.success is True
        assert result.persona == PersonaId.PRODUCT_OWNER
        assert result.saved is True

    def test_cortex_set_persona_invalid_role(self, persona_tools):
        """Test setting invalid persona"""
        result = persona_tools.cortex_set_persona(role="invalid_role", save=False)
        
        assert result.success is False
        assert result.error is not None

    def test_cortex_set_persona_all_roles(self, persona_tools, mock_orchestrator):
        """Test setting all valid persona roles"""
        valid_roles = [
            "business_leader",
            "product_owner",
            "scrum_master",
            "tech_lead",
            "engineer",
        ]
        
        for role in valid_roles:
            persona_id = PersonaId(role.upper())
            mock_orchestrator.session_context.primary_persona = persona_id
            
            result = persona_tools.cortex_set_persona(role=role, save=False)
            
            assert result.success is True
            assert result.persona == persona_id

    # Test cortex_get_persona
    def test_cortex_get_persona_basic(self, persona_tools, mock_orchestrator):
        """Test getting current persona state"""
        mock_orchestrator.session_context.primary_persona = PersonaId.ENGINEER
        mock_orchestrator.session_context.active_depth = DepthLevel.FULL
        mock_orchestrator.get_current_state.return_value = {
            "primary_persona": PersonaId.ENGINEER,
            "active_depth": DepthLevel.FULL,
            "inference_confidence": 0.95,
        }
        
        result = persona_tools.cortex_get_persona()
        
        assert isinstance(result, PersonaState)
        assert result.persona == PersonaId.ENGINEER
        assert result.depth == DepthLevel.FULL

    def test_cortex_get_persona_returns_all_fields(self, persona_tools, mock_orchestrator):
        """Test that get_persona returns all state fields"""
        mock_orchestrator.get_current_state.return_value = {
            "primary_persona": PersonaId.TECH_LEAD,
            "active_depth": DepthLevel.DETAILED,
            "inference_confidence": 0.85,
        }
        
        result = persona_tools.cortex_get_persona()
        
        assert hasattr(result, "persona")
        assert hasattr(result, "depth")
        assert hasattr(result, "confidence")

    def test_cortex_get_persona_unknown_state(self, persona_tools, mock_orchestrator):
        """Test getting persona when in unknown state"""
        mock_orchestrator.session_context.primary_persona = PersonaId.UNKNOWN
        mock_orchestrator.get_current_state.return_value = {
            "primary_persona": PersonaId.UNKNOWN,
            "active_depth": DepthLevel.STANDARD,
            "inference_confidence": 0.0,
        }
        
        result = persona_tools.cortex_get_persona()
        
        assert result.persona == PersonaId.UNKNOWN

    # Test cortex_set_depth
    def test_cortex_set_depth_single_turn(self, persona_tools, mock_orchestrator):
        """Test overriding depth for single turn"""
        result = persona_tools.cortex_set_depth(level="executive", sticky=False)
        
        assert isinstance(result, DepthSetResult)
        assert result.success is True
        assert result.depth == DepthLevel.EXECUTIVE
        assert result.ttl_turns == 1

    def test_cortex_set_depth_sticky(self, persona_tools, mock_orchestrator):
        """Test sticky depth override"""
        result = persona_tools.cortex_set_depth(level="full", sticky=True)
        
        assert result.success is True
        assert result.depth == DepthLevel.FULL
        assert result.sticky is True

    def test_cortex_set_depth_all_levels(self, persona_tools):
        """Test setting all depth levels"""
        valid_levels = ["executive", "standard", "detailed", "full"]
        
        for level in valid_levels:
            result = persona_tools.cortex_set_depth(level=level, sticky=False)
            
            assert result.success is True
            assert result.depth == DepthLevel(level.upper())

    def test_cortex_set_depth_invalid_level(self, persona_tools):
        """Test setting invalid depth level"""
        result = persona_tools.cortex_set_depth(level="invalid_level", sticky=False)
        
        assert result.success is False
        assert result.error is not None

    # Test cortex_infer_persona
    def test_cortex_infer_persona_from_context(self, persona_tools, mock_orchestrator):
        """Test inferring persona from context"""
        context = {
            "vocabulary_complexity": "high",
            "code_interest": True,
            "query_type": "technical",
        }
        
        mock_orchestrator.role_resolver.infer_role.return_value = (
            PersonaId.ENGINEER,
            0.85,
        )
        
        result = persona_tools.cortex_infer_persona(context=context)
        
        assert isinstance(result, InferenceResult)
        assert result.inferred_persona == PersonaId.ENGINEER
        assert result.confidence == 0.85

    def test_cortex_infer_persona_business_context(self, persona_tools, mock_orchestrator):
        """Test inferring business leader persona"""
        context = {
            "query_type": "metrics",
            "keywords": ["ROI", "revenue", "KPI"],
        }
        
        mock_orchestrator.role_resolver.infer_role.return_value = (
            PersonaId.BUSINESS_LEADER,
            0.92,
        )
        
        result = persona_tools.cortex_infer_persona(context=context)
        
        assert result.inferred_persona == PersonaId.BUSINESS_LEADER
        assert result.confidence >= 0.9

    def test_cortex_infer_persona_empty_context(self, persona_tools, mock_orchestrator):
        """Test inferring with minimal context"""
        context = {}
        
        mock_orchestrator.role_resolver.infer_role.return_value = (
            PersonaId.UNKNOWN,
            0.0,
        )
        
        result = persona_tools.cortex_infer_persona(context=context)
        
        assert result.inferred_persona == PersonaId.UNKNOWN
        assert result.confidence == 0.0

    def test_cortex_infer_persona_low_confidence_fallback(self, persona_tools, mock_orchestrator):
        """Test that low confidence triggers discovery mode"""
        context = {"ambiguous": True}
        
        mock_orchestrator.role_resolver.infer_role.return_value = (
            PersonaId.UNKNOWN,
            0.35,
        )
        
        result = persona_tools.cortex_infer_persona(context=context)
        
        assert result.confidence < 0.7
        assert result.requires_discovery is True

    # Test cortex_persona_history
    def test_cortex_persona_history_basic(self, persona_tools, mock_orchestrator):
        """Test retrieving persona switch history"""
        mock_history = [
            {
                "timestamp": "2026-02-08T10:00:00Z",
                "from_persona": PersonaId.ENGINEER,
                "to_persona": PersonaId.TECH_LEAD,
                "confidence": 0.88,
                "trigger": "explicit_keyword",
            },
            {
                "timestamp": "2026-02-08T10:01:00Z",
                "from_persona": PersonaId.TECH_LEAD,
                "to_persona": PersonaId.ENGINEER,
                "confidence": 0.92,
                "trigger": "context_signal",
            },
        ]
        
        mock_orchestrator.get_switch_history.return_value = mock_history
        
        result = persona_tools.cortex_persona_history(limit=10)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0]["to_persona"] == PersonaId.TECH_LEAD

    def test_cortex_persona_history_with_limit(self, persona_tools, mock_orchestrator):
        """Test history with limit parameter"""
        mock_history = [
            {"to_persona": PersonaId.ENGINEER, "timestamp": "time1"},
            {"to_persona": PersonaId.TECH_LEAD, "timestamp": "time2"},
            {"to_persona": PersonaId.PRODUCT_OWNER, "timestamp": "time3"},
        ]
        
        mock_orchestrator.get_switch_history.return_value = mock_history[:2]
        
        result = persona_tools.cortex_persona_history(limit=2)
        
        assert len(result) == 2

    def test_cortex_persona_history_empty(self, persona_tools, mock_orchestrator):
        """Test history when no switches have occurred"""
        mock_orchestrator.get_switch_history.return_value = []
        
        result = persona_tools.cortex_persona_history(limit=10)
        
        assert isinstance(result, list)
        assert len(result) == 0

    def test_cortex_persona_history_returns_structured_data(self, persona_tools, mock_orchestrator):
        """Test that history returns properly structured data"""
        mock_history = [
            {
                "timestamp": "2026-02-08T10:00:00Z",
                "from_persona": PersonaId.UNKNOWN,
                "to_persona": PersonaId.ENGINEER,
                "confidence": 0.8,
                "trigger": "keyword_match",
            }
        ]
        
        mock_orchestrator.get_switch_history.return_value = mock_history
        
        result = persona_tools.cortex_persona_history(limit=10)
        
        assert len(result) == 1
        entry = result[0]
        assert "timestamp" in entry
        assert "from_persona" in entry
        assert "to_persona" in entry
        assert "confidence" in entry


class TestPersonaSetResult:
    """Test PersonaSetResult data class"""

    def test_persona_set_result_success(self):
        """Test successful persona set result"""
        result = PersonaSetResult(
            success=True,
            persona=PersonaId.ENGINEER,
            saved=False,
            error=None,
        )
        
        assert result.success is True
        assert result.persona == PersonaId.ENGINEER

    def test_persona_set_result_with_save(self):
        """Test result with persistence"""
        result = PersonaSetResult(
            success=True,
            persona=PersonaId.PRODUCT_OWNER,
            saved=True,
            error=None,
        )
        
        assert result.saved is True

    def test_persona_set_result_failure(self):
        """Test failure result"""
        result = PersonaSetResult(
            success=False,
            persona=None,
            saved=False,
            error="Invalid persona role",
        )
        
        assert result.success is False
        assert result.error is not None


class TestPersonaState:
    """Test PersonaState data class"""

    def test_persona_state_creation(self):
        """Test creating persona state"""
        state = PersonaState(
            persona=PersonaId.ENGINEER,
            depth=DepthLevel.FULL,
            confidence=0.92,
        )
        
        assert state.persona == PersonaId.ENGINEER
        assert state.depth == DepthLevel.FULL
        assert state.confidence == 0.92

    def test_persona_state_unknown(self):
        """Test unknown persona state"""
        state = PersonaState(
            persona=PersonaId.UNKNOWN,
            depth=DepthLevel.STANDARD,
            confidence=0.0,
        )
        
        assert state.persona == PersonaId.UNKNOWN


class TestDepthSetResult:
    """Test DepthSetResult data class"""

    def test_depth_set_result_single_turn(self):
        """Test single-turn depth override result"""
        result = DepthSetResult(
            success=True,
            depth=DepthLevel.EXECUTIVE,
            sticky=False,
            ttl_turns=1,
            error=None,
        )
        
        assert result.success is True
        assert result.ttl_turns == 1

    def test_depth_set_result_sticky(self):
        """Test sticky depth override result"""
        result = DepthSetResult(
            success=True,
            depth=DepthLevel.FULL,
            sticky=True,
            ttl_turns=999,
            error=None,
        )
        
        assert result.sticky is True


class TestInferenceResult:
    """Test InferenceResult data class"""

    def test_inference_result_high_confidence(self):
        """Test high confidence inference"""
        result = InferenceResult(
            inferred_persona=PersonaId.ENGINEER,
            confidence=0.88,
            requires_discovery=False,
        )
        
        assert result.inferred_persona == PersonaId.ENGINEER
        assert result.requires_discovery is False

    def test_inference_result_low_confidence(self):
        """Test low confidence requiring discovery"""
        result = InferenceResult(
            inferred_persona=PersonaId.UNKNOWN,
            confidence=0.35,
            requires_discovery=True,
        )
        
        assert result.confidence < 0.7
        assert result.requires_discovery is True
