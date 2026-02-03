"""
Educational Orchestrator Tests

Tests for truth-based educational interaction with progressive disclosure.

Phase 22 Component #3: EducationalOrchestrator Tests (20 tests)

Authority: AC-EDUCATIONAL-INTERACTION-001
Rule: CORE-008 (TDD)
"""

import pytest
from unittest.mock import MagicMock, patch

from cortex.orchestrators.education.educational_orchestrator import (
    EducationalOrchestrator,
    KnowledgeLevel,
    EducationalContext,
    EducationalResponse,
)


@pytest.fixture
def orchestrator():
    """Create EducationalOrchestrator instance."""
    return EducationalOrchestrator()


@pytest.fixture
def beginner_context():
    """Create beginner-level educational context."""
    return EducationalContext(
        query="What is MasterOrchestrator?",
        knowledge_level=KnowledgeLevel.BEGINNER,
        conversation_history=[]
    )


@pytest.fixture
def intermediate_context():
    """Create intermediate-level educational context."""
    return EducationalContext(
        query="How does MasterOrchestrator handle Stage 2 routing?",
        knowledge_level=KnowledgeLevel.INTERMEDIATE,
        conversation_history=["What is MasterOrchestrator?"]
    )


@pytest.fixture
def advanced_context():
    """Create advanced-level educational context."""
    return EducationalContext(
        query="What are the trade-offs of the Mediator pattern in MasterOrchestrator?",
        knowledge_level=KnowledgeLevel.ADVANCED,
        conversation_history=["What is MasterOrchestrator?", "How does routing work?"]
    )


class TestKnowledgeLevelDetection:
    """Test knowledge level detection from queries."""
    
    def test_detects_beginner_from_simple_query(self, orchestrator):
        """Test detection of beginner level from simple query."""
        query = "What is CORTEX?"
        level = orchestrator.detect_knowledge_level(query, [])
        assert level == KnowledgeLevel.BEGINNER
    
    def test_detects_beginner_from_basic_question(self, orchestrator):
        """Test detection of beginner level from basic question."""
        query = "How does CORTEX work?"
        level = orchestrator.detect_knowledge_level(query, [])
        assert level == KnowledgeLevel.BEGINNER
    
    def test_detects_intermediate_from_component_query(self, orchestrator):
        """Test detection of intermediate level from component-specific query."""
        query = "How does MasterOrchestrator handle routing?"
        level = orchestrator.detect_knowledge_level(query, [])
        assert level == KnowledgeLevel.INTERMEDIATE
    
    def test_detects_intermediate_from_integration_query(self, orchestrator):
        """Test detection of intermediate level from integration query."""
        query = "How does wiring.yaml integrate with orchestrators?"
        level = orchestrator.detect_knowledge_level(query, [])
        assert level == KnowledgeLevel.INTERMEDIATE
    
    def test_detects_advanced_from_architecture_query(self, orchestrator):
        """Test detection of advanced level from architecture query."""
        query = "What are the trade-offs of the Mediator pattern?"
        level = orchestrator.detect_knowledge_level(query, [])
        assert level == KnowledgeLevel.ADVANCED
    
    def test_detects_advanced_from_design_decision_query(self, orchestrator):
        """Test detection of advanced level from design decision query."""
        query = "Why not use event sourcing instead?"
        level = orchestrator.detect_knowledge_level(query, [])
        assert level == KnowledgeLevel.ADVANCED
    
    def test_detects_advanced_from_long_history(self, orchestrator):
        """Test detection of advanced level from conversation history length."""
        query = "Tell me more"
        history = ["query" + str(i) for i in range(12)]
        level = orchestrator.detect_knowledge_level(query, history)
        assert level == KnowledgeLevel.ADVANCED


class TestResponseGeneration:
    """Test educational response generation."""
    
    def test_generates_response_for_beginner(self, orchestrator, beginner_context):
        """Test generation of beginner-level response."""
        response = orchestrator.generate_response(beginner_context)
        
        assert isinstance(response, EducationalResponse)
        assert response.knowledge_level == KnowledgeLevel.BEGINNER
        assert len(response.next_steps) > 0
        assert response.title
        assert response.explanation
    
    def test_generates_response_for_intermediate(self, orchestrator, intermediate_context):
        """Test generation of intermediate-level response."""
        response = orchestrator.generate_response(intermediate_context)
        
        assert isinstance(response, EducationalResponse)
        assert response.knowledge_level == KnowledgeLevel.INTERMEDIATE
        assert len(response.next_steps) > 0
    
    def test_generates_response_for_advanced(self, orchestrator, advanced_context):
        """Test generation of advanced-level response."""
        response = orchestrator.generate_response(advanced_context)
        
        assert isinstance(response, EducationalResponse)
        assert response.knowledge_level == KnowledgeLevel.ADVANCED
        assert len(response.next_steps) > 0
    
    def test_includes_evidence_in_response(self, orchestrator, beginner_context):
        """Test that response includes evidence."""
        response = orchestrator.generate_response(beginner_context)
        
        assert isinstance(response.evidence, list)
        assert len(response.evidence) > 0
    
    def test_includes_implementation_reality(self, orchestrator, beginner_context):
        """Test that response includes implementation reality."""
        response = orchestrator.generate_response(beginner_context)
        
        assert response.implementation_reality
        assert isinstance(response.implementation_reality, str)


