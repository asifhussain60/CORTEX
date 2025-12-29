"""
CORTEX 4.0 Brain Test Fixtures

Provides mock brain tier implementations for testing.

⚠️ IMPORTANT: These fixtures are for CORTEX INTERNAL TESTS ONLY.
"""

from unittest.mock import MagicMock
import pytest


@pytest.fixture
def mock_tier0():
    """Mock Tier 0 (Governance) for testing."""
    tier0 = MagicMock()
    tier0.check_rule.return_value = {"allowed": True, "rule": "TEST_RULE"}
    tier0.enforce_skull_rules.return_value = []
    tier0.get_all_rules.return_value = []
    return tier0


@pytest.fixture
def mock_tier1():
    """Mock Tier 1 (Working Memory) for testing."""
    tier1 = MagicMock()
    tier1.store_conversation.return_value = True
    tier1.get_conversation.return_value = None
    tier1.get_recent_conversations.return_value = []
    tier1.clear_old_conversations.return_value = 0
    return tier1


@pytest.fixture
def mock_tier2():
    """Mock Tier 2 (Knowledge Graph) for testing."""
    tier2 = MagicMock()
    tier2.store_pattern.return_value = True
    tier2.query_patterns.return_value = []
    tier2.get_pattern_by_id.return_value = None
    tier2.get_cross_repo_insights.return_value = []
    return tier2


@pytest.fixture
def mock_tier3():
    """Mock Tier 3 (Dev Context) for testing."""
    tier3 = MagicMock()
    tier3.get_git_metrics.return_value = {}
    tier3.store_git_metrics.return_value = True
    tier3.get_repository_context.return_value = {}
    return tier3
