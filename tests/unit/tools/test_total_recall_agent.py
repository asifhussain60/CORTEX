"""
Tests for Total Recall Agent
AC-IDs tested: AC-AGENT-001

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from cortex.tools.total_recall_agent import (
    TotalRecallAgent,
    FeatureScope,
    ComponentInfo,
    RecallResult,
    recall,
)


class TestTotalRecallAgent:
    """Tests for TotalRecallAgent."""
    
    @pytest.fixture
    def agent(self) -> TotalRecallAgent:
        """Create test instance."""
        return TotalRecallAgent()
    
    def test_agent_initialization(self, agent: TotalRecallAgent) -> None:
        """Test AC-ID: AC-AGENT-001-01 - Agent initializes correctly."""
        assert agent is not None
        assert agent.workspace_root is not None
    
    def test_recall_intent_router_component(self, agent: TotalRecallAgent) -> None:
        """Test AC-ID: AC-AGENT-001-02 - Recall intent router components."""
        result = agent.recall("classifier", scope=FeatureScope.INTENT_ROUTER)
        
        assert isinstance(result, RecallResult)
        assert len(result.matches) >= 1
        assert any("IntentClassifier" in m.name for m in result.matches)
    
    def test_recall_infrastructure_component(self, agent: TotalRecallAgent) -> None:
        """Test AC-ID: AC-AGENT-001-03 - Recall infrastructure components."""
        result = agent.recall("circuit", scope=FeatureScope.INFRASTRUCTURE)
        
        assert isinstance(result, RecallResult)
        assert len(result.matches) >= 1
        assert any("CircuitBreaker" in m.name for m in result.matches)
    
    def test_recall_all_scopes(self, agent: TotalRecallAgent) -> None:
        """Test AC-ID: AC-AGENT-001-04 - Recall across all scopes."""
        result = agent.recall("manager", scope=FeatureScope.ALL)
        
        assert isinstance(result, RecallResult)
        assert len(result.matches) >= 1
    
    def test_recall_with_usage_pattern(self, agent: TotalRecallAgent) -> None:
        """Test AC-ID: AC-AGENT-001-05 - Recall includes usage pattern."""
        result = agent.recall("CircuitBreaker", scope=FeatureScope.INFRASTRUCTURE, include_usage=True)
        
        assert len(result.matches) >= 1
        for match in result.matches:
            if match.name == "CircuitBreaker":
                assert match.usage_pattern is not None
                assert "import" in match.usage_pattern
    
    def test_recall_all_components_in_scope(self, agent: TotalRecallAgent) -> None:
        """Test AC-ID: AC-AGENT-001-06 - Recall all components in scope."""
        result = agent.recall_all(FeatureScope.INTENT_ROUTER)
        
        assert isinstance(result, RecallResult)
        assert len(result.matches) >= 10  # Intent router has 10 components
    
    def test_recall_usage_for_component(self, agent: TotalRecallAgent) -> None:
        """Test AC-ID: AC-AGENT-001-07 - Get usage pattern for specific component."""
        usage = agent.recall_usage("CircuitBreaker")
        
        assert usage is not None
        assert "import" in usage
        assert "CircuitBreaker" in usage
    
    def test_recall_no_matches(self, agent: TotalRecallAgent) -> None:
        """Test AC-ID: AC-AGENT-001-08 - Handle no matches gracefully."""
        result = agent.recall("nonexistent_component_xyz", scope=FeatureScope.ALL)
        
        assert isinstance(result, RecallResult)
        assert len(result.matches) == 0
    
    def test_recall_related_components(self, agent: TotalRecallAgent) -> None:
        """Test AC-ID: AC-AGENT-001-09 - Find related components."""
        result = agent.recall("circuit", scope=FeatureScope.INFRASTRUCTURE)
        
        assert isinstance(result, RecallResult)
        # Related components should be suggested
        assert isinstance(result.related_components, list)
    
    def test_component_info_structure(self, agent: TotalRecallAgent) -> None:
        """Test AC-ID: AC-AGENT-001-10 - ComponentInfo has required fields."""
        result = agent.recall("IntentClassifier", scope=FeatureScope.INTENT_ROUTER)
        
        assert len(result.matches) >= 1
        component = result.matches[0]
        
        assert hasattr(component, "name")
        assert hasattr(component, "entry_point")
        assert hasattr(component, "test_status")
        assert hasattr(component, "capabilities")
        assert isinstance(component.capabilities, list)


class TestRecallConvenienceFunction:
    """Tests for the recall() convenience function."""
    
    def test_recall_function_basic(self) -> None:
        """Test AC-ID: AC-AGENT-001-11 - Convenience function works."""
        result = recall("classifier", scope="intent_router")
        
        assert isinstance(result, RecallResult)
        assert len(result.matches) >= 1
    
    def test_recall_function_all_scope(self) -> None:
        """Test AC-ID: AC-AGENT-001-12 - Convenience function with all scope."""
        result = recall("manager", scope="all")
        
        assert isinstance(result, RecallResult)
        assert len(result.matches) >= 1
    
    def test_recall_function_with_usage(self) -> None:
        """Test AC-ID: AC-AGENT-001-13 - Convenience function includes usage."""
        result = recall("CircuitBreaker", scope="infrastructure", include_usage=True)
        
        assert len(result.matches) >= 1
        assert result.matches[0].usage_pattern is not None


class TestFeatureScope:
    """Tests for FeatureScope enum."""
    
    def test_all_scopes_defined(self) -> None:
        """Test AC-ID: AC-AGENT-001-14 - All required scopes exist."""
        expected_scopes = [
            "intent_router",
            "governance",
            "infrastructure",
            "orchestrators",
            "state",
            "intelligence",
            "mcp",
            "all",
        ]
        
        for scope in expected_scopes:
            assert FeatureScope(scope) is not None
