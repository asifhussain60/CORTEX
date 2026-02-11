"""
Orchestrator Documentation Package

Provides capability documentation generation, search, and indexing.

Author: Asif Hussain
"""

from .capability_docs import (
    CapabilityDocGenerator,
    CapabilityDocumentation,
    CapabilityIndex,
    DocumentationMetadata,
    SearchResult,
)
from .orchestrator import (
    CleanupAction,
    CleanupReport,
    DiagramGenerationOrchestrator,
    DiagramSpec,
    DiagramType,
    DocumentationCleanupOrchestrator,
    DocumentationOrchestrator,
    GenerationReport,
    ObsoleteItem,
    OrphanedFile,
    Redundancy,
    RedundancyType,
    get_cleanup_orchestrator,
    get_diagram_generator,
    get_documentation_orchestrator,
)

__all__ = [
    # Existing
    "CapabilityDocumentation",
    "CapabilityDocGenerator",
    "CapabilityIndex",
    "DocumentationMetadata",
    "SearchResult",
    # New
    "DocumentationOrchestrator",
    "DiagramGenerationOrchestrator",
    "DocumentationCleanupOrchestrator",
    "get_documentation_orchestrator",
    "get_diagram_generator",
    "get_cleanup_orchestrator",
    "DiagramType",
    "CleanupAction",
    "RedundancyType",
    "DiagramSpec",
    "Redundancy",
    "OrphanedFile",
    "ObsoleteItem",
    "CleanupReport",
    "GenerationReport",
]
