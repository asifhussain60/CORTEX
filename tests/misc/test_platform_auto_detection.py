"""
CORTEX Platform Auto-Detection Tests

Tests for automatic platform detection and configuration.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from plugins.platform_switch_plugin import (
    PlatformSwitchPlugin,
    Platform,
    PlatformConfig
)


class TestPlatformDetection:
    """Test automatic platform detection."""
    
    def test_detect_current_platform(self):
        """Test that current platform is detected correctly."""
        current = Platform.current()
        
        # Should detect one of the three supported platforms
        assert current in [Platform.MAC, Platform.WINDOWS, Platform.LINUX]
    
    def test_platform_display_names(self):
        """Test platform display names."""
        assert Platform.MAC.display_name == "macOS"
        assert Platform.WINDOWS.display_name == "Windows"
        assert Platform.LINUX.display_name == "Linux"
    
    def test_platform_config_creation(self):
        """Test platform config is created correctly."""
        for platform in Platform:
            config = PlatformConfig.for_platform(platform)
            assert config.platform == platform
            assert config.python_command
            assert config.shell
            assert config.path_separator


class TestAutomaticPlatformChange:
    """Test automatic platform change detection."""
    
    @pytest.fixture
    def temp_project(self):
        """Create temporary project structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            brain_dir = project_root / "cortex-brain"
            brain_dir.mkdir(parents=True)
            src_dir = project_root / "src"
            src_dir.mkdir(parents=True)
            yield project_root
    
    def test_first_time_setup_no_state_file(self, temp_project):
        """Test first-time setup when no state file exists."""
        with patch('plugins.platform_switch_plugin.Path.cwd', return_value=temp_project):
            plugin = PlatformSwitchPlugin()
            plugin.project_root = temp_project
            plugin._platform_state_file = temp_project / "cortex-brain" / ".platform_state.json"
            
            # Get last platform (should be None for first time)
            last_platform = plugin._get_last_platform()
            assert last_platform is None
    
    def test_save_and_load_platform_state(self, temp_project):
        """Test saving and loading platform state."""
        with patch('plugins.platform_switch_plugin.Path.cwd', return_value=temp_project):
            plugin = PlatformSwitchPlugin()
            plugin.project_root = temp_project
            plugin._platform_state_file = temp_project / "cortex-brain" / ".platform_state.json"
            
            # Save current platform
            current = Platform.current()
            plugin._save_platform_state(current)
            
            # Load it back
            loaded = plugin._get_last_platform()
            assert loaded == current
    
    def test_platform_change_detected(self, temp_project):
        """Test that platform change is detected."""
        with patch('plugins.platform_switch_plugin.Path.cwd', return_value=temp_project):
            plugin = PlatformSwitchPlugin()
            plugin.project_root = temp_project
            plugin._platform_state_file = temp_project / "cortex-brain" / ".platform_state.json"
            
            # Save a different platform than current
            current = Platform.current()
            if current == Platform.MAC:
                plugin._save_platform_state(Platform.WINDOWS)
            else:
                plugin._save_platform_state(Platform.MAC)
            
            # Load last platform
            last = plugin._get_last_platform()
            
            # Should detect change
            assert last != current
    
    def test_no_change_same_platform(self, temp_project):
        """Test that no change is detected when platform is same."""
        with patch('plugins.platform_switch_plugin.Path.cwd', return_value=temp_project):
            plugin = PlatformSwitchPlugin()
            plugin.project_root = temp_project
            plugin._platform_state_file = temp_project / "cortex-brain" / ".platform_state.json"
            
            # Save current platform
            current = Platform.current()
            plugin._save_platform_state(current)
            
            # Load it back
            last = plugin._get_last_platform()
            
            # Should be same
            assert last == current


