"""Tests for TokenOptimizationAgent health checks.

Authority: AC-AUDIT-TOKEN-OPT-001
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from cortex.orchestrators.health.agents.token_optimization_agent import (
    TokenOptimizationAgent,
)
from cortex.orchestrators.health.agents.base_agent import (
    HealthIssueSeverity,
    HealthIssueCategory,
)


class TestTokenOptimizationAgent:
    """Test suite for TokenOptimizationAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create TokenOptimizationAgent instance."""
        return TokenOptimizationAgent()
    
    @pytest.fixture
    def workspace_root(self, tmp_path):
        """Create temporary workspace root."""
        return tmp_path
    
    # =========================================================================
    # Agent Initialization Tests
    # =========================================================================
    
    def test_agent_initialization(self, agent):
        """Test agent initializes with correct name and description."""
        assert agent.name == "TokenOptimizationAgent"
        assert "token optimization" in agent.description.lower()
        assert agent.is_enabled()
    
    # =========================================================================
    # Gateway Existence Tests
    # =========================================================================
    
    def test_gateway_exists_no_issues(self, agent, workspace_root):
        """GOLDEN PATH: Gateway exists, no issues reported."""
        with patch('cortex.orchestrators.health.agents.token_optimization_agent.get_gateway') as mock_get_gateway:
            mock_gateway = Mock()
            mock_gateway.token_budget = 20000
            mock_gateway.enable_cache = True
            mock_gateway._session_tokens = {}
            mock_get_gateway.return_value = mock_gateway
            
            result = agent.check(workspace_root)
            
            assert result.agent_name == "TokenOptimizationAgent"
            assert len(result.issues) == 0
            assert result.metadata["gateway_operational"] is True
    
    def test_gateway_missing_critical_issue(self, agent, workspace_root):
        """Test gateway missing raises CRITICAL issue."""
        with patch('cortex.orchestrators.health.agents.token_optimization_agent.get_gateway') as mock_get_gateway:
            mock_get_gateway.return_value = None
            
            result = agent.check(workspace_root)
            
            assert len(result.issues) == 1
            issue = result.issues[0]
            assert issue.severity == HealthIssueSeverity.CRITICAL
            assert "not initialized" in issue.description
    
    def test_gateway_import_error_critical_issue(self, agent, workspace_root):
        """Test gateway import error raises CRITICAL issue."""
        with patch('cortex.orchestrators.health.agents.token_optimization_agent.get_gateway') as mock_get_gateway:
            mock_get_gateway.side_effect = ImportError("Module not found")
            
            result = agent.check(workspace_root)
            
            assert len(result.issues) == 1
            issue = result.issues[0]
            assert issue.severity == HealthIssueSeverity.CRITICAL
            assert "Cannot import" in issue.description
            assert "Module not found" in issue.metadata["error"]
    
    # =========================================================================
    # Token Budget Tests
    # =========================================================================
    
    def test_token_budget_correct_no_issue(self, agent, workspace_root):
        """GOLDEN PATH: Token budget is 20000, no issue."""
        with patch('cortex.orchestrators.health.agents.token_optimization_agent.get_gateway') as mock_get_gateway:
            mock_gateway = Mock()
            mock_gateway.token_budget = 20000
            mock_gateway.enable_cache = True
            mock_gateway._session_tokens = {}
            mock_get_gateway.return_value = mock_gateway
            
            result = agent.check(workspace_root)
            
            budget_issues = [i for i in result.issues if "budget" in i.description.lower()]
            assert len(budget_issues) == 0
    
    def test_token_budget_misconfigured_medium_issue(self, agent, workspace_root):
        """Test misconfigured token budget raises MEDIUM issue."""
        with patch('cortex.orchestrators.health.agents.token_optimization_agent.get_gateway') as mock_get_gateway:
            mock_gateway = Mock()
            mock_gateway.token_budget = 10000  # Wrong value
            mock_gateway.enable_cache = True
            mock_gateway._session_tokens = {}
            mock_get_gateway.return_value = mock_gateway
            
            result = agent.check(workspace_root)
            
            budget_issues = [i for i in result.issues if "misconfigured" in i.description]
            assert len(budget_issues) == 1
            issue = budget_issues[0]
            assert issue.severity == HealthIssueSeverity.MEDIUM
            assert issue.metadata["current_budget"] == 10000
            assert issue.metadata["expected_budget"] == 20000
    
    # =========================================================================
    # Cache Tests
    # =========================================================================
    
    def test_cache_enabled_no_issue(self, agent, workspace_root):
        """GOLDEN PATH: Cache enabled, no issue."""
        with patch('cortex.orchestrators.health.agents.token_optimization_agent.get_gateway') as mock_get_gateway:
            mock_gateway = Mock()
            mock_gateway.token_budget = 20000
            mock_gateway.enable_cache = True
            mock_gateway._session_tokens = {}
            mock_get_gateway.return_value = mock_gateway
            
            result = agent.check(workspace_root)
            
            cache_issues = [i for i in result.issues if "cache" in i.description.lower()]
            assert len(cache_issues) == 0
    
    def test_cache_disabled_medium_issue(self, agent, workspace_root):
        """Test cache disabled raises MEDIUM issue."""
        with patch('cortex.orchestrators.health.agents.token_optimization_agent.get_gateway') as mock_get_gateway:
            mock_gateway = Mock()
            mock_gateway.token_budget = 20000
            mock_gateway.enable_cache = False
            mock_gateway._session_tokens = {}
            mock_get_gateway.return_value = mock_gateway
            
            result = agent.check(workspace_root)
            
            cache_issues = [i for i in result.issues if "cache disabled" in i.description.lower()]
            assert len(cache_issues) == 1
            issue = cache_issues[0]
            assert issue.severity == HealthIssueSeverity.MEDIUM
    
    # =========================================================================
    # Session Tracking Tests
    # =========================================================================
    
    def test_session_tracking_active_no_issue(self, agent, workspace_root):
        """GOLDEN PATH: Session tracking active, no issue."""
        with patch('cortex.orchestrators.health.agents.token_optimization_agent.get_gateway') as mock_get_gateway:
            mock_gateway = Mock()
            mock_gateway.token_budget = 20000
            mock_gateway.enable_cache = True
            mock_gateway._session_tokens = {}
            mock_get_gateway.return_value = mock_gateway
            
            result = agent.check(workspace_root)
            
            session_issues = [i for i in result.issues if "session" in i.description.lower()]
            assert len(session_issues) == 0
    
    def test_session_tracking_missing_high_issue(self, agent, workspace_root):
        """Test missing session tracking raises HIGH issue."""
        with patch('cortex.orchestrators.health.agents.token_optimization_agent.get_gateway') as mock_get_gateway:
            mock_gateway = Mock()
            mock_gateway.token_budget = 20000
            mock_gateway.enable_cache = True
            # Missing _session_tokens attribute
            mock_gateway._session_tokens = Mock(side_effect=AttributeError)
            mock_get_gateway.return_value = mock_gateway
            
            result = agent.check(workspace_root)
            
            session_issues = [i for i in result.issues if "session" in i.description.lower() and "not initialized" in i.description.lower()]
            assert len(session_issues) == 1
            issue = session_issues[0]
            assert issue.severity == HealthIssueSeverity.HIGH
    
    # =========================================================================
    # Metrics Registration Tests
    # =========================================================================
    
    def test_metrics_registered_no_issue(self, agent, workspace_root):
        """GOLDEN PATH: Metrics registered, no issue."""
        with patch('cortex.orchestrators.health.agents.token_optimization_agent.get_gateway') as mock_get_gateway:
            mock_gateway = Mock()
            mock_gateway.token_budget = 20000
            mock_gateway.enable_cache = True
            mock_gateway._session_tokens = {}
            mock_get_gateway.return_value = mock_gateway
            
            result = agent.check(workspace_root)
            
            # Metrics import happens in _check_metrics_registration()
            # If no ImportError, no issue raised
            metrics_issues = [i for i in result.issues if "metrics" in i.description.lower()]
            assert len(metrics_issues) == 0
    
    # =========================================================================
    # Integration Tests
    # =========================================================================
    
    def test_multiple_issues_reported_correctly(self, agent, workspace_root):
        """Test multiple issues reported in single check."""
        with patch('cortex.orchestrators.health.agents.token_optimization_agent.get_gateway') as mock_get_gateway:
            mock_gateway = Mock()
            mock_gateway.token_budget = 15000  # Wrong
            mock_gateway.enable_cache = False  # Wrong
            mock_gateway._session_tokens = {}
            mock_get_gateway.return_value = mock_gateway
            
            result = agent.check(workspace_root)
            
            # Should have 2 issues: budget + cache
            assert len(result.issues) >= 2
            
            issue_descriptions = [i.description for i in result.issues]
            assert any("misconfigured" in desc for desc in issue_descriptions)
            assert any("cache disabled" in desc for desc in issue_descriptions)
    
    def test_early_exit_on_gateway_missing(self, agent, workspace_root):
        """Test early exit when gateway missing (other checks skipped)."""
        with patch('cortex.orchestrators.health.agents.token_optimization_agent.get_gateway') as mock_get_gateway:
            mock_get_gateway.return_value = None
            
            result = agent.check(workspace_root)
            
            # Only 1 issue (gateway missing), other checks not run
            assert len(result.issues) == 1
            assert result.metadata.get("gateway_missing") is True


class TestTokenOptimizationAgentIntegration:
    """Integration tests with HealthOrchestrator."""
    
    def test_agent_registers_with_orchestrator(self, tmp_path):
        """Test agent can be registered with HealthOrchestrator."""
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
        
        orchestrator = HealthOrchestrator(workspace_root=tmp_path)
        agent = TokenOptimizationAgent()
        
        orchestrator.register_agent(agent)
        
        assert "TokenOptimizationAgent" in orchestrator.list_agents()
    
    def test_orchestrator_runs_token_optimization_check(self, tmp_path):
        """Test HealthOrchestrator runs TokenOptimizationAgent check."""
        from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
        
        orchestrator = HealthOrchestrator(workspace_root=tmp_path)
        agent = TokenOptimizationAgent()
        orchestrator.register_agent(agent)
        
        with patch('cortex.orchestrators.health.agents.token_optimization_agent.get_gateway') as mock_get_gateway:
            mock_gateway = Mock()
            mock_gateway.token_budget = 20000
            mock_gateway.enable_cache = True
            mock_gateway._session_tokens = {}
            mock_get_gateway.return_value = mock_gateway
            
            report = orchestrator.run_health_check()
            
            # Verify TokenOptimizationAgent ran
            agent_names = [r.agent_name for r in report.agent_results]
            assert "TokenOptimizationAgent" in agent_names


__all__ = ["TestTokenOptimizationAgent", "TestTokenOptimizationAgentIntegration"]
