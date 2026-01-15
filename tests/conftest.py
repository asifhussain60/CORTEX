"""
Pytest Configuration

Shared fixtures and configuration for all tests.

Integrates:
- Test audit logging (governance audit trail generation)
- Common fixtures for temp dirs, mock configs, sample files
- Orchestrator registry cleanup

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import audit logger to ensure it's loaded
from src.testing.test_audit_logger import TestAuditLogger


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_project_root(temp_dir, monkeypatch):
    """
    Mock the project root for isolated tests.
    
    Sets CORTEX_ROOT env var and resets path resolver cache.
    """
    from src.core import path_resolver
    
    # Set environment variable
    monkeypatch.setenv("CORTEX_ROOT", str(temp_dir))
    
    # Reset cached root
    path_resolver.reset_project_root()
    
    yield temp_dir
    
    # Reset after test
    path_resolver.reset_project_root()


@pytest.fixture
def sample_yaml_file(temp_dir):
    """Create a sample YAML file for testing."""
    yaml_content = """
name: test
version: "1.0"
settings:
  debug: true
  level: info
items:
  - one
  - two
  - three
"""
    yaml_path = temp_dir / "test.yaml"
    yaml_path.write_text(yaml_content)
    return yaml_path


@pytest.fixture
def sample_json_file(temp_dir):
    """Create a sample JSON file for testing."""
    import json
    
    data = {
        "name": "test",
        "version": "1.0",
        "settings": {"debug": True}
    }
    
    json_path = temp_dir / "test.json"
    json_path.write_text(json.dumps(data, indent=2))
    return json_path


@pytest.fixture
def clean_registry():
    """Provide a clean orchestrator registry."""
    from src.mcp.registry import OrchestratorRegistry
    
    registry = OrchestratorRegistry()
    registry.clear()
    
    yield registry
    
    # Clean up after test
    OrchestratorRegistry.reset()


@pytest.fixture
def audit_logger(request):
    """
    Provide access to the test audit logger instance.
    
    Allows tests to query audit logging status or manually add entries if needed.
    """
    # Get the audit logger instance from the plugin manager
    plugin = request.config.pluginmanager.get_plugin("TestAuditLogger")
    if plugin and isinstance(plugin, TestAuditLogger):
        return plugin
    return None
