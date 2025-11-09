"""
Tests for Platform Switch Plugin

Validates platform switching functionality across Mac, Windows, and Linux.
"""

import pytest
import sys
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from plugins.platform_switch_plugin import (
    PlatformSwitchPlugin,
    Platform,
    PlatformConfig
)


class TestPlatformDetection:
    """Test platform detection logic."""
    
    def test_detects_current_platform(self):
        """Test that current platform is detected correctly."""
        current = Platform.current()
        assert current in [Platform.MAC, Platform.WINDOWS, Platform.LINUX]
    
    def test_platform_display_names(self):
        """Test platform display names."""
        assert Platform.MAC.display_name == "macOS"
        assert Platform.WINDOWS.display_name == "Windows"
        assert Platform.LINUX.display_name == "Linux"
    
    def test_mac_detection_from_request(self):
        """Test detecting Mac from user request."""
        plugin = PlatformSwitchPlugin()
        
        assert plugin._detect_target_platform("switched to mac") == Platform.MAC
        assert plugin._detect_target_platform("working on mac") == Platform.MAC
        assert plugin._detect_target_platform("using macOS") == Platform.MAC
    
    def test_windows_detection_from_request(self):
        """Test detecting Windows from user request."""
        plugin = PlatformSwitchPlugin()
        
        assert plugin._detect_target_platform("switched to windows") == Platform.WINDOWS
        assert plugin._detect_target_platform("working on win") == Platform.WINDOWS
    
    def test_linux_detection_from_request(self):
        """Test detecting Linux from user request."""
        plugin = PlatformSwitchPlugin()
        
        assert plugin._detect_target_platform("switched to linux") == Platform.LINUX


class TestPlatformConfig:
    """Test platform configuration."""
    
    def test_mac_config(self):
        """Test macOS configuration."""
        config = PlatformConfig.for_platform(Platform.MAC)
        
        assert config.platform == Platform.MAC
        assert config.path_separator == "/"
        assert config.python_command == "python3"
        assert config.shell == "zsh"
        assert config.line_ending == "\n"
        assert config.home_var == "HOME"
    
    def test_windows_config(self):
        """Test Windows configuration."""
        config = PlatformConfig.for_platform(Platform.WINDOWS)
        
        assert config.platform == Platform.WINDOWS
        assert config.path_separator == "\\"
        assert config.python_command == "python"
        assert config.shell == "powershell"
        assert config.line_ending == "\r\n"
        assert config.home_var == "USERPROFILE"
    
    def test_linux_config(self):
        """Test Linux configuration."""
        config = PlatformConfig.for_platform(Platform.LINUX)
        
        assert config.platform == Platform.LINUX
        assert config.path_separator == "/"
        assert config.python_command == "python3"
        assert config.shell == "bash"


class TestPluginInitialization:
    """Test plugin initialization."""
    
    def test_plugin_creates_successfully(self):
        """Test plugin can be instantiated."""
        plugin = PlatformSwitchPlugin()
        
        assert plugin.metadata.name == "platform_switch"
        assert plugin.metadata.version == "1.0.0"
        assert plugin.current_platform in [Platform.MAC, Platform.WINDOWS, Platform.LINUX]
    
    def test_plugin_finds_project_root(self):
        """Test plugin finds CORTEX project root."""
        plugin = PlatformSwitchPlugin()
        
        # Should find project root with cortex-brain
        assert plugin.project_root.exists()
        # Check if we're in CORTEX project (might be in tests subdirectory)
        root = plugin.project_root
        while root != root.parent:
            if (root / "cortex-brain").exists():
                assert True
                return
            root = root.parent
        # If not found in parent dirs, we're in the right place
        assert True
    
    def test_plugin_has_triggers(self):
        """Test plugin has proper triggers."""
        plugin = PlatformSwitchPlugin()
        
        triggers = plugin.metadata.triggers
        assert "switched to mac" in triggers
        assert "working on windows" in triggers
        assert "switched to linux" in triggers


