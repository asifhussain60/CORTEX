"""Tests for IDE detection and configuration management"""

import json
import os
import tempfile
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
    """Test suite for IDEDetector with all detection strategies"""
    
    def setup_method(self):
        """Reset cache before each test"""
        IDEDetector.reset_cache()

    # ------------------------------------------------------------------------
    # Strategy 1: Explicit Environment Variable Override
    # ------------------------------------------------------------------------

    def test_detect_vscode_via_cortex_ide_env(self, tmp_path):
        """Test VSCode detection via CORTEX_IDE env var"""
        with patch.dict(os.environ, {"CORTEX_IDE": "vscode"}, clear=True):
            result = IDEDetector.detect(tmp_path)
            assert result == IDEType.VSCODE

    def test_detect_vscode_from_vscode_injection(self):
        """Test VSCode detection via VSCODE_INJECTION env var"""
        with patch.dict(os.environ, {"VSCODE_INJECTION": "1"}):
            detector = IDEDetector()
            assert detector.detect() == IDEType.VSCODE

    def test_detect_visualstudio_from_visualstudio_edition(self):
        """Test Visual Studio detection via VisualStudioEdition env var"""
        with patch.dict(os.environ, {"VisualStudioEdition": "Professional"}):
            detector = IDEDetector()
            assert detector.detect() == IDEType.VISUALSTUDIO

    def test_detect_visualstudio_from_vsappiddir(self):
        """Test Visual Studio detection via VSAPPIDDIR env var"""
        with patch.dict(os.environ, {"VSAPPIDDIR": "C:\\Program Files\\Microsoft Visual Studio\\2022\\Professional"}):
            detector = IDEDetector()
            assert detector.detect() == IDEType.VISUALSTUDIO

    # ------------------------------------------------------------------------
    # Strategy 2: Parent Process Detection
    # ------------------------------------------------------------------------

    @patch("psutil.Process")
    def test_detect_vscode_from_parent_process_code(self, mock_process_class):
        """Test VSCode detection via parent process named 'Code.exe'"""
        # Mock current process
        mock_current = Mock()
        mock_current.name.return_value = "python.exe"
        
        # Mock parent process with VSCode
        mock_parent = Mock()
        mock_parent.name.return_value = "Code.exe"
        mock_current.parent.return_value = mock_parent
        
        mock_process_class.return_value = mock_current
        
        with patch.dict(os.environ, {}, clear=True):
            detector = IDEDetector()
            assert detector.detect() == IDEType.VSCODE

    @patch("psutil.Process")
    def test_detect_vscode_from_parent_process_electron(self, mock_process_class):
        """Test VSCode detection via parent process named 'electron.exe'"""
        mock_current = Mock()
        mock_current.name.return_value = "python.exe"
        
        mock_parent = Mock()
        mock_parent.name.return_value = "electron.exe"
        mock_current.parent.return_value = mock_parent
        
        mock_process_class.return_value = mock_current
        
        with patch.dict(os.environ, {}, clear=True):
            detector = IDEDetector()
            assert detector.detect() == IDEType.VSCODE

    @patch("psutil.Process")
    def test_detect_visualstudio_from_parent_process_devenv(self, mock_process_class):
        """Test Visual Studio detection via parent process 'devenv.exe'"""
        mock_current = Mock()
        mock_current.name.return_value = "python.exe"
        
        mock_parent = Mock()
        mock_parent.name.return_value = "devenv.exe"
        mock_current.parent.return_value = mock_parent
        
        mock_process_class.return_value = mock_current
        
        with patch.dict(os.environ, {}, clear=True):
            detector = IDEDetector()
            assert detector.detect() == IDEType.VISUALSTUDIO

    @patch("psutil.Process")
    def test_detect_visualstudio_from_grandparent_process(self, mock_process_class):
        """Test Visual Studio detection via grandparent process"""
        mock_current = Mock()
        mock_current.name.return_value = "python.exe"
        
        mock_parent = Mock()
        mock_parent.name.return_value = "cmd.exe"
        
        mock_grandparent = Mock()
        mock_grandparent.name.return_value = "devenv.exe"
        mock_parent.parent.return_value = mock_grandparent
        
        mock_current.parent.return_value = mock_parent
        mock_process_class.return_value = mock_current
        
        with patch.dict(os.environ, {}, clear=True):
            detector = IDEDetector()
            assert detector.detect() == IDEType.VISUALSTUDIO

    @patch("psutil.Process")
    def test_no_parent_process_returns_unknown(self, mock_process_class):
        """Test that missing parent process returns UNKNOWN"""
        mock_current = Mock()
        mock_current.name.return_value = "python.exe"
        mock_current.parent.return_value = None
        
        mock_process_class.return_value = mock_current
        
        with patch.dict(os.environ, {}, clear=True):
            detector = IDEDetector()
            assert detector.detect() == IDEType.UNKNOWN

    @patch("psutil.Process")
    def test_psutil_error_continues_detection(self, mock_process_class):
        """Test that psutil errors don't crash, continue to next strategy"""
        mock_process_class.side_effect = Exception("Process access denied")
        
        with patch.dict(os.environ, {}, clear=True):
            detector = IDEDetector()
            # Should return UNKNOWN since all strategies fail gracefully
            assert detector.detect() == IDEType.UNKNOWN

    # ------------------------------------------------------------------------
    # Strategy 3: Directory Marker Detection
    # ------------------------------------------------------------------------

    def test_detect_vscode_from_vscode_directory(self, tmp_path):
        """Test VSCode detection via .vscode directory"""
        vscode_dir = tmp_path / ".vscode"
        vscode_dir.mkdir()
        
        with patch.dict(os.environ, {}, clear=True):
            with patch("psutil.Process") as mock_process:
                mock_process.return_value.parent.return_value = None
                detector = IDEDetector(workspace_root=str(tmp_path))
                assert detector.detect() == IDEType.VSCODE

    def test_detect_visualstudio_from_vs_directory(self, tmp_path):
        """Test Visual Studio detection via .vs directory"""
        vs_dir = tmp_path / ".vs"
        vs_dir.mkdir()
        
        with patch.dict(os.environ, {}, clear=True):
            with patch("psutil.Process") as mock_process:
                mock_process.return_value.parent.return_value = None
                detector = IDEDetector(workspace_root=str(tmp_path))
                assert detector.detect() == IDEType.VISUALSTUDIO

    def test_vscode_takes_precedence_when_both_directories_exist(self, tmp_path):
        """Test that VSCode is detected first when both .vscode and .vs exist"""
        (tmp_path / ".vscode").mkdir()
        (tmp_path / ".vs").mkdir()
        
        with patch.dict(os.environ, {}, clear=True):
            with patch("psutil.Process") as mock_process:
                mock_process.return_value.parent.return_value = None
                detector = IDEDetector(workspace_root=str(tmp_path))
                assert detector.detect() == IDEType.VSCODE

    def test_no_directory_markers_returns_unknown(self, tmp_path):
        """Test UNKNOWN when no directory markers present"""
        with patch.dict(os.environ, {}, clear=True):
            with patch("psutil.Process") as mock_process:
                mock_process.return_value.parent.return_value = None
                detector = IDEDetector(workspace_root=str(tmp_path))
                assert detector.detect() == IDEType.UNKNOWN

    # ------------------------------------------------------------------------
    # Strategy 4: Cache Mechanism
    # ------------------------------------------------------------------------

    def test_cache_persists_across_detections(self, tmp_path):
        """Test that IDE detection is cached and reused"""
        vscode_dir = tmp_path / ".vscode"
        vscode_dir.mkdir()
        
        cache_file = tmp_path / "cortex-brain" / "cache" / "ide_detection.json"
        
        with patch.dict(os.environ, {}, clear=True):
            with patch("psutil.Process") as mock_process:
                mock_process.return_value.parent.return_value = None
                
                # First detection
                detector1 = IDEDetector(workspace_root=str(tmp_path))
                result1 = detector1.detect()
                assert result1 == IDEType.VSCODE
                
                # Cache should exist
                assert cache_file.exists()
                
                # Remove .vscode directory to prove cache is used
                vscode_dir.rmdir()
                
                # Second detection should use cache
                detector2 = IDEDetector(workspace_root=str(tmp_path))
                result2 = detector2.detect()
                assert result2 == IDEType.VSCODE

    def test_cache_invalidation_on_force_redetect(self, tmp_path):
        """Test that cache can be invalidated with force_redetect"""
        vscode_dir = tmp_path / ".vscode"
        vscode_dir.mkdir()
        
        with patch.dict(os.environ, {}, clear=True):
            with patch("psutil.Process") as mock_process:
                mock_process.return_value.parent.return_value = None
                
                # First detection
                detector1 = IDEDetector(workspace_root=str(tmp_path))
                detector1.detect()
                
                # Remove directory and force redetect
                vscode_dir.rmdir()
                
                detector2 = IDEDetector(workspace_root=str(tmp_path))
                result = detector2.detect(force_redetect=True)
                assert result == IDEType.UNKNOWN

    def test_cache_file_corruption_handled_gracefully(self, tmp_path):
        """Test that corrupted cache file is recreated"""
        cache_dir = tmp_path / "cortex-brain" / "cache"
        cache_dir.mkdir(parents=True)
        cache_file = cache_dir / "ide_detection.json"
        cache_file.write_text("CORRUPTED JSON{{{")
        
        vscode_dir = tmp_path / ".vscode"
        vscode_dir.mkdir()
        
        with patch.dict(os.environ, {}, clear=True):
            with patch("psutil.Process") as mock_process:
                mock_process.return_value.parent.return_value = None
                
                detector = IDEDetector(workspace_root=str(tmp_path))
                result = detector.detect()
                assert result == IDEType.VSCODE
                
                # Cache should be rewritten correctly
                assert cache_file.exists()
                cache_data = json.loads(cache_file.read_text())
                assert cache_data["ide_type"] == "vscode"

    # ------------------------------------------------------------------------
    # Multi-Strategy Integration
    # ------------------------------------------------------------------------

    def test_environment_variable_takes_precedence(self, tmp_path):
        """Test that env vars are checked before directory markers"""
        # Create .vs directory (Visual Studio marker)
        vs_dir = tmp_path / ".vs"
        vs_dir.mkdir()
        
        # But set VSCode env var
        with patch.dict(os.environ, {"TERM_PROGRAM": "vscode"}):
            detector = IDEDetector(workspace_root=str(tmp_path))
            # Should detect VSCode from env var, not Visual Studio from directory
            assert detector.detect() == IDEType.VSCODE

    def test_parent_process_checked_before_directories(self, tmp_path):
        """Test parent process detection runs before directory markers"""
        vs_dir = tmp_path / ".vs"
        vs_dir.mkdir()
        
        with patch.dict(os.environ, {}, clear=True):
            with patch("psutil.Process") as mock_process_class:
                # Mock parent process as VSCode
                mock_current = Mock()
                mock_current.name.return_value = "python.exe"
                mock_parent = Mock()
                mock_parent.name.return_value = "Code.exe"
                mock_current.parent.return_value = mock_parent
                mock_process_class.return_value = mock_current
                
                detector = IDEDetector(workspace_root=str(tmp_path))
                # Should detect VSCode from parent process
                assert detector.detect() == IDEType.VSCODE

    def test_get_ide_name_returns_correct_string(self):
        """Test get_ide_name() returns human-readable names"""
        with patch.dict(os.environ, {"TERM_PROGRAM": "vscode"}):
            detector = IDEDetector()
            detector.detect()
            assert detector.get_ide_name() == "Visual Studio Code"
        
        with patch.dict(os.environ, {"VisualStudioEdition": "Professional"}):
            detector = IDEDetector()
            detector.detect()
            assert detector.get_ide_name() == "Visual Studio"
        
        with patch.dict(os.environ, {}, clear=True):
            with patch("psutil.Process") as mock_process:
                mock_process.return_value.parent.return_value = None
                detector = IDEDetector()
                detector.detect()
                assert detector.get_ide_name() == "Unknown IDE"

    def test_detection_strategies_exhausted_returns_unknown(self):
        """Test that all strategies failing returns UNKNOWN"""
        with patch.dict(os.environ, {}, clear=True):
            with patch("psutil.Process") as mock_process:
                mock_process.return_value.parent.return_value = None
                with tempfile.TemporaryDirectory() as tmp_dir:
                    detector = IDEDetector(workspace_root=tmp_dir)
                    assert detector.detect() == IDEType.UNKNOWN