class TestNextStepGeneration:
    """Test intelligent next-step generation."""
    
    def test_generates_3_to_5_options(self, orchestrator, beginner_context):
        """Test that 3-5 next-step options are generated."""
        response = orchestrator.generate_response(beginner_context)
        
        assert len(response.next_steps) >= 3
        assert len(response.next_steps) <= 5
    
    def test_each_option_has_title_and_description(self, orchestrator, beginner_context):
        """Test that each option has title and description."""
        response = orchestrator.generate_response(beginner_context)
        
        for option in response.next_steps:
            assert "title" in option
            assert "description" in option
            assert option["title"]
            assert option["description"]
    
    def test_first_option_is_deeper_dive(self, orchestrator, beginner_context):
        """Test that first option is always a deeper dive."""
        response = orchestrator.generate_response(beginner_context)
        
        first_option = response.next_steps[0]
        assert "Deep Dive" in first_option["title"] or "Implementation" in first_option["title"]
    
    def test_includes_practical_example_option(self, orchestrator, beginner_context):
        """Test that practical example option is included."""
        response = orchestrator.generate_response(beginner_context)
        
        titles = [opt["title"] for opt in response.next_steps]
        assert any("Action" in title or "Example" in title for title in titles)
    
    def test_advanced_gets_extension_points_option(self, orchestrator, advanced_context):
        """Test that advanced users get extension points option."""
        response = orchestrator.generate_response(advanced_context)
        
        titles = [opt["title"] for opt in response.next_steps]
        assert any("Extension" in title or "extend" in title.lower() for title in titles)


class TestTopicExtraction:
    """Test topic extraction from queries."""
    
    def test_extracts_master_orchestrator(self, orchestrator):
        """Test extraction of MasterOrchestrator topic."""
        topic = orchestrator._extract_topic("What is the MasterOrchestrator?")
        assert "MasterOrchestrator" in topic
    
    def test_extracts_lens_protocol(self, orchestrator):
        """Test extraction of LENS Protocol topic."""
        topic = orchestrator._extract_topic("How does LENS work?")
        assert "LENS" in topic
    
    def test_extracts_challenge_engine(self, orchestrator):
        """Test extraction of ChallengeEngine topic."""
        topic = orchestrator._extract_topic("Tell me about the ChallengeEngine")
        assert "Challenge" in topic
    
    def test_defaults_to_cortex_architecture(self, orchestrator):
        """Test default topic when no specific match."""
        topic = orchestrator._extract_topic("Tell me something random")
        assert "CORTEX" in topic or "Architecture" in topic


class TestExecuteInterface:
    """Test IOrchestrator execute interface."""
    
    def test_execute_with_query_parameter(self, orchestrator):
        """Test execute with query parameter."""
        result = orchestrator.execute({"query": "What is CORTEX?"})
        
        assert result.is_ok()
        assert result.value  # JSON response
    
    def test_execute_without_query_fails(self, orchestrator):
        """Test execute without query parameter fails."""
        result = orchestrator.execute({})
        
        assert result.is_err()
        assert "Query parameter required" in result.error
    
    def test_execute_returns_json(self, orchestrator):
        """Test execute returns valid JSON."""
        result = orchestrator.execute({"query": "What is CORTEX?"})
        
        assert result.is_ok()
        import json
        parsed = json.loads(result.value)
        assert "title" in parsed
        assert "explanation" in parsed
        assert "next_steps" in parsed
    
    def test_get_name_returns_educational_orchestrator(self, orchestrator):
        """Test get_name returns correct name."""
        assert orchestrator.get_name() == "EducationalOrchestrator"
    
    def test_get_mode_returns_educational(self, orchestrator):
        """Test get_mode returns EDUCATIONAL mode."""
        from cortex.brain.core.interfaces.i_orchestrator import OperationMode
        assert orchestrator.get_mode() == OperationMode.EDUCATIONAL


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
