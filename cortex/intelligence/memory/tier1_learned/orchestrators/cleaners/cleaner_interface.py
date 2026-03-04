"""Cleaner Interface for Vacuum Operations

Base interface for all cleanup operations in CORTEX vacuum system.

Author: CORTEX Framework
Phase: PHASE-VACUUM-REFACTOR S1
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""
# CORE-035 — domain-scoped; class name appropriate for this module

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class CleanupResult:  # CORE-035-scoped — domain-specific variant
    """Result of cleanup operation.

    Attributes:
        files_removed: List of file paths removed
        files_skipped: List of file paths skipped
        bytes_freed: Total bytes freed
        errors: List of error messages
    """

    files_removed: List[Path]
    files_skipped: List[Path]
    bytes_freed: int
    errors: List[str]

    @property
    def success(self) -> bool:
        """Check if cleanup was successful.

        Returns:
            True if no errors occurred
        """
        return len(self.errors) == 0

    @property
    def files_removed_count(self) -> int:
        """Get count of removed files.

        Returns:
            Number of files removed
        """
        return len(self.files_removed)


class CleanerInterface(ABC):
    """Abstract base class for all cleaners.

    All vacuum cleaners must implement this interface.
    """

    @abstractmethod
    def get_name(self) -> str:
        """Get cleaner name.

        Returns:
            Human-readable cleaner name
        """
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Get cleaner description.

        Returns:
            Description of what this cleaner does
        """
        pass

    @abstractmethod
    def clean(self, repo_path: Path, dry_run: bool = False) -> CleanupResult:
        """Execute cleanup operation.

        Args:
            repo_path: Path to repository root
            dry_run: If True, don't actually delete files

        Returns:
            Cleanup result with files removed/skipped
        """
        pass

    @abstractmethod
    def get_targets(self, repo_path: Path) -> List[Path]:
        """Get list of files that would be cleaned.

        Args:
            repo_path: Path to repository root

        Returns:
            List of file paths that match cleanup criteria
        """
        pass
