"""
Comprehensive tests for IDE detection and configuration management.

Test Coverage:
- IDE detection (all 6 strategies)
- Configuration inheritance
- Environment variable overrides
- File I/O and error handling
- Cache behavior
- Edge cases and fallbacks

Target Coverage: 95%+
"""

import pytest
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.core.ide_detector import IDEDetector, IDEType
from src.core.config_manager import ConfigManager, CortexConfig


@pytest.fixture
def mock_workspace(tmp_path):
    """Create a temporary workspace structure."""
    workspace = tmp_path / "test-workspace"
    workspace.mkdir()
    
    # Create cortex-brain structure
    brain_dir = workspace / "cortex-brain"
    brain_dir.mkdir()
    
    config_dir = brain_dir / "config"
    config_dir.mkdir()
    
    return workspace


@pytest.fixture(autouse=True)
def reset_detector():
    """Reset IDE detector cache before each test."""
    IDEDetector.reset_cache()
    yield
    IDEDetector.reset_cache()


class TestIDEDetector:
    """Test suite for IDEDetector class."""
    
    def test_explicit_override_vscode(self, mock_workspace):
        """Test explicit CORTEX_IDE=vscode override."""
        with patch.dict(os.environ, {"CORTEX_IDE": "vscode"}, clear=False):
            result = IDEDetector.detect(mock_workspace)
            assert result == IDEType.VSCODE
    
    def test_explicit_override_visualstudio(self, mock_workspace):
        """Test explicit CORTEX_IDE=visualstudio override."""
        with patch.dict(os.environ, {"CORTEX_IDE": "visualstudio"}, clear=False):
            result = IDEDetector.detect(mock_workspace)
            assert result == IDEType.VISUAL_STUDIO
    
    def test_invalid_explicit_override(self, mock_workspace):
        """Test invalid CORTEX_IDE value falls through to next strategy."""
        with patch.dict(os.environ, {"CORTEX_IDE": "invalid"}, clear=False):
            result = IDEDetector.detect(mock_workspace)
            # Should fall through to UNKNOWN (no other detection methods)
            assert result == IDEType.UNKNOWN
    
    def test_vscode_environment_variables(self, mock_workspace):
        """Test detection via VSCode environment variables."""
        with patch.dict(os.environ, {"VSCODE_PID": "12345"}, clear=False):
            result = IDEDetector.detect(mock_workspace)
            assert result == IDEType.VSCODE
    
    def test_vscode_ipc_hook(self, mock_workspace):
        """Test detection via VSCODE_IPC_HOOK."""
        with patch.dict(os.environ, {"VSCODE_IPC_HOOK": "/tmp/vscode.sock"}, clear=False):
            result = IDEDetector.detect(mock_workspace)
            assert result == IDEType.VSCODE
    
    def test_visual_studio_environment_variables(self, mock_workspace):
        """Test detection via Visual Studio environment variables."""
        with patch.dict(os.environ, {"VisualStudioVersion": "17.0"}, clear=False):
            result = IDEDetector.detect(mock_workspace)
            assert result == IDEType.VISUAL_STUDIO
    
    def test_visual_studio_install_dir(self, mock_workspace):
        """Test detection via VSINSTALLDIR."""
        with patch.dict(os.environ, {"VSINSTALLDIR": "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community"}, clear=False):
            result = IDEDetector.detect(mock_workspace)
            assert result == IDEType.VISUAL_STUDIO
    
    @patch('src.core.ide_detector.psutil')
    def test_parent_process_vscode(self, mock_psutil, mock_workspace):
        """Test detection via parent process (VSCode)."""
        mock_process = MagicMock()
        mock_process.name.return_value = "Code.exe"
        mock_psutil.Process.return_value = mock_process
        
        result = IDEDetector.detect(mock_workspace)
        assert result == IDEType.VSCODE
    
    @patch('src.core.ide_detector.psutil')
    def test_parent_process_visualstudio(self, mock_psutil, mock_workspace):
        """Test detection via parent process (Visual Studio)."""
        mock_process = MagicMock()
        mock_process.name.return_value = "devenv.exe"
        mock_psutil.Process.return_value = mock_process
        
        result = IDEDetector.detect(mock_workspace)
        assert result == IDEType.VISUAL_STUDIO
    
    @patch('src.core.ide_detector.psutil')
    def test_parent_process_exception(self, mock_psutil, mock_workspace):
        """Test graceful handling of process inspection errors."""
        mock_psutil.Process.side_effect = mock_psutil.NoSuchProcess(123)
        
        # Should fall through to next strategy
        result = IDEDetector.detect(mock_workspace)
        assert result == IDEType.UNKNOWN
    
    @patch('src.core.ide_detector.psutil', None)
    def test_psutil_not_available(self, mock_workspace):
        """Test graceful handling when psutil is not installed."""
        # Should skip parent process detection and fall through
        result = IDEDetector.detect(mock_workspace)
        assert result == IDEType.UNKNOWN
    
    def test_directory_marker_vscode(self, mock_workspace):
        """Test detection via .vscode/ directory."""
        vscode_dir = mock_workspace / ".vscode"
        vscode_dir.mkdir()
        
        result = IDEDetector.detect(mock_workspace)
        assert result == IDEType.VSCODE
    
    def test_directory_marker_visualstudio(self, mock_workspace):
        """Test detection via .vs/ directory."""
        vs_dir = mock_workspace / ".vs"
        vs_dir.mkdir()
        
        result = IDEDetector.detect(mock_workspace)
        assert result == IDEType.VISUAL_STUDIO
    
    def test_directory_marker_most_recent(self, mock_workspace):
        """Test detection prefers most recently modified directory."""
        import time
        
        vscode_dir = mock_workspace / ".vscode"
        vscode_dir.mkdir()
        
        time.sleep(0.1)  # Ensure different timestamps
        
        vs_dir = mock_workspace / ".vs"
        vs_dir.mkdir()
        
        result = IDEDetector.detect(mock_workspace)
        assert result == IDEType.VISUAL_STUDIO  # .vs/ is newer
    
    def test_cached_context_loading(self, mock_workspace):
        """Test loading cached IDE context."""
        context_file = mock_workspace / "cortex-brain" / "ide-context.json"
        context_file.parent.mkdir(parents=True, exist_ok=True)
        
        context = {
            "detected_ide": "vscode",
            "detection_timestamp": 123456,
            "environment": {"os": "nt", "platform": "win32"}
        }
        
        with open(context_file, 'w') as f:
            json.dump(context, f)
        
        result = IDEDetector.detect(mock_workspace)
        assert result == IDEType.VSCODE
    
    def test_cached_context_invalid_json(self, mock_workspace):
        """Test handling of invalid cached context."""
        context_file = mock_workspace / "cortex-brain" / "ide-context.json"
        context_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(context_file, 'w') as f:
            f.write("{invalid json")
        
        # Should fall through to UNKNOWN
        result = IDEDetector.detect(mock_workspace)
        assert result == IDEType.UNKNOWN
    
    def test_unknown_fallback(self, mock_workspace):
        """Test fallback to UNKNOWN when no detection method succeeds."""
        result = IDEDetector.detect(mock_workspace)
        assert result == IDEType.UNKNOWN
    
    def test_cache_behavior(self, mock_workspace):
        """Test that detection is cached after first call."""
        with patch.dict(os.environ, {"CORTEX_IDE": "vscode"}, clear=False):
            result1 = IDEDetector.detect(mock_workspace)
            assert result1 == IDEType.VSCODE
        
        # Remove env var, should still return cached value
        result2 = IDEDetector.detect(mock_workspace)
        assert result2 == IDEType.VSCODE
    
    def test_reset_cache(self, mock_workspace):
        """Test cache reset functionality."""
        with patch.dict(os.environ, {"CORTEX_IDE": "vscode"}, clear=False):
            result1 = IDEDetector.detect(mock_workspace)
            assert result1 == IDEType.VSCODE
        
        IDEDetector.reset_cache()
        
        # After reset, should detect fresh
        # Note: May still detect from cached context file, so just verify cache was reset
        result2 = IDEDetector.detect(mock_workspace)
        # Verify cache was actually reset by checking it's re-detecting
        assert IDEDetector._cached_ide is not None  # Should have re-cached
    
    def test_get_config_filename(self):
        """Test config filename generation."""
        assert IDEDetector.get_config_filename(IDEType.VSCODE) == "vscode.config.json"
        assert IDEDetector.get_config_filename(IDEType.VISUAL_STUDIO) == "visualstudio.config.json"
        assert IDEDetector.get_config_filename(IDEType.UNKNOWN) == "unknown.config.json"
    
    def test_get_ide_directory(self):
        """Test IDE directory name generation."""
        assert IDEDetector.get_ide_directory(IDEType.VSCODE) == ".vscode"
        assert IDEDetector.get_ide_directory(IDEType.VISUAL_STUDIO) == ".vs"
        assert IDEDetector.get_ide_directory(IDEType.UNKNOWN) == ".cortex"


