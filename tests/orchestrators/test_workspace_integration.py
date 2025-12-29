"""
Tests for Orchestrator Workspace Integration

Tests workspace detection and integration in BaseOrchestrator and subclass orchestrators.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.orchestrators.base.base_orchestrator import (
    BaseOrchestrator,
    OrchestratorStatus,
    OrchestratorResult,
    ValidationResult
)
from src.core.workspace_detector import WorkspaceInfo, WorkspaceDetectionMethod
from src.core.ide_detector import IDEType


# Concrete implementation for testing
class TestOrchestrator(BaseOrchestrator):
    """Test orchestrator implementation."""
    
    def execute(self) -> OrchestratorResult:
        """Simple execution that writes to target directory."""
        # Write a test file to target directory
        test_file = self.target_directory / "test_output.txt"
        test_file.write_text(f"Hello from {self.workspace_name}")
        
        return OrchestratorResult(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message=f"Test completed in workspace {self.workspace_name}",
            data={"file_created": str(test_file)}
        )


@pytest.fixture
def temp_cortex_root(tmp_path):
    """Create temporary CORTEX root structure."""
    cortex_root = tmp_path / "CORTEX"
    cortex_root.mkdir()
    (cortex_root / "cortex-brain").mkdir()
    return cortex_root


@pytest.fixture
def temp_user_workspace(tmp_path):
    """Create temporary user workspace."""
    workspace = tmp_path / "UserApp"
    workspace.mkdir()
    (workspace / "src").mkdir()
    (workspace / "tests").mkdir()
    return workspace


@pytest.fixture
def mock_workspace_info(temp_user_workspace):
    """Create mock WorkspaceInfo."""
    return WorkspaceInfo(
        workspace_id="test-workspace-uuid",
        path=temp_user_workspace,
        name="UserApp",
        project_type="python",
        ide_type=IDEType.VSCODE,
        detection_method=WorkspaceDetectionMethod.CWD_SEARCH
    )


@pytest.fixture
def orchestrator_config():
    """Create basic orchestrator configuration."""
    return {
        "name": "TestOrchestrator",
        "version": "4.0.0",
        "log_level": "INFO"
    }


class TestBaseOrchestratorWorkspaceDetection:
    """Test workspace detection in BaseOrchestrator."""
    
    def test_workspace_info_detected(self, orchestrator_config, mock_workspace_info):
        """Test orchestrator detects workspace on initialization."""
        with patch('src.orchestrators.base.base_orchestrator.detect_active_workspace', return_value=mock_workspace_info):
            orchestrator = TestOrchestrator(orchestrator_config)
            
            assert orchestrator.workspace_info is not None
            assert orchestrator.workspace_info.name == "UserApp"
    
    def test_target_directory_set(self, orchestrator_config, mock_workspace_info):
        """Test target_directory is set to workspace path."""
        with patch('src.orchestrators.base.base_orchestrator.detect_active_workspace', return_value=mock_workspace_info):
            orchestrator = TestOrchestrator(orchestrator_config)
            
            assert orchestrator.target_directory == mock_workspace_info.path
    
    def test_workspace_id_set(self, orchestrator_config, mock_workspace_info):
        """Test workspace_id is extracted from workspace info."""
        with patch('src.orchestrators.base.base_orchestrator.detect_active_workspace', return_value=mock_workspace_info):
            orchestrator = TestOrchestrator(orchestrator_config)
            
            assert orchestrator.workspace_id == "test-workspace-uuid"
    
    def test_workspace_name_set(self, orchestrator_config, mock_workspace_info):
        """Test workspace_name is extracted from workspace info."""
        with patch('src.orchestrators.base.base_orchestrator.detect_active_workspace', return_value=mock_workspace_info):
            orchestrator = TestOrchestrator(orchestrator_config)
            
            assert orchestrator.workspace_name == "UserApp"
    
    def test_workspace_detection_failure_fallback(self, orchestrator_config):
        """Test fallback to workspace_root when detection fails."""
        config = orchestrator_config.copy()
        config["workspace_root"] = "/fallback/path"
        
        with patch('src.orchestrators.base.base_orchestrator.detect_active_workspace', side_effect=Exception("Detection failed")):
            orchestrator = TestOrchestrator(config)
            
            assert orchestrator.target_directory == Path("/fallback/path")
            assert orchestrator.workspace_info is None
            assert orchestrator.workspace_id == "unknown"
            assert orchestrator.workspace_name == "unknown"


class TestBaseOrchestratorLogging:
    """Test workspace-aware logging."""
    
    def test_initialization_logging_includes_workspace(self, orchestrator_config, mock_workspace_info, caplog):
        """Test initialization logs include workspace name."""
        with patch('src.orchestrators.base.base_orchestrator.detect_active_workspace', return_value=mock_workspace_info):
            orchestrator = TestOrchestrator(orchestrator_config)
            
            assert "[workspace:UserApp]" in caplog.text
            assert "Initialized TestOrchestrator" in caplog.text
    
    def test_run_logging_includes_workspace(self, orchestrator_config, mock_workspace_info, temp_user_workspace, caplog):
        """Test run() logs include workspace name."""
        with patch('src.orchestrators.base.base_orchestrator.detect_active_workspace', return_value=mock_workspace_info):
            orchestrator = TestOrchestrator(orchestrator_config)
            result = orchestrator.run()
            
            assert "[workspace:UserApp]" in caplog.text
            assert "🎭 Orchestrator engaged" in caplog.text


class TestOrchestratorFileOperations:
    """Test orchestrators write files to correct workspace."""
    
    def test_file_written_to_target_directory(self, orchestrator_config, mock_workspace_info, temp_user_workspace):
        """Test orchestrator writes files to target directory."""
        with patch('src.orchestrators.base.base_orchestrator.detect_active_workspace', return_value=mock_workspace_info):
            orchestrator = TestOrchestrator(orchestrator_config)
            result = orchestrator.run()
            
            # Check file was created in target directory
            output_file = temp_user_workspace / "test_output.txt"
            assert output_file.exists()
            assert "Hello from UserApp" in output_file.read_text()
    
    def test_file_path_in_result_data(self, orchestrator_config, mock_workspace_info, temp_user_workspace):
        """Test result data includes file path."""
        with patch('src.orchestrators.base.base_orchestrator.detect_active_workspace', return_value=mock_workspace_info):
            orchestrator = TestOrchestrator(orchestrator_config)
            result = orchestrator.run()
            
            assert "file_created" in result.data
            assert str(temp_user_workspace) in result.data["file_created"]


class TestMultiWorkspaceScenarios:
    """Test orchestrators in multi-workspace scenarios."""
    
    def test_different_workspaces_isolated(self, orchestrator_config, tmp_path):
        """Test orchestrators targeting different workspaces are isolated."""
        # Create two workspaces
        workspace1 = tmp_path / "App1"
        workspace1.mkdir()
        
        workspace2 = tmp_path / "App2"
        workspace2.mkdir()
        
        # Create workspace info for each
        workspace_info1 = WorkspaceInfo(
            workspace_id="ws1",
            path=workspace1,
            name="App1",
            project_type="python",
            ide_type=IDEType.VSCODE,
            detection_method=WorkspaceDetectionMethod.CWD_SEARCH
        )
        
        workspace_info2 = WorkspaceInfo(
            workspace_id="ws2",
            path=workspace2,
            name="App2",
            project_type="python",
            ide_type=IDEType.VSCODE,
            detection_method=WorkspaceDetectionMethod.CWD_SEARCH
        )
        
        # Run orchestrator in workspace 1
        with patch('src.orchestrators.base.base_orchestrator.detect_active_workspace', return_value=workspace_info1):
            orch1 = TestOrchestrator(orchestrator_config)
            result1 = orch1.run()
        
        # Run orchestrator in workspace 2
        with patch('src.orchestrators.base.base_orchestrator.detect_active_workspace', return_value=workspace_info2):
            orch2 = TestOrchestrator(orchestrator_config)
            result2 = orch2.run()
        
        # Verify files written to correct workspaces
        assert (workspace1 / "test_output.txt").exists()
        assert (workspace2 / "test_output.txt").exists()
        
        # Verify content is workspace-specific
        assert "App1" in (workspace1 / "test_output.txt").read_text()
        assert "App2" in (workspace2 / "test_output.txt").read_text()
    
    def test_workspace_switch_mid_execution(self, orchestrator_config, tmp_path):
        """Test workspace info remains consistent during execution."""
        workspace = tmp_path / "MyApp"
        workspace.mkdir()
        
        workspace_info = WorkspaceInfo(
            workspace_id="consistent-ws",
            path=workspace,
            name="MyApp",
            project_type="python",
            ide_type=IDEType.VSCODE,
            detection_method=WorkspaceDetectionMethod.CWD_SEARCH
        )
        
        with patch('src.orchestrators.base.base_orchestrator.detect_active_workspace', return_value=workspace_info):
            orchestrator = TestOrchestrator(orchestrator_config)
            
            # Verify workspace info is captured at initialization
            initial_workspace = orchestrator.workspace_name
            
            # Run orchestrator
            result = orchestrator.run()
            
            # Workspace should remain the same
            assert orchestrator.workspace_name == initial_workspace
            assert result.message.endswith("MyApp")


class TestWorkspaceContextPropagation:
    """Test workspace context propagates correctly."""
    
    def test_workspace_info_accessible_in_execute(self, orchestrator_config, mock_workspace_info):
        """Test workspace_info is accessible in execute() method."""
        with patch('src.orchestrators.base.base_orchestrator.detect_active_workspace', return_value=mock_workspace_info):
            orchestrator = TestOrchestrator(orchestrator_config)
            
            # Workspace info should be set before execute() is called
            assert orchestrator.workspace_info is not None
            
            # Run and verify it's still accessible
            result = orchestrator.run()
            assert result.success is True
    
    def test_target_directory_usable_in_execute(self, orchestrator_config, mock_workspace_info, temp_user_workspace):
        """Test target_directory can be used for file operations."""
        with patch('src.orchestrators.base.base_orchestrator.detect_active_workspace', return_value=mock_workspace_info):
            orchestrator = TestOrchestrator(orchestrator_config)
            
            # Should be able to create files in target_directory
            test_file = orchestrator.target_directory / "test.txt"
            test_file.write_text("test")
            
            assert test_file.exists()
            assert test_file.parent == temp_user_workspace


class TestBackwardCompatibility:
    """Test backward compatibility with orchestrators that don't use workspace."""
    
    def test_orchestrator_without_workspace_still_works(self, orchestrator_config):
        """Test orchestrators work even if workspace detection fails."""
        config = orchestrator_config.copy()
        config["workspace_root"] = "/tmp"
        
        with patch('src.orchestrators.base.base_orchestrator.detect_active_workspace', side_effect=Exception("No workspace")):
            # Should not raise exception
            orchestrator = TestOrchestrator(config)
            
            # Should fallback to workspace_root
            assert orchestrator.target_directory == Path("/tmp")


class TestOrchestratorResult:
    """Test OrchestratorResult includes workspace information."""
    
    def test_result_message_includes_workspace(self, orchestrator_config, mock_workspace_info):
        """Test result message includes workspace name."""
        with patch('src.orchestrators.base.base_orchestrator.detect_active_workspace', return_value=mock_workspace_info):
            orchestrator = TestOrchestrator(orchestrator_config)
            result = orchestrator.run()
            
            assert "UserApp" in result.message
    
    def test_result_success_with_workspace(self, orchestrator_config, mock_workspace_info, temp_user_workspace):
        """Test successful execution with workspace context."""
        with patch('src.orchestrators.base.base_orchestrator.detect_active_workspace', return_value=mock_workspace_info):
            orchestrator = TestOrchestrator(orchestrator_config)
            result = orchestrator.run()
            
            assert result.success is True
            assert result.status == OrchestratorStatus.COMPLETED
