"""
Integration tests for Bug-Driven Learning.

Tests bug pattern extraction, learning, and test generation.
"""

import pytest


def test_bug_driven_learner_initialization(temp_project, temp_brain):
    """Test bug-driven learner initialization."""
    from src.cortex_agents.test_generator.bug_driven_learner import BugDrivenLearner
    
    learner = BugDrivenLearner()
    
    assert learner is not None
    assert hasattr(learner, "capture_bug_event")
    assert hasattr(learner, "extract_pattern")


def test_bug_pattern_extraction(temp_project, temp_brain):
    """Test bug pattern extraction from bug event."""
    from src.cortex_agents.test_generator.bug_driven_learner import BugDrivenLearner
    from src.cortex_agents.test_generator.bug_driven_learner import BugCategory, BugSeverity
    
    learner = BugDrivenLearner()
    
    # Capture bug event
    bug = learner.capture_bug_event(
        test_name="test_user_authentication",
        bug_category=BugCategory.SECURITY,
        bug_severity=BugSeverity.CRITICAL,
        description="JWT token not expiring",
        expected_behavior="Token should expire after 24 hours"
    )
    
    assert bug is not None
    
    # Extract pattern
    pattern = learner.extract_pattern(bug)
    
    assert pattern is not None
    assert pattern["category"] == "security" or pattern["bug_category"] == BugCategory.SECURITY
    assert pattern["confidence"] > 0.5


def test_bug_pattern_storage_tier2(temp_project, temp_brain):
    """Test bug pattern storage in Tier 2."""
    from src.cortex_agents.test_generator.bug_driven_learner import BugDrivenLearner, BugCategory, BugSeverity
    from src.tier2.knowledge_graph import KnowledgeGraph
    
    learner = BugDrivenLearner()
    kg = KnowledgeGraph(brain_path=temp_brain)
    
    # Capture and extract bug pattern
    bug = learner.capture_bug_event(
        test_name="test_data_validation",
        bug_category=BugCategory.LOGIC_ERROR,
        bug_severity=BugSeverity.HIGH,
        description="Off-by-one error in pagination",
        expected_behavior="Last page should show remaining items"
    )
    
    pattern = learner.extract_pattern(bug)
    
    # Store in Tier 2
    pattern_id = kg.store_pattern(
        pattern_type="bug_pattern",
        description=pattern.get("description", "Bug pattern"),
        confidence=pattern.get("confidence", 0.7)
    )
    
    assert pattern_id is not None


def test_similar_bug_detection(temp_project, temp_brain):
    """Test detection of similar bugs from learned patterns."""
    from src.cortex_agents.test_generator.bug_driven_learner import BugDrivenLearner, BugCategory, BugSeverity
    from src.tier2.knowledge_graph import KnowledgeGraph
    
    learner = BugDrivenLearner()
    kg = KnowledgeGraph(brain_path=temp_brain)
    
    # Store initial bug pattern
    bug1 = learner.capture_bug_event(
        test_name="test_sql_injection_1",
        bug_category=BugCategory.SECURITY,
        bug_severity=BugSeverity.CRITICAL,
        description="SQL injection in login form",
        expected_behavior="Input should be sanitized"
    )
    
    pattern1 = learner.extract_pattern(bug1)
    
    kg.store_pattern(
        pattern_type="bug_pattern_security",
        description=pattern1.get("description", "Security bug"),
        confidence=0.9
    )
    
    # Search for similar patterns
    similar = kg.search_patterns("SQL injection")
    
    assert len(similar) > 0