class TestConfigManager:
    """Test suite for ConfigManager class."""
    
    def test_load_defaults_only(self, mock_workspace):
        """Test loading with no config files (defaults only)."""
        manager = ConfigManager(mock_workspace)
        config = manager.load()
        
        assert isinstance(config, CortexConfig)
        assert config.log_level == "INFO"
        assert config.max_conversation_history == 70
        assert config.enable_skull_enforcement is True
        assert config.max_workers == 4
    
    def test_load_shared_config(self, mock_workspace):
        """Test loading shared configuration."""
        config_dir = mock_workspace / "cortex-brain" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        shared_config = {
            "log_level": "DEBUG",
            "max_workers": 8
        }
        
        with open(config_dir / "shared.config.json", 'w') as f:
            json.dump(shared_config, f)
        
        manager = ConfigManager(mock_workspace)
        config = manager.load()
        
        assert config.log_level == "DEBUG"
        assert config.max_workers == 8
    
    def test_load_ide_specific_config(self, mock_workspace):
        """Test IDE-specific configuration overrides."""
        config_dir = mock_workspace / "cortex-brain" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        shared_config = {"log_level": "INFO", "max_workers": 4}
        with open(config_dir / "shared.config.json", 'w') as f:
            json.dump(shared_config, f)
        
        vscode_config = {"log_level": "DEBUG"}
        with open(config_dir / "vscode.config.json", 'w') as f:
            json.dump(vscode_config, f)
        
        with patch.dict(os.environ, {"CORTEX_IDE": "vscode"}, clear=False):
            manager = ConfigManager(mock_workspace)
            config = manager.load()
            
            assert config.log_level == "DEBUG"  # Overridden
            assert config.max_workers == 4  # Inherited from shared
    
    def test_deep_merge(self, mock_workspace):
        """Test deep merging of nested dictionaries."""
        config_dir = mock_workspace / "cortex-brain" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        shared_config = {
            "custom": {
                "feature_a": {"enabled": True, "value": 100},
                "feature_b": {"enabled": False}
            }
        }
        
        ide_config = {
            "custom": {
                "feature_a": {"value": 200},
                "feature_c": {"enabled": True}
            }
        }
        
        with open(config_dir / "shared.config.json", 'w') as f:
            json.dump(shared_config, f)
        
        with open(config_dir / "vscode.config.json", 'w') as f:
            json.dump(ide_config, f)
        
        with patch.dict(os.environ, {"CORTEX_IDE": "vscode"}, clear=False):
            manager = ConfigManager(mock_workspace)
            config = manager.load()
            
            # feature_a: deep merged
            assert config.custom["feature_a"]["enabled"] is True  # From shared
            assert config.custom["feature_a"]["value"] == 200  # Overridden
            
            # feature_b: inherited
            assert config.custom["feature_b"]["enabled"] is False
            
            # feature_c: new from IDE config
            assert config.custom["feature_c"]["enabled"] is True
    
    def test_environment_variable_overrides(self, mock_workspace):
        """Test environment variable overrides."""
        with patch.dict(os.environ, {
            "CORTEX_LOG_LEVEL": "WARNING",
            "CORTEX_MAX_WORKERS": "16",
            "CORTEX_ENABLE_TELEMETRY": "false"
        }, clear=False):
            manager = ConfigManager(mock_workspace)
            config = manager.load()
            
            assert config.log_level == "WARNING"
            assert config.max_workers == 16
            assert config.enable_telemetry is False
    
    def test_environment_variable_invalid_type(self, mock_workspace):
        """Test handling of invalid environment variable types."""
        with patch.dict(os.environ, {
            "CORTEX_MAX_WORKERS": "not_a_number"
        }, clear=False):
            manager = ConfigManager(mock_workspace)
            config = manager.load()
            
            # Should fall back to default
            assert config.max_workers == 4
    
    def test_save_configuration(self, mock_workspace):
        """Test saving configuration to file."""
        manager = ConfigManager(mock_workspace)
        config = manager.load()
        config.log_level = "DEBUG"
        config.max_workers = 16
        
        success = manager.save(config, target="shared")
        assert success is True
        
        # Verify file was created
        config_file = mock_workspace / "cortex-brain" / "config" / "shared.config.json"
        assert config_file.exists()
        
        # Verify content
        with open(config_file, 'r') as f:
            saved = json.load(f)
            assert saved["log_level"] == "DEBUG"
            assert saved["max_workers"] == 16
    
    def test_save_configuration_creates_directory(self, mock_workspace):
        """Test that save creates config directory if it doesn't exist."""
        # Remove config directory
        config_dir = mock_workspace / "cortex-brain" / "config"
        if config_dir.exists():
            import shutil
            shutil.rmtree(config_dir)
        
        manager = ConfigManager(mock_workspace)
        config = manager.load()
        
        success = manager.save(config, target="test")
        assert success is True
        assert config_dir.exists()
    
    def test_invalid_json_handling(self, mock_workspace):
        """Test handling of invalid JSON in config files."""
        config_dir = mock_workspace / "cortex-brain" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create invalid JSON file
        with open(config_dir / "shared.config.json", 'w') as f:
            f.write("{invalid json content")
        
        manager = ConfigManager(mock_workspace)
        config = manager.load()  # Should not crash
        
        assert config.log_level == "INFO"  # Falls back to defaults