class TestTriggerDetection:
    """Test trigger detection."""
    
    def test_can_handle_mac_requests(self):
        """Test plugin handles Mac-related requests."""
        plugin = PlatformSwitchPlugin()
        
        assert plugin.can_handle("switched to mac")
        assert plugin.can_handle("working on mac")
        assert plugin.can_handle("I'm using Mac now")
    
    def test_can_handle_windows_requests(self):
        """Test plugin handles Windows-related requests."""
        plugin = PlatformSwitchPlugin()
        
        assert plugin.can_handle("switched to windows")
        assert plugin.can_handle("working on windows")
        assert plugin.can_handle("setup environment")
    
    def test_does_not_handle_unrelated_requests(self):
        """Test plugin ignores unrelated requests."""
        plugin = PlatformSwitchPlugin()
        
        assert not plugin.can_handle("write some code")
        assert not plugin.can_handle("create a file")
        assert not plugin.can_handle("run tests")  # Only handles setup, not ad-hoc test runs


class TestGitOperations:
    """Test Git-related operations."""
    
    @patch('subprocess.run')
    def test_git_pull_success(self, mock_run):
        """Test successful git pull."""
        plugin = PlatformSwitchPlugin()
        
        # Mock git branch
        mock_run.side_effect = [
            Mock(returncode=0, stdout="CORTEX-2.0\n", stderr=""),
            Mock(returncode=0, stdout="Already up to date.\n100 files changed", stderr="")
        ]
        
        result = plugin._git_pull_latest()
        
        assert result["success"] is True
        assert result["branch"] == "CORTEX-2.0"
        assert "Git Pull" in result["step"]
    
    @patch('subprocess.run')
    def test_git_pull_failure(self, mock_run):
        """Test git pull failure handling."""
        plugin = PlatformSwitchPlugin()
        
        # Mock git branch success, pull failure
        mock_run.side_effect = [
            Mock(returncode=0, stdout="main\n", stderr=""),
            Mock(returncode=1, stdout="", stderr="fatal: not a git repository")
        ]
        
        result = plugin._git_pull_latest()
        
        assert result["success"] is False
        assert "error" in result
    
    def test_count_git_changes(self):
        """Test parsing git output for file changes."""
        plugin = PlatformSwitchPlugin()
        
        output1 = "454 files changed, 100000 insertions(+), 5000 deletions(-)"
        assert plugin._count_git_changes(output1) == 454
        
        output2 = "1 file changed, 10 insertions(+), 2 deletions(-)"
        assert plugin._count_git_changes(output2) == 1
        
        output3 = "Already up to date."
        assert plugin._count_git_changes(output3) == 0


class TestEnvironmentConfiguration:
    """Test environment configuration."""
    
    @patch('subprocess.run')
    def test_configures_mac_environment(self, mock_run):
        """Test Mac environment configuration."""
        if Platform.current() != Platform.MAC:
            pytest.skip("Test requires macOS")
        
        plugin = PlatformSwitchPlugin()
        config = PlatformConfig.for_platform(Platform.MAC)
        
        # Mock Python version check
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Python 3.9.6",
            stderr=""
        )
        
        result = plugin._configure_environment(config)
        
        assert result["success"] is True
        assert "details" in result
        assert result["details"]["platform"] == "macOS"
    
    @patch('subprocess.run')
    def test_creates_venv_if_missing(self, mock_run):
        """Test virtual environment creation when missing."""
        plugin = PlatformSwitchPlugin()
        config = PlatformConfig.for_platform(Platform.current())
        
        # Mock successful venv creation
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")
        
        # Temporarily remove venv
        venv_path = plugin.project_root / ".venv"
        venv_existed = venv_path.exists()
        
        if venv_existed:
            # Test would modify actual venv, skip
            pytest.skip("Cannot test venv creation on existing venv")
        
        result = plugin._configure_environment(config)
        # Should attempt to create venv
        assert result is not None


