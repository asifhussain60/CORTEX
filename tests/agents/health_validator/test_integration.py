"""Integration tests for HealthValidator agent."""

import pytest
from unittest.mock import Mock, patch

from src.cortex_agents.health_validator import HealthValidator
from src.cortex_agents.base_agent import AgentRequest


class TestHealthValidatorIntegration:
    """Test HealthValidator agent integration."""
    
    def test_agent_initialization(self):
        """Test agent initializes with all components."""
        agent = HealthValidator("TestValidator")
        
        assert agent.name == "TestValidator"
        assert agent.db_validator is not None
        assert agent.test_validator is not None
        assert agent.git_validator is not None
        assert agent.disk_validator is not None
        assert agent.perf_validator is not None
        assert agent.analyzer is not None
        assert agent.formatter is not None
    
    def test_can_handle_health_check(self):
        """Test agent recognizes health check intent."""
        agent = HealthValidator("TestValidator")
        
        request = AgentRequest(
            intent="health_check",
            context={},
            user_message="Check system health"
        )
        
        assert agent.can_handle(request) is True
    
    def test_can_handle_validate(self):
        """Test agent recognizes validate intent."""
        agent = HealthValidator("TestValidator")
        
        request = AgentRequest(
            intent="validate",
            context={},
            user_message="Validate system"
        )
        
        assert agent.can_handle(request) is True
    
    def test_cannot_handle_other_intent(self):
        """Test agent rejects unrelated intents."""
        agent = HealthValidator("TestValidator")
        
        request = AgentRequest(
            intent="execute_code",
            context={},
            user_message="Run this code"
        )
        
        assert agent.can_handle(request) is False
    
    @patch('src.cortex_agents.health_validator.validators.database_validator.DatabaseValidator.check')
    @patch('src.cortex_agents.health_validator.validators.test_validator.TestValidator.check')
    @patch('src.cortex_agents.health_validator.validators.git_validator.GitValidator.check')
    @patch('src.cortex_agents.health_validator.validators.disk_validator.DiskValidator.check')
    @patch('src.cortex_agents.health_validator.validators.performance_validator.PerformanceValidator.check')
    def test_execute_all_passing(self, mock_perf, mock_disk, mock_git, mock_test, mock_db):
        """Test execution with all checks passing."""
        # Mock all validators to return pass
        mock_db.return_value = {"status": "pass", "details": [], "errors": [], "warnings": []}
        mock_test.return_value = {"status": "pass", "details": [], "errors": [], "warnings": []}
        mock_git.return_value = {"status": "pass", "details": [], "errors": [], "warnings": []}
        mock_disk.return_value = {"status": "pass", "details": [], "errors": [], "warnings": []}
        mock_perf.return_value = {"status": "pass", "details": [], "errors": [], "warnings": []}
        
        agent = HealthValidator("TestValidator")
        request = AgentRequest(
            intent="health_check",
            context={},
            user_message="Check system health"
        )
        
        response = agent.execute(request)
        
        assert response.success is True
        assert response.result["status"] == "healthy"
        assert response.result["risk_level"] == "low"
        assert len(response.result["errors"]) == 0
    
    @patch('src.cortex_agents.health_validator.validators.database_validator.DatabaseValidator.check')
    @patch('src.cortex_agents.health_validator.validators.test_validator.TestValidator.check')
    @patch('src.cortex_agents.health_validator.validators.git_validator.GitValidator.check')
    @patch('src.cortex_agents.health_validator.validators.disk_validator.DiskValidator.check')
    @patch('src.cortex_agents.health_validator.validators.performance_validator.PerformanceValidator.check')
    def test_execute_with_failure(self, mock_perf, mock_disk, mock_git, mock_test, mock_db):
        """Test execution with critical failure."""
        # Mock database failure
        mock_db.return_value = {
            "status": "fail",
            "details": [],
            "errors": ["Tier 1: database not found"],
            "warnings": []
        }
        mock_test.return_value = {"status": "pass", "details": [], "errors": [], "warnings": []}
        mock_git.return_value = {"status": "pass", "details": [], "errors": [], "warnings": []}
        mock_disk.return_value = {"status": "pass", "details": [], "errors": [], "warnings": []}
        mock_perf.return_value = {"status": "pass", "details": [], "errors": [], "warnings": []}
        
        agent = HealthValidator("TestValidator")
        request = AgentRequest(
            intent="health_check",
            context={},
            user_message="Check system health"
        )
        
        response = agent.execute(request)
        
        assert response.success is False
        assert response.result["status"] == "unhealthy"
        assert response.result["risk_level"] == "critical"
        assert len(response.result["errors"]) > 0
    
    @patch('src.cortex_agents.health_validator.validators.database_validator.DatabaseValidator.check')
    @patch('src.cortex_agents.health_validator.validators.test_validator.TestValidator.check')
    @patch('src.cortex_agents.health_validator.validators.git_validator.GitValidator.check')
    @patch('src.cortex_agents.health_validator.validators.disk_validator.DiskValidator.check')
    @patch('src.cortex_agents.health_validator.validators.performance_validator.PerformanceValidator.check')
    def test_execute_with_warnings(self, mock_perf, mock_disk, mock_git, mock_test, mock_db):
        """Test execution with warnings."""
        mock_db.return_value = {"status": "pass", "details": [], "errors": [], "warnings": []}
        mock_test.return_value = {"status": "pass", "details": [], "errors": [], "warnings": []}
        mock_git.return_value = {
            "status": "warn",
            "details": [],
            "errors": [],
            "warnings": ["High uncommitted changes: 60"]
        }
        mock_disk.return_value = {"status": "pass", "details": [], "errors": [], "warnings": []}
        mock_perf.return_value = {"status": "pass", "details": [], "errors": [], "warnings": []}
        
        agent = HealthValidator("TestValidator")
        request = AgentRequest(
            intent="health_check",
            context={},
            user_message="Check system health"
        )
        
        response = agent.execute(request)
        
        assert response.success is True  # Degraded is still "success"
        assert response.result["status"] == "degraded"
        assert len(response.result["warnings"]) > 0
    
    def test_skip_tests_option(self):
        """Test skipping test execution via context."""
        agent = HealthValidator("TestValidator")
        request = AgentRequest(
            intent="health_check",
            context={"skip_tests": True},
            user_message="Check system health without running tests"
        )
        
        response = agent.execute(request)
        
        assert response.result["checks"]["tests"]["status"] == "skip"
    
    def test_response_includes_suggestions(self):
        """Test response includes action suggestions."""
        agent = HealthValidator("TestValidator")
        request = AgentRequest(
            intent="health_check",
            context={},
            user_message="Check system health"
        )
        
        response = agent.execute(request)
        
        assert "suggestions" in response.result
        assert isinstance(response.result["suggestions"], list)
    
    def test_response_includes_metadata(self):
        """Test response includes check metadata."""
        agent = HealthValidator("TestValidator")
        request = AgentRequest(
            intent="health_check",
            context={},
            user_message="Check system health"
        )
        
        response = agent.execute(request)
        
        assert "total_checks" in response.metadata
        assert "passed" in response.metadata
        assert "failed" in response.metadata
        assert "warnings" in response.metadata
        assert "skipped" in response.metadata
