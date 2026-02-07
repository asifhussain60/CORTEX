"""
Test Autonomous Plan Execution MCP Tool - Phase 40

AC-ID: PHASE-40-AUTONOMOUS-EXECUTION-001
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from cortex.mcp.tools.plan_management_tool import (
    cortex_plan_execute_autonomous,
    _generate_progress_bar
)


class TestProgressBarGeneration:
    """Test ASCII progress bar generation"""
    
    def test_progress_bar_0_percent(self):
        """Test 0% progress bar"""
        bar = _generate_progress_bar(0, 10, 1)
        assert bar == "[░░░░░░░░░░]   0%"
    
    def test_progress_bar_50_percent(self):
        """Test 50% progress bar"""
        bar = _generate_progress_bar(5, 10, 10)
        assert bar == "[█████░░░░░]  50%"
    
    def test_progress_bar_100_percent(self):
        """Test 100% progress bar"""
        bar = _generate_progress_bar(10, 10, 10)
        assert bar == "[██████████] 100%"
    
    def test_progress_bar_intermediate(self):
        """Test intermediate progress"""
        bar = _generate_progress_bar(3, 10, 10)
        assert bar == "[███░░░░░░░]  30%"


class TestAutonomousExecution:
    """Test cortex_plan_execute_autonomous tool"""
    
    @patch('cortex.mcp.tools.plan_management_tool.cortex_plan_setup')
    @patch('cortex.mcp.tools.plan_management_tool.cortex_plan_teardown')
    @patch('cortex.mcp.tools.plan_management_tool.cortex_plan_sync')
    @patch('cortex.mcp.tools.plan_management_tool.AutonomousExecutionEngine')
    @patch('builtins.open')
    @patch('yaml.safe_load')
    @patch('pathlib.Path.exists')
    def test_successful_autonomous_execution(
        self,
        mock_exists,
        mock_yaml_load,
        mock_open,
        mock_engine_class,
        mock_sync,
        mock_teardown,
        mock_setup
    ):
        """Test successful autonomous phase execution"""
        # Setup mocks
        mock_setup.return_value = {"success": True}
        mock_teardown.return_value = {"success": True}
        mock_sync.return_value = {"success": True}
        mock_exists.return_value = True
        
        mock_yaml_load.return_value = {
            "phase_id": "phase-40",
            "title": "Test Phase",
            "description": "Test phase description",
            "estimated_hours": 2,
            "stages": [
                {"name": "Stage 1", "description": "First stage"},
                {"name": "Stage 2", "description": "Second stage"}
            ]
        }
        
        # Mock engine execution
        mock_engine = MagicMock()
        mock_engine_class.return_value = mock_engine
        
        # Mock Result type with both sync and async behavior
        from cortex.core.result import Ok
        mock_result = Ok({
            "plan_id": "phase-40",
            "status": "COMPLETE",
            "total_duration_seconds": 120.5,
            "phases_completed": 2,
            "checkpoint": {
                "test_results": {
                    "passed": 50,
                    "failed": 0,
                    "coverage": 95.0
                }
            }
        })
        
        # Make execute_plan_autonomously return the Result directly (decorator makes it sync)
        mock_engine.execute_plan_autonomously.return_value = mock_result
        
        # Execute
        result = cortex_plan_execute_autonomous(
            phase_id="phase-40",
            registry_root="cortex-registry/_cortex-master",
            show_progress=False  # Disable for test
        )
        
        # Assert
        assert result["success"] is True
        assert result["phase_id"] == "phase-40"
        assert result["stages_completed"] == 2
        assert result["total_stages"] == 2
        assert result["duration_seconds"] == 120.5
        assert "phase-40 completed autonomously" in result["message"]
    
    @patch('cortex.mcp.tools.plan_management_tool.cortex_plan_setup')
    def test_setup_failure_stops_execution(self, mock_setup):
        """Test that setup failure prevents execution"""
        mock_setup.return_value = {
            "success": False,
            "error": "Git checkpoint failed"
        }
        
        result = cortex_plan_execute_autonomous(
            phase_id="phase-40",
            registry_root="cortex-registry/_cortex-master"
        )
        
        assert result["success"] is False
        assert "Setup failed" in result["error"]
    
    @patch('cortex.mcp.tools.plan_management_tool.cortex_plan_setup')
    @patch('pathlib.Path.exists')
    def test_missing_phase_file(self, mock_exists, mock_setup):
        """Test handling of missing phase file"""
        mock_setup.return_value = {"success": True}
        mock_exists.return_value = False  # Phase file doesn't exist
        
        result = cortex_plan_execute_autonomous(
            phase_id="phase-99",
            registry_root="cortex-registry/_cortex-master"
        )
        
        assert result["success"] is False
        assert "not found in registry" in result["message"]
    
    @patch('cortex.mcp.tools.plan_management_tool.cortex_plan_setup')
    @patch('builtins.open')
    @patch('yaml.safe_load')
    @patch('pathlib.Path.exists')
    def test_phase_without_stages(
        self,
        mock_exists,
        mock_yaml_load,
        mock_open,
        mock_setup
    ):
        """Test phase with no stages defined"""
        mock_setup.return_value = {"success": True}
        mock_exists.return_value = True
        mock_yaml_load.return_value = {
            "phase_id": "phase-empty",
            "title": "Empty Phase",
            "stages": [],  # No stages
            "tasks": []     # No tasks
        }
        
        result = cortex_plan_execute_autonomous(
            phase_id="phase-empty",
            registry_root="cortex-registry/_cortex-master"
        )
        
        assert result["success"] is False
        assert "no executable stages" in result["message"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