# ============================================================================
# CONFIG MANAGER TESTS
# ============================================================================


class TestConfigManager:
    """Test suite for ConfigManager with inheritance and deep merging"""

    # ------------------------------------------------------------------------
    # Configuration Loading
    # ------------------------------------------------------------------------

    def test_load_shared_config_only(self, tmp_path):
        """Test loading shared config when IDE is unknown"""
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {
            "brain": {
                "max_conversations": 70,
                "tdd_enforcement": True
            },
            "orchestrator": {
                "auto_cleanup": True
            }
        }
        
        (config_dir / "shared.config.json").write_text(json.dumps(shared_config))
        
        with patch("src.core.config_manager.IDEDetector") as mock_detector_class:
            mock_detector = Mock()
            mock_detector.detect.return_value = IDEType.UNKNOWN
            mock_detector_class.return_value = mock_detector
            
            manager = ConfigManager(workspace_root=str(tmp_path))
            config = manager.load()
            
            assert config["brain"]["max_conversations"] == 70
            assert config["brain"]["tdd_enforcement"] is True
            assert config["orchestrator"]["auto_cleanup"] is True

    def test_load_vscode_config_with_shared(self, tmp_path):
        """Test VSCode config overrides shared config"""
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {
            "brain": {"max_conversations": 70},
            "orchestrator": {"auto_cleanup": True}
        }
        
        vscode_config = {
            "brain": {"max_conversations": 100},  # Override
            "ide": {"integration_mode": "copilot_chat"}  # New key
        }
        
        (config_dir / "shared.config.json").write_text(json.dumps(shared_config))
        (config_dir / "vscode.config.json").write_text(json.dumps(vscode_config))
        
        with patch("src.core.config_manager.IDEDetector") as mock_detector_class:
            mock_detector = Mock()
            mock_detector.detect.return_value = IDEType.VSCODE
            mock_detector_class.return_value = mock_detector
            
            manager = ConfigManager(workspace_root=str(tmp_path))
            config = manager.load()
            
            # VSCode override
            assert config["brain"]["max_conversations"] == 100
            # Shared value preserved
            assert config["orchestrator"]["auto_cleanup"] is True
            # VSCode-specific value
            assert config["ide"]["integration_mode"] == "copilot_chat"

    def test_load_visualstudio_config_with_shared(self, tmp_path):
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
        
        with patch("src.core.config_manager.IDEDetector") as mock_detector_class:
            mock_detector = Mock()
            mock_detector.detect.return_value = IDEType.VISUALSTUDIO
            mock_detector_class.return_value = mock_detector
            
            manager = ConfigManager(workspace_root=str(tmp_path))
            config = manager.load()
            
            assert config["brain"]["max_conversations"] == 50
            assert config["orchestrator"]["auto_cleanup"] is True
            assert config["ide"]["integration_mode"] == "extension"

    # ------------------------------------------------------------------------
    # Deep Merge Logic
    # ------------------------------------------------------------------------

    def test_deep_merge_nested_dicts(self, tmp_path):
        """Test that nested dictionaries are merged recursively"""
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {
            "brain": {
                "tier0": {"enforcement": "strict"},
                "tier1": {"max_conversations": 70}
            }
        }
        
        vscode_config = {
            "brain": {
                "tier1": {"max_conversations": 100, "fifo_enabled": True}
            }
        }
        
        (config_dir / "shared.config.json").write_text(json.dumps(shared_config))
        (config_dir / "vscode.config.json").write_text(json.dumps(vscode_config))
        
        with patch("src.core.config_manager.IDEDetector") as mock_detector_class:
            mock_detector = Mock()
            mock_detector.detect.return_value = IDEType.VSCODE
            mock_detector_class.return_value = mock_detector
            
            manager = ConfigManager(workspace_root=str(tmp_path))
            config = manager.load()
            
            # tier0 from shared preserved
            assert config["brain"]["tier0"]["enforcement"] == "strict"
            # tier1 max_conversations overridden
            assert config["brain"]["tier1"]["max_conversations"] == 100
            # tier1 fifo_enabled added from VSCode
            assert config["brain"]["tier1"]["fifo_enabled"] is True

    def test_deep_merge_preserves_lists(self, tmp_path):
        """Test that lists are replaced, not merged"""
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {
            "orchestrator": {
                "enabled_phases": ["phase1", "phase2", "phase3"]
            }
        }
        
        vscode_config = {
            "orchestrator": {
                "enabled_phases": ["phase1", "phase4"]  # Complete replacement
            }
        }
        
        (config_dir / "shared.config.json").write_text(json.dumps(shared_config))
        (config_dir / "vscode.config.json").write_text(json.dumps(vscode_config))
        
        with patch("src.core.config_manager.IDEDetector") as mock_detector_class:
            mock_detector = Mock()
            mock_detector.detect.return_value = IDEType.VSCODE
            mock_detector_class.return_value = mock_detector
            
            manager = ConfigManager(workspace_root=str(tmp_path))
            config = manager.load()
            
            # List completely replaced, not merged
            assert config["orchestrator"]["enabled_phases"] == ["phase1", "phase4"]

    def test_deep_merge_preserves_primitives(self, tmp_path):
        """Test that primitive values are overridden correctly"""
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {
            "brain": {
                "max_conversations": 70,
                "tdd_enforcement": True,
                "timeout": 30
            }
        }
        
        vscode_config = {
            "brain": {
                "max_conversations": 100,  # Override int
                "tdd_enforcement": False,  # Override bool
                "timeout": 60  # Override int
            }
        }
        
        (config_dir / "shared.config.json").write_text(json.dumps(shared_config))
        (config_dir / "vscode.config.json").write_text(json.dumps(vscode_config))
        
        with patch("src.core.config_manager.IDEDetector") as mock_detector_class:
            mock_detector = Mock()
            mock_detector.detect.return_value = IDEType.VSCODE
            mock_detector_class.return_value = mock_detector
            
            manager = ConfigManager(workspace_root=str(tmp_path))
            config = manager.load()
            
            assert config["brain"]["max_conversations"] == 100
            assert config["brain"]["tdd_enforcement"] is False
            assert config["brain"]["timeout"] == 60

    # ------------------------------------------------------------------------
    # Environment Variable Overrides
    # ------------------------------------------------------------------------

    def test_env_var_overrides_max_conversations(self, tmp_path):
        """Test CORTEX_MAX_CONVERSATIONS env var override"""
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {"brain": {"max_conversations": 70}}
        (config_dir / "shared.config.json").write_text(json.dumps(shared_config))
        
        with patch.dict(os.environ, {"CORTEX_MAX_CONVERSATIONS": "150"}):
            with patch("src.core.config_manager.IDEDetector") as mock_detector_class:
                mock_detector = Mock()
                mock_detector.detect.return_value = IDEType.UNKNOWN
                mock_detector_class.return_value = mock_detector
                
                manager = ConfigManager(workspace_root=str(tmp_path))
                config = manager.load()
                
                assert config["brain"]["max_conversations"] == 150

    def test_env_var_overrides_tdd_enforcement(self, tmp_path):
        """Test CORTEX_TDD_ENFORCEMENT env var override"""
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {"brain": {"tdd_enforcement": True}}
        (config_dir / "shared.config.json").write_text(json.dumps(shared_config))
        
        with patch.dict(os.environ, {"CORTEX_TDD_ENFORCEMENT": "false"}):
            with patch("src.core.config_manager.IDEDetector") as mock_detector_class:
                mock_detector = Mock()
                mock_detector.detect.return_value = IDEType.UNKNOWN
                mock_detector_class.return_value = mock_detector
                
                manager = ConfigManager(workspace_root=str(tmp_path))
                config = manager.load()
                
                assert config["brain"]["tdd_enforcement"] is False

    def test_env_var_invalid_value_ignored(self, tmp_path):
        """Test that invalid env var values are ignored"""
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {"brain": {"max_conversations": 70}}
        (config_dir / "shared.config.json").write_text(json.dumps(shared_config))
        
        with patch.dict(os.environ, {"CORTEX_MAX_CONVERSATIONS": "INVALID"}):
            with patch("src.core.config_manager.IDEDetector") as mock_detector_class:
                mock_detector = Mock()
                mock_detector.detect.return_value = IDEType.UNKNOWN
                mock_detector_class.return_value = mock_detector
                
                manager = ConfigManager(workspace_root=str(tmp_path))
                config = manager.load()
                
                # Should keep shared config value
                assert config["brain"]["max_conversations"] == 70

    # ------------------------------------------------------------------------
    # Error Handling
    # ------------------------------------------------------------------------

    def test_missing_shared_config_raises_error(self, tmp_path):
        """Test that missing shared.config.json raises FileNotFoundError"""
        with patch("src.core.config_manager.IDEDetector") as mock_detector_class:
            mock_detector = Mock()
            mock_detector.detect.return_value = IDEType.UNKNOWN
            mock_detector_class.return_value = mock_detector
            
            manager = ConfigManager(workspace_root=str(tmp_path))
            with pytest.raises(FileNotFoundError, match="shared.config.json"):
                manager.load()

    def test_missing_ide_config_uses_shared_only(self, tmp_path):
        """Test that missing IDE config falls back to shared config"""
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {"brain": {"max_conversations": 70}}
        (config_dir / "shared.config.json").write_text(json.dumps(shared_config))
        
        with patch("src.core.config_manager.IDEDetector") as mock_detector_class:
            mock_detector = Mock()
            mock_detector.detect.return_value = IDEType.VSCODE
            mock_detector_class.return_value = mock_detector
            
            manager = ConfigManager(workspace_root=str(tmp_path))
            config = manager.load()
            
            # Should have shared config values
            assert config["brain"]["max_conversations"] == 70

    def test_corrupted_shared_config_raises_json_error(self, tmp_path):
        """Test that corrupted shared config raises JSON error"""
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        (config_dir / "shared.config.json").write_text("INVALID JSON{{{")
        
        with patch("src.core.config_manager.IDEDetector") as mock_detector_class:
            mock_detector = Mock()
            mock_detector.detect.return_value = IDEType.UNKNOWN
            mock_detector_class.return_value = mock_detector
            
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
        
        with patch("src.core.config_manager.IDEDetector") as mock_detector_class:
            mock_detector = Mock()
            mock_detector.detect.return_value = IDEType.VSCODE
            mock_detector_class.return_value = mock_detector
            
            manager = ConfigManager(workspace_root=str(tmp_path))
            config = manager.load()
            
            # Should fall back to shared config
            assert config["brain"]["max_conversations"] == 70

    # ------------------------------------------------------------------------
    # End-to-End Integration
    # ------------------------------------------------------------------------

    def test_full_inheritance_chain_vscode(self, tmp_path):
        """Test complete VSCode inheritance: shared → vscode → env vars"""
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
                "max_conversations": 100,  # Override
                "fifo_enabled": True  # New
            },
            "ide": {
                "integration_mode": "copilot_chat"
            }
        }
        
        (config_dir / "shared.config.json").write_text(json.dumps(shared_config))
        (config_dir / "vscode.config.json").write_text(json.dumps(vscode_config))
        
        with patch.dict(os.environ, {"CORTEX_TDD_ENFORCEMENT": "false"}):
            with patch("src.core.config_manager.IDEDetector") as mock_detector_class:
                mock_detector = Mock()
                mock_detector.detect.return_value = IDEType.VSCODE
                mock_detector_class.return_value = mock_detector
                
                manager = ConfigManager(workspace_root=str(tmp_path))
                config = manager.load()
                
                # VSCode override
                assert config["brain"]["max_conversations"] == 100
                # Env var override
                assert config["brain"]["tdd_enforcement"] is False
                # Shared value preserved
                assert config["brain"]["timeout"] == 30
                # VSCode-specific value
                assert config["brain"]["fifo_enabled"] is True
                assert config["ide"]["integration_mode"] == "copilot_chat"
                # Orchestrator from shared
                assert config["orchestrator"]["auto_cleanup"] is True
                assert config["orchestrator"]["phase_validation"] == "strict"

    def test_full_inheritance_chain_visualstudio(self, tmp_path):
        """Test complete Visual Studio inheritance: shared → visualstudio → env vars"""
        config_dir = tmp_path / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {
            "brain": {
                "max_conversations": 70,
                "tdd_enforcement": True
            },
            "orchestrator": {
                "auto_cleanup": True
            }
        }
        
        vs_config = {
            "brain": {
                "max_conversations": 50
            },
            "ide": {
                "integration_mode": "extension",
                "msbuild_integration": True
            }
        }
        
        (config_dir / "shared.config.json").write_text(json.dumps(shared_config))
        (config_dir / "visualstudio.config.json").write_text(json.dumps(vs_config))
        
        with patch.dict(os.environ, {"CORTEX_MAX_CONVERSATIONS": "200"}):
            with patch("src.core.config_manager.IDEDetector") as mock_detector_class:
                mock_detector = Mock()
                mock_detector.detect.return_value = IDEType.VISUALSTUDIO
                mock_detector_class.return_value = mock_detector
                
                manager = ConfigManager(workspace_root=str(tmp_path))
                config = manager.load()
                
                # Env var override (highest priority)
                assert config["brain"]["max_conversations"] == 200
                # Shared value preserved
                assert config["brain"]["tdd_enforcement"] is True
                # Visual Studio-specific values
                assert config["ide"]["integration_mode"] == "extension"
                assert config["ide"]["msbuild_integration"] is True
                # Orchestrator from shared
                assert config["orchestrator"]["auto_cleanup"] is True

    def test_get_returns_nested_value(self, tmp_path):
        """Test get() method retrieves nested values with dot notation"""
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
        
        with patch("src.core.config_manager.IDEDetector") as mock_detector_class:
            mock_detector = Mock()
            mock_detector.detect.return_value = IDEType.UNKNOWN
            mock_detector_class.return_value = mock_detector
            
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
        
        with patch("src.core.config_manager.IDEDetector") as mock_detector_class:
            mock_detector = Mock()
            mock_detector.detect.return_value = IDEType.UNKNOWN
            mock_detector_class.return_value = mock_detector
            
            manager = ConfigManager(workspace_root=str(tmp_path))
            config1 = manager.load()
            assert config1["brain"]["max_conversations"] == 70
            
            # Modify config file
            new_config = {"brain": {"max_conversations": 150}}
            shared_file.write_text(json.dumps(new_config))
            
            # Reload should pick up new value
            config2 = manager.reload()
            assert config2["brain"]["max_conversations"] == 150
