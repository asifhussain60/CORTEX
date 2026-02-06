"""Comprehensive tests for cache key builder module.

Tests cache key generation:
- Determinism (same inputs → same keys)
- Uniqueness (different inputs → different keys)
- Git integration (detects repo state changes)
- Error handling (missing repo, no git)
"""

import pytest
import hashlib
from pathlib import Path
from unittest.mock import patch, MagicMock
from cortex.lens.cache.cache_key_builder import (
    build_cache_key,
    get_repo_state_hash,
    detect_changes,
    _get_git_head,
    _get_latest_mtime,
    _count_source_files
)


class TestBuildCacheKey:
    """Test cache key generation from request context."""

    def test_build_cache_key_returns_valid_sha256(self) -> None:
        """build_cache_key() should return valid SHA256 hex string."""
        key = build_cache_key(
            user_request="analyze module.py",
            repo_path="/repo",
            lens_version="2.0"
        )
        
        # SHA256 produces 64 hex characters
        assert isinstance(key, str)
        assert len(key) == 64
        assert all(c in "0123456789abcdef" for c in key)

    def test_same_context_generates_same_key(self) -> None:
        """Identical contexts should generate identical cache keys."""
        request = "analyze module.py"
        repo = "/repo"
        version = "2.0"
        
        key1 = build_cache_key(request, repo, version)
        key2 = build_cache_key(request, repo, version)
        
        # Deterministic: same inputs → same output
        assert key1 == key2

    def test_different_requests_generate_different_keys(self) -> None:
        """Different requests should generate different keys."""
        repo = "/repo"
        version = "2.0"
        
        key1 = build_cache_key("analyze module.py", repo, version)
        key2 = build_cache_key("analyze other.py", repo, version)
        
        assert key1 != key2

    def test_different_versions_generate_different_keys(self) -> None:
        """Different LENS versions should generate different keys."""
        request = "analyze module.py"
        repo = "/repo"
        
        key1 = build_cache_key(request, repo, "2.0")
        key2 = build_cache_key(request, repo, "2.1")
        
        assert key1 != key2

    @patch('cortex.lens.cache.cache_key_builder.get_repo_state_hash')
    def test_fallback_on_repo_state_error(self, mock_hash) -> None:
        """Should handle errors in repo state hashing gracefully."""
        mock_hash.side_effect = Exception("Git error")
        
        # Should not raise, should fallback to path hash
        key = build_cache_key("analyze", "/repo", "2.0")
        
        assert isinstance(key, str)
        assert len(key) == 64


class TestGetRepoStateHash:
    """Test repository state hash generation."""

    def test_returns_valid_hash_format(self) -> None:
        """get_repo_state_hash() should return 32-char hex string."""
        # Use actual CORTEX repo
        hash_val = get_repo_state_hash("/Users/asifhussain/PROJECTS/CORTEX")
        
        assert isinstance(hash_val, str)
        assert len(hash_val) == 32  # First 32 chars of SHA256
        assert all(c in "0123456789abcdef" for c in hash_val)

    def test_raises_on_missing_repo(self) -> None:
        """Should raise ValueError for non-existent repository."""
        with pytest.raises(ValueError, match="does not exist"):
            get_repo_state_hash("/nonexistent/path")

    @patch('cortex.lens.cache.cache_key_builder._get_git_head')
    @patch('cortex.lens.cache.cache_key_builder._get_latest_mtime')
    @patch('cortex.lens.cache.cache_key_builder._count_source_files')
    def test_combines_git_and_file_stats(self, mock_count, mock_mtime, mock_git, tmp_path) -> None:
        """Should combine git HEAD, mtime, and file count in hash."""
        mock_git.return_value = "abc12345"
        mock_mtime.return_value = "1234567890"
        mock_count.return_value = "42"
        
        # Create a valid temporary repo path
        (tmp_path / "module.py").write_text("# test")
        
        hash_val = get_repo_state_hash(str(tmp_path))
        
        # Verify all components were called
        mock_git.assert_called_once()
        mock_mtime.assert_called_once()
        mock_count.assert_called_once()
        
        # Hash should be deterministic based on these inputs
        expected_string = "abc12345:1234567890:42"
        expected_hash = hashlib.sha256(expected_string.encode()).hexdigest()[:32]
        assert hash_val == expected_hash


