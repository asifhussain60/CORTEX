"""Unit Tests for Pre-Commit Health Hook

Tests pre-commit hook enforcement logic.

Author: CORTEX Framework
Phase: PHASE-95 S4
CORE Rules: CORE-008 (TDD)
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from cortex.orchestrators.health.hooks.pre_commit_health import (
    check_staged_files,
    main as pre_commit_main,
)


class TestPreCommitHook:
    """Test suite for pre-commit hook."""
    
    @patch("subprocess.run")
    def test_check_staged_files_no_violations(self, mock_run: Mock) -> None:
        """Test checking staged files with no violations.
        
        Args:
            mock_run: Mock subprocess.run
        """
        mock_run.return_value = Mock(
            returncode=0,
            stdout="cortex/utils.py\ntests/test_utils.py\n"
        )
        
        passed, violations = check_staged_files()
        
        assert passed is True
        assert len(violations) == 0
    
    @patch("subprocess.run")
    def test_check_versioned_filename(self, mock_run: Mock) -> None:
        """Test detection of versioned filename.
        
        Args:
            mock_run: Mock subprocess.run
        """
        mock_run.return_value = Mock(
            returncode=0,
            stdout="cortex/utils_v2.py\n"
        )
        
        passed, violations = check_staged_files()
        
        assert passed is False
        assert len(violations) == 1
        assert "CORE-028" in violations[0]
        assert "versioned filename" in violations[0].lower()
    
    @patch("subprocess.run")
    def test_check_backup_file(self, mock_run: Mock) -> None:
        """Test detection of backup file.
        
        Args:
            mock_run: Mock subprocess.run
        """
        mock_run.return_value = Mock(
            returncode=0,
            stdout="cortex/utils.py.backup\n"
        )
        
        passed, violations = check_staged_files()
        
        assert passed is False
        assert len(violations) == 1
        assert "backup file" in violations[0].lower()
    
    @patch("subprocess.run")
    def test_check_config_outside_registry(self, mock_run: Mock) -> None:
        """Test detection of config outside registry.
        
        Args:
            mock_run: Mock subprocess.run
        """
        mock_run.return_value = Mock(
            returncode=0,
            stdout="cortex/config.yaml\n"
        )
        
        passed, violations = check_staged_files()
        
        assert passed is False
        assert len(violations) == 1
        assert "outside registry" in violations[0].lower()
    
    @patch("subprocess.run")
    def test_check_database_in_root(self, mock_run: Mock) -> None:
        """Test detection of database in root.
        
        Args:
            mock_run: Mock subprocess.run
        """
        mock_run.return_value = Mock(
            returncode=0,
            stdout="governance.db\n"
        )
        
        passed, violations = check_staged_files()
        
        assert passed is False
        assert len(violations) == 1
        assert "database in root" in violations[0].lower()
    
    @patch("subprocess.run")
    def test_check_multiple_violations(self, mock_run: Mock) -> None:
        """Test detection of multiple violations.
        
        Args:
            mock_run: Mock subprocess.run
        """
        mock_run.return_value = Mock(
            returncode=0,
            stdout="cortex/utils_v2.py\ntest.db\ncortex/config.yaml\n"
        )
        
        passed, violations = check_staged_files()
        
        assert passed is False
        assert len(violations) == 3
    
    @patch("subprocess.run")
    def test_git_command_failure(self, mock_run: Mock) -> None:
        """Test handling of git command failure.
        
        Args:
            mock_run: Mock subprocess.run
        """
        mock_run.return_value = Mock(returncode=1)
        
        passed, violations = check_staged_files()
        
        assert passed is False
        assert "Failed to get staged files" in violations[0]
    
    @patch("cortex.orchestrators.health.hooks.pre_commit_health.check_staged_files")
    def test_main_with_violations(self, mock_check: Mock, capsys) -> None:
        """Test main function with violations.
        
        Args:
            mock_check: Mock check_staged_files
            capsys: Pytest capsys fixture
        """
        mock_check.return_value = (False, ["violation 1", "violation 2"])
        
        exit_code = pre_commit_main()
        
        assert exit_code == 1
        captured = capsys.readouterr()
        assert "COMMIT BLOCKED" in captured.out
    
    @patch("cortex.orchestrators.health.hooks.pre_commit_health.check_staged_files")
    def test_main_without_violations(self, mock_check: Mock, capsys) -> None:
        """Test main function without violations.
        
        Args:
            mock_check: Mock check_staged_files
            capsys: Pytest capsys fixture
        """
        mock_check.return_value = (True, [])
        
        exit_code = pre_commit_main()
        
        assert exit_code == 0
        captured = capsys.readouterr()
        assert "passed" in captured.out
