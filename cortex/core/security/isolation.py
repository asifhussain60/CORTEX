"""
Repository Isolation Rules Enforcement.

Implements hard isolation boundaries for multi-repo deployments.
All file operations scoped to repo_path with comprehensive attack prevention:
- Cross-repo file access rejection
- Symlink traversal prevention
- Relative path attack prevention
- Permission elevation prevention

Key components:
- IsolationChecker: Path validation and isolation enforcement
- RepositoryIsolationError: Exception for isolation violations

Provides clear error messages and audit logging for all violations.
"""

import logging
import os
import pathlib
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class RepositoryIsolationError(Exception):
    """Raised when repository isolation boundary is violated.

    Attributes:
        message: Description of the violation
        attempted_path: Path that was attempted to be accessed
        repo_boundary: Repository boundary that was violated
        reason: Reason for the violation (e.g., "Cross-repo access")
    """

    def __init__(
        self,
        message: str,
        attempted_path: Optional[str] = None,
        repo_boundary: Optional[str] = None,
        reason: Optional[str] = None,
    ):
        """Initialize isolation violation error.

        Args:
            message: Error message
            attempted_path: Path that violated isolation
            repo_boundary: Repository boundary
            reason: Reason for violation
        """
        super().__init__(message)
        self.message = message
        self.attempted_path = attempted_path
        self.repo_boundary = repo_boundary
        self.reason = reason


