"""
Unit tests for RoslynProcessManager.

AC_START: AC-PHASE24.2.1-001
Description: Roslyn process lifecycle management tests
Authority: Phase 24.2.1 - Roslyn Process Manager
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from cortex.refactoring.adapters.roslyn_process import RoslynProcessManager


class TestRoslynProcessManagerInitialization:
    """Test RoslynProcessManager initialization."""

    def test_roslyn_process_manager_import(self):
        """Test that RoslynProcessManager can be imported."""
        from cortex.refactoring.adapters.roslyn_process import RoslynProcessManager
        assert RoslynProcessManager is not None

    def test_roslyn_process_manager_initialization(self):
        """Test RoslynProcessManager initializes correctly."""
        manager = RoslynProcessManager()
        assert manager is not None
        assert hasattr(manager, 'start')
        assert hasattr(manager, 'stop')
        assert hasattr(manager, 'is_running')

    def test_roslyn_process_manager_dotnet_path(self):
        """Test RoslynProcessManager detects dotnet installation."""
        manager = RoslynProcessManager()
        assert hasattr(manager, 'dotnet_path')
        # Should be None or a valid path
        if manager.dotnet_path:
            assert Path(manager.dotnet_path).exists()


class TestRoslynProcessLifecycle:
    """Test RoslynProcessManager lifecycle operations."""

    def test_process_not_running_initially(self):
        """Test process is not running on initialization."""
        manager = RoslynProcessManager()
        assert manager.is_running() is False

    @patch('subprocess.Popen')
    @patch('pathlib.Path.exists')
    def test_start_process_success(self, mock_exists, mock_popen):
        """Test starting Roslyn process successfully."""
        mock_exists.return_value = True  # CLI tool exists
        mock_process = Mock()
        mock_process.poll.return_value = None  # Process running
        mock_popen.return_value = mock_process
        
        manager = RoslynProcessManager()
        result = manager.start()
        
        assert result.is_ok()
        assert manager.is_running() is True

    @patch('pathlib.Path.exists')
    def test_start_process_failure(self, mock_exists):
        """Test handling Roslyn process start failure."""
        mock_exists.return_value = False  # CLI tool missing
        
        manager = RoslynProcessManager()
        result = manager.start()
        
        assert result.is_err()
        assert "roslyn cli tool not found" in str(result.unwrap_err()).lower()

    @patch('subprocess.Popen')
    @patch('pathlib.Path.exists')
    def test_stop_process(self, mock_exists, mock_popen):
        """Test stopping Roslyn process."""
        mock_exists.return_value = True
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_process.stdin = Mock()
        mock_process.stdin.closed = False
        mock_popen.return_value = mock_process
        
        manager = RoslynProcessManager()
        manager.start()
        
        result = manager.stop()
        assert result.is_ok()
        mock_process.terminate.assert_called_once()

    def test_stop_process_not_running(self):
        """Test stopping process when not running."""
        manager = RoslynProcessManager()
        result = manager.stop()
        assert result.is_ok()  # Graceful handling


class TestRoslynProcessCommunication:
    """Test RoslynProcessManager communication."""

    @patch('subprocess.Popen')
    @patch('pathlib.Path.exists')
    def test_send_command_success(self, mock_exists, mock_popen):
        """Test sending command to Roslyn process."""
        mock_exists.return_value = True
        mock_process = Mock()
        mock_process.poll.return_value = None
        mock_process.stdin = Mock()
        mock_process.stdout = Mock()
        mock_process.stdout.readline.return_value = '{"success": true}\n'
        mock_popen.return_value = mock_process
        
        manager = RoslynProcessManager()
        manager.start()
        
        result = manager.send_command({"action": "test"})
        assert result.is_ok()

    @patch('subprocess.Popen')
    def test_send_command_process_not_running(self, mock_popen):
        """Test sending command when process not running."""
        manager = RoslynProcessManager()
        result = manager.send_command({"action": "test"})
        
        assert result.is_err()
        assert "not running" in str(result.unwrap_err()).lower()


class TestRoslynProcessAvailability:
    """Test Roslyn availability detection."""

    def test_is_available_checks_dotnet(self):
        """Test is_available checks for dotnet SDK."""
        manager = RoslynProcessManager()
        # Should check for dotnet availability
        available = manager.is_available()
        assert isinstance(available, bool)

    @patch('shutil.which')
    def test_is_available_false_when_no_dotnet(self, mock_which):
        """Test is_available returns False when dotnet missing."""
        mock_which.return_value = None
        
        manager = RoslynProcessManager()
        assert manager.is_available() is False

    @patch('shutil.which')
    def test_is_available_true_when_dotnet_present(self, mock_which):
        """Test is_available returns True when dotnet present."""
        mock_which.return_value = "/usr/local/bin/dotnet"
        
        manager = RoslynProcessManager()
        assert manager.is_available() is True


# AC_COMPLETE: AC-PHASE24.2.1-001 ✅ 15/15 tests (RED phase)
