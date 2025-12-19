"""
Integration tests for Tier 2 (Knowledge Graph).

Tests pattern storage, learning, and cross-tier integration.
"""

import pytest


def test_tier2_initialization(temp_brain):
    """Test Tier 2 knowledge graph initialization."""
    from src.tier2.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph(brain_path=temp_brain)
    
    assert kg is not None
    assert kg.is_initialized()


def test_tier2_pattern_storage(temp_brain):
    """Test pattern storage and retrieval."""
    from src.tier2.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph(brain_path=temp_brain)
    
    # Store pattern
    pattern_id = kg.store_pattern(
        pattern_type="integration_test_pattern",
        description="Common pattern in integration testing",
        confidence=0.85
    )
    
    assert pattern_id is not None
    
    # Retrieve pattern
    pattern = kg.get_pattern(pattern_id)
    
    assert pattern is not None
    assert pattern["pattern_type"] == "integration_test_pattern"
    assert pattern["confidence"] == 0.85


def test_tier2_pattern_learning(temp_brain):
    """Test pattern learning and confidence updates."""
    from src.tier2.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph(brain_path=temp_brain)
    
    # Store pattern
    pattern_id = kg.store_pattern(
        pattern_type="learned_pattern",
        description="Pattern that improves with usage",
        confidence=0.5
    )
    
    # Simulate pattern usage and learning
    for _ in range(5):
        kg.increment_pattern_usage(pattern_id)
    
    # Update confidence based on usage
    kg.update_pattern_confidence(pattern_id, 0.9)
    
    # Verify learning
    pattern = kg.get_pattern(pattern_id)
    assert pattern["confidence"] == 0.9
    assert pattern["usage_count"] >= 5


def test_tier2_semantic_search(temp_brain):
    """Test semantic search using FTS5."""
    from src.tier2.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph(brain_path=temp_brain)
    
    # Store multiple patterns
    kg.store_pattern(
        pattern_type="testing_pattern",
        description="Unit testing best practices",
        confidence=0.8
    )
    
    kg.store_pattern(
        pattern_type="testing_pattern",
        description="Integration testing strategies",
        confidence=0.85
    )
    
    # Search patterns
    results = kg.search_patterns("integration testing")
    
    assert len(results) > 0
    assert any("integration" in r["description"].lower() for r in results)


def test_tier2_tier3_integration(temp_brain):
    """Test Tier 2 integration with Tier 3 for context-aware learning."""
    from src.tier2.knowledge_graph import KnowledgeGraph
    from src.tier3.development_context import DevelopmentContext
    
    kg = KnowledgeGraph(brain_path=temp_brain)
    dev_context = DevelopmentContext(brain_path=temp_brain)
    
    # Store pattern about high complexity
    pattern_id = kg.store_pattern(
        pattern_type="complexity_pattern",
        description="High complexity indicates refactoring need",
        confidence=0.85
    )
    
    # Store related metrics in Tier 3
    dev_context.store_metric(
        file_path="src/complex_file.py",
        metric_type="complexity",
        value=50.0
    )
    
    # Verify cross-tier data exists
    pattern = kg.get_pattern(pattern_id)
    metrics = dev_context.get_metrics("src/complex_file.py")
    
    assert pattern is not None
    assert len(metrics) > 0
