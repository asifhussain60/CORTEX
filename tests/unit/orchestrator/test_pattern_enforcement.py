"""
Tests for pattern enforcement.

AC-CONV-001-05: Communication Pattern Enforcement (12 tests)
"""

import pytest
from pathlib import Path
import tempfile
import yaml

from cortex.brain.core.orchestrator.pattern_enforcer import PatternEnforcer


@pytest.fixture
def temp_registry():
    """Create temporary pattern registry."""
    temp_dir = tempfile.mkdtemp()
    registry_path = Path(temp_dir)
    
    # Create patterns
    patterns = [
        {
            "pattern_id": "req-resp-001",
            "name": "Request Response",
            "pattern_type": "request-response",
            "required_fields": ["user_id", "action"]
        },
        {
            "pattern_id": "event-001",
            "name": "Event Driven",
            "pattern_type": "event-driven",
            "required_fields": ["event_source"]
        }
    ]
    
    for pattern in patterns:
        with open(registry_path / f"{pattern['pattern_id']}.yaml", "w") as f:
            yaml.dump(pattern, f)
    
    yield registry_path
    
    import shutil
    shutil.rmtree(temp_dir)


def test_load_patterns(temp_registry):
    """Test loading patterns from registry."""
    enforcer = PatternEnforcer(registry_path=temp_registry)
    assert enforcer.get_pattern_count() == 2


def test_validate_valid_request(temp_registry):
    """Test validating a valid request."""
    enforcer = PatternEnforcer(registry_path=temp_registry)
    
    request = {"user_id": "123", "action": "create"}
    result = enforcer.validate_request("req-resp-001", request)
    
    assert result.is_ok()


def test_validate_request_missing_field(temp_registry):
    """Test validation fails with missing required field."""
    enforcer = PatternEnforcer(registry_path=temp_registry)
    
    request = {"user_id": "123"}  # Missing 'action'
    result = enforcer.validate_request("req-resp-001", request)
    
    assert not result.is_ok()
    assert "action" in result.unwrap_err()


def test_validate_request_pattern_not_found(temp_registry):
    """Test validation with non-existent pattern."""
    enforcer = PatternEnforcer(registry_path=temp_registry)
    
    result = enforcer.validate_request("nonexistent", {"data": "test"})
    assert not result.is_ok()
    assert "not found" in result.unwrap_err()


def test_validate_request_response_pattern(temp_registry):
    """Test validating response for request-response pattern."""
    enforcer = PatternEnforcer(registry_path=temp_registry)
    
    # Valid response
    response = {"response": "Created successfully"}
    result = enforcer.validate_response("req-resp-001", response)
    assert result.is_ok()
    
    # Valid with 'result' instead
    response2 = {"result": {"status": "ok"}}
    result2 = enforcer.validate_response("req-resp-001", response2)
    assert result2.is_ok()


def test_validate_request_response_missing_fields(temp_registry):
    """Test request-response validation fails without response/result."""
    enforcer = PatternEnforcer(registry_path=temp_registry)
    
    response = {"status": "ok"}  # Missing response/result
    result = enforcer.validate_response("req-resp-001", response)
    
    assert not result.is_ok()
    assert "response" in result.unwrap_err() or "result" in result.unwrap_err()


def test_validate_event_driven_pattern(temp_registry):
    """Test validating response for event-driven pattern."""
    enforcer = PatternEnforcer(registry_path=temp_registry)
    
    # Valid event
    response = {"event_type": "user.created", "data": {}}
    result = enforcer.validate_response("event-001", response)
    assert result.is_ok()


def test_validate_event_driven_missing_event_type(temp_registry):
    """Test event-driven validation fails without event_type."""
    enforcer = PatternEnforcer(registry_path=temp_registry)
    
    response = {"data": {"user": "123"}}  # Missing event_type
    result = enforcer.validate_response("event-001", response)
    
    assert not result.is_ok()
    assert "event_type" in result.unwrap_err()


def test_log_violations(temp_registry):
    """Test that violations are logged."""
    enforcer = PatternEnforcer(registry_path=temp_registry)
    
    # Trigger a violation
    request = {"user_id": "123"}  # Missing 'action'
    enforcer.validate_request("req-resp-001", request)
    
    violations = enforcer.get_violations()
    assert len(violations) == 1
    assert violations[0]["pattern_id"] == "req-resp-001"
    assert "action" in violations[0]["violation"]


def test_multiple_violations(temp_registry):
    """Test logging multiple violations."""
    enforcer = PatternEnforcer(registry_path=temp_registry)
    
    # Trigger multiple violations
    enforcer.validate_request("req-resp-001", {})  # Missing both fields
    enforcer.validate_response("event-001", {})  # Missing event_type
    
    violations = enforcer.get_violations()
    assert len(violations) == 2


def test_clear_violations(temp_registry):
    """Test clearing violation log."""
    enforcer = PatternEnforcer(registry_path=temp_registry)
    
    enforcer.validate_request("req-resp-001", {})
    assert len(enforcer.get_violations()) >= 1
    
    enforcer.clear_violations()
    assert len(enforcer.get_violations()) == 0


def test_empty_registry():
    """Test behavior with empty registry."""
    temp_dir = tempfile.mkdtemp()
    registry_path = Path(temp_dir)
    
    enforcer = PatternEnforcer(registry_path=registry_path)
    assert enforcer.get_pattern_count() == 0
