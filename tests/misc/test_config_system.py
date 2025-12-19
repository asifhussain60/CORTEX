"""
Comprehensive tests for IDE detection and configuration management system.

Tests the complete configuration workflow:
1. IDE detection (6 strategies)
2. Configuration inheritance (shared → IDE-specific → env vars)
3. Deep merging
4. Cache management
5. Error handling

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import json
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest
import psutil

from src.core.ide_detector import IDEDetector, IDEType
from src.core.config_manager import ConfigManager


# ============================================================================
# IDE DETECTOR TESTS
# ============================================================================


class TestIDEDetector:
    """Test suite for IDEDetector (class-method based implementation)"""
    
    def setup_method(self):
        """Reset cache before each test"""
        IDEDetector.reset_cache()
    
    # ------------------------------------------------------------------------
    # Strategy 1: Explicit Override (CORTEX_IDE)
    # ------------------------------------------------------------------------
    
    def test_explicit_vscode_override(self, tmp_path):
        """Test CORTEX_IDE=vscode override"""
        with patch.dict(os.environ, {"CORTEX_IDE": "vscode"}, clear=True):
            result = IDEDetector.detect(tmp_path)
            assert result == IDEType.VSCODE
    
    def test_explicit_visualstudio_override(self, tmp_path):
        """Test CORTEX_IDE=visualstudio override"""
        with patch.dict(os.environ, {"CORTEX_IDE": "visualstudio"}, clear=True):
            result = IDEDetector.detect(tmp_path)
            assert result == IDEType.VISUAL_STUDIO
    
    def test_invalid_cortex_ide_ignored(self, tmp_path):
        """Test invalid CORTEX_IDE value continues to next strategy"""
        with patch.dict(os.environ, {"CORTEX_IDE": "invalid_ide"}, clear=True):
            result = IDEDetector.detect(tmp_path)
            # Should fall through to UNKNOWN
            assert result == IDEType.UNKNOWN
    
    # ------------------------------------------------------------------------
    # Strategy 2: IDE-Specific Environment Variables
    # ------------------------------------------------------------------------
    
    def test_vscode_detection_via_vscode_pid(self, tmp_path):
        """Test VSCode detection via VSCODE_PID"""
        with patch.dict(os.environ, {"VSCODE_PID": "12345"}, clear=True):
            result = IDEDetector.detect(tmp_path)
            assert result == IDEType.VSCODE
    
    def test_vscode_detection_via_ipc_hook(self, tmp_path):
        """Test VSCode detection via VSCODE_IPC_HOOK"""
        with patch.dict(os.environ, {"VSCODE_IPC_HOOK": "/tmp/vscode-ipc.sock"}, clear=True):
            result = IDEDetector.detect(tmp_path)
            assert result == IDEType.VSCODE
    
    def test_visualstudio_detection_via_version(self, tmp_path):
        """Test Visual Studio detection via VisualStudioVersion"""
        with patch.dict(os.environ, {"VisualStudioVersion": "17.0"}, clear=True):
            result = IDEDetector.detect(tmp_path)
            assert result == IDEType.VISUAL_STUDIO
    
    def test_visualstudio_detection_via_installdir(self, tmp_path):
        """Test Visual Studio detection via VSINSTALLDIR"""
        with patch.dict(os.environ, {"VSINSTALLDIR": "C:\\Program Files\\Microsoft Visual Studio\\2022"}, clear=True):
            result = IDEDetector.detect(tmp_path)
            assert result == IDEType.VISUAL_STUDIO
    
    # ------------------------------------------------------------------------
    # Strategy 3: Parent Process Detection
    # ------------------------------------------------------------------------
    
    @patch("psutil.Process")
    def test_vscode_via_parent_process_code(self, mock_process_class, tmp_path):
        """Test VSCode detection via Code.exe parent process"""
        mock_parent = Mock()
        mock_parent.name.return_value = "Code.exe"
        mock_process_class.return_value = mock_parent
        
        with patch.dict(os.environ, {}, clear=True):
            with patch("os.getppid", return_value=9999):
                result = IDEDetector.detect(tmp_path)
                assert result == IDEType.VSCODE
    
    @patch("psutil.Process")
    def test_visualstudio_via_parent_process_devenv(self, mock_process_class, tmp_path):
        """Test Visual Studio detection via devenv.exe parent process"""
        mock_parent = Mock()
        mock_parent.name.return_value = "devenv.exe"
        mock_process_class.return_value = mock_parent
        
        with patch.dict(os.environ, {}, clear=True):
            with patch("os.getppid", return_value=9999):
                result = IDEDetector.detect(tmp_path)
                assert result == IDEType.VISUAL_STUDIO
    
    @patch("psutil.Process")
    def test_psutil_error_continues_gracefully(self, mock_process_class, tmp_path):
        """Test that psutil errors don't crash, continue to next strategy"""
        mock_process_class.side_effect = psutil.NoSuchProcess(1234)
        
        with patch.dict(os.environ, {}, clear=True):
            result = IDEDetector.detect(tmp_path)
            # Should default to UNKNOWN after all strategies fail
            assert result == IDEType.UNKNOWN
    
    # ------------------------------------------------------------------------
    # Strategy 4: Directory Markers
    # ------------------------------------------------------------------------
    
    def test_vscode_directory_marker(self, tmp_path):
        """Test VSCode detection via .vscode directory"""
        vscode_dir = tmp_path / ".vscode"
        vscode_dir.mkdir()
        
        with patch.dict(os.environ, {}, clear=True):
            with patch("psutil.Process", side_effect=psutil.NoSuchProcess(1)):
                result = IDEDetector.detect(tmp_path)
                assert result == IDEType.VSCODE
    
    def test_visualstudio_directory_marker(self, tmp_path):
        """Test Visual Studio detection via .vs directory"""
        vs_dir = tmp_path / ".vs"
        vs_dir.mkdir()
        
        with patch.dict(os.environ, {}, clear=True):
            with patch("psutil.Process", side_effect=psutil.NoSuchProcess(1)):
                result = IDEDetector.detect(tmp_path)
                assert result == IDEType.VISUAL_STUDIO
    
    def test_most_recent_directory_wins(self, tmp_path):
        """Test that most recently modified directory marker wins"""
        import time
        
        vs_dir = tmp_path / ".vs"
        vs_dir.mkdir()
        time.sleep(0.1)  # Ensure different timestamps
        
        vscode_dir = tmp_path / ".vscode"
        vscode_dir.mkdir()
        
        with patch.dict(os.environ, {}, clear=True):
            with patch("psutil.Process", side_effect=psutil.NoSuchProcess(1)):
                result = IDEDetector.detect(tmp_path)
                # VSCode should win (more recent)
                assert result == IDEType.VSCODE
    
    # ------------------------------------------------------------------------
    # Strategy 5: Cached Context
    # ------------------------------------------------------------------------
    
    def test_cache_persists_across_calls(self, tmp_path):
        """Test that detection is cached after first call"""
        vscode_dir = tmp_path / ".vscode"
        vscode_dir.mkdir()
        
        with patch.dict(os.environ, {}, clear=True):
            with patch("psutil.Process", side_effect=psutil.NoSuchProcess(1)):
                # First call detects from directory
                result1 = IDEDetector.detect(tmp_path)
                assert result1 == IDEType.VSCODE
                
                # Remove directory
                vscode_dir.rmdir()
                
                # Second call should use cached value
                result2 = IDEDetector.detect(tmp_path)
                assert result2 == IDEType.VSCODE
    
    def test_saved_context_file_loaded(self, tmp_path):
        """Test that saved IDE context is loaded from file"""
        # Manually create context file
        context_dir = tmp_path / "cortex-brain"
        context_dir.mkdir()
        context_file = context_dir / "ide-context.json"
        context_file.write_text(json.dumps({
            "detected_ide": "visualstudio",
            "detection_time": 1234567890
        }))
        
        with patch.dict(os.environ, {}, clear=True):
            with patch("psutil.Process", side_effect=psutil.NoSuchProcess(1)):
                result = IDEDetector.detect(tmp_path)
                assert result == IDEType.VISUAL_STUDIO
    
    def test_corrupted_context_file_ignored(self, tmp_path):
        """Test that corrupted context file is ignored gracefully"""
        context_dir = tmp_path / "cortex-brain"
        context_dir.mkdir()
        context_file = context_dir / "ide-context.json"
        context_file.write_text("CORRUPTED{{{")
        
        with patch.dict(os.environ, {}, clear=True):
            with patch("psutil.Process", side_effect=psutil.NoSuchProcess(1)):
                result = IDEDetector.detect(tmp_path)
                assert result == IDEType.UNKNOWN
    
    # ------------------------------------------------------------------------
    # Strategy 6: Default to Unknown
    # ------------------------------------------------------------------------
    
    def test_unknown_when_all_strategies_fail(self, tmp_path):
        """Test UNKNOWN returned when all detection strategies fail"""
        with patch.dict(os.environ, {}, clear=True):
            with patch("psutil.Process", side_effect=psutil.NoSuchProcess(1)):
                result = IDEDetector.detect(tmp_path)
                assert result == IDEType.UNKNOWN
    
    # ------------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------------
    
    def test_get_config_filename(self):
        """Test get_config_filename returns correct filenames"""
        assert IDEDetector.get_config_filename(IDEType.VSCODE) == "vscode.config.json"
        assert IDEDetector.get_config_filename(IDEType.VISUAL_STUDIO) == "visualstudio.config.json"
        assert IDEDetector.get_config_filename(IDEType.UNKNOWN) == "unknown.config.json"
    
    def test_get_ide_directory(self):
        """Test get_ide_directory returns correct directory names"""
        assert IDEDetector.get_ide_directory(IDEType.VSCODE) == ".vscode"
        assert IDEDetector.get_ide_directory(IDEType.VISUAL_STUDIO) == ".vs"
        assert IDEDetector.get_ide_directory(IDEType.UNKNOWN) == ".cortex"
    
    def test_reset_cache(self, tmp_path):
        """Test reset_cache clears cached IDE"""
        with patch.dict(os.environ, {"CORTEX_IDE": "vscode"}, clear=True):
            result1 = IDEDetector.detect(tmp_path)
            assert result1 == IDEType.VSCODE
        
        IDEDetector.reset_cache()
        
        with patch.dict(os.environ, {"CORTEX_IDE": "visualstudio"}, clear=True):
            result2 = IDEDetector.detect(tmp_path)
            assert result2 == IDEType.VISUAL_STUDIO


