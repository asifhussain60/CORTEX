"""
Tests for Testing Infrastructure

Validates pytest fixtures, mock factories, and test utilities.

Copyright © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch

from tests.utils import (
    MockFactory,
    TempWorkspaceManager,
    ConfigFileBuilder,
    AssertionHelpers,
    TestIsolation,
    create_cortex_config,
    create_orchestrator_result,
    create_config_dict
)
from src.core.config_manager import CortexConfig
from src.core.ide_detector import IDEType
from src.orchestrators.base.base_orchestrator import OrchestratorStatus, OrchestratorResult


# ============================================================================
# FIXTURE TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.cortex_v4
class TestCortexFixtures:
    """Test CORTEX 4.0 pytest fixtures"""
    
    def test_cortex_workspace_structure(self, cortex_workspace):
        """Test that cortex_workspace fixture creates correct structure"""
        assert cortex_workspace.exists()
        assert (cortex_workspace / "cortex-brain").exists()
        
        # Check brain tiers
        for tier in ["tier0", "tier1", "tier2", "tier3"]:
            assert (cortex_workspace / "cortex-brain" / tier).exists()
        
        # Check config directory
        assert (cortex_workspace / "cortex-brain" / "config").exists()
        
        # Check document categories
        docs = cortex_workspace / "cortex-brain" / "documents"
        for category in ["reports", "analysis", "summaries", "investigations", "planning", "implementation-guides"]:
            assert (docs / category).exists()
    
    def test_shared_config_fixture(self, cortex_workspace, shared_config):
        """Test that shared_config fixture creates valid config"""
        config_file = cortex_workspace / "cortex-brain" / "config" / "shared.config.json"
        assert config_file.exists()
        
        # Verify content
        assert "brain" in shared_config
        assert shared_config["brain"]["max_conversations"] == 70
        assert shared_config["brain"]["tdd_enforcement"] is True
    
    def test_vscode_config_fixture(self, cortex_workspace, vscode_config):
        """Test that vscode_config fixture creates valid config"""
        config_file = cortex_workspace / "cortex-brain" / "config" / "vscode.config.json"
        assert config_file.exists()
        
        # Verify content
        assert "brain" in vscode_config
        assert vscode_config["brain"]["max_conversations"] == 100
        assert vscode_config["ide"]["integration_mode"] == "copilot_chat"
    
    def test_config_manager_fixture(self, config_manager):
        """Test that config_manager fixture creates valid manager"""
        assert config_manager is not None
        assert config_manager.workspace_root.exists()
    
    def test_cortex_config_fixture(self, cortex_config):
        """Test that cortex_config fixture loads configuration"""
        assert isinstance(cortex_config, CortexConfig)
        assert cortex_config.workspace_root.exists()
        assert cortex_config.log_level in ["DEBUG", "INFO", "WARNING", "ERROR"]
    
    def test_orchestrator_phases_fixture(self, mock_orchestrator):
        """Test that mock_orchestrator fixture creates valid orchestrator"""
        assert mock_orchestrator.name == "MockOrchestrator"
        assert mock_orchestrator.workspace_root.exists()
    
    def test_mock_orchestrator_fixture(self, mock_orchestrator):
        """Test that mock_orchestrator can execute"""
        result = mock_orchestrator.execute()
        assert result.success is True
        assert result.status == OrchestratorStatus.COMPLETED


# ============================================================================
# MOCK FACTORY TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.cortex_v4
class TestMockFactory:
    """Test MockFactory utilities"""
    
    def test_create_cortex_config(self, tmp_path):
        """Test CortexConfig creation"""
        config = MockFactory.create_cortex_config(
            workspace_root=tmp_path,
            log_level="DEBUG",
            max_conversation_history=50
        )
        
        assert isinstance(config, CortexConfig)
        assert config.workspace_root == tmp_path
        assert config.log_level == "DEBUG"
        assert config.max_conversation_history == 50
    
    def test_create_orchestrator_result(self):
        """Test OrchestratorResult creation"""
        result = MockFactory.create_orchestrator_result(
            status=OrchestratorStatus.COMPLETED,
            success=True,
            message="Test completed"
        )
        
        assert isinstance(result, OrchestratorResult)
        assert result.status == OrchestratorStatus.COMPLETED
        assert result.success is True
        assert result.message == "Test completed"
    
    def test_create_config_dict(self, tmp_path):
        """Test configuration dict creation"""
        config = MockFactory.create_config_dict(
            workspace_root=tmp_path,
            brain={"max_conversations": 150}
        )
        
        assert "brain" in config
        assert config["brain"]["max_conversations"] == 150
        assert "orchestrator" in config
    
    def test_convenience_exports(self, tmp_path):
        """Test that convenience exports work"""
        config = create_cortex_config(workspace_root=tmp_path)
        assert isinstance(config, CortexConfig)
        
        result = create_orchestrator_result()
        assert isinstance(result, OrchestratorResult)
        
        config_dict = create_config_dict(workspace_root=tmp_path)
        assert isinstance(config_dict, dict)


# ============================================================================
# TEMP WORKSPACE MANAGER TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.cortex_v4
class TestTempWorkspaceManager:
    """Test TempWorkspaceManager context manager"""
    
    def test_context_manager_creates_workspace(self):
        """Test workspace creation via context manager"""
        with TempWorkspaceManager() as workspace:
            assert workspace.exists()
            assert (workspace / "cortex-brain").exists()
    
    def test_context_manager_cleanup(self):
        """Test workspace cleanup after context manager"""
        workspace_path = None
        with TempWorkspaceManager() as workspace:
            workspace_path = workspace
            assert workspace.exists()
        
        # After context manager, workspace should be cleaned up
        assert not workspace_path.exists()
    
    def test_brain_structure_created(self):
        """Test that brain structure is created correctly"""
        with TempWorkspaceManager() as workspace:
            brain = workspace / "cortex-brain"
            
            # Check tiers
            for tier in ["tier0", "tier1", "tier2", "tier3"]:
                assert (brain / tier).exists()
            
            # Check config
            assert (brain / "config").exists()
            
            # Check documents
            docs = brain / "documents"
            assert (docs / "reports").exists()
            assert (docs / "analysis").exists()


# ============================================================================
# CONFIG FILE BUILDER TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.cortex_v4
class TestConfigFileBuilder:
    """Test ConfigFileBuilder"""
    
    def test_add_shared_config(self, temp_config_dir):
        """Test adding shared config"""
        builder = ConfigFileBuilder(temp_config_dir)
        config = {"brain": {"max_conversations": 70}}
        
        builder.add_shared_config(config)
        
        config_file = temp_config_dir / "shared.config.json"
        assert config_file.exists()
        
        loaded = json.loads(config_file.read_text())
        assert loaded["brain"]["max_conversations"] == 70
    
    def test_add_vscode_config(self, temp_config_dir):
        """Test adding VSCode config"""
        builder = ConfigFileBuilder(temp_config_dir)
        config = {"ide": {"integration_mode": "copilot_chat"}}
        
        builder.add_vscode_config(config)
        
        config_file = temp_config_dir / "vscode.config.json"
        assert config_file.exists()
    
    def test_add_visualstudio_config(self, temp_config_dir):
        """Test adding Visual Studio config"""
        builder = ConfigFileBuilder(temp_config_dir)
        config = {"ide": {"integration_mode": "extension"}}
        
        builder.add_visualstudio_config(config)
        
        config_file = temp_config_dir / "visualstudio.config.json"
        assert config_file.exists()
    
    def test_add_corrupted_config(self, temp_config_dir):
        """Test adding corrupted config for error testing"""
        builder = ConfigFileBuilder(temp_config_dir)
        
        builder.add_corrupted_config("corrupted.json")
        
        config_file = temp_config_dir / "corrupted.json"
        assert config_file.exists()
        
        # Should not be valid JSON
        with pytest.raises(json.JSONDecodeError):
            json.loads(config_file.read_text())
    
    def test_builder_chaining(self, temp_config_dir):
        """Test builder method chaining"""
        builder = ConfigFileBuilder(temp_config_dir)
        
        builder \
            .add_shared_config({"brain": {"max_conversations": 70}}) \
            .add_vscode_config({"ide": {"integration_mode": "copilot_chat"}})
        
        assert (temp_config_dir / "shared.config.json").exists()
        assert (temp_config_dir / "vscode.config.json").exists()


# ============================================================================
# ASSERTION HELPERS TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.cortex_v4
class TestAssertionHelpers:
    """Test AssertionHelpers"""
    
    def test_assert_config_has_keys(self):
        """Test config key assertion"""
        config = {"key1": "value1", "key2": "value2"}
        
        # Should not raise
        AssertionHelpers.assert_config_has_keys(config, "key1", "key2")
        
        # Should raise
        with pytest.raises(AssertionError, match="Config missing key: key3"):
            AssertionHelpers.assert_config_has_keys(config, "key3")
    
    def test_assert_path_exists(self, tmp_path):
        """Test path existence assertion"""
        existing_path = tmp_path / "test.txt"
        existing_path.touch()
        
        # Should not raise
        AssertionHelpers.assert_path_exists(existing_path)
        
        # Should raise
        non_existing = tmp_path / "nonexistent.txt"
        with pytest.raises(AssertionError, match="Path does not exist"):
            AssertionHelpers.assert_path_exists(non_existing)
    
    def test_assert_file_contains(self, tmp_path):
        """Test file content assertion"""
        file_path = tmp_path / "test.txt"
        file_path.write_text("Hello World")
        
        # Should not raise
        AssertionHelpers.assert_file_contains(file_path, "Hello")
        
        # Should raise
        with pytest.raises(AssertionError, match="File does not contain"):
            AssertionHelpers.assert_file_contains(file_path, "Goodbye")
    
    def test_assert_orchestrator_success(self):
        """Test orchestrator success assertion"""
        result_success = create_orchestrator_result(success=True, status=OrchestratorStatus.COMPLETED)
        
        # Should not raise
        AssertionHelpers.assert_orchestrator_success(result_success)
        
        # Should raise
        result_failure = create_orchestrator_result(success=False, status=OrchestratorStatus.FAILED)
        with pytest.raises(AssertionError, match="Orchestrator failed"):
            AssertionHelpers.assert_orchestrator_success(result_failure)
    
    def test_assert_no_errors(self):
        """Test no errors assertion"""
        result_no_errors = create_orchestrator_result(errors=[])
        
        # Should not raise
        AssertionHelpers.assert_no_errors(result_no_errors)
        
        # Should raise
        result_with_errors = create_orchestrator_result(errors=["Error 1"])
        with pytest.raises(AssertionError, match="Orchestrator has errors"):
            AssertionHelpers.assert_no_errors(result_with_errors)


# ============================================================================
# TEST ISOLATION TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.cortex_v4
class TestTestIsolation:
    """Test TestIsolation utilities"""
    
    def test_clear_environment_vars(self):
        """Test environment variable clearing"""
        import os
        
        # Set test env vars
        os.environ["TEST_VAR_1"] = "value1"
        os.environ["TEST_VAR_2"] = "value2"
        
        # Clear them
        TestIsolation.clear_environment_vars("TEST_VAR_1", "TEST_VAR_2")
        
        # Verify cleared
        assert "TEST_VAR_1" not in os.environ
        assert "TEST_VAR_2" not in os.environ
    
    def test_cleanup_temp_files(self, tmp_path):
        """Test temporary file cleanup"""
        # Create test files
        test_file = tmp_path / "test.txt"
        test_file.touch()
        
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        (test_dir / "nested.txt").touch()
        
        # Cleanup
        TestIsolation.cleanup_temp_files(test_file, test_dir)
        
        # Verify cleaned
        assert not test_file.exists()
        assert not test_dir.exists()


# ============================================================================
# IDE DETECTOR MOCK TESTS
# ============================================================================

@pytest.mark.unit
@pytest.mark.cortex_v4
@pytest.mark.requires_ide
class TestIDEDetectorMocks:
    """Test IDE detector mock fixtures"""
    
    def test_mock_ide_detector_vscode(self, mock_ide_detector_vscode):
        """Test VSCode mock"""
        assert mock_ide_detector_vscode == IDEType.VSCODE
    
    def test_mock_ide_detector_visualstudio(self, mock_ide_detector_visualstudio):
        """Test Visual Studio mock"""
        assert mock_ide_detector_visualstudio == IDEType.VISUAL_STUDIO
    
    def test_mock_ide_detector_unknown(self, mock_ide_detector_unknown):
        """Test Unknown IDE mock"""
        assert mock_ide_detector_unknown == IDEType.UNKNOWN


# ============================================================================
# CACHE RESET FIXTURE TEST
# ============================================================================

@pytest.mark.unit
@pytest.mark.cortex_v4
class TestCacheResetFixture:
    """Test reset_ide_detector_cache fixture"""
    
    def test_cache_reset_before_test(self, reset_ide_detector_cache, tmp_path):
        """Test that cache is reset before test"""
        from src.core.ide_detector import IDEDetector
        
        # Cache should be empty at start
        with patch.dict('os.environ', {"CORTEX_IDE": "vscode"}, clear=True):
            result = IDEDetector.detect(tmp_path)
            assert result == IDEType.VSCODE