class TestAutoConfiguration:
    """Test automatic configuration when platform changes."""
    
    @pytest.fixture
    def mock_plugin(self, tmp_path):
        """Create mock plugin with temp directory."""
        with patch('plugins.platform_switch_plugin.Path.cwd', return_value=tmp_path):
            brain_dir = tmp_path / "cortex-brain"
            brain_dir.mkdir(parents=True)
            src_dir = tmp_path / "src"
            src_dir.mkdir(parents=True)
            
            plugin = PlatformSwitchPlugin()
            plugin.project_root = tmp_path
            plugin._platform_state_file = brain_dir / ".platform_state.json"
            yield plugin
    
    def test_auto_configure_runs_on_platform_change(self, mock_plugin):
        """Test that auto-configure runs when platform changes."""
        # Mock git pull
        with patch.object(mock_plugin, '_git_pull_latest') as mock_git:
            mock_git.return_value = {"success": True, "name": "Git Pull"}
            
            # Mock dependency check
            with patch.object(mock_plugin, '_check_dependencies_exist') as mock_deps:
                mock_deps.return_value = {"success": True, "name": "Dependencies"}
                
                # Run auto-configure
                result = mock_plugin._auto_configure_platform(Platform.current())
                
                # Verify it ran
                assert result['success'] == True
                assert result['auto_mode'] == True
                assert len(result['steps']) > 0
    
    def test_auto_configure_lightweight(self, mock_plugin):
        """Test that auto-configure is lightweight (doesn't install)."""
        with patch.object(mock_plugin, '_git_pull_latest') as mock_git:
            mock_git.return_value = {"success": True, "name": "Git Pull"}
            
            with patch.object(mock_plugin, '_check_dependencies_exist') as mock_deps:
                mock_deps.return_value = {"success": True, "name": "Dependencies"}
                
                # Should NOT call heavy operations like install
                with patch.object(mock_plugin, '_verify_dependencies') as mock_verify:
                    result = mock_plugin._auto_configure_platform(Platform.current())
                    
                    # verify_dependencies (which installs) should NOT be called
                    mock_verify.assert_not_called()


class TestManualSetup:
    """Test manual /setup command."""
    
    def test_setup_command_registered(self):
        """Test that /setup command is registered."""
        plugin = PlatformSwitchPlugin()
        commands = plugin.register_commands()
        
        # Should have exactly 1 command now (/setup only)
        assert len(commands) == 1
        assert commands[0].command == "/setup"
    
    def test_no_platform_specific_commands(self):
        """Test that /mac, /windows, /linux are NOT registered."""
        plugin = PlatformSwitchPlugin()
        commands = plugin.register_commands()
        
        # Get all command strings
        command_strings = [cmd.command for cmd in commands]
        
        # Should NOT have platform-specific commands
        assert "/mac" not in command_strings
        assert "/windows" not in command_strings
        assert "/linux" not in command_strings
    
    def test_setup_aliases_present(self):
        """Test that /setup has useful aliases."""
        plugin = PlatformSwitchPlugin()
        commands = plugin.register_commands()
        
        setup_cmd = commands[0]
        assert "/env" in setup_cmd.aliases
        assert "/environment" in setup_cmd.aliases


class TestPluginInitialization:
    """Test plugin initialization with auto-detection."""
    
    @pytest.fixture
    def temp_project(self):
        """Create temporary project structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            brain_dir = project_root / "cortex-brain"
            brain_dir.mkdir(parents=True)
            src_dir = project_root / "src"
            src_dir.mkdir(parents=True)
            yield project_root
    
    def test_initialize_checks_platform(self, temp_project):
        """Test that initialize checks for platform changes."""
        with patch('plugins.platform_switch_plugin.Path.cwd', return_value=temp_project):
            with patch.object(PlatformSwitchPlugin, '_check_and_handle_platform_change') as mock_check:
                plugin = PlatformSwitchPlugin()
                plugin.project_root = temp_project
                
                result = plugin.initialize()
                
                # Should call platform change check
                mock_check.assert_called_once()
                assert result == True


class TestDependencyCheck:
    """Test dependency checking (not installation)."""
    
    def test_check_dependencies_exist(self):
        """Test quick dependency check."""
        plugin = PlatformSwitchPlugin()
        config = PlatformConfig.for_platform(Platform.current())
        
        result = plugin._check_dependencies_exist(config)
        
        assert 'name' in result
        assert 'success' in result
        assert 'message' in result
        
        # Should check Python and Git (both typically available)
        assert 'Python' in result['message']
        assert 'Git' in result['message']


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