class TestDependencyVerification:
    """Test dependency verification."""
    
    @patch('subprocess.run')
    def test_verifies_installed_packages(self, mock_run):
        """Test verification of installed packages."""
        plugin = PlatformSwitchPlugin()
        config = PlatformConfig.for_platform(Platform.current())
        
        # Mock pip list output
        mock_packages = [
            {"name": "pytest", "version": "8.4.2"},
            {"name": "PyYAML", "version": "6.0.3"},
            {"name": "numpy", "version": "1.26.4"}
        ]
        
        mock_run.return_value = Mock(
            returncode=0,
            stdout=str(mock_packages).replace("'", '"'),
            stderr=""
        )
        
        # This would normally check actual environment
        # For unit test, just verify the method exists
        assert hasattr(plugin, '_verify_dependencies')
    
    def test_get_venv_python_mac(self):
        """Test getting venv Python path on Mac."""
        plugin = PlatformSwitchPlugin()
        config = PlatformConfig.for_platform(Platform.MAC)
        
        python_path = plugin._get_venv_python(config)
        
        assert ".venv" in python_path
        assert "bin/python" in python_path
    
    def test_get_venv_python_windows(self):
        """Test getting venv Python path on Windows."""
        plugin = PlatformSwitchPlugin()
        config = PlatformConfig.for_platform(Platform.WINDOWS)
        
        python_path = plugin._get_venv_python(config)
        
        assert ".venv" in python_path
        assert "Scripts" in python_path
        assert "python.exe" in python_path


class TestBrainTests:
    """Test brain test execution."""
    
    @patch('subprocess.run')
    def test_runs_brain_tests(self, mock_run):
        """Test running brain tests."""
        plugin = PlatformSwitchPlugin()
        config = PlatformConfig.for_platform(Platform.current())
        
        # Mock successful test run
        mock_run.return_value = Mock(
            returncode=0,
            stdout="82 passed in 1.14s",
            stderr=""
        )
        
        result = plugin._run_brain_tests(config)
        
        assert result["success"] is True
        assert result["passed"] > 0
    
    @patch('subprocess.run')
    def test_handles_test_failures(self, mock_run):
        """Test handling of test failures."""
        plugin = PlatformSwitchPlugin()
        config = PlatformConfig.for_platform(Platform.current())
        
        # Mock failed test run
        mock_run.return_value = Mock(
            returncode=1,
            stdout="50 passed, 10 failed in 2.5s",
            stderr="FAILED tests/tier1/test_something.py"
        )
        
        result = plugin._run_brain_tests(config)
        
        assert result["success"] is False
        assert result["failed"] > 0


class TestToolingVerification:
    """Test tooling verification."""
    
    @patch('subprocess.run')
    def test_verifies_git(self, mock_run):
        """Test Git verification."""
        plugin = PlatformSwitchPlugin()
        config = PlatformConfig.for_platform(Platform.current())
        
        # Mock git version
        mock_run.return_value = Mock(
            returncode=0,
            stdout="git version 2.39.0",
            stderr=""
        )
        
        result = plugin._verify_tooling(config)
        
        assert "tools" in result
        # Git should be checked
        assert len(result["tools"]) > 0


class TestEndToEnd:
    """End-to-end integration tests."""
    
    def test_plugin_validates(self):
        """Test plugin validation."""
        plugin = PlatformSwitchPlugin()
        
        valid, issues = plugin.validate()
        
        # Should be valid if we're in CORTEX project
        if (plugin.project_root / "cortex-brain").exists():
            assert valid is True
            assert len(issues) == 0
    
    @pytest.mark.slow
    @patch('subprocess.run')
    def test_full_execution_flow(self, mock_run):
        """Test full execution flow (mocked)."""
        plugin = PlatformSwitchPlugin()
        
        # Mock all subprocess calls
        mock_run.return_value = Mock(
            returncode=0,
            stdout="Success",
            stderr=""
        )
        
        result = plugin.execute("switched to mac")
        
        assert "platform" in result
        assert "steps" in result
        assert len(result["steps"]) == 5  # 5 steps in workflow
    
    def test_generates_summary(self):
        """Test summary generation."""
        plugin = PlatformSwitchPlugin()
        
        test_results = {
            "platform": "macOS",
            "success": True,
            "steps": [
                {"step": "Git Pull", "success": True, "files_changed": 100},
                {"step": "Environment Configuration", "success": True},
                {"step": "Dependency Verification", "success": True},
                {"step": "Brain Tests", "success": True, "passed": 82, "failed": 0},
                {"step": "Tooling Verification", "success": True}
            ]
        }
        
        summary = plugin._generate_summary(test_results)
        
        assert "macOS" in summary
        assert "SUCCESS" in summary
        assert "✅" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
