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
    TempScriptCleaner: Clean phase-specific and ad-hoc scripts
    OrphanedTestCleaner: Clean misplaced test files
    ArchivedPhaseExecutorCleaner: Clean old archived phase executors
    BuildArtifactCleaner: Clean build artifacts (obj/, bin/, __pycache__)

Usage:
    ```python
    from tier1.orchestrators.cleaners import (
        CleanerRegistry,
        RootDatabaseCleaner,
        TempScriptCleaner,
        OrphanedTestCleaner,
        ArchivedPhaseExecutorCleaner,
        BuildArtifactCleaner,
    )
    
    registry = CleanerRegistry()
    cleaner = RootDatabaseCleaner(config)
    registry.register(cleaner)
    ```

Author: CORTEX Architect
Phase: PHASE-VAC-001-05 | Phase 104 Enhancement
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
from .temp_script import TempScriptCleaner
from .orphaned_test import OrphanedTestCleaner
from .archived_phase_executor import ArchivedPhaseExecutorCleaner
from .build_artifact import BuildArtifactCleaner

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
    "TempScriptCleaner",
    "OrphanedTestCleaner",
    "ArchivedPhaseExecutorCleaner",
    "BuildArtifactCleaner",
    # Backward compatibility
    "DatabaseMigrationCleaner",
]
