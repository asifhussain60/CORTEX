"""
Tests for InteractionOrchestrator integration with ConversationProtocol.

AC-CONV-001-04: InteractionOrchestrator Integration (15 tests)
"""

import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path
import tempfile
import yaml

from cortex.orchestrators.core.interaction_orchestrator import (
    InteractionOrchestrator,
    CommunicationPattern,
    PatternViolationError,
)
from cortex.brain.core.orchestrator.conversation_protocol import (
    ConversationProtocol,
    RoundContext,
)
from cortex.brain.core.result import Ok, Err


@pytest.fixture
def mock_orchestrator():
    """Create a mock orchestrator."""
    orch = Mock()
    orch.execute = Mock(return_value=Ok({"result": "success"}))
    return orch


@pytest.fixture
def conversation_protocol(mock_orchestrator):
    """Create a ConversationProtocol with mock orchestrator."""
    return ConversationProtocol(orchestrator=mock_orchestrator, max_turns=5)


@pytest.fixture
def temp_pattern_registry():
    """Create temporary pattern registry."""
    temp_dir = tempfile.mkdtemp()
    registry_path = Path(temp_dir) / "patterns"
    registry_path.mkdir()
    
    # Create a sample pattern
    pattern = {
        "pattern_id": "request-response-001",
        "name": "Basic Request-Response",
        "pattern_type": "request-response",
        "required_fields": ["user_input"],
        "optional_fields": ["context"],
        "validation_rules": {
            "min_length": 5
        }
    }
    
    with open(registry_path / "request-response.yaml", "w") as f:
        yaml.dump(pattern, f)
    
    yield registry_path
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir)


def test_interaction_orchestrator_creation(conversation_protocol, temp_pattern_registry):
    """Test creating an InteractionOrchestrator."""
    orch = InteractionOrchestrator(
        conversation_protocol=conversation_protocol,
        pattern_registry_path=temp_pattern_registry
    )
    
    assert orch.conversation_protocol == conversation_protocol
    assert len(orch.patterns) == 1
    assert "request-response-001" in orch.patterns


def test_load_patterns(temp_pattern_registry):
    """Test loading patterns from registry."""
    mock_conv = Mock()
    orch = InteractionOrchestrator(mock_conv, temp_pattern_registry)
    
    patterns = orch.list_available_patterns()
    assert "request-response-001" in patterns


def test_execute_turn_with_valid_pattern(conversation_protocol, temp_pattern_registry):
    """Test executing a turn with valid pattern."""
    orch = InteractionOrchestrator(conversation_protocol, temp_pattern_registry)
    
    round_context = RoundContext(
        round_number=1,
        user_input="Test request",
        previous_context={"user_input": "Test request"},
        orchestrator_name="TestOrch"
    )
    
    # Mock the execute_turn to return proper result
    conversation_protocol.execute_turn = Mock(
        return_value=Ok({"response": "Test response"})
    )
    
    result = orch.execute_turn_with_pattern(
        round_context,
        "request-response-001",
        validate_strict=True
    )
    
    assert result.is_ok()


def test_execute_turn_pattern_not_found(conversation_protocol, temp_pattern_registry):
    """Test executing with non-existent pattern."""
    orch = InteractionOrchestrator(conversation_protocol, temp_pattern_registry)
    
    round_context = RoundContext(
        round_number=1,
        user_input="Test",
        previous_context={},
        orchestrator_name="TestOrch"
    )
    
    result = orch.execute_turn_with_pattern(
        round_context,
        "nonexistent-pattern",
        validate_strict=True
    )
    
    assert not result.is_ok()
    assert "not found" in result.unwrap_err()


def test_validate_input_missing_required_field(conversation_protocol, temp_pattern_registry):
    """Test validation fails when required field is missing."""
    orch = InteractionOrchestrator(conversation_protocol, temp_pattern_registry)
    
    round_context = RoundContext(
        round_number=1,
        user_input="Test request",
        previous_context={},  # Missing user_input field
        orchestrator_name="TestOrch"
    )
    
    result = orch.execute_turn_with_pattern(
        round_context,
        "request-response-001",
        validate_strict=True
    )
    
    assert not result.is_ok()
    assert "Required field" in result.unwrap_err()


def test_validate_input_too_short(conversation_protocol, temp_pattern_registry):
    """Test validation fails when input is too short."""
    orch = InteractionOrchestrator(conversation_protocol, temp_pattern_registry)
    
    round_context = RoundContext(
        round_number=1,
        user_input="Hi",  # Too short (min: 5)
        previous_context={"user_input": "Hi"},
        orchestrator_name="TestOrch"
    )
    
    result = orch.execute_turn_with_pattern(
        round_context,
        "request-response-001",
        validate_strict=True
    )
    
    assert not result.is_ok()
    assert "too short" in result.unwrap_err()


