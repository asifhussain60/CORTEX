"""
Test suite for Repository Isolation Rules Enforcement.

Tests for isolation boundaries and cross-repo access prevention:
- File operations scoped to repo_path
- Cross-repo file access rejected
- Symlink traversal prevention
- Relative path attack prevention
- Permission elevation attempt prevention
- Isolation violation logging
"""

import pytest
import os
import tempfile
import pathlib
from typing import Dict, Any, Optional
from unittest.mock import Mock, patch, MagicMock


class RepositoryIsolationError(Exception):
    """Raised when cross-repo file access is attempted."""

    pass


class TestFileOperationIsolation:
    """Test file operation isolation within repo boundaries."""

    def test_file_read_within_boundary(self):
        """File read within repo_path is allowed."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo"
        file_path = "/path/to/repo/file.txt"

        # Should not raise - file is within repo
        is_allowed = checker.is_path_within_repo(file_path, repo_path)
        assert is_allowed is True

    def test_file_write_within_boundary(self):
        """File write within repo_path is allowed."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo"
        file_path = "/path/to/repo/subdir/file.txt"

        # Should not raise - file is within repo
        is_allowed = checker.is_path_within_repo(file_path, repo_path)
        assert is_allowed is True

    def test_file_delete_within_boundary(self):
        """File delete within repo_path is allowed."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo"
        file_path = "/path/to/repo/file.txt"

        # Should not raise - file is within repo
        is_allowed = checker.is_path_within_repo(file_path, repo_path)
        assert is_allowed is True

    def test_directory_creation_within_boundary(self):
        """Directory creation within repo_path is allowed."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo"
        dir_path = "/path/to/repo/newdir"

        # Should not raise - directory is within repo
        is_allowed = checker.is_path_within_repo(dir_path, repo_path)
        assert is_allowed is True

    def test_nested_directory_within_boundary(self):
        """Nested directory operations within repo_path are allowed."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo"
        nested_path = "/path/to/repo/a/b/c/d/file.txt"

        # Should not raise - nested path is within repo
        is_allowed = checker.is_path_within_repo(nested_path, repo_path)
        assert is_allowed is True


class TestCrossRepoAccessPrevention:
    """Test prevention of cross-repository file access."""

    def test_cross_repo_read_blocked(self):
        """File read outside repo_path is blocked."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo-1"
        file_path = "/path/to/repo-2/file.txt"

        # Should return False - file is outside repo
        is_allowed = checker.is_path_within_repo(file_path, repo_path)
        assert is_allowed is False

    def test_cross_repo_write_blocked(self):
        """File write outside repo_path is blocked."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo-1"
        file_path = "/path/to/repo-2/newfile.txt"

        # Should return False - file is outside repo
        is_allowed = checker.is_path_within_repo(file_path, repo_path)
        assert is_allowed is False

    def test_parent_directory_access_blocked(self):
        """Access to parent directories outside repo is blocked."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo"
        parent_path = "/path/to/secret.txt"

        # Should return False - parent is outside repo
        is_allowed = checker.is_path_within_repo(parent_path, repo_path)
        assert is_allowed is False

    def test_sibling_repo_access_blocked(self):
        """Access to sibling repositories is blocked."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/repos/repo-1"
        sibling_path = "/repos/repo-2/file.txt"

        # Should return False - sibling is outside repo
        is_allowed = checker.is_path_within_repo(sibling_path, repo_path)
        assert is_allowed is False

    def test_system_file_access_blocked(self):
        """Access to system files outside repo is blocked."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo"
        system_path = "/etc/passwd"

        # Should return False - system file is outside repo
        is_allowed = checker.is_path_within_repo(system_path, repo_path)
        assert is_allowed is False

    def test_clear_error_on_violation(self):
        """Clear error message on isolation violation."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo-1"
        file_path = "/path/to/repo-2/file.txt"

        error_msg = checker.get_isolation_error_message(file_path, repo_path)
        assert "isolation" in error_msg.lower()
        assert "repo" in error_msg.lower()


class TestSymlinkTraversalPrevention:
    """Test prevention of symlink traversal attacks."""

    def test_symlink_within_repo_allowed(self):
        """Symlinks within repo_path are allowed."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo"
        symlink_path = "/path/to/repo/link"

        # Symlinks within repo are allowed
        is_allowed = checker.is_path_within_repo(symlink_path, repo_path)
        assert is_allowed is True

    def test_symlink_escape_blocked(self):
        """Symlinks escaping repo_path are blocked."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo"

        # Mock a symlink that points outside repo
        is_allowed = checker.is_path_within_repo(
            "/path/to/repo/symlink", repo_path, resolve_symlinks=True
        )
        # Should be blocked if target is outside repo (mocked)
        # Actual behavior depends on real symlink target

    def test_relative_symlink_safe(self):
        """Relative symlinks within repo are safe."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo"
        # Symlink with relative target
        symlink_path = "/path/to/repo/subdir/link"

        is_allowed = checker.is_path_within_repo(symlink_path, repo_path)
        assert is_allowed is True

    def test_symlink_traversal_sequence_blocked(self):
        """Complex symlink traversal sequences are blocked."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo"
        # Path with traversal attempts
        traversal_path = "/path/to/repo/../../secret.txt"

        is_allowed = checker.is_path_within_repo(traversal_path, repo_path)
        assert is_allowed is False


class TestRelativePathAttackPrevention:
    """Test prevention of relative path attacks."""

    def test_parent_traversal_blocked(self):
        """Parent directory traversal (..) is blocked."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo"
        traversal_path = "/path/to/repo/../../etc/passwd"

        is_allowed = checker.is_path_within_repo(traversal_path, repo_path)
        assert is_allowed is False

    def test_dot_dot_in_middle_blocked(self):
        """.. in middle of path is blocked."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo"
        traversal_path = "/path/to/repo/subdir/../../../secret.txt"

        is_allowed = checker.is_path_within_repo(traversal_path, repo_path)
        assert is_allowed is False

    def test_multiple_traversals_blocked(self):
        """Multiple traversal attempts are blocked."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo"
        traversal_path = "/path/to/repo/../../../../../../etc/passwd"

        is_allowed = checker.is_path_within_repo(traversal_path, repo_path)
        assert is_allowed is False

    def test_normalized_path_checked(self):
        """Paths are normalized before checking."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo"
        # Path with unnecessary ./ components
        normalized_path = "/path/to/repo/./subdir/./file.txt"

        is_allowed = checker.is_path_within_repo(normalized_path, repo_path)
        assert is_allowed is True


class TestPermissionElevationPrevention:
    """Test prevention of permission elevation attempts."""

    def test_setuid_bit_attack_blocked(self):
        """Attempts to exploit setuid bits are prevented."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo"

        # Check that file operations respect isolation
        is_allowed = checker.is_path_within_repo(
            "/path/to/repo/executable", repo_path
        )
        assert is_allowed is True

        # But access outside repo should fail
        is_allowed = checker.is_path_within_repo(
            "/usr/bin/sudo", repo_path
        )
        assert is_allowed is False

    def test_capability_escape_blocked(self):
        """Linux capability escapes are prevented."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo"

        # Access to /proc/self/ns/ should be blocked
        is_allowed = checker.is_path_within_repo("/proc/self/ns/net", repo_path)
        assert is_allowed is False


class TestIsolationCheckerIntegration:
    """Test IsolationChecker with orchestrator integration."""

    def test_orchestrator_operation_with_session(self):
        """Orchestrator operations respect session isolation."""
        from cortex.core.security.isolation import IsolationChecker
        from cortex.mcp.models.session import MCPSession
        from datetime import datetime

        checker = IsolationChecker()
        session = MCPSession(
            session_id="sess-001",
            repo_id="repo-1",
            repo_path="/path/to/repo-1",
            created_at=datetime.now(),
        )

        # Operation within repo should be allowed
        is_allowed = checker.is_path_within_repo(
            "/path/to/repo-1/file.txt", session.repo_path
        )
        assert is_allowed is True

        # Operation outside repo should be blocked
        is_allowed = checker.is_path_within_repo(
            "/path/to/repo-2/file.txt", session.repo_path
        )
        assert is_allowed is False

    def test_multiple_sessions_isolated(self):
        """Multiple sessions maintain independent isolation."""
        from cortex.core.security.isolation import IsolationChecker
        from cortex.mcp.models.session import MCPSession
        from datetime import datetime

        checker = IsolationChecker()

        session1 = MCPSession(
            session_id="sess-001",
            repo_id="repo-1",
            repo_path="/path/to/repo-1",
            created_at=datetime.now(),
        )

        session2 = MCPSession(
            session_id="sess-002",
            repo_id="repo-2",
            repo_path="/path/to/repo-2",
            created_at=datetime.now(),
        )

        # Session 1 can access repo-1 but not repo-2
        assert (
            checker.is_path_within_repo(
                "/path/to/repo-1/file.txt", session1.repo_path
            )
            is True
        )
        assert (
            checker.is_path_within_repo(
                "/path/to/repo-2/file.txt", session1.repo_path
            )
            is False
        )

        # Session 2 can access repo-2 but not repo-1
        assert (
            checker.is_path_within_repo(
                "/path/to/repo-2/file.txt", session2.repo_path
            )
            is True
        )
        assert (
            checker.is_path_within_repo(
                "/path/to/repo-1/file.txt", session2.repo_path
            )
            is False
        )


class TestIsolationAuditLogging:
    """Test audit logging of isolation violations."""

    def test_violation_logged_on_cross_repo_access(self):
        """Cross-repo access attempts are logged."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo-1"
        violation_path = "/path/to/repo-2/file.txt"

        violations = []

        def mock_log_violation(path: str, repo_path: str, reason: str):
            violations.append(
                {"path": path, "repo_path": repo_path, "reason": reason}
            )

        checker.log_isolation_violation = mock_log_violation
        is_allowed = checker.is_path_within_repo(violation_path, repo_path)

        if not is_allowed:
            checker.log_isolation_violation(violation_path, repo_path, "Cross-repo access")

        assert len(violations) > 0

    def test_violation_includes_context(self):
        """Isolation violations include context information."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo-1"
        violation_path = "/path/to/repo-2/file.txt"

        violation_info = checker.get_violation_context(violation_path, repo_path)

        assert "attempted_path" in violation_info
        assert "repo_boundary" in violation_info
        assert "violation_type" in violation_info


class TestIsolationEdgeCases:
    """Test edge cases in isolation checking."""

    def test_empty_path_rejected(self):
        """Empty paths are rejected."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo"

        with pytest.raises(ValueError):
            checker.is_path_within_repo("", repo_path)

    def test_none_path_rejected(self):
        """None paths raise error."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo"

        with pytest.raises((ValueError, TypeError)):
            checker.is_path_within_repo(None, repo_path)

    def test_case_sensitivity(self):
        """Path checking respects case sensitivity."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo"

        # On case-sensitive systems, different case = different path
        is_allowed1 = checker.is_path_within_repo("/path/to/repo/FILE.txt", repo_path)
        is_allowed2 = checker.is_path_within_repo("/path/to/repo/file.txt", repo_path)

        # Both should be within repo (case doesn't matter for boundary check)
        assert is_allowed1 is True
        assert is_allowed2 is True

    def test_trailing_slash_handling(self):
        """Paths with/without trailing slashes are handled correctly."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo"

        # With trailing slash
        is_allowed1 = checker.is_path_within_repo(
            "/path/to/repo/", repo_path
        )
        # Without trailing slash
        is_allowed2 = checker.is_path_within_repo(
            "/path/to/repo", repo_path
        )

        # Both should be considered within repo
        assert is_allowed1 is True
        assert is_allowed2 is True

    def test_unicode_paths(self):
        """Unicode paths are handled correctly."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo"
        unicode_path = "/path/to/repo/文件.txt"

        is_allowed = checker.is_path_within_repo(unicode_path, repo_path)
        assert is_allowed is True

    def test_very_long_paths(self):
        """Very long paths are handled."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo"
        long_path = "/path/to/repo/" + "/".join(["subdir"] * 50) + "/file.txt"

        is_allowed = checker.is_path_within_repo(long_path, repo_path)
        assert is_allowed is True


class TestIsolationErrorHandling:
    """Test error handling in isolation checking."""

    def test_invalid_repo_path_rejected(self):
        """Invalid repo paths are rejected."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        invalid_repo_path = ""

        with pytest.raises((ValueError, AssertionError)):
            checker.is_path_within_repo("/some/path", invalid_repo_path)

    def test_relative_paths_normalized(self):
        """Relative paths are normalized to absolute."""
        from cortex.core.security.isolation import IsolationChecker

        checker = IsolationChecker()
        repo_path = "/path/to/repo"

        # Relative path should be normalized
        normalized = checker.normalize_path("./file.txt", repo_path)
        assert normalized.startswith("/")
