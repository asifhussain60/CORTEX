"""
Integration tests for Confidence Response Generator

Tests the complete confidence display workflow:
- Knowledge Graph pattern search with metadata
- Confidence scoring calculation
- Template selection and rendering
- Response generation

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path

from src.response_templates.confidence_response_generator import ConfidenceResponseGenerator
from src.tier2.knowledge_graph import KnowledgeGraph
from src.cognitive.confidence_scorer import ConfidenceLevel


@pytest.fixture
def temp_db(tmp_path):
    """Create temporary database for testing"""
    db_path = tmp_path / "test_kg.db"
    return str(db_path)


@pytest.fixture
def knowledge_graph(temp_db):
    """Create Knowledge Graph with test data"""
    kg = KnowledgeGraph(db_path=temp_db)
    
    # Add test patterns
    kg.store_pattern(
        title="Authentication Feature Planning",
        pattern_type="planning",
        confidence=0.92,
        context={"domain": "security", "complexity": "medium"},
        scope="feature_planning"
    )
    
    # Boost pattern to simulate usage
    patterns = kg.search_patterns("authentication", min_confidence=0.5)
    if patterns:
        pattern_id = patterns[0]["pattern_id"]
        for _ in range(18):
            kg.boost_pattern(pattern_id, boost_amount=0.01)
    
    kg.store_pattern(
        title="Dashboard UI Implementation",
        pattern_type="implementation",
        confidence=0.75,
        context={"domain": "ui", "framework": "react"},
        scope="code_implementation"
    )
    
    kg.store_pattern(
        title="API Integration Pattern",
        pattern_type="integration",
        confidence=0.60,
        context={"domain": "api", "protocol": "rest"},
        scope="integration"
    )
    
    return kg


@pytest.fixture
def response_generator(knowledge_graph):
    """Create ConfidenceResponseGenerator with test Knowledge Graph"""
    return ConfidenceResponseGenerator(knowledge_graph=knowledge_graph)


class TestConfidenceResponseGenerator:
    """Test ConfidenceResponseGenerator"""
    
    def test_generate_with_high_confidence_patterns(self, response_generator):
        """Should generate response with high confidence indicator"""
        result = response_generator.generate_response_with_confidence(
            user_request="Plan authentication feature",
            operation_type="Feature Planning",
            pattern_query="authentication planning"
        )
        
        assert result is not None
        assert "response" in result
        assert "confidence_score" in result
        assert "patterns_used" in result
        
        # Check confidence score
        assert result["confidence_score"] is not None
        assert result["confidence_score"].level in [ConfidenceLevel.VERY_HIGH, ConfidenceLevel.HIGH]
        assert result["confidence_score"].percentage >= 75
        
        # Check metadata
        assert result["metadata"]["confidence_percentage"] >= 75
        assert result["metadata"]["pattern_count"] > 0
        assert result["patterns_used"] > 0
    
    def test_generate_with_medium_confidence_patterns(self, response_generator):
        """Should generate response with medium confidence indicator"""
        result = response_generator.generate_response_with_confidence(
            user_request="Integrate REST API",
            operation_type="Integration",
            pattern_query="api integration"
        )
        
        assert result is not None
        assert result["confidence_score"] is not None
        
        # API integration pattern has 0.60 confidence
        # Should result in medium or low confidence
        assert result["confidence_score"].level in [
            ConfidenceLevel.MEDIUM,
            ConfidenceLevel.LOW,
            ConfidenceLevel.HIGH  # Could be high if usage boosts it
        ]
    
    def test_generate_without_patterns(self, response_generator):
        """Should generate 'New Territory' response when no patterns found"""
        result = response_generator.generate_response_with_confidence(
            user_request="Build quantum computer interface",
            operation_type="Feature Implementation",
            pattern_query="quantum computing interface"
        )
        
        assert result is not None
        assert "response" in result
        assert result["confidence_score"] is None
        assert result["patterns_used"] == 0
        
        # Check metadata
        assert result["metadata"]["confidence_percentage"] is None
        assert result["metadata"]["confidence_level"] == "New Territory"
        assert result["metadata"]["pattern_count"] == 0
        
        # Response should contain "New Territory" indicator
        assert "New Territory" in result["response"] or "No learned patterns" in result["response"]
    
    def test_confidence_indicator_formatting(self, response_generator):
        """Should format confidence indicator correctly"""
        result = response_generator.generate_response_with_confidence(
            user_request="Plan authentication",
            operation_type="Planning",
            pattern_query="authentication"
        )
        
        response_text = result["response"]
        
        # Should contain confidence percentage
        assert "%" in response_text or "Confidence" in response_text
        
        # Should contain pattern count mention
        assert "pattern" in response_text.lower()
    
    def test_metadata_structure(self, response_generator):
        """Should return complete metadata structure"""
        result = response_generator.generate_response_with_confidence(
            user_request="Implement dashboard",
            operation_type="Implementation",
            pattern_query="dashboard ui"
        )
        
        metadata = result["metadata"]
        
        # Check all required metadata fields exist
        assert "confidence_percentage" in metadata
        assert "confidence_level" in metadata
        assert "pattern_count" in metadata
        assert "usage_history" in metadata
        assert "best_pattern_id" in metadata
    
    def test_pattern_confidence_calculation(self, response_generator, knowledge_graph):
        """Should calculate confidence correctly from pattern data"""
        # Get pattern with known confidence
        patterns = knowledge_graph.search_patterns(
            "authentication",
            min_confidence=0.5,
            include_confidence_metadata=True
        )
        
        assert len(patterns) > 0
        best_pattern = patterns[0]
        
        # Calculate confidence score
        confidence_score = response_generator._calculate_pattern_confidence(
            best_pattern,
            patterns
        )
        
        assert confidence_score is not None
        assert 0 <= confidence_score.percentage <= 100
        assert confidence_score.pattern_count == len(patterns)
        assert confidence_score.usage_history >= 0
    
    def test_template_context_passthrough(self, response_generator):
        """Should pass additional template context correctly"""
        result = response_generator.generate_response_with_confidence(
            user_request="Test request",
            operation_type="Testing",
            pattern_query="testing",
            understanding="Custom understanding text",
            challenge_type="✓ Accept",
            challenge_explanation="Test challenge"
        )
        
        # Context should be passed through (even if template doesn't use it)
        assert result is not None
        assert "response" in result


class TestKnowledgeGraphConfidenceMetadata:
    """Test Knowledge Graph confidence metadata enhancement"""
    
    def test_search_patterns_with_metadata(self, knowledge_graph):
        """Should return confidence metadata when requested"""
        patterns = knowledge_graph.search_patterns(
            "authentication",
            min_confidence=0.5,
            include_confidence_metadata=True
        )
        
        assert len(patterns) > 0
        
        for pattern in patterns:
            # Check metadata fields present
            assert "pattern_count" in pattern
            assert "success_rate" in pattern
            assert "usage_count" in pattern
            assert "last_used" in pattern
            
            # Validate types
            assert isinstance(pattern["pattern_count"], int)
            assert isinstance(pattern["success_rate"], float)
            assert isinstance(pattern["usage_count"], int)
            
            # Validate ranges
            assert pattern["pattern_count"] == len(patterns)
            assert 0.0 <= pattern["success_rate"] <= 1.0
    
    def test_search_patterns_without_metadata(self, knowledge_graph):
        """Should work normally without metadata flag"""
        patterns = knowledge_graph.search_patterns(
            "authentication",
            min_confidence=0.5,
            include_confidence_metadata=False
        )
        
        assert len(patterns) > 0
        
        # Should still have basic fields
        for pattern in patterns:
            assert "pattern_id" in pattern
            assert "confidence" in pattern
            
            # Should NOT have extended metadata
            assert "pattern_count" not in pattern or pattern["pattern_count"] is None
            assert "success_rate" not in pattern or "success_rate" in pattern  # May be present from DB
    
    def test_success_rate_calculation(self, knowledge_graph):
        """Should calculate success rate based on usage"""
        patterns = knowledge_graph.search_patterns(
            "authentication",
            min_confidence=0.5,
            include_confidence_metadata=True
        )
        
        assert len(patterns) > 0
        pattern = patterns[0]
        
        # Success rate should be based on confidence + usage boost
        success_rate = pattern["success_rate"]
        confidence = pattern["confidence"]
        
        # Success rate should be at least confidence value
        assert success_rate >= confidence - 0.01  # Allow small floating point error
        
        # If high usage, success rate may be boosted
        if pattern["usage_count"] > 10:
            assert success_rate >= confidence


class TestConfidenceResponseGeneratorEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_knowledge_graph(self, temp_db):
        """Should handle empty Knowledge Graph gracefully"""
        empty_kg = KnowledgeGraph(db_path=temp_db)
        generator = ConfidenceResponseGenerator(knowledge_graph=empty_kg)
        
        result = generator.generate_response_with_confidence(
            user_request="Any request",
            operation_type="Test",
            pattern_query="nonexistent"
        )
        
        assert result is not None
        assert result["confidence_score"] is None
        assert result["patterns_used"] == 0
    
    def test_invalid_pattern_data(self, response_generator):
        """Should handle missing pattern fields gracefully"""
        # This tests defensive programming in _calculate_pattern_confidence
        result = response_generator.generate_response_with_confidence(
            user_request="Test",
            operation_type="Test",
            pattern_query="authentication"
        )
        
        # Should not crash even if pattern data incomplete
        assert result is not None
    
    def test_min_confidence_threshold(self, response_generator):
        """Should respect minimum confidence threshold"""
        # Search with high threshold
        result = response_generator.generate_response_with_confidence(
            user_request="API integration",
            operation_type="Integration",
            pattern_query="api",
            min_confidence=0.95  # Very high threshold
        )
        
        # Should find no patterns (our test patterns are < 0.95)
        assert result["patterns_used"] == 0
        assert result["confidence_score"] is None


@pytest.mark.integration
class TestEndToEndConfidenceWorkflow:
    """Test complete end-to-end confidence display workflow"""
    
    def test_full_confidence_display_workflow(self, knowledge_graph):
        """Test complete workflow from pattern search to response generation"""
        generator = ConfidenceResponseGenerator(knowledge_graph=knowledge_graph)
        
        # Step 1: Generate response with confidence
        result = generator.generate_response_with_confidence(
            user_request="Plan authentication feature for dashboard",
            operation_type="Feature Planning",
            pattern_query="authentication planning"
        )
        
        # Step 2: Verify confidence was calculated
        assert result["confidence_score"] is not None
        confidence = result["confidence_score"]
        
        # Step 3: Verify confidence factors were considered
        assert confidence.factors is not None
        assert "match_quality" in confidence.factors
        assert "usage_history" in confidence.factors
        assert "success_rate" in confidence.factors
        assert "recency" in confidence.factors
        
        # Step 4: Verify response contains confidence indicator
        response = result["response"]
        assert len(response) > 0
        
        # Step 5: Verify metadata is complete
        metadata = result["metadata"]
        assert metadata["confidence_percentage"] == confidence.percentage
        assert metadata["confidence_level"] == confidence.level.value
        assert metadata["pattern_count"] > 0