def test_validate_output_request_response(conversation_protocol, temp_pattern_registry):
    """Test output validation for request-response pattern."""
    orch = InteractionOrchestrator(conversation_protocol, temp_pattern_registry)
    
    round_context = RoundContext(
        round_number=1,
        user_input="Valid request",
        previous_context={"user_input": "Valid request"},
        orchestrator_name="TestOrch"
    )
    
    # Mock output without response field
    conversation_protocol.execute_turn = Mock(
        return_value=Ok({"status": "ok"})  # Missing response/result
    )
    
    result = orch.execute_turn_with_pattern(
        round_context,
        "request-response-001",
        validate_strict=True
    )
    
    assert not result.is_ok()
    assert "response" in result.unwrap_err() or "result" in result.unwrap_err()


def test_non_strict_validation_logs_warning(conversation_protocol, temp_pattern_registry, capsys):
    """Test non-strict validation logs warnings instead of failing."""
    orch = InteractionOrchestrator(conversation_protocol, temp_pattern_registry)
    
    round_context = RoundContext(
        round_number=1,
        user_input="Valid request",
        previous_context={"user_input": "Valid request"},
        orchestrator_name="TestOrch"
    )
    
    conversation_protocol.execute_turn = Mock(
        return_value=Ok({"status": "ok"})  # Missing response field
    )
    
    result = orch.execute_turn_with_pattern(
        round_context,
        "request-response-001",
        validate_strict=False  # Non-strict
    )
    
    # Should succeed but log warning
    assert result.is_ok()
    captured = capsys.readouterr()
    assert "WARNING" in captured.out


def test_get_pattern(conversation_protocol, temp_pattern_registry):
    """Test retrieving a specific pattern."""
    orch = InteractionOrchestrator(conversation_protocol, temp_pattern_registry)
    
    pattern = orch.get_pattern("request-response-001")
    assert pattern is not None
    assert pattern.name == "Basic Request-Response"
    assert pattern.pattern_type == "request-response"


def test_get_nonexistent_pattern(conversation_protocol, temp_pattern_registry):
    """Test retrieving a pattern that doesn't exist."""
    orch = InteractionOrchestrator(conversation_protocol, temp_pattern_registry)
    
    pattern = orch.get_pattern("nonexistent")
    assert pattern is None


def test_list_available_patterns(conversation_protocol, temp_pattern_registry):
    """Test listing all available patterns."""
    orch = InteractionOrchestrator(conversation_protocol, temp_pattern_registry)
    
    patterns = orch.list_available_patterns()
    assert isinstance(patterns, list)
    assert "request-response-001" in patterns


def test_empty_pattern_registry(conversation_protocol):
    """Test behavior with empty pattern registry."""
    temp_dir = tempfile.mkdtemp()
    registry_path = Path(temp_dir) / "empty"
    registry_path.mkdir()
    
    orch = InteractionOrchestrator(conversation_protocol, registry_path)
    
    assert len(orch.patterns) == 0
    assert orch.list_available_patterns() == []


def test_pattern_loading_with_invalid_yaml(conversation_protocol, capsys):
    """Test that invalid YAML files are skipped with warning."""
    temp_dir = tempfile.mkdtemp()
    registry_path = Path(temp_dir) / "patterns"
    registry_path.mkdir()
    
    # Create invalid YAML
    with open(registry_path / "invalid.yaml", "w") as f:
        f.write("invalid: yaml: content:\n  - broken")
    
    orch = InteractionOrchestrator(conversation_protocol, registry_path)
    
    # Should handle gracefully
    captured = capsys.readouterr()
    assert "WARNING" in captured.out or "Failed to load" in captured.out


def test_full_round_trip_with_pattern(conversation_protocol, temp_pattern_registry):
    """Test full round-trip: input → protocol → orchestrator → output with pattern."""
    orch = InteractionOrchestrator(conversation_protocol, temp_pattern_registry)
    
    round_context = RoundContext(
        round_number=1,
        user_input="Execute test workflow",
        previous_context={"user_input": "Execute test workflow"},
        orchestrator_name="WorkflowOrchestrator"
    )
    
    conversation_protocol.execute_turn = Mock(
        return_value=Ok({
            "response": "Workflow executed successfully",
            "status": "complete"
        })
    )
    
    result = orch.execute_turn_with_pattern(
        round_context,
        "request-response-001",
        validate_strict=True
    )
    
    assert result.is_ok()
    output = result.unwrap()
    assert output["response"] == "Workflow executed successfully"
    assert output["status"] == "complete"
