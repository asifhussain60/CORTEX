"""Cleaners Package — Plugin architecture for vacuum operations.

This package provides the base interfaces and registry for vacuum cleaner
plugins. Each cleaner is responsible for a specific cleanup domain.

Public API:
    CleanerInterface: ABC for all cleaner implementations
    CleanerRegistry: Plugin registration and retrieval
    Analysis, Report, RollbackResult: Data models
    RootDatabaseCleaner: Clean orphaned root databases
    RootArtifactsCleaner: Relocate root artifacts
    MarkdownSprawlCleaner: Remove temporary markdown files

Usage:
    ```python
    from tier1.orchestrators.cleaners import (
        CleanerRegistry,
        RootDatabaseCleaner,
    )
    
    registry = CleanerRegistry()
    cleaner = RootDatabaseCleaner(config)
    registry.register(cleaner)
    ```

Author: CORTEX Architect
Phase: PHASE-VAC-001-05
"""

# Import base classes from our new plugin architecture
from .base import (
    CleanerInterface,
    Analysis,
    Report,
    RollbackResult,
)
from .registry import CleanerRegistry

# Import cleaner implementations
from .root_database import RootDatabaseCleaner
from .root_artifacts import RootArtifactsCleaner
from .markdown_sprawl import MarkdownSprawlCleaner

# Backward compatibility aliases
DatabaseMigrationCleaner = RootDatabaseCleaner  # Old name for compatibility

__all__ = [
    # Base classes
    "CleanerInterface",
    "CleanerRegistry",
    "Analysis",
    "Report",
    "RollbackResult",
    # Cleaner implementations
    "RootDatabaseCleaner",
    "RootArtifactsCleaner",
    "MarkdownSprawlCleaner",
    # Backward compatibility
    "DatabaseMigrationCleaner",
]
