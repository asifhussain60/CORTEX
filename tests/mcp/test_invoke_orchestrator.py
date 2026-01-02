"""
Comprehensive tests for invoke_orchestrator MCP tool.

Tests cover orchestrator discovery, invocation, error handling,
and result formatting.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import yaml
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.mcp.tools.invoke_orchestrator import (
    invoke_orchestrator,
    reload_registry,
    list_orchestrators,
    get_registry
)


class TestGetRegistry:
    """Test registry initialization."""
    
    @patch('src.mcp.tools.invoke_orchestrator.OrchestratorRegistry')
    def test_get_registry_initializes_once(self, mock_registry_class):
        """Registry initializes only once (singleton pattern)."""
        # Reset global registry
        import src.mcp.tools.invoke_orchestrator as orch_module
        orch_module._registry = None
        
        mock_instance = Mock()
        mock_registry_class.return_value = mock_instance
        
        # First call initializes
        registry1 = get_registry()
        assert registry1 == mock_instance
        
        # Second call returns same instance
        registry2 = get_registry()
        assert registry2 == mock_instance
        
        # Registry class only called once
        assert mock_registry_class.call_count == 1


class TestInvokeOrchestrator:
    """Test invoke_orchestrator tool."""
    
    @pytest.fixture
    def mock_registry(self):
        """Create mock registry."""
        with patch('src.mcp.tools.invoke_orchestrator.get_registry') as mock_get:
            registry = Mock()
            mock_get.return_value = registry
            yield registry
    
    def test_invoke_nonexistent_orchestrator(self, mock_registry):
        """Invoke orchestrator that doesn't exist."""
        mock_registry.exists.return_value = False
        mock_registry.list_orchestrators.return_value = ["planning_system", "ado_operations"]
        
        result = invoke_orchestrator("nonexistent", "Test request")
        
        assert result["status"] == "error"
        assert "not found" in result["error"]
        assert "planning_system" in result["error"]
    
    def test_invoke_guided_orchestrator(self, mock_registry):
        """Cannot invoke guided orchestrator via MCP."""
        from src.mcp.registry import OrchestratorDefinition
        
        mock_registry.exists.return_value = True
        mock_registry.get.return_value = OrchestratorDefinition(
            name="tdd_orchestrator",
            class_name="TddOrchestrator",
            module_path="src.orchestrators.tdd",
            config_path="test.yaml",
            type="guided"
        )
        
        result = invoke_orchestrator("tdd_orchestrator", "Test request")
        
        assert result["status"] == "error"
        assert "not autonomous" in result["error"]
    
    def test_invoke_success(self, mock_registry):
        """Successfully invoke orchestrator."""
        from src.mcp.registry import OrchestratorDefinition
        
        # Setup mock orchestrator
        mock_orchestrator = Mock()
        mock_orchestrator.execute.return_value = {
            "artifacts": ["plan.md", "context/analysis.md"],
            "summary": "Created plan with 5 phases",
            "progress": {"current_phase": 5, "total_phases": 5},
            "metadata": {"duration": 120}
        }
        
        mock_registry.exists.return_value = True
        mock_registry.get.return_value = OrchestratorDefinition(
            name="planning_system",
            class_name="PlanningOrchestratorV5",
            module_path="src.orchestrators.planning_v5",
            config_path="test.yaml",
            type="autonomous"
        )
        mock_registry.instantiate.return_value = mock_orchestrator
        
        result = invoke_orchestrator(
            "planning_system",
            "Create plan for user authentication"
        )
        
        assert result["status"] == "success"
        assert result["orchestrator"] == "planning_system"
        assert len(result["artifacts"]) == 2
        assert result["summary"] == "Created plan with 5 phases"
        assert "execution_time" in result
        
        # Verify orchestrator was called with correct parameters
        mock_orchestrator.execute.assert_called_once_with(
            user_request="Create plan for user authentication",
            options={}
        )
    
    def test_invoke_with_options(self, mock_registry):
        """Invoke orchestrator with custom options."""
        from src.mcp.registry import OrchestratorDefinition
        
        mock_orchestrator = Mock()
        mock_orchestrator.execute.return_value = {
            "summary": "Execution completed"
        }
        
        mock_registry.exists.return_value = True
        mock_registry.get.return_value = OrchestratorDefinition(
            name="planning_system",
            class_name="PlanningOrchestratorV5",
            module_path="src.orchestrators.planning_v5",
            config_path="test.yaml",
            type="autonomous"
        )
        mock_registry.instantiate.return_value = mock_orchestrator
        
        options = {"mode": "supervised", "checkpoint": True}
        result = invoke_orchestrator(
            "planning_system",
            "Test request",
            options=options
        )
        
        assert result["status"] == "success"
        
        # Verify options passed to orchestrator
        mock_orchestrator.execute.assert_called_once_with(
            user_request="Test request",
            options=options
        )
    
    def test_invoke_instantiation_failure(self, mock_registry):
        """Handle orchestrator instantiation failure."""
        from src.mcp.registry import OrchestratorDefinition
        
        mock_registry.exists.return_value = True
        mock_registry.get.return_value = OrchestratorDefinition(
            name="planning_system",
            class_name="PlanningOrchestratorV5",
            module_path="src.orchestrators.planning_v5",
            config_path="test.yaml",
            type="autonomous"
        )
        mock_registry.instantiate.return_value = None
        
        result = invoke_orchestrator("planning_system", "Test request")
        
        assert result["status"] == "error"
        assert "Failed to instantiate" in result["error"]
    
    def test_invoke_execution_failure(self, mock_registry):
        """Handle orchestrator execution failure."""
        from src.mcp.registry import OrchestratorDefinition
        
        mock_orchestrator = Mock()
        mock_orchestrator.execute.side_effect = RuntimeError("Database connection failed")
        
        mock_registry.exists.return_value = True
        mock_registry.get.return_value = OrchestratorDefinition(
            name="planning_system",
            class_name="PlanningOrchestratorV5",
            module_path="src.orchestrators.planning_v5",
            config_path="test.yaml",
            type="autonomous"
        )
        mock_registry.instantiate.return_value = mock_orchestrator
        
        result = invoke_orchestrator("planning_system", "Test request")
        
        assert result["status"] == "error"
        assert "execution failed" in result["error"]
        assert "traceback" in result
    
    def test_invoke_registry_initialization_failure(self):
        """Handle registry initialization failure."""
        with patch('src.mcp.tools.invoke_orchestrator.get_registry') as mock_get:
            mock_get.side_effect = FileNotFoundError("Config not found")
            
            result = invoke_orchestrator("planning_system", "Test request")
            
            assert result["status"] == "error"
            assert "Failed to initialize" in result["error"]


