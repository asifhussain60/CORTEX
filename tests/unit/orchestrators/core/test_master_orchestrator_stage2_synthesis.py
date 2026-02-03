"""
Phase 20.5 Component 3: MasterOrchestrator Stage 2 Knowledge Synthesis Tests

Validates that MasterOrchestrator invokes KnowledgeSynthesisEngine at Stage 2.

Authority: AC-KNOWLEDGE-SYNTHESIS-001
"""

import pytest
from unittest.mock import MagicMock, patch
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
from cortex.brain.knowledge.unified_intelligence_context import (
    UnifiedIntelligenceContext,
    LENSIntelligence,
    CompanyKnowledge,
    CORTEXKnowledge,
    SynthesisResult,
)


@pytest.fixture
def master_orchestrator():
    """Create MasterOrchestrator instance."""
    return MasterOrchestrator()


@pytest.fixture
def mock_synthesis_engine():
    """Mock KnowledgeSynthesisEngine."""
    with patch("cortex.orchestrators.core.master_orchestrator.get_synthesis_engine") as mock:
        engine = MagicMock()
        mock.return_value = engine
        yield engine


@pytest.fixture
def sample_request():
    """Sample Stage 2 request."""
    return {
        "operation": "IMPLEMENT",
        "description": "Add authentication feature",
        "file_path": "/app/auth.py",
        "company_name": "AcmeCorp",
        "domain": "security",
        "keywords": ["auth", "login"],
        "context": {}
    }


@pytest.fixture
def sample_routing_result():
    """Sample IntentRouter result with LENS insights."""
    return {
        "intent": "IMPLEMENT",
        "target_orchestrator": "TDDOrchestrator",
        "confidence_score": 0.9,
        "reasoning": "Implementation request detected",
        "context": {
            "lens_insights": {
                "git_analysis": {"commits": 42},
                "ast_analysis": {"complexity": 5},
                "comment_analysis": {"coverage": 0.8},
                "company_knowledge": {
                    "domain_rules": {"security": {"requires_2fa": True}},
                    "compliance_standards": ["OWASP"]
                }
            }
        }
    }


@pytest.fixture
def sample_unified_context():
    """Sample UnifiedIntelligenceContext."""
    return UnifiedIntelligenceContext(
        lens_intelligence=LENSIntelligence(
            git_analysis={"commits": 42},
            ast_analysis={"complexity": 5},
            comment_analysis={"coverage": 0.8}
        ),
        company_knowledge=CompanyKnowledge(
            domain_rules={"security": {"requires_2fa": True}},
            compliance_standards=["OWASP"],
            precedence="OVERRIDE"
        ),
        cortex_knowledge=CORTEXKnowledge(
            best_practices={"CORE-008": {"title": "TDD Required"}},
            patterns={"implement": ["TDD-first"]},
            anti_patterns=["no-tests"]
        ),
        synthesis_result=SynthesisResult(
            cited_rules=["CORE-008", "CORE-011"],
            violations=[],
            guidance=["Write tests before implementation"],
            merged_practices={"CORE-008": {"title": "TDD Required"}}
        )
    )


def test_stage_2_routing_invokes_synthesis(
    master_orchestrator,
    mock_synthesis_engine,
    sample_request,
    sample_routing_result,
    sample_unified_context
):
    """Test that _stage_2_routing() invokes synthesis engine."""
    # Mock IntentRouter
    with patch.object(master_orchestrator, "intent_router") as mock_router:
        mock_router.route_with_lens_auto_fetch.return_value = sample_routing_result
        mock_synthesis_engine.synthesize_unified_context.return_value = sample_unified_context
        
        # Call Stage 2
        result = master_orchestrator._stage_2_routing(sample_request)
        
        # Verify synthesis was called
        mock_synthesis_engine.synthesize_unified_context.assert_called_once()
        call_args = mock_synthesis_engine.synthesize_unified_context.call_args
        assert call_args[1]["intent_type"] == "IMPLEMENT"
        assert call_args[1]["file_path"] == "/app/auth.py"