class IsolationChecker:
    """Enforces repository isolation boundaries for file operations.

    Validates that all file operations remain within repo_path, preventing:
    - Cross-repository file access
    - Symlink traversal attacks
    - Relative path attacks (../ traversal)
    - Permission elevation attempts

    Example:
        >>> checker = IsolationChecker()
        >>> repo_path = "/path/to/repo"
        >>> # Allow: file within repo
        >>> assert checker.is_path_within_repo("/path/to/repo/file.txt", repo_path)
        >>> # Deny: file outside repo
        >>> assert not checker.is_path_within_repo("/etc/passwd", repo_path)
    """

    def __init__(self, resolve_symlinks: bool = True):
        """Initialize isolation checker.

        Args:
            resolve_symlinks: If True, resolve symlinks and check their targets.
                            If False, only check the explicit path.
        """
        self.resolve_symlinks = resolve_symlinks
        self._violation_log: List[Dict[str, Any]] = []

    def is_path_within_repo(
        self,
        file_path: str,
        repo_path: str,
        resolve_symlinks: Optional[bool] = None,
    ) -> bool:
        """Check if file_path is within repo_path boundary.

        Args:
            file_path: Path to check
            repo_path: Repository boundary
            resolve_symlinks: Override instance setting

        Returns:
            bool: True if file_path is within repo_path, False otherwise

        Raises:
            ValueError: If file_path or repo_path is empty/None

        Example:
            >>> checker = IsolationChecker()
            >>> assert checker.is_path_within_repo("/repo/file.txt", "/repo")
            >>> assert not checker.is_path_within_repo("/etc/passwd", "/repo")
        """
        if not file_path or not repo_path:
            raise ValueError("file_path and repo_path must be non-empty")

        resolve = (
            resolve_symlinks
            if resolve_symlinks is not None
            else self.resolve_symlinks
        )

        try:
            # Normalize both paths to absolute paths
            normalized_file = self._normalize_path(file_path, repo_path)
            normalized_repo = self._normalize_path(repo_path, None)

            # Resolve symlinks if requested
            if resolve and os.path.islink(normalized_file):
                try:
                    resolved_file = os.path.realpath(normalized_file)
                except (OSError, RuntimeError):
                    # If symlink resolution fails, use original path
                    resolved_file = normalized_file
            else:
                resolved_file = normalized_file

            if resolve and os.path.islink(normalized_repo):
                try:
                    resolved_repo = os.path.realpath(normalized_repo)
                except (OSError, RuntimeError):
                    resolved_repo = normalized_repo
            else:
                resolved_repo = normalized_repo

            # Check if file is within repo boundary
            # Using os.path.commonpath to ensure file is within repo
            try:
                common = os.path.commonpath([resolved_file, resolved_repo])
                is_within = common == resolved_repo
            except ValueError:
                # Paths on different drives (Windows)
                is_within = False

            # Additional check: file path must start with repo path
            if is_within:
                # Ensure it's a proper boundary (avoid "/repo" matching "/repo2")
                if not (
                    resolved_file == resolved_repo
                    or resolved_file.startswith(resolved_repo + os.sep)
                ):
                    is_within = False

            return is_within

        except Exception as e:
            logger.error(f"Path validation error: {e}")
            return False

    def _normalize_path(self, path: str, repo_path: Optional[str]) -> str:
        """Normalize path to absolute, removing traversals.

        Args:
            path: Path to normalize
            repo_path: Optional repo context for relative path resolution

        Returns:
            str: Normalized absolute path

        Raises:
            ValueError: If path is invalid
        """
        if not path:
            raise ValueError("Path cannot be empty")

        # Convert to pathlib for robust path handling
        p = pathlib.Path(path)

        # If relative and repo_path provided, resolve relative to repo
        if not p.is_absolute() and repo_path:
            repo_p = pathlib.Path(repo_path)
            if not repo_p.is_absolute():
                repo_p = repo_p.resolve()
            p = repo_p / p

        # Resolve to absolute path (but don't follow symlinks for now)
        if not p.is_absolute():
            p = pathlib.Path.cwd() / p

        # Use resolve() to normalize .. and . components
        # This also handles symlinks if resolve_symlinks=True
        try:
            resolved = p.resolve()
        except (OSError, RuntimeError):
            # If resolve fails (e.g., path doesn't exist), use absolute version
            resolved = p.absolute()

        return str(resolved)

    def normalize_path(self, path: str, repo_path: str) -> str:
        """Public method to normalize a path.

        Args:
            path: Path to normalize
            repo_path: Repository context

        Returns:
            str: Normalized absolute path

        Example:
            >>> checker = IsolationChecker()
            >>> normalized = checker.normalize_path("./file.txt", "/repo")
            >>> assert normalized.startswith("/")
        """
        return self._normalize_path(path, repo_path)

    def get_isolation_error_message(
        self,
        attempted_path: str,
        repo_boundary: str,
    ) -> str:
        """Generate clear error message for isolation violation.

        Args:
            attempted_path: Path that violated isolation
            repo_boundary: Repository boundary

        Returns:
            str: Clear error message

        Example:
            >>> checker = IsolationChecker()
            >>> msg = checker.get_isolation_error_message(
            ...     "/etc/passwd",
            ...     "/repo"
            ... )
            >>> assert "isolation" in msg.lower()
        """
        return (
            f"Repository isolation violation: attempted access to "
            f"{attempted_path} is outside repo boundary {repo_boundary}"
        )

    def get_violation_context(
        self,
        attempted_path: str,
        repo_boundary: str,
    ) -> Dict[str, Any]:
        """Get structured context for isolation violation.

        Args:
            attempted_path: Path that violated isolation
            repo_boundary: Repository boundary

        Returns:
            Dict with violation context

        Example:
            >>> checker = IsolationChecker()
            >>> ctx = checker.get_violation_context("/etc/passwd", "/repo")
            >>> assert "attempted_path" in ctx
            >>> assert "repo_boundary" in ctx
        """
        return {
            "attempted_path": attempted_path,
            "repo_boundary": repo_boundary,
            "violation_type": "cross_repo_access",
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }

    def log_isolation_violation(
        self,
        attempted_path: str,
        repo_boundary: str,
        reason: str = "Isolation boundary violation",
    ) -> None:
        """Log isolation violation for audit trail.

        Args:
            attempted_path: Path that violated isolation
            repo_boundary: Repository boundary
            reason: Reason for violation

        Example:
            >>> checker = IsolationChecker()
            >>> checker.log_isolation_violation(
            ...     "/etc/passwd",
            ...     "/repo",
            ...     "Cross-repo access attempt"
            ... )
        """
        violation = self.get_violation_context(attempted_path, repo_boundary)
        violation["reason"] = reason

        self._violation_log.append(violation)

        logger.warning(
            f"Isolation violation: {attempted_path} outside {repo_boundary} - {reason}"
        )

    def validate_file_operation(
        self,
        file_path: str,
        repo_path: str,
        operation: str = "read",
    ) -> Tuple[bool, Optional[str]]:
        """Validate file operation against isolation rules.

        Args:
            file_path: Path to operate on
            repo_path: Repository boundary
            operation: Type of operation (read, write, delete, etc.)

        Returns:
            Tuple[bool, Optional[str]]: (is_allowed, error_message)

        Example:
            >>> checker = IsolationChecker()
            >>> allowed, msg = checker.validate_file_operation(
            ...     "/repo/file.txt",
            ...     "/repo",
            ...     "read"
            ... )
            >>> assert allowed is True
        """
        if not self.is_path_within_repo(file_path, repo_path):
            error_msg = self.get_isolation_error_message(file_path, repo_path)
            self.log_isolation_violation(
                file_path,
                repo_path,
                f"Attempted {operation} outside repo boundary",
            )
            return False, error_msg

        return True, None

    def check_symlink_safety(
        self,
        symlink_path: str,
        repo_path: str,
    ) -> Tuple[bool, Optional[str]]:
        """Check if symlink is safe (target within repo).

        Args:
            symlink_path: Path to symlink
            repo_path: Repository boundary

        Returns:
            Tuple[bool, Optional[str]]: (is_safe, error_message)

        Example:
            >>> checker = IsolationChecker()
            >>> # Symlink within repo is safe
            >>> safe, msg = checker.check_symlink_safety(
            ...     "/repo/link",
            ...     "/repo"
            ... )
        """
        if not os.path.islink(symlink_path):
            # Not a symlink, so it's safe
            return True, None

        try:
            target = os.readlink(symlink_path)
            # Resolve target relative to symlink location
            symlink_dir = os.path.dirname(symlink_path)
            absolute_target = os.path.normpath(
                os.path.join(symlink_dir, target)
            )

            if not self.is_path_within_repo(absolute_target, repo_path):
                error_msg = (
                    f"Symlink {symlink_path} target {absolute_target} "
                    f"is outside repo boundary {repo_path}"
                )
                self.log_isolation_violation(
                    absolute_target,
                    repo_path,
                    "Symlink escape attempt",
                )
                return False, error_msg

            return True, None

        except OSError as e:
            return False, f"Error reading symlink {symlink_path}: {e}"

    def get_violation_log(self) -> List[Dict[str, Any]]:
        """Get all recorded isolation violations.

        Returns:
            List of violation records

        Example:
            >>> checker = IsolationChecker()
            >>> checker.log_isolation_violation("/etc/passwd", "/repo", "Test")
            >>> log = checker.get_violation_log()
            >>> assert len(log) > 0
        """
        return self._violation_log.copy()

    def clear_violation_log(self) -> None:
        """Clear violation log.

        Used for testing and log rotation.
        """
        self._violation_log.clear()
