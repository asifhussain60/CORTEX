"""
Vacuum Orchestrator Module - feat08-cleanup

Enhanced vacuum with generic pattern-based cleanup

Author: Asif Hussain
Version: 2.0.0
Created: 2026-01-08
"""

from src.orchestrators.vacuum.enhanced_vacuum import (
    VacuumOrchestrator,
    MultiRepoVacuum,
    CleanupPattern,
    CleanupCategory,
    CleanupItem,
    CleanupResult,
    generate_cleanup_report
)

from src.orchestrators.vacuum.structure_validator import (
    RepositoryStructureValidator,
    StructureViolation,
    StructureReport,
    generate_structure_report
)

__all__ = [
    "VacuumOrchestrator",
    "MultiRepoVacuum",
    "CleanupPattern",
    "CleanupCategory",
    "CleanupItem",
    "CleanupResult",
    "generate_cleanup_report",
    "RepositoryStructureValidator",
    "StructureViolation",
    "StructureReport",
    "generate_structure_report"
]

__version__ = "2.0.0"