class TestReloadRegistry:
    """Test reload_registry function."""
    
    def test_reload_success(self):
        """Successfully reload registry - integration test."""
        # This is an integration test with real registry
        # Just verify it doesn't crash and returns success
        result = reload_registry()
        
        assert result["status"] == "success"
        assert "statistics" in result
        assert "message" in result
    
    def test_reload_with_existing_registry(self):
        """Reload when registry already exists."""
        import src.mcp.tools.invoke_orchestrator as orch_module
        
        # Ensure registry exists
        get_registry()
        
        # Reload should call reload on existing registry
        result = reload_registry()
        
        assert result["status"] == "success"
        assert "statistics" in result


class TestListOrchestrators:
    """Test list_orchestrators function."""
    
    @patch('src.mcp.tools.invoke_orchestrator.get_registry')
    def test_list_success(self, mock_get):
        """Successfully list orchestrators."""
        from src.mcp.registry import OrchestratorDefinition
        
        mock_registry = Mock()
        mock_registry.list_orchestrators.return_value = ["planning_system", "ado_operations"]
        mock_registry.get_statistics.return_value = {
            "total": 2,
            "autonomous": 2,
            "guided": 0
        }
        
        def mock_get_definition(name):
            if name == "planning_system":
                return OrchestratorDefinition(
                    name="planning_system",
                    class_name="PlanningOrchestratorV5",
                    module_path="src.orchestrators.planning_v5",
                    config_path="test.yaml",
                    type="autonomous",
                    description="Planning system v5"
                )
            elif name == "ado_operations":
                return OrchestratorDefinition(
                    name="ado_operations",
                    class_name="AdoOrchestratorV2",
                    module_path="src.orchestrators.ado_v2",
                    config_path="test.yaml",
                    type="autonomous",
                    description="ADO operations"
                )
        
        mock_registry.get = mock_get_definition
        mock_get.return_value = mock_registry
        
        result = list_orchestrators()
        
        assert result["status"] == "success"
        assert "orchestrators" in result
        assert "planning_system" in result["orchestrators"]
        assert result["orchestrators"]["planning_system"]["type"] == "autonomous"
        assert "statistics" in result
    
    @patch('src.mcp.tools.invoke_orchestrator.get_registry')
    def test_list_failure(self, mock_get):
        """Handle list failure."""
        mock_get.side_effect = Exception("Registry unavailable")
        
        result = list_orchestrators()
        
        assert result["status"] == "error"
        assert "Failed to list" in result["error"]