def test_stage_2_routing_attaches_unified_intelligence(
    master_orchestrator,
    mock_synthesis_engine,
    sample_request,
    sample_routing_result,
    sample_unified_context
):
    """Test that unified intelligence is attached to result."""
    with patch.object(master_orchestrator, "intent_router") as mock_router:
        mock_router.route_with_lens_auto_fetch.return_value = sample_routing_result
        mock_synthesis_engine.synthesize_unified_context.return_value = sample_unified_context
        
        result = master_orchestrator._stage_2_routing(sample_request)
        
        # Verify unified intelligence attached
        assert "unified_intelligence" in result
        assert "cited_rules" in result
        assert "violations" in result
        assert "guidance" in result
        assert result["cited_rules"] == ["CORE-008", "CORE-011"]


def test_stage_2_routing_handles_synthesis_failure(
    master_orchestrator,
    mock_synthesis_engine,
    sample_request,
    sample_routing_result
):
    """Test graceful degradation if synthesis fails."""
    with patch.object(master_orchestrator, "intent_router") as mock_router:
        mock_router.route_with_lens_auto_fetch.return_value = sample_routing_result
        mock_synthesis_engine.synthesize_unified_context.side_effect = Exception("Synthesis error")
        
        # Should not raise exception
        result = master_orchestrator._stage_2_routing(sample_request)
        
        # Should still have IntentRouter result
        assert result["intent"] == "IMPLEMENT"
        assert result["target_orchestrator"] == "TDDOrchestrator"


def test_stage_2_routing_with_no_lens_insights(
    master_orchestrator,
    mock_synthesis_engine,
    sample_request,
    sample_unified_context
):
    """Test synthesis when no LENS insights available."""
    # Result without LENS insights
    minimal_result = {
        "intent": "IMPLEMENT",
        "target_orchestrator": "TDDOrchestrator",
        "confidence_score": 0.9,
        "reasoning": "Implementation request",
        "context": {}
    }
    
    with patch.object(master_orchestrator, "intent_router") as mock_router:
        mock_router.route_with_lens_auto_fetch.return_value = minimal_result
        mock_synthesis_engine.synthesize_unified_context.return_value = sample_unified_context
        
        result = master_orchestrator._stage_2_routing(sample_request)
        
        # Synthesis should still be called (with empty LENS)
        mock_synthesis_engine.synthesize_unified_context.assert_called_once()
        call_args = mock_synthesis_engine.synthesize_unified_context.call_args
        lens_intel = call_args[1]["lens_intelligence"]
        assert lens_intel.git_analysis == {}


def test_stage_2_routing_logs_synthesis_activity(
    master_orchestrator,
    mock_synthesis_engine,
    sample_request,
    sample_routing_result,
    sample_unified_context
):
    """Test that synthesis activity is logged."""
    with patch.object(master_orchestrator, "intent_router") as mock_router:
        with patch.object(master_orchestrator, "logger") as mock_logger:
            mock_router.route_with_lens_auto_fetch.return_value = sample_routing_result
            mock_synthesis_engine.synthesize_unified_context.return_value = sample_unified_context
            
            master_orchestrator._stage_2_routing(sample_request)
            
            # Verify synthesis log
            log_calls = [call for call in mock_logger.log_operation_complete.call_args_list
                        if call[1]["ac_id"] == "AC-KNOWLEDGE-SYNTHESIS-001"]
            assert len(log_calls) >= 1
            assert log_calls[0][1]["operation"] == "STAGE_2_UNIFIED_SYNTHESIS"


def test_stage_2_routing_preserves_intent_router_result(
    master_orchestrator,
    mock_synthesis_engine,
    sample_request,
    sample_routing_result,
    sample_unified_context
):
    """Test that IntentRouter result is preserved."""
    with patch.object(master_orchestrator, "intent_router") as mock_router:
        mock_router.route_with_lens_auto_fetch.return_value = sample_routing_result
        mock_synthesis_engine.synthesize_unified_context.return_value = sample_unified_context
        
        result = master_orchestrator._stage_2_routing(sample_request)
        
        # Original fields preserved
        assert result["intent"] == "IMPLEMENT"
        assert result["target_orchestrator"] == "TDDOrchestrator"
        assert result["confidence_score"] == 0.9
        assert result["reasoning"] == "Implementation request detected"
        # Enhanced with synthesis
        assert "unified_intelligence" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
