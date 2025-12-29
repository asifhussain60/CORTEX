"""
Pytest Configuration for All Plugin Tests

Provides shared fixtures and configuration for all CORTEX plugin tests.
Fixtures defined here are available to all plugin test modules.

Copyright © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add src to path (for all plugin tests)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


# ============================================
# Shared Mock Agent Fixtures
# ============================================

@pytest.fixture
def mock_agent_request():
    """Create mock AgentRequest object for plugin testing."""
    request = Mock()
    request.intent = "test_intent"
    request.command = "/test"
    request.args = []
    request.kwargs = {}
    request.user_message = "Test message"
    return request


@pytest.fixture
def mock_agent_context(tmp_path):
    """Create mock agent execution context."""
    context = Mock()
    context.project_root = tmp_path
    context.brain_path = tmp_path / "cortex-brain"
    context.current_file = None
    
    # Create brain directory structure
    context.brain_path.mkdir(parents=True, exist_ok=True)
    
    return context


# ============================================
# Shared Project Structure Fixtures
# ============================================

@pytest.fixture
def mock_project_structure(tmp_path):
    """Create standard CORTEX project structure for testing."""
    project_root = tmp_path / "test_project"
    project_root.mkdir(parents=True, exist_ok=True)
    
    # Create standard directories
    (project_root / "src").mkdir(parents=True, exist_ok=True)
    (project_root / "src" / "plugins").mkdir(parents=True, exist_ok=True)
    (project_root / "tests").mkdir(parents=True, exist_ok=True)
    (project_root / "cortex-brain").mkdir(parents=True, exist_ok=True)
    
    # Create standard test categories
    test_categories = [
        "tier0", "tier1", "tier2", "tier3",
        "plugins", "integration", "edge_cases",
        "unit", "entry_point"
    ]
    
    for category in test_categories:
        (project_root / "tests" / category).mkdir(parents=True, exist_ok=True)
    
    return project_root


# ============================================
# Pytest Configuration
# ============================================

def pytest_configure(config):
    """Configure pytest with custom markers for plugin tests."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "plugin: marks tests as plugin-specific tests"
    )