class TestDetectChanges:
    """Test repository change detection."""

    def test_detects_no_changes_same_hash(self) -> None:
        """Should return False when hashes match."""
        hash_val = "abc123def456"
        assert detect_changes(hash_val, hash_val) is False

    def test_detects_changes_different_hash(self) -> None:
        """Should return True when hashes differ."""
        old = "abc123"
        new = "def456"
        assert detect_changes(old, new) is True

    def test_works_with_sha256_hashes(self) -> None:
        """Should work with real SHA256 hash values."""
        hash1 = hashlib.sha256(b"state1").hexdigest()
        hash2 = hashlib.sha256(b"state2").hexdigest()
        
        # Same hash
        assert detect_changes(hash1, hash1) is False
        
        # Different hashes
        assert detect_changes(hash1, hash2) is True


class TestGetGitHead:
    """Test git HEAD commit extraction."""

    @patch('subprocess.run')
    def test_returns_short_sha(self, mock_run) -> None:
        """Should return first 8 chars of git commit SHA."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "abc123def456abcd\n"
        mock_run.return_value = mock_result
        
        sha = _get_git_head(Path("/repo"))
        
        assert sha == "abc123de"  # First 8 chars

    @patch('subprocess.run')
    def test_fallback_on_git_error(self, mock_run) -> None:
        """Should fallback to path hash if git fails."""
        mock_run.side_effect = FileNotFoundError()
        
        sha = _get_git_head(Path("/repo"))
        
        # Should return fallback hash
        assert isinstance(sha, str)
        assert len(sha) == 8

    @patch('subprocess.run')
    def test_fallback_on_git_timeout(self, mock_run) -> None:
        """Should fallback if git command times out."""
        from subprocess import TimeoutExpired
        mock_run.side_effect = TimeoutExpired("git", 2)
        
        sha = _get_git_head(Path("/repo"))
        
        assert isinstance(sha, str)
        assert len(sha) == 8


class TestGetLatestMtime:
    """Test file modification time detection."""

    def test_finds_latest_mtime_in_repo(self, tmp_path) -> None:
        """Should find the newest file modification time."""
        # Create test files with different mtimes
        file1 = tmp_path / "old.py"
        file1.write_text("# old")
        
        import time
        time.sleep(0.1)
        
        file2 = tmp_path / "new.py"
        file2.write_text("# new")
        
        mtime = _get_latest_mtime(tmp_path)
        
        assert isinstance(mtime, str)
        assert mtime.isdigit()
        assert int(mtime) > 0

    def test_skips_git_directory(self, tmp_path) -> None:
        """Should skip files in .git directory."""
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        git_file = git_dir / "config"
        git_file.write_text("git config")
        
        py_file = tmp_path / "module.py"
        py_file.write_text("# python")
        
        mtime = _get_latest_mtime(tmp_path)
        
        # Should use py_file mtime, not git_file
        assert isinstance(mtime, str)

    def test_handles_empty_repo(self, tmp_path) -> None:
        """Should handle repository with no Python files."""
        mtime = _get_latest_mtime(tmp_path)
        
        assert mtime == "0"


class TestCountSourceFiles:
    """Test source file counting."""

    def test_counts_python_files(self, tmp_path) -> None:
        """Should count .py files in repository."""
        (tmp_path / "module1.py").write_text("# code")
        (tmp_path / "module2.py").write_text("# code")
        (tmp_path / "README.md").write_text("# readme")
        
        count = _count_source_files(tmp_path)
        
        assert count == "2"

    def test_counts_recursively(self, tmp_path) -> None:
        """Should count files in subdirectories."""
        (tmp_path / "mod1.py").write_text("# code")
        sub = tmp_path / "subdir"
        sub.mkdir()
        (sub / "mod2.py").write_text("# code")
        
        count = _count_source_files(tmp_path)
        
        assert count == "2"

    def test_handles_empty_repo(self, tmp_path) -> None:
        """Should return '0' for repository with no Python files."""
        count = _count_source_files(tmp_path)
        
        assert count == "0"


class TestIntegration:
    """Integration tests for full cache key workflow."""

    def test_full_workflow_same_repo_state(self) -> None:
        """Full workflow: same repo → same cache key."""
        repo = "/Users/asifhussain/PROJECTS/CORTEX"
        request = "analyze cortex.py"
        
        # First request
        key1 = build_cache_key(request, repo, "2.0")
        
        # Second request (identical context)
        key2 = build_cache_key(request, repo, "2.0")
        
        assert key1 == key2

    def test_version_invalidation(self) -> None:
        """Different LENS versions should invalidate cache."""
        repo = "/Users/asifhussain/PROJECTS/CORTEX"
        request = "analyze cortex.py"
        
        key_v2_0 = build_cache_key(request, repo, "2.0")
        key_v2_1 = build_cache_key(request, repo, "2.1")
        
        # Version change should invalidate
        assert key_v2_0 != key_v2_1
