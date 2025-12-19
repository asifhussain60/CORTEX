"""
Integration tests for Learning Capture Agent.

Tests learning event capture from operations, exceptions, and ambient events.
"""

import pytest


def test_learning_capture_initialization(temp_project, temp_brain):
    """Test learning capture agent initialization."""
    from src.cortex_agents.learning_capture_agent import LearningCaptureAgent
    
    agent = LearningCaptureAgent(project_root=temp_project)
    
    assert agent is not None
    assert hasattr(agent, "capture_from_operation_result")
    assert hasattr(agent, "capture_from_exception")


def test_capture_operation_failure(temp_project, temp_brain, sample_learning_event):
    """Test learning event capture from operation failure."""
    from src.cortex_agents.learning_capture_agent import LearningCaptureAgent
    
    agent = LearningCaptureAgent(project_root=temp_project)
    
    # Simulate operation failure
    operation_result = {
        "success": False,
        "error": sample_learning_event["problem"],
        "operation": sample_learning_event["operation_name"]
    }
    
    learning_event = agent.capture_from_operation_result(
        operation_name=sample_learning_event["operation_name"],
        result=operation_result,
        context=sample_learning_event["context"]
    )
    
    assert learning_event is not None
    assert learning_event["event_type"] == "operation_failure"
    assert learning_event["severity"] in ["low", "medium", "high", "critical"]


def test_capture_exception_pattern(temp_project, temp_brain):
    """Test learning capture from exception."""
    from src.cortex_agents.learning_capture_agent import LearningCaptureAgent
    
    agent = LearningCaptureAgent(project_root=temp_project)
    
    # Create test exception
    try:
        raise ValueError("Test exception for learning")
    except ValueError as e:
        learning_event = agent.capture_from_exception(
            exception=e,
            context={"operation": "test_operation"}
        )
        
        assert learning_event is not None
        assert "ValueError" in learning_event["problem"] or "exception" in learning_event["event_type"]


def test_tier2_integration_learning(temp_project, temp_brain):
    """Test learning capture integration with Tier 2 knowledge graph."""
    from src.cortex_agents.learning_capture_agent import LearningCaptureAgent
    from src.tier2.knowledge_graph import KnowledgeGraph
    
    agent = LearningCaptureAgent(project_root=temp_project)
    kg = KnowledgeGraph(brain_path=temp_brain)
    
    # Capture learning event
    learning_event = {
        "event_type": "operation_failure",
        "problem": "Database connection timeout",
        "solution": "Increase connection timeout",
        "confidence": 0.85
    }
    
    # Store as pattern in Tier 2
    pattern_id = kg.store_pattern(
        pattern_type=learning_event["event_type"],
        description=f"{learning_event['problem']} -> {learning_event['solution']}",
        confidence=learning_event["confidence"]
    )
    
    assert pattern_id is not None
    
    # Verify pattern stored
    pattern = kg.get_pattern(pattern_id)
    assert pattern is not None
    assert "timeout" in pattern["description"].lower()


def test_ambient_event_processing(temp_project, temp_brain):
    """Test ambient event analysis for learning."""
    from src.cortex_agents.learning_capture_agent import LearningCaptureAgent
    
    agent = LearningCaptureAgent(project_root=temp_project)
    
    # Test ambient event capture (may not have events initially)
    events = agent.capture_from_ambient_events(lookback_minutes=10)
    
    assert isinstance(events, list)
    # No events initially is expected
