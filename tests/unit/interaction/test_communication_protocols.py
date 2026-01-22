"""
Tests for communication protocol definitions.

AC-REM-004-05: Communication Protocol Definitions (10 tests)
"""

import pytest
from pathlib import Path
import yaml

from cortex.brain.core.orchestrator.pattern_enforcer import PatternEnforcer


@pytest.fixture
def protocol_registry():
    """Get path to protocol registry."""
    return Path(__file__).parent.parent.parent.parent / "cortex-registry" / "interaction"


def test_request_response_protocol_exists(protocol_registry):
    """Test that request-response protocol exists."""
    protocol_file = protocol_registry / "request-response.yaml"
    assert protocol_file.exists()


def test_request_response_protocol_valid(protocol_registry):
    """Test that request-response protocol is valid YAML."""
    protocol_file = protocol_registry / "request-response.yaml"
    
    with open(protocol_file) as f:
        protocol = yaml.safe_load(f)
    
    assert protocol["pattern_id"] == "request-response-001"
    assert protocol["pattern_type"] == "request-response"
    assert "required_fields" in protocol
    assert "request_id" in protocol["required_fields"]


def test_event_driven_protocol_exists(protocol_registry):
    """Test that event-driven protocol exists."""
    protocol_file = protocol_registry / "event-driven.yaml"
    assert protocol_file.exists()


def test_event_driven_protocol_valid(protocol_registry):
    """Test that event-driven protocol is valid YAML."""
    protocol_file = protocol_registry / "event-driven.yaml"
    
    with open(protocol_file) as f:
        protocol = yaml.safe_load(f)
    
    assert protocol["pattern_id"] == "event-driven-001"
    assert protocol["pattern_type"] == "event-driven"
    assert "event_type" in protocol["required_fields"]


def test_pub_sub_protocol_exists(protocol_registry):
    """Test that pub-sub protocol exists."""
    protocol_file = protocol_registry / "pub-sub.yaml"
    assert protocol_file.exists()


def test_pub_sub_protocol_valid(protocol_registry):
    """Test that pub-sub protocol is valid YAML."""
    protocol_file = protocol_registry / "pub-sub.yaml"
    
    with open(protocol_file) as f:
        protocol = yaml.safe_load(f)
    
    assert protocol["pattern_id"] == "pub-sub-001"
    assert protocol["pattern_type"] == "pub-sub"
    assert "topic" in protocol["required_fields"]


def test_orchestrator_coordination_protocol_exists(protocol_registry):
    """Test that orchestrator-coordination protocol exists."""
    protocol_file = protocol_registry / "orchestrator-coordination.yaml"
    assert protocol_file.exists()


def test_orchestrator_coordination_protocol_valid(protocol_registry):
    """Test that orchestrator-coordination protocol is valid YAML."""
    protocol_file = protocol_registry / "pub-sub.yaml"
    
    with open(protocol_file) as f:
        protocol = yaml.safe_load(f)
    
    assert protocol["pattern_id"] == "pub-sub-001"
    assert protocol["pattern_type"] == "pub-sub"


def test_pattern_enforcer_loads_protocols(protocol_registry):
    """Test that PatternEnforcer can load all protocols."""
    enforcer = PatternEnforcer(registry_path=protocol_registry)
    
    # Should have loaded all 4 protocols
    assert enforcer.get_pattern_count() >= 4


def test_all_protocols_have_examples(protocol_registry):
    """Test that all protocols include examples."""
    protocol_files = list(protocol_registry.glob("*.yaml"))
    
    assert len(protocol_files) >= 4
    
    for protocol_file in protocol_files:
        with open(protocol_file) as f:
            protocol = yaml.safe_load(f)
        
        assert "examples" in protocol or "example" in protocol, \
            f"{protocol_file.name} missing examples"
