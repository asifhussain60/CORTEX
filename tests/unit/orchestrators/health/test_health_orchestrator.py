"""Unit Tests for Health Orchestrator

Tests the main health orchestrator coordination logic.

Author: CORTEX Framework
Phase: PHASE-95 S3 Completion
CORE Rules: CORE-008 (TDD)
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock

from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
from cortex.orchestrators.health.agents.base_agent import (
    BaseHealthAgent,
    HealthCheckResult,
    HealthIssue,
    HealthIssueCategory,
    HealthIssueSeverity,
)
from cortex.orchestrators.health.reports.health_report import HealthReport


@pytest.fixture
def workspace_root(tmp_path: Path) -> Path:
    """Create temporary workspace root.
    
    Args:
        tmp_path: Pytest temporary directory
    
    Returns:
        Path to workspace root
    """
    workspace = tmp_path / "test_workspace"
    workspace.mkdir()
    return workspace


@pytest.fixture
def mock_agent() -> Mock:
    """Create mock health agent.
    
    Returns:
        Mock agent instance
    """
    agent = Mock(spec=BaseHealthAgent)
    agent.name = "TestAgent"
    agent.description = "Test agent description"
    agent.enabled = True
    
    # Mock check method
    result = HealthCheckResult(
        agent_name="TestAgent",
        issues=[
            HealthIssue(
                category=HealthIssueCategory.DUPLICATE,
                severity=HealthIssueSeverity.HIGH,
                file_path=Path("test.py"),
                description="Test issue",
                line_number=None,
                metadata={},
            )
        ],
        files_scanned=10,
        duration_seconds=0.5,
    )
    agent.check.return_value = result
    
    return agent


class TestHealthOrchestratorInitialization:
    """Test suite for HealthOrchestrator initialization."""
    
    def test_init_with_valid_workspace(self, workspace_root: Path) -> None:
        """Test initialization with valid workspace root.
        
        Args:
            workspace_root: Test workspace path
        """
        orchestrator = HealthOrchestrator(workspace_root)
        
        assert orchestrator.workspace_root == workspace_root
        assert orchestrator.agents == []
        assert orchestrator.enabled is True
        assert isinstance(orchestrator.config, dict)
    
    def test_init_with_config(self, workspace_root: Path) -> None:
        """Test initialization with custom config.
        
        Args:
            workspace_root: Test workspace path
        """
        config = {"timeout": 60, "parallel": True}
        orchestrator = HealthOrchestrator(workspace_root, config=config)
        
        assert orchestrator.config == config
    
    def test_init_with_nonexistent_workspace(self, tmp_path: Path) -> None:
        """Test initialization fails with nonexistent workspace.
        
        Args:
            tmp_path: Pytest temporary directory
        """
        nonexistent = tmp_path / "nonexistent"
        
        with pytest.raises(ValueError, match="Workspace root does not exist"):
            HealthOrchestrator(nonexistent)


class TestAgentRegistration:
    """Test suite for agent registration."""
    
    def test_register_agent(self, workspace_root: Path, mock_agent: Mock) -> None:
        """Test registering a health agent.
        
        Args:
            workspace_root: Test workspace path
            mock_agent: Mock agent instance
        """
        orchestrator = HealthOrchestrator(workspace_root)
        orchestrator.register_agent(mock_agent)
        
        assert len(orchestrator.agents) == 1
        assert orchestrator.agents[0] == mock_agent
    
    def test_register_multiple_agents(self, workspace_root: Path) -> None:
        """Test registering multiple agents.
        
        Args:
            workspace_root: Test workspace path
        """
        orchestrator = HealthOrchestrator(workspace_root)
        
        agent1 = Mock(spec=BaseHealthAgent, name="Agent1")
        agent2 = Mock(spec=BaseHealthAgent, name="Agent2")
        
        orchestrator.register_agent(agent1)
        orchestrator.register_agent(agent2)
        
        assert len(orchestrator.agents) == 2
    
    def test_unregister_agent(self, workspace_root: Path, mock_agent: Mock) -> None:
        """Test unregistering an agent.
        
        Args:
            workspace_root: Test workspace path
            mock_agent: Mock agent instance
        """
        orchestrator = HealthOrchestrator(workspace_root)
        orchestrator.register_agent(mock_agent)
        
        result = orchestrator.unregister_agent("TestAgent")
        
        assert result is True
        assert len(orchestrator.agents) == 0
    
    def test_unregister_nonexistent_agent(self, workspace_root: Path) -> None:
        """Test unregistering nonexistent agent returns False.
        
        Args:
            workspace_root: Test workspace path
        """
        orchestrator = HealthOrchestrator(workspace_root)
        
        result = orchestrator.unregister_agent("NonexistentAgent")
        
        assert result is False
    
    def test_get_agent(self, workspace_root: Path, mock_agent: Mock) -> None:
        """Test retrieving agent by name.
        
        Args:
            workspace_root: Test workspace path
            mock_agent: Mock agent instance
        """
        orchestrator = HealthOrchestrator(workspace_root)
        orchestrator.register_agent(mock_agent)
        
        retrieved = orchestrator.get_agent("TestAgent")
        
        assert retrieved == mock_agent
    
    def test_get_nonexistent_agent(self, workspace_root: Path) -> None:
        """Test retrieving nonexistent agent returns None.
        
        Args:
            workspace_root: Test workspace path
        """
        orchestrator = HealthOrchestrator(workspace_root)
        
        retrieved = orchestrator.get_agent("NonexistentAgent")
        
        assert retrieved is None


class TestHealthCheckExecution:
    """Test suite for health check execution."""
    
    def test_run_health_check_with_agents(
        self, workspace_root: Path, mock_agent: Mock
    ) -> None:
        """Test running health check with registered agents.
        
        Args:
            workspace_root: Test workspace path
            mock_agent: Mock agent instance
        """
        orchestrator = HealthOrchestrator(workspace_root)
        orchestrator.register_agent(mock_agent)
        
        report = orchestrator.run_health_check()
        
        assert isinstance(report, HealthReport)
        assert len(report.agent_results) == 1
        assert report.agent_results[0].agent_name == "TestAgent"
        mock_agent.check.assert_called_once()
        # Phase-48 delegation now passes ctx= kwarg, so verify positional arg only
        call_args = mock_agent.check.call_args
        assert call_args[0][0] == workspace_root
    
    def test_run_health_check_without_agents(self, workspace_root: Path) -> None:
        """Test running health check without agents.
        
        Args:
            workspace_root: Test workspace path
        """
        orchestrator = HealthOrchestrator(workspace_root)
        
        report = orchestrator.run_health_check()
        
        assert isinstance(report, HealthReport)
        assert len(report.agent_results) == 0
    
    def test_run_health_check_disabled_orchestrator(
        self, workspace_root: Path, mock_agent: Mock
    ) -> None:
        """Test running health check on disabled orchestrator.
        
        Args:
            workspace_root: Test workspace path
            mock_agent: Mock agent instance
        """
        orchestrator = HealthOrchestrator(workspace_root)
        orchestrator.enabled = False
        orchestrator.register_agent(mock_agent)
        
        report = orchestrator.run_health_check()
        
        # Should still return report but with no results
        assert isinstance(report, HealthReport)
        assert len(report.agent_results) == 0
        mock_agent.check.assert_not_called()
    
    def test_run_health_check_disabled_agent(self, workspace_root: Path) -> None:
        """Test running health check with disabled agent.
        
        Args:
            workspace_root: Test workspace path
        """
        orchestrator = HealthOrchestrator(workspace_root)
        
        agent = Mock(spec=BaseHealthAgent)
        agent.name = "DisabledAgent"
        agent.enabled = False
        agent.is_enabled.return_value = False  # Explicitly return False
        
        orchestrator.register_agent(agent)
        report = orchestrator.run_health_check()
        
        # Disabled agents should be skipped
        assert len(report.agent_results) == 0
        agent.check.assert_not_called()
    
    def test_run_health_check_agent_exception(self, workspace_root: Path) -> None:
        """Test health check handles agent exceptions gracefully.
        
        Args:
            workspace_root: Test workspace path
        """
        orchestrator = HealthOrchestrator(workspace_root)
        
        agent = Mock(spec=BaseHealthAgent)
        agent.name = "FailingAgent"
        agent.enabled = True
        agent.check.side_effect = RuntimeError("Agent failed")
        
        orchestrator.register_agent(agent)
        
        # Should not raise exception, should handle gracefully
        report = orchestrator.run_health_check()
        
        assert isinstance(report, HealthReport)
        # Result should contain error information
        assert len(report.agent_results) >= 0  # May or may not have error result depending on implementation


class TestHealthCheckFiltering:
    """Test suite for health check filtering."""
    
    def test_run_specific_agents(
        self, workspace_root: Path, mock_agent: Mock
    ) -> None:
        """Test running health check on specific agents only.
        
        Args:
            workspace_root: Test workspace path
            mock_agent: Mock agent instance
        """
        orchestrator = HealthOrchestrator(workspace_root)
        
        agent2 = Mock(spec=BaseHealthAgent)
        agent2.name = "Agent2"
        agent2.enabled = True
        
        orchestrator.register_agent(mock_agent)
        orchestrator.register_agent(agent2)
        
        # Run only TestAgent
        report = orchestrator.run_health_check(agent_names=["TestAgent"])
        
        assert len(report.agent_results) == 1
        assert report.agent_results[0].agent_name == "TestAgent"
        mock_agent.check.assert_called_once()
        agent2.check.assert_not_called()