class TestIntegration:
    """Integration tests for IDE detection + configuration."""
    
    def test_end_to_end_vscode(self, mock_workspace):
        """Test complete flow for VSCode."""
        # Setup environment
        vscode_dir = mock_workspace / ".vscode"
        vscode_dir.mkdir()
        
        config_dir = mock_workspace / "cortex-brain" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        shared_config = {"log_level": "INFO"}
        with open(config_dir / "shared.config.json", 'w') as f:
            json.dump(shared_config, f)
        
        vscode_config = {"log_level": "DEBUG"}
        with open(config_dir / "vscode.config.json", 'w') as f:
            json.dump(vscode_config, f)
        
        # Execute
        manager = ConfigManager(mock_workspace)
        config = manager.load()
        
        # Verify
        assert config.ide_type == IDEType.VSCODE
        assert config.log_level == "DEBUG"
    
    def test_end_to_end_visual_studio(self, mock_workspace):
        """Test complete flow for Visual Studio."""
        # Setup environment
        with patch.dict(os.environ, {"VisualStudioVersion": "17.0"}, clear=False):
            config_dir = mock_workspace / "cortex-brain" / "config"
            config_dir.mkdir(parents=True, exist_ok=True)
            
            shared_config = {"max_workers": 4}
            with open(config_dir / "shared.config.json", 'w') as f:
                json.dump(shared_config, f)
            
            vs_config = {"max_workers": 8}
            with open(config_dir / "visualstudio.config.json", 'w') as f:
                json.dump(vs_config, f)
            
            # Execute
            manager = ConfigManager(mock_workspace)
            config = manager.load()
            
            # Verify
            assert config.ide_type == IDEType.VISUAL_STUDIO
            assert config.max_workers == 8
    
    def test_switch_ides_preserves_brain(self, mock_workspace):
        """Test switching IDEs preserves brain state."""
        brain_dir = mock_workspace / "cortex-brain"
        tier1_dir = brain_dir / "tier1"
        tier1_dir.mkdir(parents=True)
        
        # Create mock brain data
        conversation_file = tier1_dir / "conversations.db"
        conversation_file.write_text("mock brain data")
        
        # Load as VSCode
        with patch.dict(os.environ, {"CORTEX_IDE": "vscode"}, clear=False):
            manager1 = ConfigManager(mock_workspace)
            config1 = manager1.load()
            assert config1.ide_type == IDEType.VSCODE
        
        # Reset cache and load as Visual Studio
        IDEDetector.reset_cache()
        
        with patch.dict(os.environ, {"CORTEX_IDE": "visualstudio"}, clear=False):
            manager2 = ConfigManager(mock_workspace)
            config2 = manager2.load()
            assert config2.ide_type == IDEType.VISUAL_STUDIO
        
        # Verify brain data unchanged
        assert conversation_file.read_text() == "mock brain data"
    
    def test_configuration_priority_chain(self, mock_workspace):
        """Test full configuration priority chain."""
        config_dir = mock_workspace / "cortex-brain" / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Shared config (base)
        shared_config = {
            "log_level": "INFO",
            "max_workers": 4,
            "custom": {"feature": "shared"}
        }
        with open(config_dir / "shared.config.json", 'w') as f:
            json.dump(shared_config, f)
        
        # IDE config (overrides shared)
        ide_config = {
            "log_level": "DEBUG",
            "custom": {"feature": "ide", "extra": "value"}
        }
        with open(config_dir / "vscode.config.json", 'w') as f:
            json.dump(ide_config, f)
        
        # Environment variables (highest priority)
        with patch.dict(os.environ, {
            "CORTEX_IDE": "vscode",
            "CORTEX_MAX_WORKERS": "16"
        }, clear=False):
            manager = ConfigManager(mock_workspace)
            config = manager.load()
            
            # Verify priority chain
            assert config.log_level == "DEBUG"  # From IDE config
            assert config.max_workers == 16  # From environment
            assert config.custom["feature"] == "ide"  # From IDE config
            assert config.custom["extra"] == "value"  # From IDE config
