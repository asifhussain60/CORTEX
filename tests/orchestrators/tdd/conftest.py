"""
Pytest Configuration for TDD Orchestrator v4.0 Tests

Provides shared fixtures for TDD orchestrator tests.
"""

import pytest
from unittest.mock import Mock
from pathlib import Path


@pytest.fixture
def brain_connector():
    """Create mock brain connector."""
    brain = Mock()
    brain.get_patterns = Mock(return_value=[])
    brain.learn_pattern = Mock(return_value=True)
    return brain


@pytest.fixture
def knowledge_graph():
    """Create mock knowledge graph."""
    kg = Mock()
    # Return empty list for strategy weights query
    kg.search = Mock(return_value=[])
    kg.search_patterns = Mock(return_value=[])  # AgentLearningEngine uses this
    kg.add_node = Mock(return_value=True)
    kg.add_relationship = Mock(return_value=True)
    kg.get_pattern_data = Mock(return_value=None)
    kg.save_pattern = Mock(return_value=True)
    return kg


@pytest.fixture
def mcp_gateway():
    """Create mock MCP gateway."""
    mcp = Mock()
    mcp.call = Mock(return_value={"status": "success"})
    return mcp


@pytest.fixture
def config():
    """Create test configuration."""
    return {
        "workspace_root": str(Path("/mock/workspace")),
        "tdd": {
            "test_framework": "pytest",
            "coverage_threshold": 0.90
        }
    }
