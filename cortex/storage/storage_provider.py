"""
Storage provider abstract interface.
Authority: Phase 50 Stage 1 - Storage Backend Abstraction
AC-PHASE50-S1-001: IKnowledgeProvider defines all storage operations
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional


class IKnowledgeProvider(ABC):
    """
    Abstract interface for knowledge storage backends.

    Implementations:
    - LocalFileSystemProvider: File system storage
    - S3StorageProvider: AWS S3 storage
    - AzureBlobProvider: Azure Blob Storage
    - CachedKnowledgeProvider: Decorator for caching
    """

    @abstractmethod
    def read(self, path: str) -> str:
        """
        Read knowledge content from storage.

        Args:
            path: Logical path (e.g., "company/domains/engineering.yaml")

        Returns:
            File content as string

        Raises:
            StorageError: If path not found or permission denied
            NetworkError: If remote storage unavailable
        """
        pass

    @abstractmethod
    def write(self, path: str, content: str) -> None:
        """
        Write knowledge content to storage.

        Args:
            path: Logical path
            content: Content to write

        Raises:
            StorageError: If write fails
            PermissionError: If insufficient permissions
        """
        pass

    @abstractmethod
    def list(self, path: str) -> List[str]:
        """
        List entries in a directory.

        Args:
            path: Directory path

        Returns:
            List of entry names (relative paths)
        """
        pass

    @abstractmethod
    def exists(self, path: str) -> bool:
        """
        Check if a path exists in storage.

        Args:
            path: Logical path

        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    def delete(self, path: str) -> None:
        """
        Delete an entry from storage.

        Args:
            path: Logical path

        Raises:
            StorageError: If deletion fails
        """
        pass
