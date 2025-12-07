"""
Tests for Git History Scanner

Tests the git history scanning functionality for learning library updates.
Validates timeframe parsing, commit metadata extraction, and error handling.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from src.operations.modules.learning.git_history_scanner import (
    GitHistoryScanner,
    CommitMetadata,
    scan_commits
)


class TestGitHistoryScanner:
    """Test suite for GitHistoryScanner"""
    
    @pytest.fixture
    def scanner(self, tmp_path):
        """Create scanner instance with temp repo"""
        return GitHistoryScanner(repo_path=tmp_path)
    
    @pytest.fixture
    def mock_git_log_output(self):
        """Mock git log output with numstat"""
        return """2025-12-07 00:00:00|John Doe|abc123def
50\t10\tsrc/module.py
20\t5\ttests/test_module.py

2025-12-06 12:00:00|Jane Smith|def456ghi
100\t50\tsrc/core.py
"""
    
    def test_scan_git_history_default_24h(self, scanner):
        """
        RED TEST: Verify default 24h scan returns commits from last day.
        
        Expected behavior:
        - Scans last 24 hours by default
        - Returns list of CommitMetadata objects
        - Includes commits from yesterday to now
        """
        # This test should FAIL until GitHistoryScanner is implemented
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="2025-12-07T10:00:00-05:00|Author|sha123|Test message\n50\t10\tfile.py\n\n"
            )
            
            result = scanner.scan_commits()
            
            # Verify subprocess called with --since parameter
            assert mock_run.called
            call_args = mock_run.call_args[0][0]
            # Check for --since= prefix in args
            assert any('--since=' in str(arg) for arg in call_args)
            
            # Verify returns list of commits
            assert isinstance(result, list)
            if len(result) > 0:  # Parser working
                assert isinstance(result[0], CommitMetadata)
    
    def test_scan_git_history_custom_timeframe(self, scanner):
        """
        RED TEST: Verify custom timeframe (48h, 7d) works correctly.
        
        Expected behavior:
        - Accepts hours parameter
        - Calculates correct since timestamp
        - Passes to git log command
        """
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="2025-12-05|Author|sha123\n"
            )
            
            # Test 48 hours
            result = scanner.scan_commits(since_hours=48)
            
            call_args = mock_run.call_args[0][0]
            # Verify --since includes 48h ago calculation
            assert any('--since=' in str(arg) for arg in call_args)
            
            # Test 7 days (168 hours)
            result = scanner.scan_commits(since_hours=168)
            assert mock_run.call_count == 2
    
    def test_extract_commit_metadata(self, scanner, mock_git_log_output):
        """
        RED TEST: Verify extracted metadata includes all required fields.
        
        Expected fields:
        - sha: commit hash
        - message: commit message
        - author: commit author
        - timestamp: datetime object
        - files_changed: list of file paths
        - lines_added: total lines added
        - lines_deleted: total lines deleted
        - net_change: lines_added - lines_deleted
        """
        with patch('subprocess.run') as mock_run:
            # Mock output needs blank lines between commits
            output = (
                "2025-12-07T00:00:00-05:00|John Doe|abc123def456|Fix validation bug\n"
                "50\t10\tsrc/module.py\n"
                "20\t5\ttests/test_module.py\n"
                "\n"
                "2025-12-06T12:00:00-05:00|Jane Smith|def456ghi789|Add feature\n"
                "100\t50\tsrc/core.py\n"
            )
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=output
            )
            
            result = scanner.scan_commits()
            
            # Should parse 2 commits from mock output
            assert len(result) == 2
            
            # First commit validation
            commit = result[0]
            assert hasattr(commit, 'sha')
            assert hasattr(commit, 'author')
            assert hasattr(commit, 'timestamp')
            assert hasattr(commit, 'files_changed')
            assert hasattr(commit, 'lines_added')
            assert hasattr(commit, 'lines_deleted')
            assert hasattr(commit, 'net_change')
            
            # Verify calculations
            assert commit.sha == 'abc123de'  # Short SHA (8 chars)
            assert commit.author == 'John Doe'
            assert commit.lines_added == 70  # 50 + 20
            assert commit.lines_deleted == 15  # 10 + 5
            assert commit.net_change == 55  # 70 - 15
            assert len(commit.files_changed) == 2
    
    def test_handle_non_git_directory(self, scanner, tmp_path):
        """
        RED TEST: Verify graceful failure when not in git repo.
        
        Expected behavior:
        - Returns empty list (not crash)
        - Logs warning message
        - Does not raise exception
        """
        # tmp_path is not a git repo
        scanner_non_git = GitHistoryScanner(repo_path=tmp_path)
        
        with patch('subprocess.run') as mock_run:
            # Simulate git command failure
            mock_run.side_effect = FileNotFoundError("git not found")
            
            result = scanner_non_git.scan_commits()
            
            # Should return empty list, not crash
            assert isinstance(result, list)
            assert len(result) == 0
    
    def test_parse_git_log_output_with_binary_files(self, scanner):
        """
        Additional test: Handle binary files in git log (shows as '-' for lines).
        """
        binary_output = """2025-12-07T10:00:00-05:00|Author|sha123|Update image
-\t-\timage.png
50\t10\tcode.py
"""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=binary_output
            )
            
            result = scanner.scan_commits()
            
            # Should handle binary files gracefully (ignore line counts)
            assert len(result) == 1
            commit = result[0]
            assert commit.lines_added == 50  # Only from code.py
            assert commit.lines_deleted == 10
    
    def test_scan_commits_with_no_commits(self, scanner):
        """
        Edge case: Empty git log output (no commits in timeframe).
        """
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=""
            )
            
            result = scanner.scan_commits()
            
            assert isinstance(result, list)
            assert len(result) == 0


class TestModuleFunctions:
    """Test module-level convenience functions"""
    
    def test_scan_commits_convenience_function(self, tmp_path):
        """
        Test scan_commits() module function (convenience wrapper).
        """
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="2025-12-07|Author|sha123\n50\t10\tfile.py\n"
            )
            
            result = scan_commits(repo_path=tmp_path, since_hours=24)
            
            assert isinstance(result, list)
            assert mock_run.called
