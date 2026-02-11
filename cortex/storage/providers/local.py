"""Local filesystem storage provider."""

import os
import shutil
from pathlib import Path
from typing import List

from cortex.storage.config import StorageConfig
from cortex.storage.errors import (
    ConfigurationError,
    NotFoundError,
    PermissionError,
    StorageError,
)
from cortex.storage.provider import IKnowledgeProvider


class LocalFileSystemProvider(IKnowledgeProvider):
    """
    Local filesystem implementation of IKnowledgeProvider.

    Wraps local filesystem operations with abstraction layer,
    enabling seamless backend swapping to S3, Azure, etc.

    AC-PHASE50-S2-001: Wraps filesystem operations with abstraction
    AC-PHASE50-S2-002: Supports all IKnowledgeProvider methods
    AC-PHASE50-S2-003: Maps filesystem errors to StorageError hierarchy
    AC-PHASE50-S2-004: Prevents directory traversal attacks
    AC-PHASE50-S2-005: Supports relative and absolute paths
    """

    def __init__(self, config: StorageConfig) -> None:
        """
        Initialize LocalFileSystemProvider.

        Args:
            config: StorageConfig with backend="local" and endpoint=base_path

        Raises:
            ConfigurationError: If endpoint is None or invalid
        """
        # AC-PHASE50-S2-001: Store configuration
        if config.endpoint is None:
            raise ConfigurationError("LocalFileSystemProvider requires endpoint (base directory path)")

        self.config = config
        self.base_path = Path(config.endpoint).resolve()

        # AC-PHASE50-S2-001: Create base directory if missing
        try:
            self.base_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ConfigurationError(f"Failed to create base directory: {e}") from e

    def _resolve_path(self, path: str) -> Path:
        """
        Resolve and validate path.

        AC-PHASE50-S2-004: Prevent directory traversal attacks
        AC-PHASE50-S2-005: Support relative and absolute paths

        Args:
            path: Relative path within base directory

        Returns:
            Resolved absolute path

        Raises:
            PermissionError: If path traversal attempted
        """
        try:
            # Resolve relative to base path
            full_path = (self.base_path / path).resolve()

            # Verify path is within base directory
            if not str(full_path).startswith(str(self.base_path)):
                raise PermissionError(f"Path traversal detected: {path}")

            return full_path
        except PermissionError:
            raise
        except Exception as e:
            raise StorageError(f"Failed to resolve path {path}: {e}") from e

    def read(self, path: str) -> str:
        """
        Read file content.

        AC-PHASE50-S2-002: Implement read() method
        AC-PHASE50-S2-003: Map filesystem errors to StorageError hierarchy

        Args:
            path: Relative path to file

        Returns:
            File content as string

        Raises:
            NotFoundError: If file doesn't exist
            PermissionError: If access denied or path traversal attempted
            StorageError: On other filesystem errors
        """
        try:
            full_path = self._resolve_path(path)

            if not full_path.exists():
                raise NotFoundError(f"File not found: {path}")

            if not full_path.is_file():
                raise StorageError(f"Path is not a file: {path}")

            with open(full_path, "r") as f:
                return f.read()

        except (NotFoundError, PermissionError):
            raise
        except Exception as e:
            raise StorageError(f"Failed to read {path}: {e}") from e

    def write(self, path: str, content: str) -> None:
        """
        Write content to file.

        AC-PHASE50-S2-002: Implement write() method
        AC-PHASE50-S2-003: Map filesystem errors to StorageError hierarchy

        Args:
            path: Relative path to file
            content: Content to write

        Raises:
            PermissionError: If access denied or path traversal attempted
            StorageError: On other filesystem errors
        """
        try:
            full_path = self._resolve_path(path)

            # AC-PHASE50-S2-002: Create parent directories
            full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, "w") as f:
                f.write(content)

        except PermissionError:
            raise
        except Exception as e:
            raise StorageError(f"Failed to write {path}: {e}") from e

    def list(self, path: str) -> List[str]:
        """
        List directory contents.

        AC-PHASE50-S2-002: Implement list() method
        AC-PHASE50-S2-003: Map filesystem errors to StorageError hierarchy

        Args:
            path: Relative path to directory (empty string = root)

        Returns:
            List of relative paths (files and directories)

        Raises:
            NotFoundError: If directory doesn't exist
            PermissionError: If access denied or path traversal attempted
            StorageError: On other filesystem errors
        """
        try:
            full_path = self._resolve_path(path) if path else self.base_path

            if not full_path.exists():
                raise NotFoundError(f"Directory not found: {path}")

            if not full_path.is_dir():
                raise StorageError(f"Path is not a directory: {path}")

            entries = []
            for entry in full_path.iterdir():
                # Return relative paths
                relative = entry.relative_to(self.base_path)
                entries.append(str(relative))

            return sorted(entries)

        except (NotFoundError, PermissionError):
            raise
        except Exception as e:
            raise StorageError(f"Failed to list {path}: {e}") from e

    def exists(self, path: str) -> bool:
        """
        Check if path exists.

        AC-PHASE50-S2-002: Implement exists() method

        Args:
            path: Relative path to check

        Returns:
            True if path exists, False otherwise
        """
        try:
            full_path = self._resolve_path(path)
            return full_path.exists()
        except PermissionError:
            # Path traversal is treated as not existing
            return False
        except Exception:
            # Other errors return False
            return False

    def delete(self, path: str) -> None:
        """
        Delete file or directory.

        AC-PHASE50-S2-002: Implement delete() method
        AC-PHASE50-S2-003: Map filesystem errors to StorageError hierarchy

        Args:
            path: Relative path to delete

        Raises:
            NotFoundError: If path doesn't exist
            PermissionError: If access denied or path traversal attempted
            StorageError: On other filesystem errors
        """
        try:
            full_path = self._resolve_path(path)

            if not full_path.exists():
                raise NotFoundError(f"Path not found: {path}")

            if full_path.is_dir():
                # Remove directory and contents
                shutil.rmtree(full_path)
            else:
                # Remove file
                full_path.unlink()

        except (NotFoundError, PermissionError):
            raise
        except Exception as e:
            raise StorageError(f"Failed to delete {path}: {e}") from e