# ============================================================================
# CONFIG MANAGER TESTS
# ============================================================================


class TestConfigManager:
    """Test suite for ConfigManager with inheritance and deep merging"""
    
    def setup_method(self):
        """Reset IDE detector cache before each test"""
        IDEDetector.reset_cache()
    
    # ------------------------------------------------------------------------
    # Configuration Loading
    # ------------------------------------------------------------------------
    
    def test_load_shared_config_only_when_unknown_ide(self, tmp_path):
        """Test loading shared config when IDE is unknown"""
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {
            "brain": {"max_conversations": 70, "tdd_enforcement": True},
            "orchestrator": {"auto_cleanup": True}
        }
        (config_dir / "shared.config.json").write_text(json.dumps(shared_config))
        
        with patch.dict(os.environ, {}, clear=True):
            with patch("psutil.Process", side_effect=psutil.NoSuchProcess(1)):
                manager = ConfigManager(workspace_root=str(tmp_path))
                config = manager.load()
                
                assert config["brain"]["max_conversations"] == 70
                assert config["brain"]["tdd_enforcement"] is True
                assert config["orchestrator"]["auto_cleanup"] is True
    
    def test_vscode_config_overrides_shared(self, tmp_path):
        """Test VSCode config overrides shared config"""
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {
            "brain": {"max_conversations": 70},
            "orchestrator": {"auto_cleanup": True}
        }
        vscode_config = {
            "brain": {"max_conversations": 100},
            "ide": {"integration_mode": "copilot_chat"}
        }
        
        (config_dir / "shared.config.json").write_text(json.dumps(shared_config))
        (config_dir / "vscode.config.json").write_text(json.dumps(vscode_config))
        
        with patch.dict(os.environ, {"CORTEX_IDE": "vscode"}, clear=True):
            manager = ConfigManager(workspace_root=str(tmp_path))
            config = manager.load()
            
            assert config["brain"]["max_conversations"] == 100  # VSCode override
            assert config["orchestrator"]["auto_cleanup"] is True  # Shared preserved
            assert config["ide"]["integration_mode"] == "copilot_chat"  # VSCode-specific
    
    def test_visualstudio_config_overrides_shared(self, tmp_path):
        """Test Visual Studio config overrides shared config"""
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {
            "brain": {"max_conversations": 70},
            "orchestrator": {"auto_cleanup": True}
        }
        vs_config = {
            "brain": {"max_conversations": 50},
            "ide": {"integration_mode": "extension"}
        }
        
        (config_dir / "shared.config.json").write_text(json.dumps(shared_config))
        (config_dir / "visualstudio.config.json").write_text(json.dumps(vs_config))
        
        with patch.dict(os.environ, {"CORTEX_IDE": "visualstudio"}, clear=True):
            manager = ConfigManager(workspace_root=str(tmp_path))
            config = manager.load()
            
            assert config["brain"]["max_conversations"] == 50
            assert config["orchestrator"]["auto_cleanup"] is True
            assert config["ide"]["integration_mode"] == "extension"
    
    # ------------------------------------------------------------------------
    # Deep Merge Logic
    # ------------------------------------------------------------------------
    
    def test_deep_merge_nested_dicts(self, tmp_path):
        """Test recursive deep merging of nested dictionaries"""
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {
            "brain": {
                "tier0": {"enforcement": "strict"},
                "tier1": {"max_conversations": 70, "fifo_enabled": False}
            }
        }
        vscode_config = {
            "brain": {
                "tier1": {"max_conversations": 100, "cache_size": 200}
            }
        }
        
        (config_dir / "shared.config.json").write_text(json.dumps(shared_config))
        (config_dir / "vscode.config.json").write_text(json.dumps(vscode_config))
        
        with patch.dict(os.environ, {"CORTEX_IDE": "vscode"}, clear=True):
            manager = ConfigManager(workspace_root=str(tmp_path))
            config = manager.load()
            
            # tier0 preserved from shared
            assert config["brain"]["tier0"]["enforcement"] == "strict"
            # tier1 max_conversations overridden
            assert config["brain"]["tier1"]["max_conversations"] == 100
            # tier1 fifo_enabled preserved from shared
            assert config["brain"]["tier1"]["fifo_enabled"] is False
            # tier1 cache_size added from VSCode
            assert config["brain"]["tier1"]["cache_size"] == 200
    
    def test_deep_merge_replaces_lists(self, tmp_path):
        """Test that lists are replaced, not merged"""
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {
            "orchestrator": {"enabled_phases": ["phase1", "phase2", "phase3"]}
        }
        vscode_config = {
            "orchestrator": {"enabled_phases": ["phase1", "phase4"]}
        }
        
        (config_dir / "shared.config.json").write_text(json.dumps(shared_config))
        (config_dir / "vscode.config.json").write_text(json.dumps(vscode_config))
        
        with patch.dict(os.environ, {"CORTEX_IDE": "vscode"}, clear=True):
            manager = ConfigManager(workspace_root=str(tmp_path))
            config = manager.load()
            
            # List completely replaced
            assert config["orchestrator"]["enabled_phases"] == ["phase1", "phase4"]
    
    # ------------------------------------------------------------------------
    # Environment Variable Overrides
    # ------------------------------------------------------------------------
    
    def test_env_var_overrides_max_conversations(self, tmp_path):
        """Test CORTEX_MAX_CONVERSATIONS env var override"""
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {"brain": {"max_conversations": 70}}
        (config_dir / "shared.config.json").write_text(json.dumps(shared_config))
        
        with patch.dict(os.environ, {"CORTEX_MAX_CONVERSATIONS": "150"}, clear=True):
            with patch("psutil.Process", side_effect=psutil.NoSuchProcess(1)):
                manager = ConfigManager(workspace_root=str(tmp_path))
                config = manager.load()
                
                assert config["brain"]["max_conversations"] == 150
    
    def test_env_var_overrides_tdd_enforcement(self, tmp_path):
        """Test CORTEX_TDD_ENFORCEMENT env var override"""
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {"brain": {"tdd_enforcement": True}}
        (config_dir / "shared.config.json").write_text(json.dumps(shared_config))
        
        with patch.dict(os.environ, {"CORTEX_TDD_ENFORCEMENT": "false"}, clear=True):
            with patch("psutil.Process", side_effect=psutil.NoSuchProcess(1)):
                manager = ConfigManager(workspace_root=str(tmp_path))
                config = manager.load()
                
                assert config["brain"]["tdd_enforcement"] is False
    
    def test_invalid_env_var_ignored(self, tmp_path):
        """Test that invalid env var values are ignored"""
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {"brain": {"max_conversations": 70}}
        (config_dir / "shared.config.json").write_text(json.dumps(shared_config))
        
        with patch.dict(os.environ, {"CORTEX_MAX_CONVERSATIONS": "INVALID"}, clear=True):
            with patch("psutil.Process", side_effect=psutil.NoSuchProcess(1)):
                manager = ConfigManager(workspace_root=str(tmp_path))
                config = manager.load()
                
                # Should keep original value
                assert config["brain"]["max_conversations"] == 70
    
    # ------------------------------------------------------------------------
    # Error Handling
    # ------------------------------------------------------------------------
    
    def test_missing_shared_config_raises_error(self, tmp_path):
        """Test that missing shared.config.json raises FileNotFoundError"""
        with patch.dict(os.environ, {}, clear=True):
            with patch("psutil.Process", side_effect=psutil.NoSuchProcess(1)):
                manager = ConfigManager(workspace_root=str(tmp_path))
                with pytest.raises(FileNotFoundError, match="shared.config.json"):
                    manager.load()
    
    def test_missing_ide_config_uses_shared_only(self, tmp_path):
        """Test that missing IDE config falls back to shared config"""
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {"brain": {"max_conversations": 70}}
        (config_dir / "shared.config.json").write_text(json.dumps(shared_config))
        
        with patch.dict(os.environ, {"CORTEX_IDE": "vscode"}, clear=True):
            manager = ConfigManager(workspace_root=str(tmp_path))
            config = manager.load()
            
            # Should use shared config
            assert config["brain"]["max_conversations"] == 70
    
    def test_corrupted_shared_config_raises_json_error(self, tmp_path):
        """Test that corrupted shared config raises JSON error"""
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        (config_dir / "shared.config.json").write_text("INVALID JSON{{{")
        
        with patch.dict(os.environ, {}, clear=True):
            with patch("psutil.Process", side_effect=psutil.NoSuchProcess(1)):
                manager = ConfigManager(workspace_root=str(tmp_path))
                with pytest.raises(json.JSONDecodeError):
                    manager.load()
    
    def test_corrupted_ide_config_uses_shared_only(self, tmp_path):
        """Test that corrupted IDE config falls back to shared config"""
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {"brain": {"max_conversations": 70}}
        (config_dir / "shared.config.json").write_text(json.dumps(shared_config))
        (config_dir / "vscode.config.json").write_text("CORRUPTED{{{")
        
        with patch.dict(os.environ, {"CORTEX_IDE": "vscode"}, clear=True):
            manager = ConfigManager(workspace_root=str(tmp_path))
            config = manager.load()
            
            # Should fall back to shared config
            assert config["brain"]["max_conversations"] == 70
    
    # ------------------------------------------------------------------------
    # End-to-End Integration
    # ------------------------------------------------------------------------
    
    def test_full_inheritance_chain(self, tmp_path):
        """Test complete inheritance: shared → IDE-specific → env vars"""
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {
            "brain": {
                "max_conversations": 70,
                "tdd_enforcement": True,
                "timeout": 30
            },
            "orchestrator": {
                "auto_cleanup": True,
                "phase_validation": "strict"
            }
        }
        vscode_config = {
            "brain": {
                "max_conversations": 100,
                "fifo_enabled": True
            },
            "ide": {
                "integration_mode": "copilot_chat"
            }
        }
        
        (config_dir / "shared.config.json").write_text(json.dumps(shared_config))
        (config_dir / "vscode.config.json").write_text(json.dumps(vscode_config))
        
        with patch.dict(os.environ, {"CORTEX_IDE": "vscode", "CORTEX_TDD_ENFORCEMENT": "false"}, clear=True):
            manager = ConfigManager(workspace_root=str(tmp_path))
            config = manager.load()
            
            # VSCode override
            assert config["brain"]["max_conversations"] == 100
            # Env var override (highest priority)
            assert config["brain"]["tdd_enforcement"] is False
            # Shared value preserved
            assert config["brain"]["timeout"] == 30
            # VSCode-specific values
            assert config["brain"]["fifo_enabled"] is True
            assert config["ide"]["integration_mode"] == "copilot_chat"
            # Orchestrator from shared
            assert config["orchestrator"]["auto_cleanup"] is True
            assert config["orchestrator"]["phase_validation"] == "strict"
    
    # ------------------------------------------------------------------------
    # Utility Methods
    # ------------------------------------------------------------------------
    
    def test_get_returns_nested_value(self, tmp_path):
        """Test get() method retrieves nested values"""
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {
            "brain": {
                "tier1": {
                    "max_conversations": 70
                }
            }
        }
        (config_dir / "shared.config.json").write_text(json.dumps(shared_config))
        
        with patch.dict(os.environ, {}, clear=True):
            with patch("psutil.Process", side_effect=psutil.NoSuchProcess(1)):
                manager = ConfigManager(workspace_root=str(tmp_path))
                manager.load()
                
                assert manager.get("brain.tier1.max_conversations") == 70
                assert manager.get("brain.tier1") == {"max_conversations": 70}
                assert manager.get("nonexistent.key", default=42) == 42
    
    def test_reload_clears_cache(self, tmp_path):
        """Test that reload() clears cached config and reloads"""
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {"brain": {"max_conversations": 70}}
        shared_file = config_dir / "shared.config.json"
        shared_file.write_text(json.dumps(shared_config))
        
        with patch.dict(os.environ, {}, clear=True):
            with patch("psutil.Process", side_effect=psutil.NoSuchProcess(1)):
                manager = ConfigManager(workspace_root=str(tmp_path))
                config1 = manager.load()
                assert config1["brain"]["max_conversations"] == 70
                
                # Modify config file
                new_config = {"brain": {"max_conversations": 150}}
                shared_file.write_text(json.dumps(new_config))
                
                # Reset IDE detector cache
                IDEDetector.reset_cache()
                
                # Reload should pick up new value
                config2 = manager.reload()
                assert config2["brain"]["max_conversations"] == 150


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestConfigSystemIntegration:
    """End-to-end integration tests for IDE detection + configuration"""
    
    def setup_method(self):
        """Reset caches before each test"""
        IDEDetector.reset_cache()
    
    def test_vscode_workspace_full_flow(self, tmp_path):
        """Test complete VSCode workspace configuration flow"""
        # Create VSCode workspace structure
        vscode_dir = tmp_path / ".vscode"
        vscode_dir.mkdir()
        
        # Create config files
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {"brain": {"max_conversations": 70}}
        vscode_config = {
            "brain": {"max_conversations": 100},
            "ide": {"integration_mode": "copilot_chat"}
        }
        
        (config_dir / "shared.config.json").write_text(json.dumps(shared_config))
        (config_dir / "vscode.config.json").write_text(json.dumps(vscode_config))
        
        # Detect IDE and load config
        with patch.dict(os.environ, {}, clear=True):
            with patch("psutil.Process", side_effect=psutil.NoSuchProcess(1)):
                ide_type = IDEDetector.detect(tmp_path)
                assert ide_type == IDEType.VSCODE
                
                manager = ConfigManager(workspace_root=str(tmp_path))
                config = manager.load()
                
                assert config["brain"]["max_conversations"] == 100
                assert config["ide"]["integration_mode"] == "copilot_chat"
    
    def test_visualstudio_workspace_full_flow(self, tmp_path):
        """Test complete Visual Studio workspace configuration flow"""
        # Create Visual Studio workspace structure
        vs_dir = tmp_path / ".vs"
        vs_dir.mkdir()
        
        # Create config files
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {"brain": {"max_conversations": 70}}
        vs_config = {
            "brain": {"max_conversations": 50},
            "ide": {"integration_mode": "extension"}
        }
        
        (config_dir / "shared.config.json").write_text(json.dumps(shared_config))
        (config_dir / "visualstudio.config.json").write_text(json.dumps(vs_config))
        
        # Detect IDE and load config
        with patch.dict(os.environ, {}, clear=True):
            with patch("psutil.Process", side_effect=psutil.NoSuchProcess(1)):
                ide_type = IDEDetector.detect(tmp_path)
                assert ide_type == IDEType.VISUAL_STUDIO
                
                manager = ConfigManager(workspace_root=str(tmp_path))
                config = manager.load()
                
                assert config["brain"]["max_conversations"] == 50
                assert config["ide"]["integration_mode"] == "extension"
